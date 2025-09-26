"""
Main Window for Activity Recorder GUI
活动记录器主窗口
"""

import sys
import asyncio
import logging
import contextlib
from datetime import datetime, timedelta
from typing import Dict, Any

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QMenuBar, QStatusBar, QSystemTrayIcon, QMenu, QMessageBox,
    QApplication, QSplitter, QLabel, QPushButton, QProgressBar
)
from PyQt6.QtCore import (
    Qt, QTimer, pyqtSignal, pyqtSlot, QThread, QObject, QSystemSemaphore,
    QSharedMemory, QCoreApplication, QMetaObject
)
from PyQt6.QtGui import (
    QIcon,
    QAction,
    QCloseEvent,
    QPixmap,
    QGuiApplication,
    QPalette,
    QColor,
)

# Import our components
from .config_manager import GUIConfig
from .widgets.status_widget import StatusWidget
from .widgets.activity_list import ActivityListWidget
from .widgets.screenshot_preview import ScreenshotPreviewWidget

# Import backend components
from storage import ActivityStorage
from workflow import ActivityRecorderWorkflow



class RecordingWorker(QObject):
    """Worker thread for running the recording workflow"""

    # Signals
    recording_started = pyqtSignal()
    recording_stopped = pyqtSignal()
    activity_recorded = pyqtSignal(dict)  # New activity data
    error_occurred = pyqtSignal(str)  # Error message
    status_updated = pyqtSignal(str)  # Status message

    def __init__(self):
        super().__init__()
        self.workflow = None
        self.is_running = False
        self.loop = None
        self.recording_task = None
        self.config = {}
        self.stop_event = None

    def update_config(self, config: Dict[str, Any]):
        """Store the latest config for use within the worker thread"""
        self.config = config or {}

    @pyqtSlot()
    def start_recording(self):
        """Start the recording process"""
        if self.is_running:
            return

        config = self.config or {}

        try:
            # Initialize workflow with config
            self.workflow = ActivityRecorderWorkflow()

            # Update workflow configuration based on GUI settings
            if 'interval' in config:
                self.workflow.config.SCREENSHOT_INTERVAL = config['interval']

            self.is_running = True

            # Create stop event
            self.stop_event = asyncio.Event()

            # Start async loop in this thread
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)

            # Start the recording task
            self.recording_task = self.loop.create_task(self._run_continuous_recording())
            self.recording_started.emit()

            # Run until the task completes (instead of run_forever)
            try:
                self.loop.run_until_complete(self.recording_task)
            except asyncio.CancelledError:
                logging.info("Recording task was cancelled")

        except Exception as exc:
            self.error_occurred.emit(f"录制启动失败: {str(exc)}")
        finally:
            # Clean up resources after loop has stopped
            self._cleanup_recording()

    @pyqtSlot()
    def stop_recording(self):
        """Stop the recording process"""
        if not self.is_running:
            return

        logging.info("Worker received stop signal")
        self.is_running = False

        # Signal the async task to stop
        if self.stop_event:
            try:
                if self.loop and self.loop.is_running():
                    self.loop.call_soon_threadsafe(self.stop_event.set)
            except Exception as e:
                logging.error(f"Error setting stop event: {e}")

        # Cancel the recording task
        if self.recording_task and not self.recording_task.done():
            try:
                if self.loop and self.loop.is_running():
                    self.loop.call_soon_threadsafe(self.recording_task.cancel)
                else:
                    self.recording_task.cancel()
            except Exception as e:
                logging.error(f"Error cancelling task: {e}")

    async def _run_continuous_recording(self):
        """Run continuous recording"""
        logging.info("Starting continuous recording loop")
        try:
            while self.is_running:
                # Check if stop was requested
                if self.stop_event and self.stop_event.is_set():
                    logging.info("Stop event detected")
                    break

                # Run single cycle
                result = await self.workflow.run_single_cycle()

                if result.get("success", False):
                    self.activity_recorded.emit(result)
                    self.status_updated.emit(f"录制成功: {result.get('activity_description', 'N/A')[:50]}...")
                else:
                    self.status_updated.emit(f"录制失败: {result.get('error', 'Unknown error')}")

                # Wait for next cycle or stop event
                if self.is_running and not (self.stop_event and self.stop_event.is_set()):
                    try:
                        interval = self.workflow.config.get_screenshot_interval()
                        # Wait for either timeout or stop event
                        await asyncio.wait_for(
                            self.stop_event.wait() if self.stop_event else asyncio.sleep(interval),
                            timeout=interval
                        )
                        # If stop event was set, break the loop
                        if self.stop_event and self.stop_event.is_set():
                            break
                    except asyncio.TimeoutError:
                        # Normal timeout, continue the loop
                        continue
                    except asyncio.CancelledError:
                        logging.info("Recording sleep cancelled")
                        break

        except asyncio.CancelledError:
            logging.info("Recording task cancelled")
            self.status_updated.emit("录制已停止")
        except Exception as exc:
            logging.error(f"Recording error: {exc}")
            self.error_occurred.emit(f"录制过程中出错: {str(exc)}")
        finally:
            logging.info("Recording loop finished")
            self.is_running = False

    def _cleanup_recording(self):
        """Clean up recording resources"""
        logging.info("Cleaning up recording resources")

        try:
            # Clean up the task first
            if self.recording_task and not self.recording_task.done():
                with contextlib.suppress(Exception):
                    self.recording_task.cancel()

            # Clean up the event loop
            if self.loop and not self.loop.is_closed():
                with contextlib.suppress(Exception):
                    # Cancel any remaining tasks
                    try:
                        pending = asyncio.all_tasks(self.loop) if hasattr(asyncio, 'all_tasks') else asyncio.Task.all_tasks(self.loop)
                        for t in pending:
                            if not t.done():
                                t.cancel()
                    except Exception:
                        pass

                    # Close the loop
                    self.loop.close()

        finally:
            # Clear references
            self.recording_task = None
            self.loop = None
            self.workflow = None
            self.stop_event = None
            self.is_running = False

            # Emit stopped signal last
            try:
                self.recording_stopped.emit()
            except Exception as e:
                logging.debug(f"Failed to emit recording_stopped signal: {e}")



