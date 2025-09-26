import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

class Config:
    """Configuration management for the activity recorder"""

    # API Configuration
    DASHSCOPE_API_KEY: Optional[str] = None
    MODEL_NAME: str = "qwen3-vl-plus"

    # Screenshot Configuration
    SCREENSHOT_INTERVAL: int = 180  # 3 minutes in seconds
    SCREENSHOT_DIR: str = "screenshots"

    # Storage Configuration
    ACTIVITY_LOG_FILE: str = "activity_log.json"

    # LangGraph Configuration
    MAX_RETRIES: int = 3
    RETRY_DELAY: int = 5

    @classmethod
    def get_api_key(cls) -> str:
        """Get API key from environment"""
        api_key = os.getenv("DASHSCOPE_API_KEY")
        if not api_key:
            raise ValueError("DASHSCOPE_API_KEY environment variable is not set")
        return api_key

    @classmethod
    def get_model_name(cls) -> str:
        """Get model name from environment or use default"""
        return os.getenv("MODEL_NAME", cls.MODEL_NAME)

    @classmethod
    def get_screenshot_interval(cls) -> int:
        """Get screenshot interval from environment or use default"""
        return int(os.getenv("SCREENSHOT_INTERVAL", cls.SCREENSHOT_INTERVAL))

    @classmethod
    def validate_config(cls) -> bool:
        """Validate that all required configuration is present"""
        api_key = cls.get_api_key()
        if not api_key or api_key == "your-api-key-here":
            raise ValueError("DASHSCOPE_API_KEY is not properly configured")
        return True