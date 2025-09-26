"""
Activity List Widget
活动列表组件
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QLabel, QLineEdit, QPushButton, QDateEdit, QComboBox,
    QGroupBox, QSplitter, QTextEdit, QCheckBox, QSpinBox
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal, QTimer
from PyQt6.QtGui import QColor, QBrush, QFont
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import os


class ActivityListWidget(QWidget):
    """Widget for displaying and filtering activity records"""

    # Signals
    activity_selected = pyqtSignal(dict)  # Emit selected activity data
    request_screenshot = pyqtSignal(str)  # Request screenshot for path

    def __init__(self, parent=None):
        super().__init__(parent)
        self.activities = []
        self.filtered_activities = []

        self.init_ui()
        self.setup_filters()

    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)

        # Filter section
        filter_group = QGroupBox("筛选条件")
        filter_layout = QVBoxLayout(filter_group)

        # Date range filter
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("日期范围:"))

        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate().addDays(-7))
        self.start_date.setCalendarPopup(True)
        date_layout.addWidget(self.start_date)

        date_layout.addWidget(QLabel("到"))

        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setCalendarPopup(True)
        date_layout.addWidget(self.end_date)

        date_layout.addStretch()
        filter_layout.addLayout(date_layout)

        # Search and status filter
        search_layout = QHBoxLayout()

        search_layout.addWidget(QLabel("搜索:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入关键词搜索活动描述...")
        search_layout.addWidget(self.search_input)

        search_layout.addWidget(QLabel("状态:"))
        self.status_filter = QComboBox()
        self.status_filter.addItems(["全部", "分析成功", "分析失败"])
        search_layout.addWidget(self.status_filter)

        # Show screenshots checkbox
        self.show_screenshots_cb = QCheckBox("显示截图")
        self.show_screenshots_cb.setChecked(True)
        search_layout.addWidget(self.show_screenshots_cb)

        # Results per page
        search_layout.addWidget(QLabel("每页:"))
        self.page_size_spin = QSpinBox()
        self.page_size_spin.setRange(10, 500)
        self.page_size_spin.setValue(100)
        self.page_size_spin.setSuffix(" 条")
        search_layout.addWidget(self.page_size_spin)

        filter_layout.addLayout(search_layout)

        # Filter buttons
        button_layout = QHBoxLayout()
        self.apply_filter_btn = QPushButton("应用筛选")
        self.apply_filter_btn.clicked.connect(self.apply_filters)
        button_layout.addWidget(self.apply_filter_btn)

        self.clear_filter_btn = QPushButton("清除筛选")
        self.clear_filter_btn.clicked.connect(self.clear_filters)
        button_layout.addWidget(self.clear_filter_btn)

        self.refresh_btn = QPushButton("刷新")
        self.refresh_btn.clicked.connect(self.refresh_data)
        button_layout.addWidget(self.refresh_btn)

        button_layout.addStretch()
        filter_layout.addLayout(button_layout)

        layout.addWidget(filter_group)

        # Main content splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Activity table
        self.activity_table = QTableWidget()
        self.setup_table()
        splitter.addWidget(self.activity_table)

        # Details panel
        details_group = QGroupBox("活动详情")
        details_layout = QVBoxLayout(details_group)

        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setMaximumHeight(200)
        details_layout.addWidget(self.details_text)

        # Screenshot info
        screenshot_layout = QHBoxLayout()
        self.screenshot_path_label = QLabel("截图: 无")
        screenshot_layout.addWidget(self.screenshot_path_label)

        self.view_screenshot_btn = QPushButton("查看截图")
        self.view_screenshot_btn.setEnabled(False)
        self.view_screenshot_btn.clicked.connect(self.view_screenshot)
        screenshot_layout.addWidget(self.view_screenshot_btn)

        details_layout.addLayout(screenshot_layout)

        splitter.addWidget(details_group)

        # Set splitter proportions
        splitter.setSizes([700, 500])
        layout.addWidget(splitter)

        # Status bar
        status_layout = QHBoxLayout()
        self.status_label = QLabel("总计: 0 条记录")
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        layout.addLayout(status_layout)

    def setup_table(self):
        """Setup the activity table"""
        headers = ["时间", "活动描述", "置信度", "状态", "截图"]
        self.activity_table.setColumnCount(len(headers))
        self.activity_table.setHorizontalHeaderLabels(headers)

        # Set column widths
        header = self.activity_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)  # Time
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Description
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)  # Confidence
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)  # Status
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)  # Screenshot

        self.activity_table.setColumnWidth(0, 150)  # Time
        self.activity_table.setColumnWidth(2, 80)   # Confidence
        self.activity_table.setColumnWidth(3, 80)   # Status
        self.activity_table.setColumnWidth(4, 80)   # Screenshot

        # Set selection behavior
        self.activity_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.activity_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)

        # Connect selection change
        self.activity_table.itemSelectionChanged.connect(self.on_selection_changed)

        # Set alternating row colors
        self.activity_table.setAlternatingRowColors(True)

        # Set sorting
        self.activity_table.setSortingEnabled(True)

    def setup_filters(self):
        """Setup filter connections"""
        self.start_date.dateChanged.connect(self.on_filter_changed)
        self.end_date.dateChanged.connect(self.on_filter_changed)
        self.search_input.textChanged.connect(self.on_filter_changed)
        self.status_filter.currentTextChanged.connect(self.on_filter_changed)
        self.show_screenshots_cb.toggled.connect(self.on_filter_changed)
        self.page_size_spin.valueChanged.connect(self.on_filter_changed)

        # Auto-apply filters after typing delay
        self.filter_timer = QTimer()
        self.filter_timer.setSingleShot(True)
        self.filter_timer.timeout.connect(self.apply_filters)

    def on_filter_changed(self):
        """Handle filter changes with delay"""
        self.filter_timer.stop()
        self.filter_timer.start(500)  # 500ms delay

    def load_activities(self, activities: List[Dict[str, Any]]):
        """Load activities data"""
        self.activities = activities
        self.apply_filters()

    def apply_filters(self):
        """Apply current filters to the activity list"""
        if not self.activities:
            return

        filtered = []
        start_date = self.start_date.date().toPyDate()
        end_date = self.end_date.date().toPyDate()
        search_text = self.search_input.text().lower()
        status_filter = self.status_filter.currentText()
        show_screenshots = self.show_screenshots_cb.isChecked()

        for activity in self.activities:
            # Parse timestamp
            try:
                activity_date = datetime.fromisoformat(activity.get("timestamp", "")).date()
            except:
                continue

            # Date filter
            if not (start_date <= activity_date <= end_date):
                continue

            # Search filter
            description = activity.get("activity_description", "").lower()
            if search_text and search_text not in description:
                continue

            # Status filter
            is_successful = activity.get("analysis_successful", False)
            if status_filter == "分析成功" and not is_successful:
                continue
            elif status_filter == "分析失败" and is_successful:
                continue

            # Screenshot filter
            has_screenshot = bool(activity.get("screenshot_path", "").strip())
            if not show_screenshots and not has_screenshot:
                continue

            filtered.append(activity)

        self.filtered_activities = filtered
        self.update_table()

    def update_table(self):
        """Update the table with filtered activities"""
        page_size = self.page_size_spin.value()
        activities_to_show = self.filtered_activities[:page_size]

        self.activity_table.setRowCount(len(activities_to_show))

        for row, activity in enumerate(activities_to_show):
            # Time
            timestamp = activity.get("timestamp", "")
            try:
                dt = datetime.fromisoformat(timestamp)
                time_str = dt.strftime("%m-%d %H:%M:%S")
            except:
                time_str = timestamp[:16] if len(timestamp) >= 16 else timestamp

            self.activity_table.setItem(row, 0, QTableWidgetItem(time_str))

            # Description
            description = activity.get("activity_description", "无描述")
            desc_item = QTableWidgetItem(description[:100] + "..." if len(description) > 100 else description)
            desc_item.setToolTip(description)  # Full description in tooltip
            self.activity_table.setItem(row, 1, desc_item)

            # Confidence
            confidence = activity.get("confidence", "unknown")
            conf_item = QTableWidgetItem(confidence)
            if confidence == "high":
                conf_item.setBackground(QBrush(QColor(200, 255, 200)))
            elif confidence == "low":
                conf_item.setBackground(QBrush(QColor(255, 220, 220)))
            self.activity_table.setItem(row, 2, conf_item)

            # Status
            is_successful = activity.get("analysis_successful", False)
            status_item = QTableWidgetItem("成功" if is_successful else "失败")
            if is_successful:
                status_item.setBackground(QBrush(QColor(200, 255, 200)))
            else:
                status_item.setBackground(QBrush(QColor(255, 220, 220)))
            self.activity_table.setItem(row, 3, status_item)

            # Screenshot
            has_screenshot = bool(activity.get("screenshot_path", "").strip())
            screenshot_item = QTableWidgetItem("有" if has_screenshot else "无")
            if has_screenshot:
                screenshot_item.setBackground(QBrush(QColor(220, 240, 255)))
            self.activity_table.setItem(row, 4, screenshot_item)

        # Update status
        total_count = len(self.activities)
        filtered_count = len(self.filtered_activities)
        shown_count = len(activities_to_show)

        status_text = f"总计: {total_count} 条记录"
        if filtered_count != total_count:
            status_text += f" | 筛选后: {filtered_count} 条"
        if shown_count != filtered_count:
            status_text += f" | 显示: {shown_count} 条"

        self.status_label.setText(status_text)

    def clear_filters(self):
        """Clear all filters"""
        self.start_date.setDate(QDate.currentDate().addDays(-7))
        self.end_date.setDate(QDate.currentDate())
        self.search_input.clear()
        self.status_filter.setCurrentText("全部")
        self.show_screenshots_cb.setChecked(True)

    def refresh_data(self):
        """Request data refresh"""
        self.apply_filters()

    def on_selection_changed(self):
        """Handle selection changes"""
        current_row = self.activity_table.currentRow()
        if 0 <= current_row < len(self.filtered_activities):
            activity = self.filtered_activities[current_row]
            self.show_activity_details(activity)
            self.activity_selected.emit(activity)

    def show_activity_details(self, activity: Dict[str, Any]):
        """Show detailed information for selected activity"""
        # Format details
        details = []
        details.append(f"时间: {activity.get('timestamp', 'N/A')}")
        details.append(f"描述: {activity.get('activity_description', 'N/A')}")
        details.append(f"置信度: {activity.get('confidence', 'N/A')}")
        details.append(f"分析状态: {'成功' if activity.get('analysis_successful', False) else '失败'}")

        if activity.get('error'):
            details.append(f"错误信息: {activity['error']}")

        analysis_result = activity.get('analysis_result', {})
        if analysis_result and isinstance(analysis_result, dict):
            if 'reasoning_content' in analysis_result:
                details.append(f"分析过程: {analysis_result['reasoning_content'][:200]}...")

        self.details_text.setPlainText("\n\n".join(details))

        # Update screenshot info
        screenshot_path = activity.get('screenshot_path', '')
        if screenshot_path and screenshot_path.strip():
            if os.path.exists(screenshot_path):
                self.screenshot_path_label.setText(f"截图: {os.path.basename(screenshot_path)}")
                self.view_screenshot_btn.setEnabled(True)
            else:
                self.screenshot_path_label.setText(f"截图: {os.path.basename(screenshot_path)} (文件不存在)")
                self.view_screenshot_btn.setEnabled(False)
        else:
            self.screenshot_path_label.setText("截图: 无")
            self.view_screenshot_btn.setEnabled(False)

    def view_screenshot(self):
        """View the screenshot for selected activity"""
        current_row = self.activity_table.currentRow()
        if 0 <= current_row < len(self.filtered_activities):
            activity = self.filtered_activities[current_row]
            screenshot_path = activity.get('screenshot_path', '')
            if screenshot_path:
                self.request_screenshot.emit(screenshot_path)

    def get_selected_activity(self) -> Optional[Dict[str, Any]]:
        """Get currently selected activity"""
        current_row = self.activity_table.currentRow()
        if 0 <= current_row < len(self.filtered_activities):
            return self.filtered_activities[current_row]
        return None