class MainWindow(QMainWindow):
    """Main application window"""

    def __init__(self):
        super().__init__()

        # Initialize configuration
        self.gui_config = GUIConfig()
        self.storage = ActivityStorage()

        # Recording worker
        self.recording_worker = None
        self.recording_thread = None

        # System tray
        self.tray_icon = None
        self._force_quit = False  # Flag to force quit instead of minimize to tray

        # Timers
        self.data_refresh_timer = QTimer()
        self.data_refresh_timer.timeout.connect(self.refresh_data)
        self.data_refresh_timer.start(5000)  # Refresh every 5 seconds

        # Initialize UI
        self.init_ui()
        self.setup_system_tray()
        self.setup_menus()
        self.restore_window_state()

        # Load initial data
        self.refresh_data()

    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("活动记录器 - Auto Activity Recorder")
        self.setMinimumSize(1200, 800)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)

        # Create tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        # Status and control tab
        self.create_status_tab()

        # Activity viewer tab
        self.create_activity_tab()

        # Time query tab
        self.create_time_query_tab()

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Add permanent widgets to status bar
        self.recording_status_label = QLabel("状态: 未录制")
        self.status_bar.addPermanentWidget(self.recording_status_label)

        self.activity_count_label = QLabel("活动记录: 0")
        self.status_bar.addPermanentWidget(self.activity_count_label)

    def create_status_tab(self):
        """Create the status and control tab"""
        status_widget = QWidget()
        layout = QHBoxLayout(status_widget)

        # Left side: Status widget
        self.status_widget = StatusWidget()
        self.status_widget.start_recording.connect(self.start_recording)
        self.status_widget.stop_recording.connect(self.stop_recording)
        self.status_widget.open_settings.connect(self.show_settings)

        layout.addWidget(self.status_widget, stretch=1)

        # Right side: Recent screenshot preview
        preview_group = QWidget()
        preview_layout = QVBoxLayout(preview_group)

        preview_title = QLabel("最近截图预览")
        preview_title.setStyleSheet("font-weight: bold; font-size: 14px; margin: 5px;")
        preview_layout.addWidget(preview_title)

        self.preview_widget = ScreenshotPreviewWidget()
        preview_layout.addWidget(self.preview_widget)

        layout.addWidget(preview_group, stretch=1)

        self.tab_widget.addTab(status_widget, "状态控制")

    def create_activity_tab(self):
        """Create the activity viewer tab"""
        activity_widget = QWidget()
        layout = QVBoxLayout(activity_widget)

        # Create splitter for activity list and preview
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Activity list
        self.activity_list_widget = ActivityListWidget()
        self.activity_list_widget.activity_selected.connect(self.on_activity_selected)
        self.activity_list_widget.request_screenshot.connect(self.show_screenshot)
        splitter.addWidget(self.activity_list_widget)

        # Screenshot preview
        self.activity_preview_widget = ScreenshotPreviewWidget()
        splitter.addWidget(self.activity_preview_widget)

        # Set splitter proportions
        splitter.setSizes([800, 400])
        layout.addWidget(splitter)

        self.tab_widget.addTab(activity_widget, "活动记录")

    def create_time_query_tab(self):
        """Create the time query tab"""
        from .time_query_widget import TimeQueryWidget

        self.time_query_widget = TimeQueryWidget()
        self.tab_widget.addTab(self.time_query_widget, "时间查询")

    def setup_menus(self):
        """Setup menu bar"""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("文件")

        # Settings action
        settings_action = QAction("设置", self)
        settings_action.setShortcut("Ctrl+,")
        settings_action.triggered.connect(self.show_settings)
        file_menu.addAction(settings_action)

        file_menu.addSeparator()

        # Export action
        export_action = QAction("导出数据", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self.export_data)
        file_menu.addAction(export_action)

        file_menu.addSeparator()

        # Exit action
        exit_action = QAction("退出", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.force_quit)
        file_menu.addAction(exit_action)

        # Recording menu
        recording_menu = menubar.addMenu("录制")

        # Start recording action
        start_action = QAction("开始录制", self)
        start_action.setShortcut("Ctrl+R")
        start_action.triggered.connect(self.start_recording)
        recording_menu.addAction(start_action)

        # Stop recording action
        stop_action = QAction("停止录制", self)
        stop_action.setShortcut("Ctrl+S")
        stop_action.triggered.connect(self.stop_recording)
        recording_menu.addAction(stop_action)

        # View menu
        view_menu = menubar.addMenu("查看")

        # Refresh action
        refresh_action = QAction("刷新", self)
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(self.refresh_data)
        view_menu.addAction(refresh_action)

        # Help menu
        help_menu = menubar.addMenu("帮助")

        # About action
        about_action = QAction("关于", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def setup_system_tray(self):
        """Setup system tray icon"""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return

        # Create tray icon (using a simple colored pixmap as placeholder)
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.GlobalColor.blue)
        self.tray_icon = QSystemTrayIcon(QIcon(pixmap), self)

        # Create tray menu
        tray_menu = QMenu()

        # Show/Hide action
        show_action = tray_menu.addAction("显示窗口")
        show_action.triggered.connect(self.show_window)

        tray_menu.addSeparator()

        # Recording actions
        start_action = tray_menu.addAction("开始录制")
        start_action.triggered.connect(self.start_recording)

        stop_action = tray_menu.addAction("停止录制")
        stop_action.triggered.connect(self.stop_recording)

        tray_menu.addSeparator()

        # Exit action
        exit_action = tray_menu.addAction("退出")
        exit_action.triggered.connect(self.force_quit)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.on_tray_activated)
        self.tray_icon.show()

    def on_tray_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_window()

    def show_window(self):
        """Show and raise the window"""
        self.show()
        self.raise_()
        self.activateWindow()

    def force_quit(self):
        """Force quit the application"""
        self._force_quit = True
        self.close()

    def start_recording(self):
        """Start recording"""
        if self.recording_worker and self.recording_thread and self.recording_thread.isRunning():
            return

        # Get current settings
        config = self.gui_config.get_recording_settings()

        # Create worker and thread
        self.recording_worker = RecordingWorker()
        self.recording_worker.update_config(config)
        self.recording_thread = QThread()

        # Move worker to thread
        self.recording_worker.moveToThread(self.recording_thread)

        # Connect signals
        self.recording_thread.started.connect(self.recording_worker.start_recording)
        self.recording_worker.recording_started.connect(self.on_recording_started)
        self.recording_worker.recording_stopped.connect(self.on_recording_stopped)
        self.recording_worker.activity_recorded.connect(self.on_activity_recorded)
        self.recording_worker.error_occurred.connect(self.on_recording_error)
        self.recording_worker.status_updated.connect(self.update_status_message)

        # Start thread
        self.recording_thread.start()

    def stop_recording(self):
        """Stop recording"""
        if not self.recording_worker and not self.recording_thread:
            return

        logging.info("Stopping recording...")

        try:
            # 1) Request the async task to stop immediately from the main thread
            # Avoid relying on a queued Qt slot that can't run while the worker's
            # long-running start slot is executing. Instead, post directly to the
            # worker's asyncio loop which is thread-safe.
            if self.recording_worker:
                try:
                    # Best-effort flip of the flag (not strictly required when using the event)
                    self.recording_worker.is_running = False

                    loop = getattr(self.recording_worker, "loop", None)
                    stop_event = getattr(self.recording_worker, "stop_event", None)
                    task = getattr(self.recording_worker, "recording_task", None)

                    if loop:
                        def _request_async_stop():  # runs in worker's asyncio loop thread
                            try:
                                if stop_event:
                                    stop_event.set()
                                if task and not task.done():
                                    task.cancel()
                            except Exception as _e:
                                logging.error(f"Error requesting async stop: {_e}")

                        try:
                            loop.call_soon_threadsafe(_request_async_stop)
                        except Exception as e:
                            logging.error(f"Failed to schedule async stop: {e}")
                    else:
                        # Fallback to queued Qt slot if loop not ready
                        QMetaObject.invokeMethod(
                            self.recording_worker,
                            "stop_recording",
                            Qt.ConnectionType.QueuedConnection
                        )
                except Exception as e:
                    logging.error(f"Error posting stop to worker: {e}")

            # 2) Quit the QThread event loop so it can finish once the async task ends
            if self.recording_thread and self.recording_thread.isRunning():
                try:
                    self.recording_thread.quit()
                except Exception as e:
                    logging.debug(f"Error quitting recording thread: {e}")

                # 3) Wait for the thread to finish; give it enough time for cleanup
                if not self.recording_thread.wait(5000):  # Wait up to 5 seconds
                    logging.warning("Recording thread did not stop gracefully, terminating...")
                    self.recording_thread.terminate()
                    if not self.recording_thread.wait(2000):  # Give it 2 more seconds
                        logging.error("Failed to terminate recording thread - forcing cleanup")
                else:
                    logging.info("Recording thread stopped successfully")

        except Exception as e:
            logging.error(f"Error stopping recording: {e}")

        finally:
            # Always clean up worker and thread objects, but only after the thread has stopped
            try:
                if self.recording_thread and self.recording_thread.isRunning():
                    # As a last guard, don't delete objects while the thread is still running
                    logging.debug("Deferring deletion until thread stops")
                else:
                    if self.recording_worker:
                        try:
                            self.recording_worker.deleteLater()
                        except Exception:
                            pass
                        self.recording_worker = None

                    if self.recording_thread:
                        try:
                            self.recording_thread.deleteLater()
                        except Exception:
                            pass
                        self.recording_thread = None
            finally:
                # If something went wrong above, still null the references
                if self.recording_thread and self.recording_thread.isRunning():
                    # Avoid deleting running thread; keep references to prevent destruction crash
                    pass
                else:
                    self.recording_worker = None
                    self.recording_thread = None

            logging.info("Recording cleanup completed")

    def on_recording_started(self):
        """Handle recording started"""
        self.status_widget.set_recording_state(True)
        self.recording_status_label.setText("状态: 正在录制")

        # Set next capture time
        interval = self.gui_config.get("recording.interval", 180)
        next_time = datetime.now() + timedelta(seconds=interval)
        self.status_widget.set_next_capture_time(next_time)

        self.status_bar.showMessage("录制已开始", 3000)

    def on_recording_stopped(self):
        """Handle recording stopped"""
        self.status_widget.set_recording_state(False)
        self.recording_status_label.setText("状态: 未录制")
        self.status_bar.showMessage("录制已停止", 3000)

    def on_activity_recorded(self, activity_data):
        """Handle new activity recorded"""
        # Update status widget with latest activity
        description = activity_data.get('activity_description', 'N/A')
        timestamp = activity_data.get('timestamp', '')
        self.status_widget.update_last_activity(description, timestamp)

        # Load latest screenshot in preview
        screenshot_path = activity_data.get('screenshot_path', '')
        if screenshot_path:
            self.preview_widget.load_screenshot(screenshot_path)

        # Refresh activity list
        self.refresh_data()

        # Update next capture time
        interval = self.gui_config.get("recording.interval", 180)
        next_time = datetime.now() + timedelta(seconds=interval)
        self.status_widget.set_next_capture_time(next_time)

    def on_recording_error(self, error_message):
        """Handle recording error"""
        self.status_bar.showMessage(f"录制错误: {error_message}", 10000)
        self.status_widget.add_log_message(error_message, "ERROR")

    def update_status_message(self, message):
        """Update status message"""
        self.status_bar.showMessage(message, 3000)

    def on_activity_selected(self, activity_data):
        """Handle activity selection"""
        screenshot_path = activity_data.get('screenshot_path', '')
        if screenshot_path:
            self.activity_preview_widget.load_screenshot(screenshot_path)

    def show_screenshot(self, screenshot_path):
        """Show screenshot in preview"""
        # Switch to activity tab and load screenshot
        self.tab_widget.setCurrentIndex(1)  # Activity tab
        self.activity_preview_widget.load_screenshot(screenshot_path)

    def refresh_data(self):
        """Refresh activity data"""
        try:
            # Get recent activities
            activities = self.storage.get_recent_activities(limit=1000)

            # Update activity list
            self.activity_list_widget.load_activities(activities)

            # Update activity count
            self.activity_count_label.setText(f"活动记录: {len(activities)}")

            # Get statistics
            stats = self.storage.get_activity_statistics()
            success_rate = stats.get('success_rate', 0)

            # Update interval setting in status widget
            interval = self.gui_config.get("recording.interval", 180)
            self.status_widget.set_interval(interval)

        except Exception as e:
            # Safety check: only show status message if status_bar exists
            if hasattr(self, 'status_bar'):
                self.status_bar.showMessage(f"数据刷新失败: {str(e)}", 5000)
            else:
                print(f"数据刷新失败: {str(e)}")  # Fallback to console output

    def show_settings(self):
        """Show settings dialog"""
        from .settings_dialog import SettingsDialog

        dialog = SettingsDialog(self)
        dialog.settings_changed.connect(self.on_settings_changed)
        dialog.exec()

    def on_settings_changed(self):
        """Handle settings changes"""
        # Reload configuration
        self.gui_config = GUIConfig()

        # Update UI with new settings
        self.refresh_data()

        # Update status widget interval
        interval = self.gui_config.get("recording.interval", 180)
        self.status_widget.set_interval(interval)

        self.status_bar.showMessage("设置已更新", 3000)

    def export_data(self):
        """Export activity data"""
        from PyQt6.QtWidgets import QFileDialog
        from datetime import datetime

        default_name = f"activity_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "导出活动数据",
            default_name,
            "JSON文件 (*.json);;所有文件 (*.*)"
        )

        if file_path:
            try:
                success = self.storage.export_activities(file_path)
                if success:
                    QMessageBox.information(self, "成功", f"数据已导出到:\n{file_path}")
                else:
                    QMessageBox.warning(self, "失败", "数据导出失败")
            except Exception as e:
                QMessageBox.warning(self, "错误", f"导出失败:\n{str(e)}")

    def show_about(self):
        """Show about dialog"""
        about_text = """
        <h2>活动记录器 v1.0</h2>
        <p>自动截图并使用AI分析用户活动的工具</p>
        <p><b>功能特色:</b></p>
        <ul>
        <li>自动定时截图</li>
        <li>AI智能活动分析</li>
        <li>活动记录管理</li>
        <li>时间段查询</li>
        </ul>
        <p><b>技术支持:</b> DashScope + Qwen-VL</p>
        """
        QMessageBox.about(self, "关于", about_text)

    def restore_window_state(self):
        """Restore window state from config"""
        window_config = self.gui_config.get("window", {})

        # Restore size and position
        self.resize(
            window_config.get("width", 1200),
            window_config.get("height", 800)
        )

        if "x" in window_config and "y" in window_config:
            self.move(window_config["x"], window_config["y"])

        # Restore maximized state
        if window_config.get("maximized", False):
            self.showMaximized()

    def save_window_state(self):
        """Save window state to config"""
        if self.isMaximized():
            self.gui_config.set("window.maximized", True)
        else:
            self.gui_config.set("window.maximized", False)
            self.gui_config.set("window.width", self.width())
            self.gui_config.set("window.height", self.height())
            self.gui_config.set("window.x", self.x())
            self.gui_config.set("window.y", self.y())

        self.gui_config.save_config()

    def closeEvent(self, event: QCloseEvent):
        """Handle close event"""
        # Check if we should minimize to tray instead of closing
        minimize_to_tray = self.gui_config.get("general.minimize_to_tray", True)

        if minimize_to_tray and self.tray_icon and self.tray_icon.isVisible() and not self._force_quit:
            # Minimize to system tray
            event.ignore()
            self.hide()
            self.tray_icon.showMessage(
                "活动记录器",
                "程序已最小化到系统托盘",
                QSystemTrayIcon.MessageIcon.Information,
                2000
            )
        else:
            # Actually close the application
            self._perform_shutdown()
            event.accept()

    def _perform_shutdown(self):
        """Perform application shutdown"""
        # Save window state
        self.save_window_state()

        # Stop recording if running (with proper cleanup)
        if self.recording_worker or self.recording_thread:
            self.stop_recording()

        # Stop timers
        if hasattr(self, 'data_refresh_timer'):
            self.data_refresh_timer.stop()

        # Clean up tray icon
        if self.tray_icon:
            self.tray_icon.hide()
            self.tray_icon.deleteLater()

        # Quit the application
        QCoreApplication.quit()


