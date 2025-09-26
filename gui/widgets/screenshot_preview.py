"""
Screenshot Preview Widget
截图预览组件
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QDialog, QDialogButtonBox, QTextEdit, QGroupBox,
    QSizePolicy, QApplication
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QPixmap, QFont, QPainter, QPen, QColor
from PIL import Image
import os
from datetime import datetime
from typing import Optional


class ScreenshotPreviewWidget(QWidget):
    """Widget for previewing screenshots with scaling and full-screen options"""

    # Signals
    image_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_image_path = None
        self.original_pixmap = None

        self.init_ui()

    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)

        # Info section
        info_layout = QHBoxLayout()

        self.info_label = QLabel("未选择截图")
        self.info_label.setStyleSheet("color: #666; font-size: 12px;")
        info_layout.addWidget(self.info_label)

        info_layout.addStretch()

        # Full screen button
        self.fullscreen_btn = QPushButton("全屏查看")
        self.fullscreen_btn.setEnabled(False)
        self.fullscreen_btn.clicked.connect(self.show_fullscreen)
        info_layout.addWidget(self.fullscreen_btn)

        # Save as button
        self.save_btn = QPushButton("另存为")
        self.save_btn.setEnabled(False)
        self.save_btn.clicked.connect(self.save_image)
        info_layout.addWidget(self.save_btn)

        layout.addLayout(info_layout)

        # Image scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: 2px dashed #ccc;
                border-radius: 8px;
                background-color: #f8f9fa;
            }
        """)

        # Image label
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setMinimumSize(300, 200)
        self.image_label.setStyleSheet("color: #999; font-size: 14px;")
        self.image_label.setText("选择一个活动记录查看对应截图")
        self.image_label.mousePressEvent = self.on_image_clicked
        self.image_label.setCursor(Qt.CursorShape.PointingHandCursor)

        self.scroll_area.setWidget(self.image_label)
        self.scroll_area.setWidgetResizable(True)
        layout.addWidget(self.scroll_area)

        # Scaling controls
        control_layout = QHBoxLayout()

        self.scale_label = QLabel("缩放: 100%")
        control_layout.addWidget(self.scale_label)

        control_layout.addStretch()

        self.fit_btn = QPushButton("适应窗口")
        self.fit_btn.setEnabled(False)
        self.fit_btn.clicked.connect(self.fit_to_window)
        control_layout.addWidget(self.fit_btn)

        self.actual_size_btn = QPushButton("实际大小")
        self.actual_size_btn.setEnabled(False)
        self.actual_size_btn.clicked.connect(self.show_actual_size)
        control_layout.addWidget(self.actual_size_btn)

        layout.addLayout(control_layout)

    def load_screenshot(self, image_path: str):
        """Load and display a screenshot"""
        if not image_path or not os.path.exists(image_path):
            self.clear_image()
            return

        try:
            # Load image
            pixmap = QPixmap(image_path)
            if pixmap.isNull():
                self.show_error("无法加载图片")
                return

            self.current_image_path = image_path
            self.original_pixmap = pixmap

            # Update info
            file_info = os.stat(image_path)
            file_size = file_info.st_size / 1024  # KB
            modified_time = datetime.fromtimestamp(file_info.st_mtime)

            info_text = f"{os.path.basename(image_path)} | {pixmap.width()}x{pixmap.height()} | {file_size:.1f}KB | {modified_time.strftime('%Y-%m-%d %H:%M:%S')}"
            self.info_label.setText(info_text)

            # Enable buttons
            self.fullscreen_btn.setEnabled(True)
            self.save_btn.setEnabled(True)
            self.fit_btn.setEnabled(True)
            self.actual_size_btn.setEnabled(True)

            # Fit to window by default
            self.fit_to_window()

        except Exception as e:
            self.show_error(f"加载图片失败: {str(e)}")

    def clear_image(self):
        """Clear the current image"""
        self.current_image_path = None
        self.original_pixmap = None

        self.image_label.clear()
        self.image_label.setText("未找到截图文件")
        self.info_label.setText("未选择截图")

        # Disable buttons
        self.fullscreen_btn.setEnabled(False)
        self.save_btn.setEnabled(False)
        self.fit_btn.setEnabled(False)
        self.actual_size_btn.setEnabled(False)

        self.scale_label.setText("缩放: 100%")

    def show_error(self, message: str):
        """Show error message"""
        self.image_label.clear()
        self.image_label.setText(f"❌ {message}")
        self.image_label.setStyleSheet("color: #dc3545; font-size: 14px;")

    def fit_to_window(self):
        """Fit image to window size"""
        if not self.original_pixmap:
            return

        # Get available size
        available_size = self.scroll_area.viewport().size()
        available_size.setWidth(available_size.width() - 20)  # Margin
        available_size.setHeight(available_size.height() - 20)

        # Scale pixmap to fit
        scaled_pixmap = self.original_pixmap.scaled(
            available_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        self.image_label.setPixmap(scaled_pixmap)
        self.image_label.setFixedSize(scaled_pixmap.size())

        # Calculate scale percentage
        scale_x = scaled_pixmap.width() / self.original_pixmap.width()
        scale_y = scaled_pixmap.height() / self.original_pixmap.height()
        scale = min(scale_x, scale_y)

        self.scale_label.setText(f"缩放: {scale * 100:.0f}%")

    def show_actual_size(self):
        """Show image at actual size"""
        if not self.original_pixmap:
            return

        self.image_label.setPixmap(self.original_pixmap)
        self.image_label.setFixedSize(self.original_pixmap.size())
        self.scale_label.setText("缩放: 100%")

    def on_image_clicked(self, event):
        """Handle image click"""
        if self.original_pixmap:
            self.image_clicked.emit()
            self.show_fullscreen()

    def show_fullscreen(self):
        """Show image in fullscreen dialog"""
        if not self.current_image_path:
            return

        dialog = FullscreenImageDialog(self.current_image_path, self)
        dialog.exec()

    def save_image(self):
        """Save image to a new location"""
        if not self.current_image_path:
            return

        from PyQt6.QtWidgets import QFileDialog

        default_name = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存截图",
            default_name,
            "PNG图片 (*.png);;JPEG图片 (*.jpg);;所有文件 (*.*)"
        )

        if file_path:
            try:
                # Copy the file
                pixmap = QPixmap(self.current_image_path)
                pixmap.save(file_path)

                # Show success message
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.information(self, "成功", f"截图已保存到:\n{file_path}")

            except Exception as e:
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.warning(self, "错误", f"保存截图失败:\n{str(e)}")

    def resizeEvent(self, event):
        """Handle resize events"""
        super().resizeEvent(event)
        # Auto fit to window when widget is resized
        if self.original_pixmap and self.fit_btn.isEnabled():
            # Small delay to avoid too frequent updates
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(100, self.fit_to_window)


