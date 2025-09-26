"""
GUI Configuration Manager
GUI配置管理器
"""

import json
import os
from typing import Dict, Any, Optional
from config import Config


class GUIConfig:
    """GUI Configuration Management"""

    def __init__(self):
        self.config_file = "gui_config.json"
        self.default_config = {
            # Window settings
            "window": {
                "width": 1200,
                "height": 800,
                "x": 100,
                "y": 100,
                "maximized": False
            },
            # Recording settings
            "recording": {
                "interval": 180,  # seconds
                "auto_start": False,
                "enable_thinking": True,
                "thinking_budget": 50
            },
            # API settings
            "api": {
                "api_key": Config.DASHSCOPE_API_KEY,
                "model_name": Config.MODEL_NAME,
                "base_url": "https://dashscope.aliyuncs.com/api/v1"
            },
            # Prompt settings
            "prompts": {
                "default_prompt": """请分析这张屏幕截图，描述用户当前正在进行的活动。请用中文回答，并且简洁明了地描述：

1. 用户正在使用什么应用程序或网站
2. 用户正在进行什么具体活动（比如编程、浏览网页、写文档、看视频等）
3. 如果能看出来，用户在处理什么具体内容

请用一到两句话简洁地总结用户的当前活动。""",
                "custom_prompts": []
            },
            # UI settings
            "ui": {
                "theme": "auto",  # light, dark, auto
                "language": "zh_CN",  # zh_CN, en_US
                "show_screenshots": True,
                "compact_view": False
            },
            # Data settings
            "data": {
                "keep_days": 30,
                "keep_screenshots": 50,
                "auto_cleanup": True,
                "export_format": "json"  # json, csv, excel
            }
        }
        self.config = self.load_config()

    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                # Merge with default config to handle new settings
                return self._merge_config(self.default_config, loaded_config)
            except (json.JSONDecodeError, FileNotFoundError):
                pass

        return self.default_config.copy()

    def save_config(self) -> bool:
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Failed to save GUI config: {e}")
            return False

    def _merge_config(self, default: Dict[str, Any], loaded: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merge loaded config with default config"""
        result = default.copy()

        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value

        return result

    def get(self, key_path: str, default_value: Optional[Any] = None) -> Any:
        """Get configuration value using dot notation (e.g., 'window.width')"""
        keys = key_path.split('.')
        value = self.config

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default_value

        return value

    def set(self, key_path: str, value: Any) -> None:
        """Set configuration value using dot notation"""
        keys = key_path.split('.')
        config = self.config

        # Navigate to the parent of the target key
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]

        # Set the value
        config[keys[-1]] = value

    def get_recording_settings(self) -> Dict[str, Any]:
        """Get all recording related settings"""
        return {
            "interval": self.get("recording.interval", 180),
            "auto_start": self.get("recording.auto_start", False),
            "enable_thinking": self.get("recording.enable_thinking", True),
            "thinking_budget": self.get("recording.thinking_budget", 50)
        }

    def get_api_settings(self) -> Dict[str, Any]:
        """Get all API related settings"""
        return {
            "api_key": self.get("api.api_key", Config.DASHSCOPE_API_KEY),
            "model_name": self.get("api.model_name", Config.MODEL_NAME),
            "base_url": self.get("api.base_url", "https://dashscope.aliyuncs.com/api/v1")
        }

    def get_prompt_settings(self) -> Dict[str, Any]:
        """Get all prompt related settings"""
        return {
            "default_prompt": self.get("prompts.default_prompt"),
            "custom_prompts": self.get("prompts.custom_prompts", [])
        }

    def add_custom_prompt(self, name: str, prompt: str) -> None:
        """Add a custom prompt"""
        custom_prompts = self.get("prompts.custom_prompts", [])
        custom_prompts.append({"name": name, "prompt": prompt})
        self.set("prompts.custom_prompts", custom_prompts)

    def remove_custom_prompt(self, index: int) -> bool:
        """Remove a custom prompt by index"""
        custom_prompts = self.get("prompts.custom_prompts", [])
        if 0 <= index < len(custom_prompts):
            custom_prompts.pop(index)
            self.set("prompts.custom_prompts", custom_prompts)
            return True
        return False

    def reset_to_defaults(self) -> None:
        """Reset configuration to defaults"""
        self.config = self.default_config.copy()

    def export_config(self, file_path: str) -> bool:
        """Export configuration to a file"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False

    def import_config(self, file_path: str) -> bool:
        """Import configuration from a file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                imported_config = json.load(f)
            self.config = self._merge_config(self.default_config, imported_config)
            return True
        except Exception:
            return False