import os
import tempfile
from typing import Dict, Any
import dashscope
from dashscope import MultiModalConversation, Generation
from config import Config
import logging
import base64

class AnalysisAgent:
    """Handles AI analysis of screenshots using DashScope native API"""

    def __init__(self):
        self.config = Config()
        self._init_dashscope()

    def _init_dashscope(self) -> None:
        """Initialize DashScope API"""
        try:
            # Set API key
            dashscope.api_key = self.config.get_api_key()

            # Set base URL (use Beijing region by default)
            dashscope.base_http_api_url = 'https://dashscope.aliyuncs.com/api/v1'

            logging.info("DashScope API initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize DashScope API: {str(e)}")
            raise

    def analyze_screenshot(self, image_base64: str, context: str = "") -> Dict[str, Any]:
        """
        Analyze a screenshot and generate activity description

        Args:
            image_base64 (str): Base64 encoded screenshot image
            context (str): Additional context for analysis

        Returns:
            Dict[str, Any]: Analysis results containing activity description
        """
        try:
            # Create prompt for activity analysis
            prompt = self._create_analysis_prompt(context)

            # Try data URL format first (most compatible)
            data_url = f"data:image/png;base64,{image_base64}"

            # Create DashScope native format message
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"image": data_url},
                        {"text": prompt}
                    ]
                }
            ]

            # Get thinking settings from config
            enable_thinking = self.config.get_enable_thinking()
            thinking_budget = self.config.get_thinking_budget()

            # Prepare API call parameters
            api_params = {
                "model": self.config.get_model_name(),
                "messages": messages,
                "stream": True,
            }

            # Only add thinking parameters if enabled
            if enable_thinking:
                api_params["enable_thinking"] = True
                api_params["thinking_budget"] = thinking_budget
                logging.info(f"Calling API with thinking enabled (budget: {thinking_budget})")
            else:
                logging.info("Calling API without thinking mode")

            # Call DashScope MultiModalConversation API
            response = MultiModalConversation.call(**api_params)

            # Check if response is None
            if response is None:
                raise Exception("API returned None - this may indicate the model does not support the requested features. Try disabling 'thinking mode' in settings.")

            # Process the streaming response
            reasoning_content = ""
            answer_content = ""
            is_answering = False

            for chunk in response:
                # Check if chunk has the expected structure
                if not hasattr(chunk, 'output') or not hasattr(chunk.output, 'choices'):
                    logging.warning(f"Unexpected chunk structure: {chunk}")
                    continue

                if not chunk.output.choices:
                    logging.warning("Empty choices in chunk")
                    continue

                # Handle empty responses
                message = chunk.output.choices[0].message
                reasoning_content_chunk = message.get("reasoning_content", None)

                if (chunk.output.choices[0].message.content == [] and reasoning_content_chunk == ""):
                    continue
                else:
                    # If thinking process
                    if reasoning_content_chunk is not None and chunk.output.choices[0].message.content == []:
                        reasoning_content += chunk.output.choices[0].message.reasoning_content
                    # If answer content
                    elif chunk.output.choices[0].message.content != []:
                        is_answering = True
                        answer_content += chunk.output.choices[0].message.content[0]["text"]

            # Return the collected answer
            if answer_content.strip():
                return {
                    "activity_description": answer_content.strip(),
                    "confidence": "high",
                    "analysis_successful": True,
                    "error": None
                }
            else:
                raise Exception("No answer content received from API")

        except AttributeError as e:
            error_msg = f"API response format error: {str(e)}. The model may not support thinking mode. Try disabling it in settings."
            logging.error(error_msg)
            return {
                "activity_description": "Analysis failed",
                "confidence": "low",
                "analysis_successful": False,
                "error": error_msg
            }
        except Exception as e:
            logging.error(f"Failed to analyze screenshot: {str(e)}")
            return {
                "activity_description": "Analysis failed",
                "confidence": "low",
                "analysis_successful": False,
                "error": str(e)
            }

    def _create_analysis_prompt(self, context: str = "") -> str:
        """
        Create analysis prompt for the AI model

        Args:
            context (str): Additional context for analysis

        Returns:
            str: Formatted prompt for analysis
        """
        base_prompt = """请分析这张屏幕截图，描述用户当前正在进行的活动。请用中文回答，并且简洁明了地描述：

1. 用户正在使用什么应用程序或网站
2. 用户正在进行什么具体活动（比如编程、浏览网页、写文档、看视频等）
3. 如果能看出来，用户在处理什么具体内容

请用一到两句话简洁地总结用户的当前活动。"""

        if context:
            base_prompt += f"\n\n额外上下文信息：{context}"

        return base_prompt

    def analyze_activity_pattern(self, recent_activities: list) -> Dict[str, Any]:
        """
        Analyze patterns in recent activities

        Args:
            recent_activities (list): List of recent activity descriptions

        Returns:
            Dict[str, Any]: Pattern analysis results
        """
        if not recent_activities:
            return {
                "pattern": "No activities to analyze",
                "trend": "unknown",
                "productivity_score": 0
            }

        try:
            # Create pattern analysis prompt
            activities_text = "\n".join([f"- {activity}" for activity in recent_activities[-10:]])

            prompt = f"""基于以下最近的活动记录，请分析用户的行为模式：

{activities_text}

请分析：
1. 用户主要在进行什么类型的活动？
2. 是否有明显的工作模式或趋势？
3. 用户的专注度如何？

请用简洁的中文回答。

重要格式要求：最后一段话必须按照"<工作内容>(专注度)"的格式输出，总长度不能超过20个字。例如："编程开发(高度专注)"或"浏览网页(中等专注)"。"""

            # Use regular Generation API for text-only analysis
            response = Generation.call(
                model='qwen-plus',  # Use text model for pattern analysis
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                stream=False,
                incremental_output=False
            )

            # Check if response was successful
            if response.status_code == 200:
                # Extract the response content
                if response.output and response.output.text:
                    # For Generation API, the response text is directly available
                    pattern_description = response.output.text

                    return {
                        "pattern": pattern_description.strip(),
                        "trend": "analyzed",
                        "analysis_successful": True
                    }
                else:
                    raise Exception("No text in response output")
            else:
                # Handle API error
                error_msg = f"Pattern API call failed with status: {response.status_code}"
                if hasattr(response, 'message'):
                    error_msg += f", message: {response.message}"
                if hasattr(response, 'code'):
                    error_msg += f", code: {response.code}"
                raise Exception(error_msg)

        except Exception as e:
            logging.error(f"Failed to analyze activity pattern: {str(e)}")
            return {
                "pattern": "Pattern analysis failed",
                "trend": "unknown",
                "analysis_successful": False,
                "error": str(e)
            }