"""
Settings Dialog
设置对话框
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QGroupBox, QLabel, QLineEdit, QPushButton, QSpinBox,
    QComboBox, QTextEdit, QCheckBox, QSlider, QDialogButtonBox,
    QMessageBox, QFileDialog, QListWidget, QListWidgetItem,
    QSplitter, QFormLayout, QProgressBar, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QObject, QTimer
from PyQt6.QtGui import QFont, QIcon
import asyncio
from typing import Dict, Any

# Import backend components
from .config_manager import GUIConfig
from analysis_agent import AnalysisAgent
from config import Config


class APITestWorker(QObject):
    """Worker for testing API connection"""

    # Signals
    test_started = pyqtSignal()
    test_completed = pyqtSignal(bool, str)  # success, message

    def __init__(self, api_key: str, model_name: str):
        super().__init__()
        self.api_key = api_key
        self.model_name = model_name

    def run_test(self):
        """Run API connection test"""
        self.test_started.emit()

        try:
            # Temporarily update config for testing
            original_api_key = Config.DASHSCOPE_API_KEY
            original_model = Config.MODEL_NAME

            Config.DASHSCOPE_API_KEY = self.api_key
            Config.MODEL_NAME = self.model_name

            # Create test agent
            agent = AnalysisAgent()

            # Create a simple test image (red square)
            import base64
            from PIL import Image
            import io

            test_img = Image.new('RGB', (100, 100), color='red')
            buffer = io.BytesIO()
            test_img.save(buffer, format='PNG')
            test_image_b64 = base64.b64encode(buffer.getvalue()).decode()

            # Test analysis
            result = agent.analyze_screenshot(test_image_b64, "API连接测试")

            # Restore original config
            Config.DASHSCOPE_API_KEY = original_api_key
            Config.MODEL_NAME = original_model

            if result.get('analysis_successful', False):
                self.test_completed.emit(True, "API连接测试成功！")
            else:
                error_msg = result.get('error', '未知错误')
                self.test_completed.emit(False, f"API测试失败: {error_msg}")

        except Exception as e:
            self.test_completed.emit(False, f"API测试异常: {str(e)}")


class SettingsDialog(QDialog):
    """Settings configuration dialog"""

    # Signals
    settings_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.gui_config = GUIConfig()

        # API test worker
        self.test_worker = None
        self.test_thread = None

        self.init_ui()
        self.load_settings()

    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("设置")
        self.setModal(True)
        self.resize(800, 600)

        layout = QVBoxLayout(self)

        # Create tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        # Create tabs
        self.create_recording_tab()
        self.create_api_tab()
        self.create_prompt_tab()
        self.create_ui_tab()
        self.create_data_tab()

        # Button box
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel |
            QDialogButtonBox.StandardButton.Apply |
            QDialogButtonBox.StandardButton.RestoreDefaults
        )

        button_box.accepted.connect(self.accept_settings)
        button_box.rejected.connect(self.reject)
        button_box.button(QDialogButtonBox.StandardButton.Apply).clicked.connect(self.apply_settings)
        button_box.button(QDialogButtonBox.StandardButton.RestoreDefaults).clicked.connect(self.restore_defaults)

        layout.addWidget(button_box)

    def create_recording_tab(self):
        """Create recording settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Recording interval group
        interval_group = QGroupBox("录制间隔")
        interval_layout = QFormLayout(interval_group)

        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(10, 3600)  # 10 seconds to 1 hour
        self.interval_spin.setSuffix(" 秒")
        self.interval_spin.setValue(180)
        interval_layout.addRow("截图间隔:", self.interval_spin)

        # Interval slider for easier adjustment
        self.interval_slider = QSlider(Qt.Orientation.Horizontal)
        self.interval_slider.setRange(10, 3600)
        self.interval_slider.setValue(180)
        self.interval_slider.valueChanged.connect(self.interval_spin.setValue)
        self.interval_spin.valueChanged.connect(self.interval_slider.setValue)
        interval_layout.addRow("快速调节:", self.interval_slider)

        # Common interval buttons
        interval_buttons_layout = QHBoxLayout()
        for label, seconds in [("30秒", 30), ("1分钟", 60), ("3分钟", 180), ("5分钟", 300), ("10分钟", 600)]:
            btn = QPushButton(label)
            btn.clicked.connect(lambda checked, s=seconds: self.interval_spin.setValue(s))
            interval_buttons_layout.addWidget(btn)

        interval_layout.addRow("常用间隔:", interval_buttons_layout)
        layout.addWidget(interval_group)

        # Auto start group
        auto_group = QGroupBox("自动启动")
        auto_layout = QVBoxLayout(auto_group)

        self.auto_start_cb = QCheckBox("程序启动时自动开始录制")
        auto_layout.addWidget(self.auto_start_cb)

        layout.addWidget(auto_group)

        # AI settings group
        ai_group = QGroupBox("AI分析设置")
        ai_layout = QFormLayout(ai_group)

        self.thinking_cb = QCheckBox("启用思考模式 (提高分析质量)")
        ai_layout.addRow("思考模式:", self.thinking_cb)

        self.thinking_budget_spin = QSpinBox()
        self.thinking_budget_spin.setRange(10, 200)
        self.thinking_budget_spin.setValue(50)
        self.thinking_budget_spin.setSuffix(" tokens")
        ai_layout.addRow("思考预算:", self.thinking_budget_spin)

        layout.addWidget(ai_group)

        layout.addStretch()
        self.tab_widget.addTab(tab, "录制设置")

    def create_api_tab(self):
        """Create API settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # API configuration group
        api_group = QGroupBox("DashScope API 配置")
        api_layout = QFormLayout(api_group)

        self.api_key_edit = QLineEdit()
        self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        api_layout.addRow("API Key:", self.api_key_edit)

        # Show/hide API key button
        key_buttons_layout = QHBoxLayout()
        self.show_key_btn = QPushButton("显示")
        self.show_key_btn.setCheckable(True)
        self.show_key_btn.toggled.connect(self.toggle_api_key_visibility)
        key_buttons_layout.addWidget(self.show_key_btn)
        key_buttons_layout.addStretch()

        api_layout.addRow("", key_buttons_layout)

        # Base URL
        self.base_url_edit = QLineEdit()
        self.base_url_edit.setPlaceholderText("https://dashscope.aliyuncs.com/api/v1")
        api_layout.addRow("Base URL:", self.base_url_edit)

        layout.addWidget(api_group)

        # Model selection group
        model_group = QGroupBox("模型选择")
        model_layout = QFormLayout(model_group)

        self.model_combo = QComboBox()
        self.model_combo.setEditable(True)
        self.model_combo.addItems([
            "qwen3-vl-plus",
            "qwen-vl-plus",
            "qwen-vl-max",
            "qwen3-vl-plus-2025-09-23"
        ])
        model_layout.addRow("VL模型:", self.model_combo)

        # Model info
        model_info = QLabel("""
        • qwen3-vl-plus: 最新的多模态模型，推荐使用
        • qwen-vl-plus: 经典版本，稳定性好
        • qwen-vl-max: 最高性能版本，成本较高
        """)
        model_info.setWordWrap(True)
        model_info.setStyleSheet("color: #666; font-size: 11px; margin: 5px;")
        model_layout.addRow("说明:", model_info)

        layout.addWidget(model_group)

        # API test group
        test_group = QGroupBox("连接测试")
        test_layout = QVBoxLayout(test_group)

        test_buttons_layout = QHBoxLayout()
        self.test_btn = QPushButton("测试连接")
        self.test_btn.clicked.connect(self.test_api_connection)
        test_buttons_layout.addWidget(self.test_btn)

        test_buttons_layout.addStretch()
        test_layout.addLayout(test_buttons_layout)

        # Test progress
        self.test_progress = QProgressBar()
        self.test_progress.setVisible(False)
        test_layout.addWidget(self.test_progress)

        # Test result
        self.test_result_label = QLabel("")
        test_layout.addWidget(self.test_result_label)

        layout.addWidget(test_group)

        layout.addStretch()
        self.tab_widget.addTab(tab, "API设置")

    def create_prompt_tab(self):
        """Create prompt settings tab"""
        tab = QWidget()
        layout = QHBoxLayout(tab)

        # Left side: Custom prompts list
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        left_layout.addWidget(QLabel("自定义提示词模板:"))

        self.prompt_list = QListWidget()
        self.prompt_list.itemClicked.connect(self.on_prompt_selected)
        left_layout.addWidget(self.prompt_list)

        # Prompt list buttons
        prompt_buttons_layout = QHBoxLayout()

        self.add_prompt_btn = QPushButton("添加")
        self.add_prompt_btn.clicked.connect(self.add_custom_prompt)
        prompt_buttons_layout.addWidget(self.add_prompt_btn)

        self.delete_prompt_btn = QPushButton("删除")
        self.delete_prompt_btn.clicked.connect(self.delete_custom_prompt)
        self.delete_prompt_btn.setEnabled(False)
        prompt_buttons_layout.addWidget(self.delete_prompt_btn)

        prompt_buttons_layout.addStretch()
        left_layout.addLayout(prompt_buttons_layout)

        layout.addWidget(left_widget)

        # Right side: Prompt editor
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        # Current prompt group
        current_group = QGroupBox("当前提示词")
        current_layout = QVBoxLayout(current_group)

        self.current_prompt_edit = QTextEdit()
        self.current_prompt_edit.setMinimumHeight(300)
        self.current_prompt_edit.setPlaceholderText("在这里编辑提示词...")
        current_layout.addWidget(self.current_prompt_edit)

        # Prompt buttons
        prompt_edit_buttons = QHBoxLayout()

        self.save_prompt_btn = QPushButton("保存为默认")
        self.save_prompt_btn.clicked.connect(self.save_current_prompt)
        prompt_edit_buttons.addWidget(self.save_prompt_btn)

        self.reset_prompt_btn = QPushButton("重置为默认")
        self.reset_prompt_btn.clicked.connect(self.reset_to_default_prompt)
        prompt_edit_buttons.addWidget(self.reset_prompt_btn)

        prompt_edit_buttons.addStretch()
        current_layout.addLayout(prompt_edit_buttons)

        right_layout.addWidget(current_group)

        # Prompt help
        help_group = QGroupBox("提示词说明")
        help_layout = QVBoxLayout(help_group)

        help_text = QLabel("""
        提示词用于指导AI如何分析截图内容。你可以：

        • 修改分析重点 (如专注于工作效率、应用使用等)
        • 调整输出格式 (如详细程度、语言风格等)
        • 添加特定要求 (如识别特定应用、关注特定内容等)

        建议包含的要素：
        - 分析目标 (分析什么)
        - 输出要求 (如何输出)
        - 语言要求 (中文/英文)
        """)
        help_text.setWordWrap(True)
        help_text.setStyleSheet("color: #666; font-size: 12px;")
        help_layout.addWidget(help_text)

        right_layout.addWidget(help_group)

        layout.addWidget(right_widget)

        # Set layout proportions
        layout.setStretch(0, 1)
        layout.setStretch(1, 2)

        self.tab_widget.addTab(tab, "提示词设置")

    def create_ui_tab(self):
        """Create UI settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Theme group
        theme_group = QGroupBox("界面主题")
        theme_layout = QFormLayout(theme_group)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["跟随系统", "浅色主题", "深色主题"])
        theme_layout.addRow("主题:", self.theme_combo)

        layout.addWidget(theme_group)

        # Language group
        lang_group = QGroupBox("语言设置")
        lang_layout = QFormLayout(lang_group)

        self.language_combo = QComboBox()
        self.language_combo.addItems(["简体中文", "English"])
        lang_layout.addRow("界面语言:", self.language_combo)

        layout.addWidget(lang_group)

        # Display settings group
        display_group = QGroupBox("显示设置")
        display_layout = QVBoxLayout(display_group)

        self.show_screenshots_cb = QCheckBox("在活动列表中显示截图预览")
        display_layout.addWidget(self.show_screenshots_cb)

        self.compact_view_cb = QCheckBox("使用紧凑视图")
        display_layout.addWidget(self.compact_view_cb)

        layout.addWidget(display_group)

        layout.addStretch()
        self.tab_widget.addTab(tab, "界面设置")

    def create_data_tab(self):
        """Create data management tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Storage group
        storage_group = QGroupBox("数据存储")
        storage_layout = QFormLayout(storage_group)

        self.keep_days_spin = QSpinBox()
        self.keep_days_spin.setRange(1, 365)
        self.keep_days_spin.setSuffix(" 天")
        storage_layout.addRow("保留天数:", self.keep_days_spin)

        self.keep_screenshots_spin = QSpinBox()
        self.keep_screenshots_spin.setRange(10, 1000)
        self.keep_screenshots_spin.setSuffix(" 张")
        storage_layout.addRow("保留截图数:", self.keep_screenshots_spin)

        self.auto_cleanup_cb = QCheckBox("自动清理过期数据")
        storage_layout.addRow("自动清理:", self.auto_cleanup_cb)

        layout.addWidget(storage_group)

        # Export group
        export_group = QGroupBox("数据导出")
        export_layout = QFormLayout(export_group)

        self.export_format_combo = QComboBox()
        self.export_format_combo.addItems(["JSON", "CSV", "Excel"])
        export_layout.addRow("默认格式:", self.export_format_combo)

        # Export buttons
        export_buttons_layout = QHBoxLayout()

        export_all_btn = QPushButton("导出全部数据")
        export_all_btn.clicked.connect(self.export_all_data)
        export_buttons_layout.addWidget(export_all_btn)

        export_range_btn = QPushButton("按日期导出")
        export_range_btn.clicked.connect(self.export_date_range)
        export_buttons_layout.addWidget(export_range_btn)

        export_buttons_layout.addStretch()
        export_layout.addRow("导出操作:", export_buttons_layout)

        layout.addWidget(export_group)

        # Backup group
        backup_group = QGroupBox("备份与恢复")
        backup_layout = QVBoxLayout(backup_group)

        backup_buttons_layout = QHBoxLayout()

        backup_config_btn = QPushButton("备份设置")
        backup_config_btn.clicked.connect(self.backup_config)
        backup_buttons_layout.addWidget(backup_config_btn)

        restore_config_btn = QPushButton("恢复设置")
        restore_config_btn.clicked.connect(self.restore_config)
        backup_buttons_layout.addWidget(restore_config_btn)

        backup_buttons_layout.addStretch()
        backup_layout.addLayout(backup_buttons_layout)

        layout.addWidget(backup_group)

        layout.addStretch()
        self.tab_widget.addTab(tab, "数据管理")

    def load_settings(self):
        """Load current settings into the UI"""
        # Recording settings
        recording_settings = self.gui_config.get_recording_settings()
        self.interval_spin.setValue(recording_settings.get("interval", 180))
        self.auto_start_cb.setChecked(recording_settings.get("auto_start", False))
        self.thinking_cb.setChecked(recording_settings.get("enable_thinking", True))
        self.thinking_budget_spin.setValue(recording_settings.get("thinking_budget", 50))

        # API settings
        api_settings = self.gui_config.get_api_settings()
        self.api_key_edit.setText(api_settings.get("api_key", ""))
        self.base_url_edit.setText(api_settings.get("base_url", ""))
        model_name = api_settings.get("model_name", "qwen3-vl-plus")

        # Set model in combo box
        index = self.model_combo.findText(model_name)
        if index >= 0:
            self.model_combo.setCurrentIndex(index)
        else:
            self.model_combo.setCurrentText(model_name)

        # Prompt settings
        prompt_settings = self.gui_config.get_prompt_settings()
        self.current_prompt_edit.setPlainText(prompt_settings.get("default_prompt", ""))
        self.load_custom_prompts()

        # UI settings
        theme_map = {"auto": 0, "light": 1, "dark": 2}
        theme = self.gui_config.get("ui.theme", "auto")
        self.theme_combo.setCurrentIndex(theme_map.get(theme, 0))

        lang_map = {"zh_CN": 0, "en_US": 1}
        language = self.gui_config.get("ui.language", "zh_CN")
        self.language_combo.setCurrentIndex(lang_map.get(language, 0))

        self.show_screenshots_cb.setChecked(self.gui_config.get("ui.show_screenshots", True))
        self.compact_view_cb.setChecked(self.gui_config.get("ui.compact_view", False))

        # Data settings
        self.keep_days_spin.setValue(self.gui_config.get("data.keep_days", 30))
        self.keep_screenshots_spin.setValue(self.gui_config.get("data.keep_screenshots", 50))
        self.auto_cleanup_cb.setChecked(self.gui_config.get("data.auto_cleanup", True))

        format_map = {"json": 0, "csv": 1, "excel": 2}
        export_format = self.gui_config.get("data.export_format", "json")
        self.export_format_combo.setCurrentIndex(format_map.get(export_format, 0))

    def load_custom_prompts(self):
        """Load custom prompts into the list"""
        self.prompt_list.clear()

        # Add default prompt
        default_item = QListWidgetItem("默认提示词")
        default_item.setData(Qt.ItemDataRole.UserRole, "default")
        self.prompt_list.addItem(default_item)

        # Add custom prompts
        custom_prompts = self.gui_config.get("prompts.custom_prompts", [])
        for prompt in custom_prompts:
            item = QListWidgetItem(prompt.get("name", "未命名"))
            item.setData(Qt.ItemDataRole.UserRole, prompt)
            self.prompt_list.addItem(item)

    def on_prompt_selected(self, item):
        """Handle prompt selection"""
        prompt_data = item.data(Qt.ItemDataRole.UserRole)

        if prompt_data == "default":
            # Load default prompt
            default_prompt = self.gui_config.get("prompts.default_prompt", "")
            self.current_prompt_edit.setPlainText(default_prompt)
            self.delete_prompt_btn.setEnabled(False)
        else:
            # Load custom prompt
            prompt_text = prompt_data.get("prompt", "")
            self.current_prompt_edit.setPlainText(prompt_text)
            self.delete_prompt_btn.setEnabled(True)

    def add_custom_prompt(self):
        """Add a new custom prompt"""
        from PyQt6.QtWidgets import QInputDialog

        name, ok = QInputDialog.getText(self, "添加提示词", "提示词名称:")
        if ok and name.strip():
            prompt_text = self.current_prompt_edit.toPlainText()
            if prompt_text.strip():
                self.gui_config.add_custom_prompt(name.strip(), prompt_text)
                self.load_custom_prompts()

                # Select the new prompt
                for i in range(self.prompt_list.count()):
                    item = self.prompt_list.item(i)
                    if isinstance(item.data(Qt.ItemDataRole.UserRole), dict):
                        if item.data(Qt.ItemDataRole.UserRole).get("name") == name.strip():
                            self.prompt_list.setCurrentItem(item)
                            break

    def delete_custom_prompt(self):
        """Delete selected custom prompt"""
        current_item = self.prompt_list.currentItem()
        if not current_item:
            return

        prompt_data = current_item.data(Qt.ItemDataRole.UserRole)
        if prompt_data == "default":
            return

        reply = QMessageBox.question(
            self, "删除提示词",
            f"确定要删除提示词 '{current_item.text()}' 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Find and remove from config
            custom_prompts = self.gui_config.get("prompts.custom_prompts", [])
            for i, prompt in enumerate(custom_prompts):
                if prompt.get("name") == prompt_data.get("name"):
                    self.gui_config.remove_custom_prompt(i)
                    break

            self.load_custom_prompts()

    def save_current_prompt(self):
        """Save current prompt as default"""
        prompt_text = self.current_prompt_edit.toPlainText()
        self.gui_config.set("prompts.default_prompt", prompt_text)

        QMessageBox.information(self, "保存成功", "提示词已保存为默认")

    def reset_to_default_prompt(self):
        """Reset to original default prompt"""
        default_prompt = self.gui_config.default_config["prompts"]["default_prompt"]
        self.current_prompt_edit.setPlainText(default_prompt)

    def toggle_api_key_visibility(self, show):
        """Toggle API key visibility"""
        if show:
            self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Normal)
            self.show_key_btn.setText("隐藏")
        else:
            self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
            self.show_key_btn.setText("显示")

    def test_api_connection(self):
        """Test API connection"""
        api_key = self.api_key_edit.text().strip()
        model_name = self.model_combo.currentText().strip()

        if not api_key:
            QMessageBox.warning(self, "警告", "请输入API Key")
            return

        if not model_name:
            QMessageBox.warning(self, "警告", "请选择模型")
            return

        # Show progress
        self.test_btn.setEnabled(False)
        self.test_progress.setVisible(True)
        self.test_progress.setRange(0, 0)  # Indeterminate progress
        self.test_result_label.setText("正在测试连接...")

        # Create test worker
        self.test_worker = APITestWorker(api_key, model_name)
        self.test_thread = QThread()

        self.test_worker.moveToThread(self.test_thread)
        self.test_thread.started.connect(self.test_worker.run_test)
        self.test_worker.test_completed.connect(self.on_test_completed)

        self.test_thread.start()

    def on_test_completed(self, success: bool, message: str):
        """Handle test completion"""
        self.test_btn.setEnabled(True)
        self.test_progress.setVisible(False)

        if success:
            self.test_result_label.setText(f"✅ {message}")
            self.test_result_label.setStyleSheet("color: #28a745;")
        else:
            self.test_result_label.setText(f"❌ {message}")
            self.test_result_label.setStyleSheet("color: #dc3545;")

        # Clean up thread
        if self.test_thread:
            self.test_thread.quit()
            self.test_thread.wait()
            self.test_thread = None
            self.test_worker = None

    def export_all_data(self):
        """Export all activity data"""
        # Implementation would go here
        QMessageBox.information(self, "导出", "数据导出功能正在开发中...")

    def export_date_range(self):
        """Export data for specific date range"""
        # Implementation would go here
        QMessageBox.information(self, "导出", "按日期导出功能正在开发中...")

    def backup_config(self):
        """Backup configuration"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "备份设置",
            f"activity_recorder_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "JSON文件 (*.json)"
        )

        if file_path:
            if self.gui_config.export_config(file_path):
                QMessageBox.information(self, "成功", f"设置已备份到:\n{file_path}")
            else:
                QMessageBox.warning(self, "失败", "备份失败")

    def restore_config(self):
        """Restore configuration"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "恢复设置", "",
            "JSON文件 (*.json)"
        )

        if file_path:
            reply = QMessageBox.question(
                self, "恢复设置",
                "这将覆盖当前的所有设置，确定要继续吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                if self.gui_config.import_config(file_path):
                    QMessageBox.information(self, "成功", "设置已恢复，重启程序生效")
                    self.load_settings()  # Reload UI
                else:
                    QMessageBox.warning(self, "失败", "恢复失败，文件可能损坏")

    def apply_settings(self):
        """Apply current settings"""
        self.save_settings()
        self.settings_changed.emit()
        QMessageBox.information(self, "成功", "设置已保存")

    def accept_settings(self):
        """Accept and save settings"""
        self.save_settings()
        self.settings_changed.emit()
        self.accept()

    def save_settings(self):
        """Save all settings"""
        # Recording settings
        self.gui_config.set("recording.interval", self.interval_spin.value())
        self.gui_config.set("recording.auto_start", self.auto_start_cb.isChecked())
        self.gui_config.set("recording.enable_thinking", self.thinking_cb.isChecked())
        self.gui_config.set("recording.thinking_budget", self.thinking_budget_spin.value())

        # API settings
        self.gui_config.set("api.api_key", self.api_key_edit.text())
        self.gui_config.set("api.base_url", self.base_url_edit.text())
        self.gui_config.set("api.model_name", self.model_combo.currentText())

        # Prompt settings
        self.gui_config.set("prompts.default_prompt", self.current_prompt_edit.toPlainText())

        # UI settings
        theme_map = {0: "auto", 1: "light", 2: "dark"}
        self.gui_config.set("ui.theme", theme_map[self.theme_combo.currentIndex()])

        lang_map = {0: "zh_CN", 1: "en_US"}
        self.gui_config.set("ui.language", lang_map[self.language_combo.currentIndex()])

        self.gui_config.set("ui.show_screenshots", self.show_screenshots_cb.isChecked())
        self.gui_config.set("ui.compact_view", self.compact_view_cb.isChecked())

        # Data settings
        self.gui_config.set("data.keep_days", self.keep_days_spin.value())
        self.gui_config.set("data.keep_screenshots", self.keep_screenshots_spin.value())
        self.gui_config.set("data.auto_cleanup", self.auto_cleanup_cb.isChecked())

        format_map = {0: "json", 1: "csv", 2: "excel"}
        self.gui_config.set("data.export_format", format_map[self.export_format_combo.currentIndex()])

        # Save to file
        self.gui_config.save_config()

    def restore_defaults(self):
        """Restore default settings"""
        reply = QMessageBox.question(
            self, "恢复默认",
            "这将恢复所有设置为默认值，确定要继续吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.gui_config.reset_to_defaults()
            self.load_settings()
            QMessageBox.information(self, "成功", "已恢复默认设置")