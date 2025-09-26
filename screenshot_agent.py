import os
import io
import base64
from datetime import datetime
from typing import Optional, Tuple
from mss import mss
from PIL import Image
from config import Config

class ScreenshotAgent:
    """Handles screenshot capture functionality"""

    def __init__(self):
        self.screenshot_dir = Config.SCREENSHOT_DIR
        self._ensure_screenshot_dir()

    def _ensure_screenshot_dir(self) -> None:
        """Create screenshots directory if it doesn't exist"""
        if not os.path.exists(self.screenshot_dir):
            os.makedirs(self.screenshot_dir)

    def capture_screenshot(self) -> Tuple[str, str]:
        """
        Capture a screenshot and return both file path and base64 encoded image

        Returns:
            Tuple[str, str]: (file_path, base64_image)
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        filepath = os.path.join(self.screenshot_dir, filename)

        try:
            with mss() as sct:
                # Capture entire screen (monitor 1)
                monitor = sct.monitors[1]
                screenshot = sct.grab(monitor)

                # Convert to PIL Image
                img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")

                # Save to file
                img.save(filepath, "PNG")

                # Convert to base64 for API usage
                buffer = io.BytesIO()
                img.save(buffer, format="PNG")
                img_base64 = base64.b64encode(buffer.getvalue()).decode()

                return filepath, img_base64

        except Exception as e:
            raise Exception(f"Failed to capture screenshot: {str(e)}")

    def get_latest_screenshot(self) -> Optional[Tuple[str, str]]:
        """
        Get the most recent screenshot

        Returns:
            Optional[Tuple[str, str]]: (file_path, base64_image) or None if no screenshots exist
        """
        if not os.path.exists(self.screenshot_dir):
            return None

        screenshot_files = [f for f in os.listdir(self.screenshot_dir) if f.endswith('.png')]
        if not screenshot_files:
            return None

        latest_file = max(screenshot_files, key=lambda f: os.path.getctime(os.path.join(self.screenshot_dir, f)))
        latest_path = os.path.join(self.screenshot_dir, latest_file)

        # Convert to base64
        try:
            with Image.open(latest_path) as img:
                buffer = io.BytesIO()
                img.save(buffer, format="PNG")
                img_base64 = base64.b64encode(buffer.getvalue()).decode()
                return latest_path, img_base64
        except Exception as e:
            raise Exception(f"Failed to process latest screenshot: {str(e)}")

    def cleanup_old_screenshots(self, keep_last_n: int = 50) -> None:
        """
        Clean up old screenshots, keeping only the most recent ones

        Args:
            keep_last_n (int): Number of recent screenshots to keep
        """
        if not os.path.exists(self.screenshot_dir):
            return

        screenshot_files = [f for f in os.listdir(self.screenshot_dir) if f.endswith('.png')]
        if len(screenshot_files) <= keep_last_n:
            return

        # Sort by creation time and remove oldest files
        screenshot_files.sort(key=lambda f: os.path.getctime(os.path.join(self.screenshot_dir, f)))
        files_to_remove = screenshot_files[:-keep_last_n]

        for file_to_remove in files_to_remove:
            file_path = os.path.join(self.screenshot_dir, file_to_remove)
            try:
                os.remove(file_path)
            except OSError:
                pass  # File might have been removed already