import os
import json
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional, Any

load_dotenv()

class Config:
    """Configuration management for the activity recorder"""

    # API Configuration
    DASHSCOPE_API_KEY: Optional[str] = None
    MODEL_NAME: str = "qwen3-vl-plus"
    BASE_URL: str = "https://dashscope.aliyuncs.com/api/v1"

    # Screenshot Configuration
    SCREENSHOT_INTERVAL: int = 180  # 3 minutes in seconds
    SCREENSHOT_DIR: str = "screenshots"

    # Storage Configuration
    ACTIVITY_LOG_FILE: str = "activity_log.json"

    # LangGraph Configuration
    MAX_RETRIES: int = 3
    RETRY_DELAY: int = 5

    # AI Analysis Configuration
    ENABLE_THINKING: bool = True
    THINKING_BUDGET: int = 50

    # GUI configuration file path
    GUI_CONFIG_FILE: str = "gui_config.json"

    @classmethod
    def _load_gui_config(cls) -> dict:
        """Load GUI configuration file"""
        try:
            config_path = Path(cls.GUI_CONFIG_FILE)
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    @classmethod
    def get_api_key(cls) -> str:
        """Get API key from GUI config, environment, or class variable"""
        # Try GUI config first
        gui_config = cls._load_gui_config()
        api_key = gui_config.get("api", {}).get("api_key")
        if api_key:
            return api_key

        # Try environment variable
        api_key = os.getenv("DASHSCOPE_API_KEY")
        if api_key:
            return api_key

        # Try class variable
        if cls.DASHSCOPE_API_KEY:
            return cls.DASHSCOPE_API_KEY

        raise ValueError("DASHSCOPE_API_KEY is not configured")

    @classmethod
    def get_model_name(cls) -> str:
        """Get model name from GUI config, environment, or use default"""
        # Try GUI config first
        gui_config = cls._load_gui_config()
        model_name = gui_config.get("api", {}).get("model_name")
        if model_name:
            return model_name

        # Try environment variable
        return os.getenv("MODEL_NAME", cls.MODEL_NAME)

    @classmethod
    def get_base_url(cls) -> str:
        """Get base URL from GUI config or use default"""
        gui_config = cls._load_gui_config()
        base_url = gui_config.get("api", {}).get("base_url")
        if base_url:
            return base_url
        return cls.BASE_URL

    @classmethod
    def get_screenshot_interval(cls) -> int:
        """Get screenshot interval from GUI config, environment, or use default"""
        # Try GUI config first
        gui_config = cls._load_gui_config()
        interval = gui_config.get("recording", {}).get("interval")
        if interval:
            return int(interval)

        # Try environment variable
        return int(os.getenv("SCREENSHOT_INTERVAL", cls.SCREENSHOT_INTERVAL))

    @classmethod
    def get_enable_thinking(cls) -> bool:
        """Get enable_thinking setting from GUI config or use default"""
        gui_config = cls._load_gui_config()
        enable_thinking = gui_config.get("recording", {}).get("enable_thinking")
        if enable_thinking is not None:
            return bool(enable_thinking)
        return cls.ENABLE_THINKING

    @classmethod
    def get_thinking_budget(cls) -> int:
        """Get thinking_budget setting from GUI config or use default"""
        gui_config = cls._load_gui_config()
        thinking_budget = gui_config.get("recording", {}).get("thinking_budget")
        if thinking_budget is not None:
            return int(thinking_budget)
        return cls.THINKING_BUDGET

    @classmethod
    def validate_config(cls) -> bool:
        """Validate that all required configuration is present"""
        api_key = cls.get_api_key()
        if not api_key or api_key == "your-api-key-here":
            raise ValueError("DASHSCOPE_API_KEY is not properly configured")
        return True