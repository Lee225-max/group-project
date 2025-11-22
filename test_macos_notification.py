#!/usr/bin/env python3
"""
测试macOS系统通知功能
"""

import subprocess
import time


def test_notification_methods():
    print("🔔 测试macOS通知各种方法... - test_macos_notification.py:11")
    
    # 方法1: 使用pync
    try:
        from pync import Notifier
        print("1. 使用pync库... - test_macos_notification.py:16")
        Notifier.notify("这是一条pync测试通知", title="测试通知", sound='default')
        print("✅ pync通知已发送 - test_macos_notification.py:18")
        time.sleep(2)
    except ImportError:
        print("❌ pync未安装，运行: pip install pync - test_macos_notification.py:21")
    except Exception as e:
        print(f"❌ pync失败: {e} - test_macos_notification.py:23")
    
    # 方法2: 使用AppleScript
    print("2. 使用AppleScript... - test_macos_notification.py:26")
    script = '''
    display notification "这是一条AppleScript测试通知" with title "测试通知" sound name "default"
    '''
    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    if result.returncode == 0:
        print("✅ AppleScript通知已发送 - test_macos_notification.py:32")
    else:
        print(f"❌ AppleScript失败: {result.stderr} - test_macos_notification.py:34")
    
    # 方法3: 使用terminal-notifier（如果安装）
    print("3. 使用terminalnotifier... - test_macos_notification.py:37")
    try:
        result = subprocess.run([
            "terminal-notifier",
            "-title", "测试通知",
            "-message", "这是一条terminal-notifier测试通知",
            "-sound", "default"
        ], capture_output=True, timeout=5)
        print("✅ terminalnotifier通知已发送 - test_macos_notification.py:45")
    except (FileNotFoundError, subprocess.TimeoutExpired):
        print("ℹ️  terminalnotifier未安装 - test_macos_notification.py:47")
    
    print("\n🎯 请检查是否收到系统通知！ - test_macos_notification.py:49")
    
    
if __name__ == "__main__":
    test_notification_methods()