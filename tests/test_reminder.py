#!/usr/bin/env python3
"""
测试系统提醒功能 - 使用相对导入
"""


import os


def test_reminder():
    """测试提醒功能"""
    print("🔔 测试系统提醒功能... - test_reminder.py:12")
    
    # 方法1：直接运行提醒模块
    try:
        # 直接执行提醒模块的测试函数
        reminder_path = os.path.join(os.path.dirname(__file__), 'src', 'scheduler', 'reminder.py')
        if os.path.exists(reminder_path):
            print("✅ 找到提醒模块文件 - test_reminder.py:19")
            
            # 读取文件内容并执行测试函数
            with open(reminder_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查文件内容
            if 'test_notification' in content:
                print("✅ 找到测试函数 - test_reminder.py:27")
            else:
                print("❌ 未找到测试函数 - test_reminder.py:29")
                
            # 直接导入
            import importlib.util
            spec = importlib.util.spec_from_file_location("reminder", reminder_path)
            reminder_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(reminder_module)
            
            # 运行测试
            if hasattr(reminder_module, 'test_notification'):
                success = reminder_module.test_notification()
                print(f"通知测试: {'✅ 成功' if success else '❌ 失败'} - test_reminder.py:40")
            else:
                print("❌ 模块中没有 test_notification 函数 - test_reminder.py:42")
                
        else:
            print(f"❌ 文件不存在: {reminder_path} - test_reminder.py:45")
            
    except Exception as e:
        print(f"❌ 测试失败: {e} - test_reminder.py:48")
        import traceback
        traceback.print_exc()
        
        
if __name__ == "__main__":
    test_reminder()