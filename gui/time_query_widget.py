"""
Time Query Widget
时间查询组件
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel,
    QPushButton, QDateTimeEdit, QDateEdit, QSpinBox, QComboBox, QTextEdit,
    QProgressBar, QRadioButton, QButtonGroup, QSplitter, QGridLayout,
    QListWidget, QListWidgetItem, QMessageBox, QFrame, QFormLayout
)
from PyQt6.QtCore import Qt, QDateTime, QDate, QTime, pyqtSignal, QThread, QObject
from PyQt6.QtGui import QFont, QColor
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging

# Import backend components
from storage import ActivityStorage
from analysis_agent import AnalysisAgent


class TimeAnalysisWorker(QObject):
    """Worker for analyzing activities in a time range"""

    # Signals
    analysis_started = pyqtSignal()
    analysis_completed = pyqtSignal(str, list)  # summary, activities
    analysis_failed = pyqtSignal(str)  # error message

    def __init__(self, activities: List[Dict[str, Any]]):
        super().__init__()
        self.activities = activities

    def run_analysis(self):
        """Run time range analysis"""
        self.analysis_started.emit()

        try:
            if not self.activities:
                self.analysis_completed.emit("在指定时间段内没有找到活动记录。", [])
                return

            # Create analysis agent
            agent = AnalysisAgent()

            # Extract activity descriptions for pattern analysis
            descriptions = []
            for activity in self.activities:
                if activity.get('analysis_successful', False):
                    desc = activity.get('activity_description', '')
                    timestamp = activity.get('timestamp', '')
                    if desc:
                        try:
                            dt = datetime.fromisoformat(timestamp)
                            time_str = dt.strftime("%H:%M")
                            descriptions.append(f"[{time_str}] {desc}")
                        except:
                            descriptions.append(desc)

            if not descriptions:
                self.analysis_completed.emit(
                    "在指定时间段内找到了活动记录，但没有成功分析的内容。",
                    self.activities
                )
                return

            # Analyze the pattern
            result = agent.analyze_activity_pattern(descriptions)

            if result.get('analysis_successful', False):
                summary = result.get('pattern', '分析完成，但没有返回具体内容。')
                self.analysis_completed.emit(summary, self.activities)
            else:
                error_msg = result.get('error', '分析失败，原因未知。')
                self.analysis_failed.emit(f"AI分析失败: {error_msg}")

        except Exception as e:
            logging.error(f"Time analysis failed: {str(e)}")
            self.analysis_failed.emit(f"分析过程中出错: {str(e)}")


class TimeQueryWidget(QWidget):
    """Widget for querying activities by time range"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.storage = ActivityStorage()

        # Analysis worker
        self.analysis_worker = None
        self.analysis_thread = None

        self.init_ui()

    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)

        # Query configuration group
        config_group = QGroupBox("时间查询设置")
        config_layout = QVBoxLayout(config_group)

        # Query mode selection
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("查询模式:"))

        self.mode_group = QButtonGroup()

        self.time_range_radio = QRadioButton("时间段模式")
        self.time_range_radio.setChecked(True)
        self.time_range_radio.toggled.connect(self.on_mode_changed)
        self.mode_group.addButton(self.time_range_radio, 0)
        mode_layout.addWidget(self.time_range_radio)

        self.duration_radio = QRadioButton("回溯模式")
        self.duration_radio.toggled.connect(self.on_mode_changed)
        self.mode_group.addButton(self.duration_radio, 1)
        mode_layout.addWidget(self.duration_radio)

        mode_layout.addStretch()
        config_layout.addLayout(mode_layout)

        # Time range mode
        self.time_range_widget = QWidget()
        time_range_layout = QFormLayout(self.time_range_widget)

        self.start_datetime = QDateTimeEdit()
        self.start_datetime.setDateTime(QDateTime.currentDateTime().addSecs(-3600))  # 1 hour ago
        self.start_datetime.setCalendarPopup(True)
        time_range_layout.addRow("开始时间:", self.start_datetime)

        self.end_datetime = QDateTimeEdit()
        self.end_datetime.setDateTime(QDateTime.currentDateTime())
        self.end_datetime.setCalendarPopup(True)
        time_range_layout.addRow("结束时间:", self.end_datetime)

        # Hourly quick query controls
        self._setting_hourly_range = False
        hourly_widget = QWidget()
        hourly_layout = QVBoxLayout(hourly_widget)
        hourly_layout.setContentsMargins(0, 0, 0, 0)
        hourly_layout.setSpacing(8)

        hourly_header_layout = QHBoxLayout()
        hourly_header_layout.setContentsMargins(0, 0, 0, 0)
        hourly_header_layout.addWidget(QLabel("选择日期:"))

        self.hourly_date_edit = QDateEdit()
        self.hourly_date_edit.setCalendarPopup(True)
        self.hourly_date_edit.setDate(QDate.currentDate())
        self.hourly_date_edit.dateChanged.connect(self.clear_hourly_selection)
        hourly_header_layout.addWidget(self.hourly_date_edit)
        hourly_header_layout.addStretch()
        hourly_layout.addLayout(hourly_header_layout)

        hour_grid = QGridLayout()
        hour_grid.setHorizontalSpacing(6)
        hour_grid.setVerticalSpacing(6)

        self.hour_button_group = QButtonGroup(self)
        self.hour_button_group.setExclusive(True)

        hours = list(range(9, 25))
        columns = 8
        for index, hour in enumerate(hours):
            btn = QPushButton(f"{hour:02d}")
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, h=hour: self.set_hourly_range(h))
            self.hour_button_group.addButton(btn, hour)
            row = index // columns
            col = index % columns
            hour_grid.addWidget(btn, row, col)

        hourly_layout.addLayout(hour_grid)

        hint_label = QLabel("提示: 选择日期后点击小时，自动填充对应的一小时区间 (24=次日00:00-01:00)")
        hint_label.setWordWrap(True)
        hint_label.setStyleSheet("color: #666; font-size: 12px;")
        hourly_layout.addWidget(hint_label)

        time_range_layout.addRow("小时快捷:", hourly_widget)

        # Quick time range buttons
        quick_range_layout = QHBoxLayout()
        for label, hours in [("过去1小时", 1), ("过去3小时", 3), ("过去6小时", 6), ("过去12小时", 12), ("今天", 24)]:
            btn = QPushButton(label)
            if label == "今天":
                btn.clicked.connect(lambda: self.set_today_range())
            else:
                btn.clicked.connect(lambda checked, h=hours: self.set_quick_range(h))
            quick_range_layout.addWidget(btn)

        time_range_layout.addRow("快速选择:", quick_range_layout)
        config_layout.addWidget(self.time_range_widget)

        # Track manual edits to clear hourly presets
        self.start_datetime.dateTimeChanged.connect(self.on_manual_datetime_changed)
        self.end_datetime.dateTimeChanged.connect(self.on_manual_datetime_changed)

        # Duration mode
        self.duration_widget = QWidget()
        duration_layout = QFormLayout(self.duration_widget)

        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(1, 1440)  # 1 minute to 24 hours
        self.duration_spin.setValue(60)  # Default 60 minutes
        self.duration_spin.setSuffix(" 分钟")
        duration_layout.addRow("回溯时间:", self.duration_spin)

        # Quick duration buttons
        quick_duration_layout = QHBoxLayout()
        for label, minutes in [("15分钟", 15), ("30分钟", 30), ("1小时", 60), ("2小时", 120), ("4小时", 240)]:
            btn = QPushButton(label)
            btn.clicked.connect(lambda checked, m=minutes: self.duration_spin.setValue(m))
            quick_duration_layout.addWidget(btn)

        duration_layout.addRow("快速选择:", quick_duration_layout)
        config_layout.addWidget(self.duration_widget)
        self.duration_widget.hide()  # Hidden by default

        # Query button
        query_layout = QHBoxLayout()
        self.query_btn = QPushButton("开始查询")
        self.query_btn.setMinimumHeight(40)
        self.query_btn.setStyleSheet("font-weight: bold; background-color: #007bff; color: white;")
        self.query_btn.clicked.connect(self.start_query)
        query_layout.addWidget(self.query_btn)

        self.clear_btn = QPushButton("清除结果")
        self.clear_btn.clicked.connect(self.clear_results)
        query_layout.addWidget(self.clear_btn)

        query_layout.addStretch()
        config_layout.addLayout(query_layout)

        layout.addWidget(config_group)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Results splitter
        results_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left side: Activity list
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        left_layout.addWidget(QLabel("时间段内的活动记录:"))

        self.activity_list = QListWidget()
        self.activity_list.itemClicked.connect(self.on_activity_selected)
        left_layout.addWidget(self.activity_list)

        # Activity list stats
        self.activity_stats_label = QLabel("活动统计: 0条记录")
        self.activity_stats_label.setStyleSheet("color: #666; font-size: 12px; margin: 5px;")
        left_layout.addWidget(self.activity_stats_label)

        results_splitter.addWidget(left_widget)

        # Right side: AI analysis results
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        # AI Summary
        summary_group = QGroupBox("AI智能汇总")
        summary_layout = QVBoxLayout(summary_group)

        self.summary_text = QTextEdit()
        self.summary_text.setMinimumHeight(200)
        self.summary_text.setReadOnly(True)
        self.summary_text.setPlaceholderText('点击"开始查询"后，AI将分析时间段内的活动模式...')
        summary_layout.addWidget(self.summary_text)

        # Analysis actions
        analysis_actions_layout = QHBoxLayout()

        self.reanalyze_btn = QPushButton("重新分析")
        self.reanalyze_btn.setEnabled(False)
        self.reanalyze_btn.clicked.connect(self.reanalyze_activities)
        analysis_actions_layout.addWidget(self.reanalyze_btn)

        self.export_summary_btn = QPushButton("导出汇总")
        self.export_summary_btn.setEnabled(False)
        self.export_summary_btn.clicked.connect(self.export_summary)
        analysis_actions_layout.addWidget(self.export_summary_btn)

        analysis_actions_layout.addStretch()
        summary_layout.addLayout(analysis_actions_layout)

        right_layout.addWidget(summary_group)

        # Activity details
        details_group = QGroupBox("活动详情")
        details_layout = QVBoxLayout(details_group)

        self.details_text = QTextEdit()
        self.details_text.setMaximumHeight(150)
        self.details_text.setReadOnly(True)
        self.details_text.setPlaceholderText("选择左侧活动记录查看详情...")
        details_layout.addWidget(self.details_text)

        right_layout.addWidget(details_group)

        results_splitter.addWidget(right_widget)

        # Set splitter proportions
        results_splitter.setSizes([400, 600])
        layout.addWidget(results_splitter)

        # Current activities cache
        self.current_activities = []

    def on_mode_changed(self):
        """Handle query mode change"""
        if self.time_range_radio.isChecked():
            self.time_range_widget.show()
            self.duration_widget.hide()
        else:
            self.time_range_widget.hide()
            self.duration_widget.show()
            self.clear_hourly_selection()

    def set_quick_range(self, hours: int):
        """Set quick time range"""
        end_time = QDateTime.currentDateTime()
        start_time = end_time.addSecs(-hours * 3600)

        self.start_datetime.setDateTime(start_time)
        self.end_datetime.setDateTime(end_time)

    def set_today_range(self):
        """Set range to today"""
        now = QDateTime.currentDateTime()
        start_of_day = QDateTime(now.date(), QTime(0, 0, 0))

        self.start_datetime.setDateTime(start_of_day)
        self.end_datetime.setDateTime(now)

    def set_hourly_range(self, hour: int):
        """Set time range using hourly preset"""
        selected_date = self.hourly_date_edit.date()
        if not selected_date.isValid():
            QMessageBox.warning(self, "错误", "请选择有效的日期后再使用小时快捷查询")
            return

        if hour == 24:
            # 24代表次日00点-01点
            start_date = selected_date.addDays(1)
            start_time = QTime(0, 0, 0)
        else:
            start_date = selected_date
            start_time = QTime(hour, 0, 0)

        start_datetime = QDateTime(start_date, start_time)
        end_datetime = start_datetime.addSecs(3600)

        # Ensure we stay in time-range mode
        if not self.time_range_radio.isChecked():
            self.time_range_radio.setChecked(True)

        self._setting_hourly_range = True
        self.start_datetime.setDateTime(start_datetime)
        self.end_datetime.setDateTime(end_datetime)
        self._setting_hourly_range = False

    def on_manual_datetime_changed(self):
        """Clear hourly selection when user manually adjusts time"""
        if getattr(self, '_setting_hourly_range', False):
            return
        self.clear_hourly_selection()

    def clear_hourly_selection(self):
        """Reset hourly quick selection buttons"""
        group = getattr(self, 'hour_button_group', None)
        if not group:
            return

        was_exclusive = group.exclusive()
        if was_exclusive:
            group.setExclusive(False)

        for button in group.buttons():
            button.setChecked(False)

        if was_exclusive:
            group.setExclusive(True)

    def start_query(self):
        """Start time query"""
        # Get time range
        if self.time_range_radio.isChecked():
            start_time = self.start_datetime.dateTime().toPyDateTime()
            end_time = self.end_datetime.dateTime().toPyDateTime()

            if start_time >= end_time:
                QMessageBox.warning(self, "错误", "开始时间必须早于结束时间")
                return

        else:  # Duration mode
            duration_minutes = self.duration_spin.value()
            end_time = datetime.now()
            start_time = end_time - timedelta(minutes=duration_minutes)

        # Query activities
        self.query_activities(start_time, end_time)

    def query_activities(self, start_time: datetime, end_time: datetime):
        """Query activities in time range"""
        try:
            # Clear previous results
            self.clear_results()

            # Show progress
            self.query_btn.setEnabled(False)
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # Indeterminate

            # Get all activities
            all_activities = self.storage.get_recent_activities(limit=10000)

            # Filter by time range
            filtered_activities = []
            for activity in all_activities:
                try:
                    activity_time = datetime.fromisoformat(activity.get('timestamp', ''))
                    if start_time <= activity_time <= end_time:
                        filtered_activities.append(activity)
                except:
                    continue

            # Sort by timestamp
            filtered_activities.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

            self.current_activities = filtered_activities

            # Update activity list
            self.update_activity_list(filtered_activities)

            # Update stats
            success_count = sum(1 for a in filtered_activities if a.get('analysis_successful', False))
            total_count = len(filtered_activities)
            time_span = end_time - start_time

            if time_span.days > 0:
                time_str = f"{time_span.days}天{time_span.seconds//3600}小时"
            else:
                hours = time_span.seconds // 3600
                minutes = (time_span.seconds % 3600) // 60
                if hours > 0:
                    time_str = f"{hours}小时{minutes}分钟"
                else:
                    time_str = f"{minutes}分钟"

            stats_text = f"活动统计: {total_count}条记录 (成功分析{success_count}条) | 时间跨度: {time_str}"
            self.activity_stats_label.setText(stats_text)

            # Start AI analysis
            if filtered_activities:
                self.start_ai_analysis(filtered_activities)
            else:
                self.progress_bar.setVisible(False)
                self.query_btn.setEnabled(True)
                self.summary_text.setPlainText("在指定时间段内没有找到活动记录。")

        except Exception as e:
            self.progress_bar.setVisible(False)
            self.query_btn.setEnabled(True)
            QMessageBox.warning(self, "查询失败", f"查询活动记录时出错:\n{str(e)}")

    def update_activity_list(self, activities: List[Dict[str, Any]]):
        """Update activity list widget"""
        self.activity_list.clear()

        for activity in activities:
            timestamp = activity.get('timestamp', '')
            try:
                dt = datetime.fromisoformat(timestamp)
                time_str = dt.strftime("%m-%d %H:%M:%S")
            except:
                time_str = timestamp[:19] if len(timestamp) >= 19 else timestamp

            description = activity.get('activity_description', '无描述')
            is_successful = activity.get('analysis_successful', False)

            # Create list item
            display_text = f"[{time_str}] {'✅' if is_successful else '❌'} {description[:80]}..."
            item = QListWidgetItem(display_text)
            item.setData(Qt.ItemDataRole.UserRole, activity)

            # Set color based on success
            if is_successful:
                item.setForeground(QColor("#000000"))
            else:
                item.setForeground(QColor("#999999"))

            self.activity_list.addItem(item)

    def start_ai_analysis(self, activities: List[Dict[str, Any]]):
        """Start AI analysis of activities"""
        if not activities:
            return

        # Create analysis worker
        self.analysis_worker = TimeAnalysisWorker(activities)
        self.analysis_thread = QThread()

        # Move worker to thread
        self.analysis_worker.moveToThread(self.analysis_thread)

        # Connect signals
        self.analysis_thread.started.connect(self.analysis_worker.run_analysis)
        self.analysis_worker.analysis_started.connect(self.on_analysis_started)
        self.analysis_worker.analysis_completed.connect(self.on_analysis_completed)
        self.analysis_worker.analysis_failed.connect(self.on_analysis_failed)

        # Start analysis
        self.analysis_thread.start()

    def on_analysis_started(self):
        """Handle analysis start"""
        self.summary_text.setPlainText("AI正在分析时间段内的活动模式，请稍候...")

    def on_analysis_completed(self, summary: str, activities: List[Dict[str, Any]]):
        """Handle analysis completion"""
        self.progress_bar.setVisible(False)
        self.query_btn.setEnabled(True)

        # Update summary
        self.summary_text.setPlainText(summary)

        # Enable action buttons
        self.reanalyze_btn.setEnabled(True)
        self.export_summary_btn.setEnabled(True)

        # Clean up thread
        if self.analysis_thread:
            self.analysis_thread.quit()
            self.analysis_thread.wait()
            self.analysis_thread = None
            self.analysis_worker = None

    def on_analysis_failed(self, error_message: str):
        """Handle analysis failure"""
        self.progress_bar.setVisible(False)
        self.query_btn.setEnabled(True)

        self.summary_text.setPlainText(f"AI分析失败: {error_message}\n\n您仍然可以查看时间段内的具体活动记录。")

        # Clean up thread
        if self.analysis_thread:
            self.analysis_thread.quit()
            self.analysis_thread.wait()
            self.analysis_thread = None
            self.analysis_worker = None

    def on_activity_selected(self, item: QListWidgetItem):
        """Handle activity selection"""
        activity = item.data(Qt.ItemDataRole.UserRole)
        if not activity:
            return

        # Show activity details
        details = []
        details.append(f"时间: {activity.get('timestamp', 'N/A')}")
        details.append(f"活动描述: {activity.get('activity_description', 'N/A')}")
        details.append(f"分析状态: {'成功' if activity.get('analysis_successful', False) else '失败'}")
        details.append(f"置信度: {activity.get('confidence', 'N/A')}")

        if activity.get('error'):
            details.append(f"错误信息: {activity['error']}")

        screenshot_path = activity.get('screenshot_path', '')
        if screenshot_path:
            details.append(f"截图文件: {screenshot_path}")

        self.details_text.setPlainText("\n\n".join(details))

    def reanalyze_activities(self):
        """Re-analyze current activities"""
        if self.current_activities:
            self.start_ai_analysis(self.current_activities)

    def export_summary(self):
        """Export analysis summary"""
        summary_text = self.summary_text.toPlainText()
        if not summary_text.strip():
            QMessageBox.information(self, "提示", "没有可导出的分析内容")
            return

        from PyQt6.QtWidgets import QFileDialog

        default_name = f"activity_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出活动汇总", default_name,
            "文本文件 (*.txt);;所有文件 (*.*)"
        )

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"活动分析汇总报告\n")
                    f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"="*50 + "\n\n")
                    f.write(summary_text)
                    f.write(f"\n\n" + "="*50 + "\n")
                    f.write(f"详细活动记录:\n\n")

                    # Add detailed activity list
                    for i, activity in enumerate(self.current_activities, 1):
                        f.write(f"{i}. [{activity.get('timestamp', 'N/A')}] ")
                        f.write(f"{activity.get('activity_description', 'N/A')}\n")

                QMessageBox.information(self, "成功", f"汇总已导出到:\n{file_path}")

            except Exception as e:
                QMessageBox.warning(self, "错误", f"导出失败:\n{str(e)}")

    def clear_results(self):
        """Clear all results"""
        self.activity_list.clear()
        self.summary_text.clear()
        self.details_text.clear()
        self.activity_stats_label.setText("活动统计: 0条记录")

        # Disable action buttons
        self.reanalyze_btn.setEnabled(False)
        self.export_summary_btn.setEnabled(False)

        # Clear cache
        self.current_activities = []

        # Reset placeholders
        self.summary_text.setPlaceholderText('点击"开始查询"后，AI将分析时间段内的活动模式...')
        self.details_text.setPlaceholderText("选择左侧活动记录查看详情...")
