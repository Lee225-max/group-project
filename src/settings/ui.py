"""
设置界面
"""

import customtkinter as ctk
from tkinter import messagebox


class SettingsFrame(ctk.CTkFrame):
    """设置界面"""

    def __init__(self, parent, current_user, db_manager):
        super().__init__(parent)
        self.current_user = current_user
        self.db_manager = db_manager

        self.setup_ui()
        self.load_current_settings()

    def setup_ui(self):
        """设置界面组件"""
        # 主容器
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # 标题
        title_label = ctk.CTkLabel(
            main_container,
            text="⚙️ 设置",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(0, 30))

        # 设置选项卡片
        settings_card = ctk.CTkFrame(main_container)
        settings_card.pack(fill="x", pady=10)

        # 主题设置
        self.create_theme_section(settings_card)

        # 复习设置
        self.create_review_section(settings_card)

        # 用户信息
        self.create_user_section(settings_card)

        # 操作按钮
        self.create_action_buttons(main_container)

    def create_theme_section(self, parent):
        """创建主题设置部分"""
        theme_frame = ctk.CTkFrame(parent)
        theme_frame.pack(fill="x", padx=15, pady=10)

        ctk.CTkLabel(
            theme_frame,
            text="外观设置",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", pady=(10, 5))

        # 主题选择
        theme_container = ctk.CTkFrame(theme_frame, fg_color="transparent")
        theme_container.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(theme_container, text="主题模式:").pack(side="left")

        self.theme_var = ctk.StringVar(value="System")
        theme_options = ["Light", "Dark", "System"]

        for option in theme_options:
            ctk.CTkRadioButton(
                theme_container,
                text=option,
                variable=self.theme_var,
                value=option,
                command=self.on_theme_change
            ).pack(side="left", padx=(20, 0))

    def create_review_section(self, parent):
        """创建复习设置部分"""
        review_frame = ctk.CTkFrame(parent)
        review_frame.pack(fill="x", padx=15, pady=10)

        ctk.CTkLabel(
            review_frame,
            text="复习设置",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", pady=(10, 5))

        # 每日复习提醒时间
        time_container = ctk.CTkFrame(review_frame, fg_color="transparent")
        time_container.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(time_container, text="每日提醒时间:").pack(side="left")

        self.reminder_time_var = ctk.StringVar(value="09:00")
        time_options = ["08:00", "09:00", "10:00", "14:00", "16:00", "20:00"]

        time_dropdown = ctk.CTkOptionMenu(
            time_container,
            variable=self.reminder_time_var,
            values=time_options,
            width=100
        )
        time_dropdown.pack(side="left", padx=(10, 0))

    def create_user_section(self, parent):
        """创建用户信息部分"""
        user_frame = ctk.CTkFrame(parent)
        user_frame.pack(fill="x", padx=15, pady=10)

        ctk.CTkLabel(
            user_frame,
            text="用户信息",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", pady=(10, 5))

        # 用户名显示
        info_container = ctk.CTkFrame(user_frame, fg_color="transparent")
        info_container.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(
            info_container,
            text=f"用户名: {self.current_user.username}",
            font=ctk.CTkFont(size=14)
        ).pack(anchor="w")

        ctk.CTkLabel(
            info_container,
            text=f"邮箱: {self.current_user.email}",
            font=ctk.CTkFont(size=14)
        ).pack(anchor="w", pady=(5, 0))

        ctk.CTkLabel(
            info_container,
            text=f"注册时间: {self.current_user.created_at.strftime('%Y-%m-%d')}",
            font=ctk.CTkFont(size=14)
        ).pack(anchor="w", pady=(5, 0))

    def create_action_buttons(self, parent):
        """创建操作按钮"""
        button_frame = ctk.CTkFrame(parent, fg_color="transparent")
        button_frame.pack(fill="x", pady=20)

        # 保存设置按钮
        save_btn = ctk.CTkButton(
            button_frame,
            text="保存设置",
            command=self.save_settings,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        save_btn.pack(side="left", padx=(0, 10), expand=True)

        # 重置按钮
        reset_btn = ctk.CTkButton(
            button_frame,
            text="重置",
            command=self.reset_settings,
            height=40,
            fg_color="gray",
            hover_color="#555555"
        )
        reset_btn.pack(side="right", padx=(10, 0), expand=True)

    def load_current_settings(self):
        """加载当前设置"""
        # 这里可以从数据库或配置文件加载用户设置
        # 暂时使用默认值
        pass

    def on_theme_change(self):
        """主题变更处理"""
        theme = self.theme_var.get()
        ctk.set_appearance_mode(theme)
        messagebox.showinfo("提示", f"主题已切换为 {theme}")

    def save_settings(self):
        """保存设置"""
        try:
            # 保存设置到数据库或配置文件
            settings = {
                "theme": self.theme_var.get(),
                "reminder_time": self.reminder_time_var.get()
            }

            # 这里可以添加保存到数据库的逻辑
            print(f"保存设置: {settings} - ui.py:188")

            messagebox.showinfo("成功", "设置已保存")

        except Exception as e:
            messagebox.showerror("错误", f"保存设置失败: {str(e)}")

    def reset_settings(self):
        """重置设置"""
        if messagebox.askyesno("确认", "确定要重置所有设置为默认值吗？"):
            self.theme_var.set("System")
            self.reminder_time_var.set("09:00")
            messagebox.showinfo("成功", "设置已重置为默认值")
