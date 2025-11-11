#!/usr/bin/env python3
"""
修复 db_manager 传递问题的脚本
"""

import os


def fix_app_py():
    """修复 app.py"""
    filepath = "src/app.py"
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 替换 show_login 方法中的 LoginFrame 调用
    old_code = '''        self.login_frame = LoginFrame(
            self.main_container,
            login_callback=self.on_login_success
        )'''
    
    new_code = '''        self.login_frame = LoginFrame(
            self.main_container,
            db_manager=self.db_manager,  # 直接传递 db_manager
            login_callback=self.on_login_success
        )'''
    
    content = content.replace(old_code, new_code)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 修复了 {filepath} - fix_db_manager.py:33")


def fix_auth_ui_py():
    """修复 auth/ui.py"""
    filepath = "src/auth/ui.py"
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 替换 LoginFrame 的 __init__ 方法
    old_init = '''    def __init__(self, parent, login_callback):
        super().__init__(parent)
        self.login_callback = login_callback
        self.auth_service = AuthService(parent.master.db_manager)'''
    
    new_init = '''    def __init__(self, parent, db_manager, login_callback):  # 添加 db_manager 参数
        super().__init__(parent)
        self.login_callback = login_callback
        self.auth_service = AuthService(db_manager)  # 直接使用传入的 db_manager'''
    
    content = content.replace(old_init, new_init)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 修复了 {filepath} - fix_db_manager.py:59")


def main():
    """主函数"""
    print("🔧 修复 db_manager 传递问题... - fix_db_manager.py:64")
    
    fix_app_py()
    fix_auth_ui_py()
    
    print("🎉 修复完成！ - fix_db_manager.py:69")
    print("现在可以运行: python run_app.py - fix_db_manager.py:70")


if __name__ == "__main__":
    main()