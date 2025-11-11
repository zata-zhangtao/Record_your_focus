#!/usr/bin/env python3
"""
Native Messaging Host for Activity Recorder Browser Extension

This script enables communication between the browser extension and the
Python backend using Chrome's native messaging protocol.

Protocol:
- Messages are JSON objects sent via stdin/stdout
- Each message is prefixed with a 4-byte length header (little-endian uint32)
- Supported commands: start_recording, stop_recording, capture_now, get_activities,
  query_time_range, get_status, update_settings
"""

import sys
import json
import struct
import logging
import asyncio
import threading
from typing import Dict, Any, Optional
from pathlib import Path

# Import existing modules
from workflow import ActivityRecorderWorkflow
from storage import ActivityStorage
from config import Config
from analysis_agent import AnalysisAgent

# Configure logging
log_file = Path(__file__).parent / "native_host.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stderr)  # stderr for debugging, stdout is for messages
    ]
)
logger = logging.getLogger(__name__)


class NativeMessagingHost:
    """Native messaging host for browser extension communication"""

    def __init__(self):
        self.workflow = ActivityRecorderWorkflow()
        self.storage = ActivityStorage()
        self.analysis_agent = AnalysisAgent()
        self.config = Config()

        # Recording state
        self.is_recording = False
        self.recording_task: Optional[asyncio.Task] = None
        self.event_loop: Optional[asyncio.AbstractEventLoop] = None
        self.loop_thread: Optional[threading.Thread] = None

    def start(self):
        """Start the native messaging host"""
        logger.info("Native messaging host started")

        # Start event loop in separate thread for async operations
        self._start_event_loop()

        try:
            while True:
                # Read message from stdin
                message = self._read_message()
                if message is None:
                    break

                # Process message and get response
                response = self._process_message(message)

                # Send response to stdout
                self._send_message(response)

        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        finally:
            self._cleanup()

    def _start_event_loop(self):
        """Start asyncio event loop in a separate thread"""
        def run_loop():
            self.event_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.event_loop)
            self.event_loop.run_forever()

        self.loop_thread = threading.Thread(target=run_loop, daemon=True)
        self.loop_thread.start()

        # Wait for loop to be ready
        while self.event_loop is None:
            pass

    def _read_message(self) -> Optional[Dict[str, Any]]:
        """
        Read a message from stdin using native messaging protocol

        Returns:
            Dict containing the message, or None if connection closed
        """
        try:
            # Read the message length (first 4 bytes)
            raw_length = sys.stdin.buffer.read(4)

            if len(raw_length) == 0:
                logger.info("Stdin closed, exiting")
                return None

            # Decode message length (little-endian uint32)
            message_length = struct.unpack('=I', raw_length)[0]

            # Read the message content
            message_bytes = sys.stdin.buffer.read(message_length)

            # Decode JSON
            message = json.loads(message_bytes.decode('utf-8'))
            logger.info(f"Received message: {message.get('command', 'unknown')}")

            return message

        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode message: {str(e)}")
            return {"command": "error", "error": "Invalid JSON"}
        except Exception as e:
            logger.error(f"Failed to read message: {str(e)}")
            return None

    def _send_message(self, message: Dict[str, Any]):
        """
        Send a message to stdout using native messaging protocol

        Args:
            message: Dict to send as JSON
        """
        try:
            # Encode message as JSON
            message_json = json.dumps(message)
            message_bytes = message_json.encode('utf-8')

            # Write message length (4 bytes, little-endian uint32)
            sys.stdout.buffer.write(struct.pack('=I', len(message_bytes)))

            # Write message content
            sys.stdout.buffer.write(message_bytes)
            sys.stdout.buffer.flush()

            logger.info(f"Sent message: {message.get('command', 'unknown')}")

        except Exception as e:
            logger.error(f"Failed to send message: {str(e)}")

    def _process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a message from the browser extension

        Args:
            message: Message dict with 'command' and optional parameters

        Returns:
            Response dict
        """
        command = message.get('command')

        try:
            if command == 'start_recording':
                return self._handle_start_recording(message)
            elif command == 'stop_recording':
                return self._handle_stop_recording()
            elif command == 'capture_now':
                return self._handle_capture_now()
            elif command == 'get_activities':
                return self._handle_get_activities(message)
            elif command == 'query_time_range':
                return self._handle_query_time_range(message)
            elif command == 'get_status':
                return self._handle_get_status()
            elif command == 'update_settings':
                return self._handle_update_settings(message)
            elif command == 'get_statistics':
                return self._handle_get_statistics()
            else:
                return {
                    "command": command,
                    "success": False,
                    "error": f"Unknown command: {command}"
                }

        except Exception as e:
            logger.error(f"Error processing command {command}: {str(e)}", exc_info=True)
            return {
                "command": command,
                "success": False,
                "error": str(e)
            }

    def _handle_start_recording(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle start_recording command"""
        if self.is_recording:
            return {
                "command": "start_recording",
                "success": False,
                "error": "Recording is already running"
            }

        # Get interval from message or use default
        interval = message.get('interval', self.config.get_screenshot_interval())

        # Update config if needed
        if interval != self.config.get_screenshot_interval():
            Config.SCREENSHOT_INTERVAL = interval

        # Start recording in event loop
        async def start_continuous_recording():
            try:
                self.is_recording = True
                logger.info(f"Starting continuous recording with interval: {interval}s")

                while self.is_recording:
                    # Run single cycle
                    result = await self.workflow.run_single_cycle()

                    if result.get("success", False):
                        logger.info(f"Cycle completed: {result.get('activity_description', 'N/A')}")
                    else:
                        logger.error(f"Cycle failed: {result.get('error', 'Unknown')}")

                    # Wait for next cycle
                    await asyncio.sleep(interval)

            except asyncio.CancelledError:
                logger.info("Recording cancelled")
                self.is_recording = False
            except Exception as e:
                logger.error(f"Recording error: {str(e)}", exc_info=True)
                self.is_recording = False

        # Schedule task in event loop
        future = asyncio.run_coroutine_threadsafe(
            start_continuous_recording(),
            self.event_loop
        )
        self.recording_task = future

        return {
            "command": "start_recording",
            "success": True,
            "interval": interval,
            "message": "Recording started"
        }

    def _handle_stop_recording(self) -> Dict[str, Any]:
        """Handle stop_recording command"""
        if not self.is_recording:
            return {
                "command": "stop_recording",
                "success": False,
                "error": "Recording is not running"
            }

        # Stop recording
        self.is_recording = False

        if self.recording_task:
            try:
                self.recording_task.cancel()
            except Exception as e:
                logger.error(f"Error cancelling recording task: {str(e)}")

        logger.info("Recording stopped")

        return {
            "command": "stop_recording",
            "success": True,
            "message": "Recording stopped"
        }

    def _handle_capture_now(self) -> Dict[str, Any]:
        """Handle capture_now command - trigger immediate screenshot"""
        async def capture():
            return await self.workflow.run_single_cycle()

        # Run capture in event loop and wait for result
        future = asyncio.run_coroutine_threadsafe(capture(), self.event_loop)

        try:
            result = future.result(timeout=30)  # 30 second timeout

            if result.get("success", False):
                return {
                    "command": "capture_now",
                    "success": True,
                    "activity": {
                        "timestamp": result.get("timestamp"),
                        "description": result.get("activity_description"),
                        "screenshot_path": result.get("screenshot_path")
                    }
                }
            else:
                return {
                    "command": "capture_now",
                    "success": False,
                    "error": result.get("error", "Capture failed")
                }

        except asyncio.TimeoutError:
            return {
                "command": "capture_now",
                "success": False,
                "error": "Capture timeout"
            }
        except Exception as e:
            return {
                "command": "capture_now",
                "success": False,
                "error": str(e)
            }

    def _handle_get_activities(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_activities command"""
        limit = message.get('limit', 10)
        date_filter = message.get('date')  # Optional YYYY-MM-DD

        if date_filter:
            activities = self.storage.get_activities_by_date(date_filter)
        else:
            activities = self.storage.get_recent_activities(limit=limit)

        return {
            "command": "get_activities",
            "success": True,
            "activities": activities,
            "count": len(activities)
        }

    def _handle_query_time_range(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle query_time_range command - AI-powered time range analysis"""
        start_time = message.get('start_time')
        end_time = message.get('end_time')
        query = message.get('query', '总结这段时间的活动')

        if not start_time or not end_time:
            return {
                "command": "query_time_range",
                "success": False,
                "error": "start_time and end_time are required"
            }

        # Get activities in time range
        data = self.storage._load_data()
        activities = data.get("activities", [])

        filtered_activities = [
            activity for activity in activities
            if start_time <= activity["timestamp"] <= end_time
        ]

        if not filtered_activities:
            return {
                "command": "query_time_range",
                "success": True,
                "summary": "该时间段内没有记录的活动",
                "activities_count": 0
            }

        # Build context for AI query
        context = f"时间范围: {start_time} 到 {end_time}\n\n活动记录:\n"
        for activity in filtered_activities:
            timestamp = activity.get("timestamp", "")
            desc = activity.get("activity_description", "无描述")
            context += f"- {timestamp}: {desc}\n"

        # Query AI for summary
        try:
            # Use analysis agent with text-only query
            async def query_ai():
                # For text query, we'll use a simple prompt
                prompt = f"{query}\n\n{context}"
                # Note: This is a simplified version - you may want to enhance the analysis_agent
                # to support text-only queries or use a different model
                return {"summary": f"分析了 {len(filtered_activities)} 条活动记录"}

            future = asyncio.run_coroutine_threadsafe(query_ai(), self.event_loop)
            result = future.result(timeout=30)

            return {
                "command": "query_time_range",
                "success": True,
                "summary": result.get("summary"),
                "activities_count": len(filtered_activities),
                "time_range": {
                    "start": start_time,
                    "end": end_time
                }
            }

        except Exception as e:
            logger.error(f"Query failed: {str(e)}")
            return {
                "command": "query_time_range",
                "success": False,
                "error": str(e)
            }

    def _handle_get_status(self) -> Dict[str, Any]:
        """Handle get_status command"""
        statistics = self.workflow.get_statistics()

        return {
            "command": "get_status",
            "success": True,
            "status": {
                "is_recording": self.is_recording,
                "interval": self.config.get_screenshot_interval(),
                "statistics": statistics
            }
        }

    def _handle_update_settings(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle update_settings command"""
        settings = message.get('settings', {})

        updated = []
        errors = []

        # Update screenshot interval
        if 'interval' in settings:
            try:
                interval = int(settings['interval'])
                Config.SCREENSHOT_INTERVAL = interval
                updated.append('interval')
            except ValueError:
                errors.append('Invalid interval value')

        # Update API key
        if 'api_key' in settings:
            Config.DASHSCOPE_API_KEY = settings['api_key']
            updated.append('api_key')

        # Update model name
        if 'model_name' in settings:
            Config.MODEL_NAME = settings['model_name']
            updated.append('model_name')

        return {
            "command": "update_settings",
            "success": len(errors) == 0,
            "updated": updated,
            "errors": errors if errors else None
        }

    def _handle_get_statistics(self) -> Dict[str, Any]:
        """Handle get_statistics command"""
        statistics = self.workflow.get_statistics()

        return {
            "command": "get_statistics",
            "success": True,
            "statistics": statistics
        }

    def _cleanup(self):
        """Cleanup resources before exit"""
        logger.info("Cleaning up...")

        # Stop recording if running
        if self.is_recording:
            self.is_recording = False
            if self.recording_task:
                self.recording_task.cancel()

        # Stop event loop
        if self.event_loop:
            self.event_loop.call_soon_threadsafe(self.event_loop.stop)

        logger.info("Native messaging host stopped")


def main():
    """Main entry point"""
    try:
        host = NativeMessagingHost()
        host.start()
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
