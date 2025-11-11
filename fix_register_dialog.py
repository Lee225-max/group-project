#!/usr/bin/env python3
"""
修复注册对话框按钮显示问题的脚本
"""

import os


def fix_register_dialog():
    """修复注册对话框"""
    filepath = "src/auth/ui.py"
    
    # 读取原始文件
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 找到 RegisterDialog 类并替换整个类
    old_register_dialog = '''class RegisterDialog(ctk.CTkToplevel):
    """注册对话框"""
    
    def __init__(self, parent, auth_service):
        super().__init__(parent)
        self.auth_service = auth_service
        
        self.title("用户注册")
        self.geometry("400x450")
        self.resizable(False, False)
        
        # 设置模态
        self.transient(parent)
        self.grab_set()
        
        self.create_widgets()
    
    def create_widgets(self):
        """创建对话框组件"""
        # 标题
        title_label = ctk.CTkLabel(
            self, 
            text="用户注册",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=20)
        
        # 表单容器
        form_frame = ctk.CTkFrame(self, fg_color="transparent")
        form_frame.pack(fill="both", expand=True, padx=30, pady=10)
        
        # 用户名
        ctk.CTkLabel(form_frame, text="用户名:", font=ctk.CTkFont(size=14)).pack(anchor="w", pady=(10, 5))
        self.username_entry = ctk.CTkEntry(form_frame, height=35, font=ctk.CTkFont(size=14))
        self.username_entry.pack(fill="x", pady=5)
        
        # 邮箱
        ctk.CTkLabel(form_frame, text="邮箱:", font=ctk.CTkFont(size=14)).pack(anchor="w", pady=(10, 5))
        self.email_entry = ctk.CTkEntry(form_frame, height=35, font=ctk.CTkFont(size=14))
        self.email_entry.pack(fill="x", pady=5)
        
        # 密码
        ctk.CTkLabel(form_frame, text="密码:", font=ctk.CTkFont(size=14)).pack(anchor="w", pady=(10, 5))
        self.password_entry = ctk.CTkEntry(form_frame, show="•", height=35, font=ctk.CTkFont(size=14))
        self.password_entry.pack(fill="x", pady=5)
        
        # 确认密码
        ctk.CTkLabel(form_frame, text="确认密码:", font=ctk.CTkFont(size=14)).pack(anchor="w", pady=(10, 5))
        self.confirm_password_entry = ctk.CTkEntry(form_frame, show="•", height=35, font=ctk.CTkFont(size=14))
        self.confirm_password_entry.pack(fill="x", pady=5)
        
        # 按钮框架
        button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=30)
        
        ctk.CTkButton(
            button_frame, 
            text="注册",
            command=self.register,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left", padx=(0, 10), expand=True)
        
        ctk.CTkButton(
            button_frame, 
            text="取消",
            command=self.destroy,
            height=40,
            fg_color="gray",
            font=ctk.CTkFont(size=14)
        ).pack(side="right", padx=(10, 0), expand=True)
    
    def register(self):
        """处理注册"""
        username = self.username_entry.get().strip()
        email = self.email_entry.get().strip()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()
        
        # 验证输入
        if not all([username, email, password, confirm_password]):
            messagebox.showerror("错误", "请填写所有字段")
            return
        
        if password != confirm_password:
            messagebox.showerror("错误", "密码不一致")
            return
        
        if len(password) < 6:
            messagebox.showerror("错误", "密码长度至少6位")
            return
        
        try:
            user = self.auth_service.register_user(username, email, password)
            messagebox.showinfo("成功", "注册成功！请登录")
            self.destroy()
        except Exception as e:
            messagebox.showerror("错误", str(e))'''
    
    new_register_dialog = '''class RegisterDialog(ctk.CTkToplevel):
    """注册对话框"""
    
    def __init__(self, parent, auth_service):
        super().__init__(parent)
        self.auth_service = auth_service
        
        self.title("用户注册")
        self.geometry("400x500")  # 增加高度以容纳按钮
        self.resizable(False, False)
        
        # 设置模态
        self.transient(parent)
        self.grab_set()
        
        self.create_widgets()
        self.center_window()
    
    def center_window(self):
        """居中显示窗口"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'+{x}+{y}')
    
    def create_widgets(self):
        """创建对话框组件"""
        # 主容器 - 使用网格布局确保正确显示
        main_container = ctk.CTkFrame(self)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 标题
        title_label = ctk.CTkLabel(
            main_container, 
            text="用户注册",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=(0, 20))
        
        # 表单容器 - 使用网格布局
        form_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        form_frame.pack(fill="both", expand=True)
        
        # 用户名
        ctk.CTkLabel(form_frame, text="用户名:", font=ctk.CTkFont(size=14)).pack(anchor="w", pady=(10, 5))
        self.username_entry = ctk.CTkEntry(form_frame, height=35, font=ctk.CTkFont(size=14))
        self.username_entry.pack(fill="x", pady=5)
        
        # 邮箱
        ctk.CTkLabel(form_frame, text="邮箱:", font=ctk.CTkFont(size=14)).pack(anchor="w", pady=(10, 5))
        self.email_entry = ctk.CTkEntry(form_frame, height=35, font=ctk.CTkFont(size=14))
        self.email_entry.pack(fill="x", pady=5)
        
        # 密码
        ctk.CTkLabel(form_frame, text="密码:", font=ctk.CTkFont(size=14)).pack(anchor="w", pady=(10, 5))
        self.password_entry = ctk.CTkEntry(form_frame, show="•", height=35, font=ctk.CTkFont(size=14))
        self.password_entry.pack(fill="x", pady=5)
        
        # 确认密码
        ctk.CTkLabel(form_frame, text="确认密码:", font=ctk.CTkFont(size=14)).pack(anchor="w", pady=(10, 5))
        self.confirm_password_entry = ctk.CTkEntry(form_frame, show="•", height=35, font=ctk.CTkFont(size=14))
        self.confirm_password_entry.pack(fill="x", pady=5)
        
        # 按钮框架 - 修复布局
        button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(20, 0))
        
        # 注册按钮
        register_btn = ctk.CTkButton(
            button_frame, 
            text="注册",
            command=self.register,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        register_btn.pack(side="left", padx=(0, 10), expand=True, fill="x")
        
        # 取消按钮
        cancel_btn = ctk.CTkButton(
            button_frame, 
            text="取消",
            command=self.destroy,
            height=40,
            fg_color="gray",
            hover_color="#555555",
            font=ctk.CTkFont(size=14)
        )
        cancel_btn.pack(side="right", padx=(10, 0), expand=True, fill="x")
        
        # 绑定回车键到注册
        self.confirm_password_entry.bind('<Return>', lambda e: self.register())
        
        # 初始焦点
        self.username_entry.focus()
    
    def register(self):
        """处理注册"""
        username = self.username_entry.get().strip()
        email = self.email_entry.get().strip()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()
        
        # 验证输入
        if not all([username, email, password, confirm_password]):
            from tkinter import messagebox
            messagebox.showerror("错误", "请填写所有字段")
            return
        
        if password != confirm_password:
            from tkinter import messagebox
            messagebox.showerror("错误", "密码不一致")
            return
        
        if len(password) < 6:
            from tkinter import messagebox
            messagebox.showerror("错误", "密码长度至少6位")
            return
        
        try:
            user = self.auth_service.register_user(username, email, password)
            from tkinter import messagebox
            messagebox.showinfo("成功", "注册成功！请登录")
            self.destroy()
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("错误", str(e))'''
    
    # 替换内容
    content = content.replace(old_register_dialog, new_register_dialog)
    
    # 写回文件
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 修复了注册对话框的按钮显示问题 - fix_register_dialog.py:253")


def main():
    """主函数"""
    print("🔧 修复注册对话框按钮显示问题... - fix_register_dialog.py:258")
    fix_register_dialog()
    print("🎉 修复完成！ - fix_register_dialog.py:260")
    print("现在注册对话框应该能正常显示提交和取消按钮了 - fix_register_dialog.py:261")


if __name__ == "__main__":
    main()