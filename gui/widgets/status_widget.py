"""
Status Widget
状态显示组件
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QProgressBar, QTextEdit
)
from PyQt6.QtCore import QTimer, pyqtSignal, Qt
from PyQt6.QtGui import QFont, QPalette, QColor
from datetime import datetime
import logging


class StatusWidget(QWidget):
    """Status display widget showing recording status and recent activity"""

    # Signals
    start_recording = pyqtSignal()
    stop_recording = pyqtSignal()
    open_settings = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_recording = False
        self.last_activity = "尚未开始录制"
        self.next_capture_time = None

        self.init_ui()
        self.setup_timer()

    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)

        # Control group
        control_group = QGroupBox("录制控制")
        control_layout = QHBoxLayout(control_group)

        # Status label
        self.status_label = QLabel("状态: 未录制")
        self.status_label.setStyleSheet("font-weight: bold; color: #666;")
        control_layout.addWidget(self.status_label)

        control_layout.addStretch()

        # Control buttons
        self.start_stop_btn = QPushButton("开始录制")
        self.start_stop_btn.setMinimumWidth(100)
        self.start_stop_btn.clicked.connect(self.toggle_recording)
        control_layout.addWidget(self.start_stop_btn)

        self.settings_btn = QPushButton("设置")
        self.settings_btn.setMinimumWidth(80)
        self.settings_btn.clicked.connect(self.open_settings.emit)
        control_layout.addWidget(self.settings_btn)

        layout.addWidget(control_group)

        # Recording info group
        info_group = QGroupBox("录制信息")
        info_layout = QVBoxLayout(info_group)

        # Next capture info
        self.next_capture_label = QLabel("下次截图: -")
        self.next_capture_label.setStyleSheet("color: #555;")
        info_layout.addWidget(self.next_capture_label)

        # Progress bar for countdown
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        info_layout.addWidget(self.progress_bar)

        # Interval info
        self.interval_label = QLabel("截图间隔: 3分钟")
        self.interval_label.setStyleSheet("color: #555;")
        info_layout.addWidget(self.interval_label)

        layout.addWidget(info_group)

        # Recent activity group
        activity_group = QGroupBox("最近活动")
        activity_layout = QVBoxLayout(activity_group)

        self.activity_text = QTextEdit()
        self.activity_text.setMaximumHeight(100)
        self.activity_text.setReadOnly(True)
        self.activity_text.setPlainText(self.last_activity)
        self.activity_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 8px;
                font-size: 12px;
            }
        """)
        activity_layout.addWidget(self.activity_text)

        layout.addWidget(activity_group)

    def setup_timer(self):
        """Setup timers for UI updates"""
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_display)
        self.update_timer.start(1000)  # Update every second

    def toggle_recording(self):
        """Toggle recording state"""
        if self.is_recording:
            self.stop_recording.emit()
        else:
            self.start_recording.emit()

    def set_recording_state(self, recording: bool):
        """Set recording state"""
        self.is_recording = recording

        if recording:
            self.status_label.setText("状态: 正在录制")
            self.status_label.setStyleSheet("font-weight: bold; color: #28a745;")
            self.start_stop_btn.setText("停止录制")
            self.start_stop_btn.setStyleSheet("background-color: #dc3545; color: white;")
            self.progress_bar.setVisible(True)
        else:
            self.status_label.setText("状态: 未录制")
            self.status_label.setStyleSheet("font-weight: bold; color: #666;")
            self.start_stop_btn.setText("开始录制")
            self.start_stop_btn.setStyleSheet("background-color: #28a745; color: white;")
            self.progress_bar.setVisible(False)
            self.next_capture_label.setText("下次截图: -")

    def set_interval(self, interval_seconds: int):
        """Set capture interval"""
        if interval_seconds < 60:
            interval_text = f"{interval_seconds}秒"
        else:
            minutes = interval_seconds // 60
            seconds = interval_seconds % 60
            if seconds == 0:
                interval_text = f"{minutes}分钟"
            else:
                interval_text = f"{minutes}分{seconds}秒"

        self.interval_label.setText(f"截图间隔: {interval_text}")
        self.capture_interval = interval_seconds

    def set_next_capture_time(self, next_time: datetime):
        """Set next capture time"""
        self.next_capture_time = next_time

    def update_last_activity(self, activity: str, timestamp: str = None):
        """Update the last activity display"""
        if timestamp:
            # Parse timestamp and format it
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                time_str = dt.strftime("%H:%M:%S")
                self.activity_text.setPlainText(f"[{time_str}] {activity}")
            except:
                self.activity_text.setPlainText(activity)
        else:
            self.activity_text.setPlainText(activity)

    def update_display(self):
        """Update the display with current information"""
        if self.is_recording and self.next_capture_time:
            now = datetime.now()
            if self.next_capture_time > now:
                time_diff = (self.next_capture_time - now).total_seconds()
                time_str = self.next_capture_time.strftime("%H:%M:%S")
                self.next_capture_label.setText(f"下次截图: {time_str} (倒计时: {int(time_diff)}秒)")

                # Update progress bar
                if hasattr(self, 'capture_interval'):
                    progress = ((self.capture_interval - time_diff) / self.capture_interval) * 100
                    self.progress_bar.setValue(int(max(0, min(100, progress))))
            else:
                self.next_capture_label.setText("下次截图: 即将开始...")
                self.progress_bar.setValue(100)

    def add_log_message(self, message: str, level: str = "INFO"):
        """Add a log message to the status display"""
        timestamp = datetime.now().strftime("%H:%M:%S")

        # Color code by log level
        color = "#666"
        if level == "ERROR":
            color = "#dc3545"
        elif level == "WARNING":
            color = "#ffc107"
        elif level == "SUCCESS":
            color = "#28a745"

        # Update the activity text with latest message
        self.activity_text.append(f'<span style="color: {color};">[{timestamp}] {message}</span>')