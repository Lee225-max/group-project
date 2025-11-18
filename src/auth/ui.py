"""
认证界面 - GUI 版本
"""

import customtkinter as ctk
from tkinter import messagebox
from src.auth.service import AuthService


class LoginFrame(ctk.CTkFrame):
    """登录界面 - GUI 版本"""

    def __init__(self, parent, db_manager, login_callback):  # 添加 db_manager 参数
        super().__init__(parent)
        self.login_callback = login_callback
        self.auth_service = AuthService(db_manager)  # 直接使用传入的 db_manager

        self.create_widgets()

    def create_widgets(self):
        """创建界面组件"""
        # 主容器
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(expand=True, fill="both", padx=50, pady=50)

        # 标题
        title_label = ctk.CTkLabel(
            main_container,
            text="智能复习闹钟",
            font=ctk.CTkFont(size=28, weight="bold"),
        )
        title_label.pack(pady=(0, 40))

        # 登录卡片
        login_card = ctk.CTkFrame(main_container)
        login_card.pack(expand=True, fill="both", padx=100)

        # 登录表单
        self.create_login_form(login_card)

    def create_login_form(self, parent):
        """创建登录表单"""
        # 表单标题
        form_title = ctk.CTkLabel(
            parent, text="用户登录", font=ctk.CTkFont(size=20, weight="bold")
        )
        form_title.pack(pady=30)

        # 用户名输入
        username_frame = ctk.CTkFrame(parent, fg_color="transparent")
        username_frame.pack(fill="x", padx=50, pady=10)

        ctk.CTkLabel(username_frame, text="用户名:", font=ctk.CTkFont(size=14)).pack(
            anchor="w"
        )
        self.username_entry = ctk.CTkEntry(
            username_frame,
            placeholder_text="请输入用户名",
            height=40,
            font=ctk.CTkFont(size=14),
        )
        self.username_entry.pack(fill="x", pady=(5, 0))

        # 密码输入
        password_frame = ctk.CTkFrame(parent, fg_color="transparent")
        password_frame.pack(fill="x", padx=50, pady=10)

        ctk.CTkLabel(password_frame, text="密码:", font=ctk.CTkFont(size=14)).pack(
            anchor="w"
        )
        self.password_entry = ctk.CTkEntry(
            password_frame,
            placeholder_text="请输入密码",
            show="•",
            height=40,
            font=ctk.CTkFont(size=14),
        )
        self.password_entry.pack(fill="x", pady=(5, 0))

        # 登录按钮
        login_btn = ctk.CTkButton(
            parent,
            text="登录",
            command=self.login,
            height=45,
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        login_btn.pack(fill="x", padx=50, pady=30)

        # 注册链接
        register_frame = ctk.CTkFrame(parent, fg_color="transparent")
        register_frame.pack(fill="x", padx=50, pady=10)

        register_btn = ctk.CTkButton(
            register_frame,
            text="没有账号？点击注册",
            command=self.show_register,
            fg_color="transparent",
            hover_color="#2b2b2b",
            font=ctk.CTkFont(size=12),
        )
        register_btn.pack()

        # 绑定回车键
        self.password_entry.bind("<Return>", lambda e: self.login())

        # 初始焦点
        self.username_entry.focus()

    def login(self):
        """处理登录"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("错误", "请输入用户名和密码")
            return

        try:
            user = self.auth_service.authenticate_user(username, password)
            if user:
                self.login_callback(user)
            else:
                messagebox.showerror("错误", "用户名或密码错误")
        except Exception as e:
            messagebox.showerror("错误", f"登录失败: {str(e)}")

    def show_register(self):
        """显示注册对话框"""
        RegisterDialog(self, self.auth_service)


class RegisterDialog(ctk.CTkToplevel):
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
        self.geometry(f"+{x}+{y}")

    def create_widgets(self):
        """创建对话框组件"""
        # 主容器 - 使用网格布局确保正确显示
        main_container = ctk.CTkFrame(self)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # 标题
        title_label = ctk.CTkLabel(
            main_container, text="用户注册", font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=(0, 20))

        # 表单容器 - 使用网格布局
        form_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        form_frame.pack(fill="both", expand=True)

        # 用户名
        ctk.CTkLabel(form_frame, text="用户名:", font=ctk.CTkFont(size=14)).pack(
            anchor="w", pady=(10, 5)
        )
        self.username_entry = ctk.CTkEntry(
            form_frame, height=35, font=ctk.CTkFont(size=14)
        )
        self.username_entry.pack(fill="x", pady=5)

        # 邮箱
        ctk.CTkLabel(form_frame, text="邮箱:", font=ctk.CTkFont(size=14)).pack(
            anchor="w", pady=(10, 5)
        )
        self.email_entry = ctk.CTkEntry(
            form_frame, height=35, font=ctk.CTkFont(size=14)
        )
        self.email_entry.pack(fill="x", pady=5)

        # 密码
        ctk.CTkLabel(form_frame, text="密码:", font=ctk.CTkFont(size=14)).pack(
            anchor="w", pady=(10, 5)
        )
        self.password_entry = ctk.CTkEntry(
            form_frame, show="•", height=35, font=ctk.CTkFont(size=14)
        )
        self.password_entry.pack(fill="x", pady=5)

        # 确认密码
        ctk.CTkLabel(form_frame, text="确认密码:", font=ctk.CTkFont(size=14)).pack(
            anchor="w", pady=(10, 5)
        )
        self.confirm_password_entry = ctk.CTkEntry(
            form_frame, show="•", height=35, font=ctk.CTkFont(size=14)
        )
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
            font=ctk.CTkFont(size=14, weight="bold"),
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
            font=ctk.CTkFont(size=14),
        )
        cancel_btn.pack(side="right", padx=(10, 0), expand=True, fill="x")

        # 绑定回车键到注册
        self.confirm_password_entry.bind("<Return>", lambda e: self.register())

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
            messagebox.showerror("错误", "请填写所有字段")
            return

        if password != confirm_password:
            messagebox.showerror("错误", "密码不一致")
            return

        if len(password) < 6:
            messagebox.showerror("错误", "密码长度至少6位")
            return

        try:
            # 添加实际注册逻辑
            self.auth_service.register_user(username, email, password)
            messagebox.showinfo("成功", "注册成功！请登录")
            self.destroy()
        except Exception as e:
            messagebox.showerror("错误", str(e))