#!/usr/bin/env python3
"""
GUI Entry Point for Auto Activity Recorder
自动活动记录器GUI版本入口点

使用方法:
    python main_gui.py          # 启动GUI应用程序
    uv run main_gui.py          # 使用uv运行GUI应用程序
"""

import sys
import os
import logging
from pathlib import Path

# Add the gui module to the Python path
sys.path.insert(0, str(Path(__file__).parent))

def setup_logging():
    """Setup logging for GUI application"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('activity_recorder_gui.log', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def check_dependencies():
    """Check if required GUI dependencies are available"""
    missing_deps = []

    try:
        import PyQt6
    except ImportError:
        missing_deps.append("PyQt6")

    try:
        import dashscope
    except ImportError:
        missing_deps.append("dashscope")

    try:
        import mss
    except ImportError:
        missing_deps.append("mss")

    try:
        from PIL import Image
    except ImportError:
        missing_deps.append("pillow")

    try:
        import langgraph
    except ImportError:
        missing_deps.append("langgraph")

    if missing_deps:
        print("❌ 缺少必要的依赖库:")
        for dep in missing_deps:
            print(f"   - {dep}")
        print("\n请运行以下命令安装依赖:")
        print("   pip install -r requirements.txt")
        print("   或")
        print("   uv pip install -r requirements.txt")
        return False

    return True

def check_display_environment():
    """Check if display environment is available for screenshots"""
    if sys.platform.startswith('linux'):
        display = os.environ.get('DISPLAY')
        if not display:
            print("⚠️  警告: 未检测到显示环境 (DISPLAY 未设置)")
            print("   在无显示环境中，截图功能可能无法正常工作")
            print("   但您仍然可以使用其他功能，如查看历史记录、设置配置等")
            return False

    return True

def show_welcome():
    """Show welcome message"""
    welcome_msg = """
╔══════════════════════════════════════════════════════════════╗
║                    自动活动记录器 GUI 版                        ║
║                Auto Activity Recorder - GUI Version         ║
║                                                              ║
║  🖥️  图形界面操作，更加直观便捷                                ║
║  ⚙️  可视化设置管理                                             ║
║  📊  智能时间查询分析                                           ║
║  📸  截图预览和管理                                             ║
╚══════════════════════════════════════════════════════════════╝
"""
    print(welcome_msg)

def main():
    """Main entry point"""
    # Setup logging
    setup_logging()

    # Show welcome message
    show_welcome()

    # Check dependencies
    print("🔍 检查系统依赖...")
    if not check_dependencies():
        sys.exit(1)

    print("✅ 依赖检查通过")

    # Check display environment
    check_display_environment()

    try:
        # Import and run GUI application
        print("🚀 启动图形界面...")

        from gui.main_window import main as gui_main
        gui_main()

    except ImportError as e:
        logging.error(f"导入GUI模块失败: {str(e)}")
        print(f"❌ GUI模块导入失败: {str(e)}")
        print("请确保所有依赖都已正确安装")
        sys.exit(1)

    except Exception as e:
        logging.error(f"GUI启动失败: {str(e)}")
        print(f"❌ GUI启动失败: {str(e)}")

        # Show error dialog if possible
        try:
            from PyQt6.QtWidgets import QApplication, QMessageBox
            if not QApplication.instance():
                app = QApplication(sys.argv)

            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setWindowTitle("启动失败")
            msg.setText("GUI应用程序启动失败")
            msg.setDetailedText(str(e))
            msg.exec()

        except:
            pass  # If even error dialog fails, just exit

        sys.exit(1)

if __name__ == "__main__":
    main()