class FullscreenImageDialog(QDialog):
    """Fullscreen image viewer dialog"""

    def __init__(self, image_path: str, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.init_ui()

    def init_ui(self):
        """Initialize the dialog"""
        self.setWindowTitle("截图全屏查看")
        self.setModal(True)
        self.resize(1200, 800)

        layout = QVBoxLayout(self)

        # Scroll area for the image
        scroll_area = QScrollArea()
        scroll_area.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Image label
        image_label = QLabel()
        pixmap = QPixmap(self.image_path)

        if not pixmap.isNull():
            # Scale to fit screen while maintaining aspect ratio
            screen_size = QApplication.primaryScreen().availableGeometry().size()
            max_size = QSize(screen_size.width() - 100, screen_size.height() - 200)

            scaled_pixmap = pixmap.scaled(
                max_size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )

            image_label.setPixmap(scaled_pixmap)
        else:
            image_label.setText("无法加载图片")

        scroll_area.setWidget(image_label)
        layout.addWidget(scroll_area)

        # Buttons
        button_box = QDialogButtonBox()

        # Actual size button
        actual_size_btn = button_box.addButton("实际大小", QDialogButtonBox.ButtonRole.ActionRole)
        actual_size_btn.clicked.connect(lambda: self.set_image_scale(image_label, pixmap, 1.0))

        # Fit to window button
        fit_btn = button_box.addButton("适合窗口", QDialogButtonBox.ButtonRole.ActionRole)
        fit_btn.clicked.connect(lambda: self.fit_image_to_dialog(image_label, pixmap, scroll_area))

        # Close button
        close_btn = button_box.addButton("关闭", QDialogButtonBox.ButtonRole.RejectRole)
        close_btn.clicked.connect(self.accept)

        layout.addWidget(button_box)

        # Enable zooming with mouse wheel
        scroll_area.wheelEvent = self.wheel_event

    def set_image_scale(self, image_label: QLabel, pixmap: QPixmap, scale: float):
        """Set image to specific scale"""
        if pixmap.isNull():
            return

        scaled_size = QSize(
            int(pixmap.width() * scale),
            int(pixmap.height() * scale)
        )

        scaled_pixmap = pixmap.scaled(
            scaled_size,
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        image_label.setPixmap(scaled_pixmap)
        image_label.setFixedSize(scaled_pixmap.size())

    def fit_image_to_dialog(self, image_label: QLabel, pixmap: QPixmap, scroll_area: QScrollArea):
        """Fit image to dialog size"""
        if pixmap.isNull():
            return

        available_size = scroll_area.viewport().size()
        available_size.setWidth(available_size.width() - 20)
        available_size.setHeight(available_size.height() - 20)

        scaled_pixmap = pixmap.scaled(
            available_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        image_label.setPixmap(scaled_pixmap)
        image_label.setFixedSize(scaled_pixmap.size())

    def wheel_event(self, event):
        """Handle mouse wheel for zooming"""
        # This would implement zoom functionality
        pass

    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == Qt.Key.Key_Escape:
            self.accept()
        else:
            super().keyPressEvent(event)