#!/usr/bin/env python3
"""
Automatic Activity Recorder
自动截图并记录用户活动的应用程序

使用方法:
    python main.py                    # 开始连续录制
    python main.py --single           # 只执行一次录制
    python main.py --stats            # 显示统计信息
    python main.py --export [file]    # 导出活动记录
"""

import argparse
import asyncio
import logging
import sys
from datetime import datetime
from typing import Optional

from workflow import ActivityRecorderWorkflow
from config import Config
from storage import ActivityStorage


def setup_logging() -> None:
    """设置日志记录"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('activity_recorder.log', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )


def print_banner() -> None:
    """打印应用程序横幅"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                    自动活动记录器                              ║
║                Automatic Activity Recorder                   ║
║                                                              ║
║  每3分钟自动截图并使用AI分析用户活动                            ║
║  Automatically screenshot and analyze user activity every    ║
║  3 minutes using AI                                          ║
╚══════════════════════════════════════════════════════════════╝
"""
    print(banner)


async def run_continuous_recording() -> None:
    """运行连续录制模式"""
    print("🔄 启动连续活动录制模式...")
    print("📸 每3分钟将自动截图并分析活动")
    print("⏹️  按 Ctrl+C 停止录制\n")

    try:
        workflow = ActivityRecorderWorkflow()
        await workflow.run_continuous()
    except KeyboardInterrupt:
        print("\n🛑 用户停止录制")
        print("📊 感谢使用自动活动记录器！")
    except Exception as e:
        logging.error(f"连续录制失败: {str(e)}")
        print(f"❌ 错误: {str(e)}")


async def run_single_recording() -> None:
    """运行单次录制模式"""
    print("📸 执行单次活动录制...")

    try:
        workflow = ActivityRecorderWorkflow()
        result = await workflow.run_single_cycle()

        if result.get("success", False):
            print(f"✅ 录制成功!")
            print(f"📄 活动描述: {result.get('activity_description', 'N/A')}")
            print(f"📁 截图路径: {result.get('screenshot_path', 'N/A')}")
        else:
            print(f"❌ 录制失败: {result.get('error', '未知错误')}")

    except Exception as e:
        logging.error(f"单次录制失败: {str(e)}")
        print(f"❌ 错误: {str(e)}")


def show_statistics() -> None:
    """显示统计信息"""
    print("📊 活动记录统计信息\n")

    try:
        storage = ActivityStorage()
        stats = storage.get_activity_statistics()

        if "error" in stats:
            print(f"❌ 获取统计信息失败: {stats['error']}")
            return

        print(f"📈 总记录数量: {stats['total_activities']}")
        print(f"✅ 成功分析: {stats['successful_analyses']}")
        print(f"❌ 分析失败: {stats['failed_analyses']}")
        print(f"📊 成功率: {stats['success_rate']}%")

        if stats['first_activity']:
            print(f"🕐 首次记录: {stats['first_activity']}")
        if stats['last_activity']:
            print(f"🕐 最近记录: {stats['last_activity']}")

        # 显示最近的活动
        recent_activities = storage.get_recent_activities(limit=5)
        if recent_activities:
            print(f"\n📋 最近5次活动:")
            for i, activity in enumerate(recent_activities, 1):
                timestamp = activity.get('timestamp', 'N/A')[:19]  # Remove microseconds
                description = activity.get('activity_description', 'N/A')
                success_icon = "✅" if activity.get('analysis_successful') else "❌"
                print(f"  {i}. [{timestamp}] {success_icon} {description}")

    except Exception as e:
        logging.error(f"显示统计信息失败: {str(e)}")
        print(f"❌ 错误: {str(e)}")


def export_activities(output_file: Optional[str] = None) -> None:
    """导出活动记录"""
    if not output_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"activities_export_{timestamp}.json"

    print(f"📤 导出活动记录到: {output_file}")

    try:
        storage = ActivityStorage()
        success = storage.export_activities(output_file)

        if success:
            print(f"✅ 导出成功: {output_file}")
        else:
            print("❌ 导出失败")

    except Exception as e:
        logging.error(f"导出活动记录失败: {str(e)}")
        print(f"❌ 错误: {str(e)}")


def validate_configuration() -> bool:
    """验证配置"""
    try:
        config = Config()
        config.validate_config()
        print("✅ 配置验证成功")
        return True
    except Exception as e:
        print(f"❌ 配置验证失败: {str(e)}")
        print("请检查以下配置:")
        print(f"  - API Key: {Config.get_api_key()[:10]}...")
        print(f"  - Model: {Config.get_model_name()}")
        print(f"  - Interval: {Config.get_screenshot_interval()}秒")
        return False


async def main() -> None:
    """主函数"""
    parser = argparse.ArgumentParser(
        description="自动截图活动记录器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python main.py                    # 开始连续录制
  python main.py --single           # 只执行一次录制
  python main.py --stats            # 显示统计信息
  python main.py --export output.json  # 导出到指定文件
        """
    )

    parser.add_argument(
        "--single",
        action="store_true",
        help="执行单次录制而不是连续录制"
    )

    parser.add_argument(
        "--stats",
        action="store_true",
        help="显示活动记录统计信息"
    )

    parser.add_argument(
        "--export",
        nargs="?",
        const=None,
        help="导出活动记录到文件"
    )

    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="设置日志级别"
    )

    args = parser.parse_args()

    # 设置日志
    setup_logging()
    logging.getLogger().setLevel(getattr(logging, args.log_level))

    # 显示横幅
    print_banner()

    # 验证配置
    if not validate_configuration():
        sys.exit(1)

    try:
        if args.stats:
            show_statistics()
        elif args.export is not None:
            export_activities(args.export)
        elif args.single:
            await run_single_recording()
        else:
            await run_continuous_recording()

    except Exception as e:
        logging.error(f"程序执行失败: {str(e)}")
        print(f"❌ 程序执行失败: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 程序被用户中断")
        sys.exit(0)
    except Exception as e:
        logging.error(f"程序启动失败: {str(e)}")
        print(f"❌ 程序启动失败: {str(e)}")
        sys.exit(1)