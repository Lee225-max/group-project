"""
主应用程序 - GUI 版本
"""

import customtkinter as ctk

# 使用相对导入
from database.manager import DatabaseManager


class ReviewAlarmApp:
    """复习闹钟主应用 - GUI 版本"""

    def __init__(self):
        # 设置主题
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        # 创建主窗口
        self.root = ctk.CTk()
        self.setup_app()

        # 初始化数据库
        self.db_manager = DatabaseManager()

        # 当前用户
        self.current_user = None

        self.setup_ui()

    def setup_app(self):
        """应用设置"""
        self.root.title("智能复习闹钟")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)

    def setup_ui(self):
        """设置用户界面"""
        # 主容器
        self.main_container = ctk.CTkFrame(self.root)
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)

        # 显示登录界面
        self.show_login()

    def show_login(self):
        """显示登录界面"""
        # 使用相对导入
        from auth.ui import LoginFrame

        self.clear_main_container()

        self.login_frame = LoginFrame(
            self.main_container,
            db_manager=self.db_manager,  # 直接传递 db_manager
            login_callback=self.on_login_success,
        )
        self.login_frame.pack(fill="both", expand=True)

    def show_main_interface(self):
        """显示主界面"""
        self.clear_main_container()

        # 创建导航栏和内容区域
        self.create_navigation_frame()
        self.create_content_frame()

        # 默认显示知识管理
        self.show_knowledge_management()

    def create_navigation_frame(self):
        """创建导航栏"""
        self.nav_frame = ctk.CTkFrame(self.main_container, width=200)
        self.nav_frame.pack(side="left", fill="y", padx=(0, 5))
        self.nav_frame.pack_propagate(False)

        # 用户信息
        user_info_frame = ctk.CTkFrame(self.nav_frame)
        user_info_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            user_info_frame,
            text=f"用户: {self.current_user.username}",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(pady=5)

        # 导航按钮
        nav_buttons = [
            ("📚 知识管理", self.show_knowledge_management),
            ("⏰ 今日复习", self.show_today_review),
            ("📊 学习统计", self.show_analytics),
            ("⚙️ 设置", self.show_settings),
            ("🚪 退出", self.logout),
        ]

        for text, command in nav_buttons:
            btn = ctk.CTkButton(
                self.nav_frame,
                text=text,
                command=command,
                height=40,
                anchor="w",
                font=ctk.CTkFont(size=14),
            )
            btn.pack(fill="x", padx=10, pady=5)

    def create_content_frame(self):
        """创建内容区域"""
        self.content_frame = ctk.CTkFrame(self.main_container)
        self.content_frame.pack(side="right", fill="both", expand=True)

    def show_knowledge_management(self):
        """显示知识管理界面"""
        self.clear_content_frame()

        placeholder = ctk.CTkLabel(
            self.content_frame,
            text="知识管理界面\n(成员B开发)",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        placeholder.pack(expand=True)

    # 新更新的地方
    def show_today_review(self):
        """显示今日复习界面"""
        self.clear_content_frame()

        # 集成成员C的模块
        from scheduler.ui import ReviewSchedulerFrame

        review_frame = ReviewSchedulerFrame(
            self.content_frame, self.current_user, self.db_manager
        )
        review_frame.pack(fill="both", expand=True)

    #

    def show_analytics(self):
        """显示统计分析界面"""
        self.clear_content_frame()

        placeholder = ctk.CTkLabel(
            self.content_frame,
            text="学习统计界面\n(成员D开发)",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        placeholder.pack(expand=True)

    def show_settings(self):
        """显示设置界面"""
        self.clear_content_frame()

        placeholder = ctk.CTkLabel(
            self.content_frame,
            text="设置界面",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        placeholder.pack(expand=True)

    def clear_main_container(self):
        """清空主容器"""
        for widget in self.main_container.winfo_children():
            widget.destroy()

    def clear_content_frame(self):
        """清空内容区域"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def on_login_success(self, user):
        """登录成功回调"""
        self.current_user = user
        self.show_main_interface()

    def logout(self):
        """退出登录"""
        self.current_user = None
        self.show_login()

    def run(self):
        """运行应用"""
        self.root.mainloop()