def apply_macos_light_palette(app: QApplication):
    """Force a light palette on macOS so auto dark mode keeps text readable"""
    if sys.platform != "darwin":
        return

    try:
        app.setStyle("Fusion")

        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#f5f5f5"))
        palette.setColor(QPalette.ColorRole.WindowText, QColor("#333333"))
        palette.setColor(QPalette.ColorRole.Base, QColor("#ffffff"))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#f0f0f0"))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#ffffff"))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#333333"))
        palette.setColor(QPalette.ColorRole.Text, QColor("#333333"))
        palette.setColor(QPalette.ColorRole.Button, QColor("#f0f0f0"))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor("#333333"))
        palette.setColor(QPalette.ColorRole.Highlight, QColor("#4c8bf5"))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
        palette.setColor(QPalette.ColorRole.Link, QColor("#1d5bd1"))
        palette.setColor(QPalette.ColorRole.PlaceholderText, QColor("#888888"))
        app.setPalette(palette)

        app.setStyleSheet(
            "QToolTip { color: #333333; background-color: #ffffff; border: 1px solid #cccccc; }"
        )

    except Exception as exc:  # pragma: no cover - fail-safe logging
        logging.getLogger(__name__).warning("Failed to apply macOS light palette: %s", exc)

def main():
    """Main entry point for GUI application"""
    # Configure high DPI behaviour before QApplication is created
    QGuiApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)

    apply_macos_light_palette(app)

    # Set application properties
    app.setApplicationName("Auto Activity Recorder")
    app.setApplicationDisplayName("活动记录器")
    app.setApplicationVersion("1.0.0")

    # Create and show main window
    main_window = MainWindow()
    main_window.show()

    # Run application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
