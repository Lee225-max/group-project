#!/usr/bin/env python3
"""
复习闹钟程序主入口
"""

import sys
import os

# 添加当前目录到Python路径，这样可以直接导入模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import ReviewAlarmApp


def main():
    """主函数"""
    try:
        app = ReviewAlarmApp()
        app.run()
    except Exception as e:
        print(f"程序启动失败: {e} - main.py:21")
        sys.exit(1)


if __name__ == "__main__":
    main()