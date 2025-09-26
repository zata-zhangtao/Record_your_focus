from typing import Dict, Any, TypedDict
from langgraph.graph import StateGraph, END
import logging
import asyncio
from datetime import datetime

from screenshot_agent import ScreenshotAgent
from analysis_agent import AnalysisAgent
from storage import ActivityStorage
from config import Config

class ActivityState(TypedDict):
    """State for the activity recording workflow"""
    screenshot_path: str
    screenshot_base64: str
    activity_description: str
    analysis_result: Dict[str, Any]
    error: str
    success: bool
    timestamp: str

class ActivityRecorderWorkflow:
    """LangGraph workflow for activity recording"""

    def __init__(self):
        self.screenshot_agent = ScreenshotAgent()
        self.analysis_agent = AnalysisAgent()
        self.storage = ActivityStorage()
        self.config = Config()
        self.graph = self._build_workflow()

    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow"""

        workflow = StateGraph(ActivityState)

        # Add nodes
        workflow.add_node("capture_screenshot", self._capture_screenshot)
        workflow.add_node("analyze_activity", self._analyze_activity)
        workflow.add_node("store_activity", self._store_activity)
        workflow.add_node("cleanup", self._cleanup)

        # Add edges
        workflow.set_entry_point("capture_screenshot")
        workflow.add_edge("capture_screenshot", "analyze_activity")
        workflow.add_edge("analyze_activity", "store_activity")
        workflow.add_edge("store_activity", "cleanup")
        workflow.add_edge("cleanup", END)

        return workflow.compile()

    def _capture_screenshot(self, state: ActivityState) -> ActivityState:
        """Capture screenshot node"""
        try:
            logging.info("Capturing screenshot...")
            screenshot_path, screenshot_base64 = self.screenshot_agent.capture_screenshot()

            state.update({
                "screenshot_path": screenshot_path,
                "screenshot_base64": screenshot_base64,
                "timestamp": datetime.now().isoformat(),
                "success": True,
                "error": None
            })

            logging.info(f"Screenshot captured successfully: {screenshot_path}")

        except Exception as e:
            error_msg = f"Failed to capture screenshot: {str(e)}"
            logging.error(error_msg)
            state.update({
                "error": error_msg,
                "success": False
            })

        return state

    def _analyze_activity(self, state: ActivityState) -> ActivityState:
        """Analyze activity node"""
        if not state.get("success", False):
            return state

        try:
            logging.info("Analyzing activity...")

            # Get context from recent activities
            recent_activities = self.storage.get_recent_activities(limit=5)
            context = self._build_context(recent_activities)

            # Analyze the screenshot
            analysis_result = self.analysis_agent.analyze_screenshot(
                state["screenshot_base64"],
                context
            )

            state.update({
                "activity_description": analysis_result["activity_description"],
                "analysis_result": analysis_result
            })

            if analysis_result["analysis_successful"]:
                logging.info(f"Activity analysis successful: {analysis_result['activity_description']}")
            else:
                logging.warning(f"Activity analysis failed: {analysis_result.get('error', 'Unknown error')}")

        except Exception as e:
            error_msg = f"Failed to analyze activity: {str(e)}"
            logging.error(error_msg)
            state.update({
                "error": error_msg,
                "activity_description": "Analysis failed",
                "analysis_result": {"analysis_successful": False, "error": error_msg}
            })

        return state

    def _store_activity(self, state: ActivityState) -> ActivityState:
        """Store activity node"""
        try:
            logging.info("Storing activity...")

            activity_data = {
                "screenshot_path": state.get("screenshot_path"),
                "activity_description": state.get("activity_description"),
                "analysis_result": state.get("analysis_result", {}),
                "confidence": state.get("analysis_result", {}).get("confidence", "unknown"),
                "analysis_successful": state.get("analysis_result", {}).get("analysis_successful", False),
                "error": state.get("error")
            }

            success = self.storage.save_activity(activity_data)

            if success:
                logging.info("Activity stored successfully")
            else:
                logging.error("Failed to store activity")

        except Exception as e:
            error_msg = f"Failed to store activity: {str(e)}"
            logging.error(error_msg)
            state.update({"error": error_msg})

        return state

    def _cleanup(self, state: ActivityState) -> ActivityState:
        """Cleanup node"""
        try:
            # Cleanup old screenshots
            self.screenshot_agent.cleanup_old_screenshots(keep_last_n=50)

            # Cleanup old activities (keep 30 days)
            self.storage.cleanup_old_activities(keep_days=30)

            logging.info("Cleanup completed")

        except Exception as e:
            logging.warning(f"Cleanup failed: {str(e)}")

        return state

    def _build_context(self, recent_activities: list) -> str:
        """Build context from recent activities"""
        if not recent_activities:
            return ""

        context_parts = []
        for activity in recent_activities[-3:]:  # Use last 3 activities for context
            if activity.get("activity_description"):
                timestamp = activity.get("timestamp", "")
                desc = activity["activity_description"]
                context_parts.append(f"{timestamp}: {desc}")

        if context_parts:
            return f"最近的活动: {'; '.join(context_parts)}"
        return ""

    async def run_single_cycle(self) -> Dict[str, Any]:
        """Run a single activity recording cycle"""
        try:
            logging.info("Starting activity recording cycle...")

            # Initialize state
            initial_state = ActivityState(
                screenshot_path="",
                screenshot_base64="",
                activity_description="",
                analysis_result={},
                error=None,
                success=False,
                timestamp=""
            )

            # Run the workflow
            result = await self.graph.ainvoke(initial_state)

            logging.info("Activity recording cycle completed")
            return result

        except Exception as e:
            error_msg = f"Activity recording cycle failed: {str(e)}"
            logging.error(error_msg)
            return {"error": error_msg, "success": False}

    async def run_continuous(self) -> None:
        """Run continuous activity recording"""
        logging.info(f"Starting continuous activity recording (interval: {self.config.get_screenshot_interval()}s)")

        try:
            while True:
                # Run single cycle
                result = await self.run_single_cycle()

                if result.get("success", False):
                    logging.info(f"Cycle completed successfully: {result.get('activity_description', 'No description')}")
                else:
                    logging.error(f"Cycle failed: {result.get('error', 'Unknown error')}")

                # Wait for next cycle
                await asyncio.sleep(self.config.get_screenshot_interval())

        except KeyboardInterrupt:
            logging.info("Activity recording stopped by user")
        except Exception as e:
            logging.error(f"Continuous recording failed: {str(e)}")
            raise

    def get_statistics(self) -> Dict[str, Any]:
        """Get activity recording statistics"""
        return self.storage.get_activity_statistics()