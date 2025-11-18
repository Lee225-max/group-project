#!/usr/bin/env python3
"""
应用程序启动脚本 - 在项目根目录运行
"""
from src.app import ReviewAlarmApp

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


def main():
    """主函数"""
    try:
        print("🚀 启动智能复习闹钟... - run_app.py:17")
        app = ReviewAlarmApp()
        app.run()
    except Exception as e:
        print(f"❌ 程序启动失败: {e} - run_app.py:21")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
