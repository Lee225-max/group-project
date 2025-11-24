#!/usr/bin/env python3
"""
主应用程序 - GUI 版本
"""

import customtkinter as ctk
import logging

# 使用相对导入
from database.manager import DatabaseManager
from auth.ui import LoginFrame


try:
    from .knowledge.ui import KnowledgeManagementFrame
    KNOWLEDGE_MODULE_AVAILABLE = True
except ImportError as e:
    KNOWLEDGE_MODULE_AVAILABLE = False
    print(f"⚠️ 知识管理模块导入失败，将使用占位符: {e} - app.py:19")

try:
    from .scheduler.ui import ReviewSchedulerFrame
    SCHEDULER_MODULE_AVAILABLE = True
except ImportError as e:
    SCHEDULER_MODULE_AVAILABLE = False
    print(f"⚠️ 复习调度模块导入失败，将使用占位符: {e} - app.py:26")

try:
    from .scheduler.reminder import get_reminder_service
    REMINDER_MODULE_AVAILABLE = True
except ImportError as e:
    REMINDER_MODULE_AVAILABLE = False
    print(f"⚠️ 提醒模块导入失败: {e} - app.py:33")


class ReviewAlarmApp:
    """复习闹钟主应用 - GUI 版本"""

    def __init__(self):
        # 设置日志
        self.logger = logging.getLogger(__name__)
        
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
        
        # 提醒服务
        self.reminder_service = None
        if REMINDER_MODULE_AVAILABLE:
            self.reminder_service = get_reminder_service(self.db_manager)

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
        self.clear_main_container()

        self.login_frame = LoginFrame(
            self.main_container,
            db_manager=self.db_manager,
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
        
        # 启动提醒服务
        self.start_reminder_system()

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
        
        # 提醒服务状态 - 修改为动态显示间隔
        if self.reminder_service and REMINDER_MODULE_AVAILABLE:
            reminder_status = self.reminder_service.get_service_status()
            
            # 动态显示提醒间隔
            if reminder_status["is_running"]:
                interval_seconds = reminder_status["interval_seconds"]
                # 格式化间隔时间
                if interval_seconds < 60:
                    status_text = f"🔔 提醒: {interval_seconds}秒"
                else:
                    minutes = interval_seconds // 60
                    status_text = f"🔔 提醒: {minutes}分钟"
            else:
                status_text = "🔕 提醒: 已停止"
                
            status_color = "green" if reminder_status["is_running"] else "gray"
            
            # 保存状态标签引用，以便后续更新
            self.status_label = ctk.CTkLabel(
                user_info_frame,
                text=status_text,
                font=ctk.CTkFont(size=12),
                text_color=status_color
            )
            self.status_label.pack(pady=2)

        # 导航按钮
        nav_buttons = [
            ("📚 知识管理", self.show_knowledge_management),
            ("⏰ 今日复习", self.show_today_review),
            ("📊 学习统计", self.show_analytics),
            ("🔔 提醒设置", self.show_reminder_settings),
            # ("⚙️ 设置", self.show_settings),
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

        if KNOWLEDGE_MODULE_AVAILABLE:
            try:
                knowledge_frame = KnowledgeManagementFrame(
                    self.content_frame,
                    self.current_user,
                    self.db_manager
                )
                knowledge_frame.pack(fill="both", expand=True)
                return
            except Exception as e:
                print(f"❌ 知识管理界面初始化失败: {e} - app.py:187")

        # 备用：显示占位符
        placeholder = ctk.CTkLabel(
            self.content_frame,
            text="知识管理界面\n(模块加载失败)",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        placeholder.pack(expand=True)

    def show_today_review(self):
        """显示今日复习界面"""
        print("🔄 切换到今日复习界面 - app.py:199")
        self.clear_content_frame()

        if SCHEDULER_MODULE_AVAILABLE:
            try:
                print("🎯 正在创建今日复习界面... - app.py:204")
                review_frame = ReviewSchedulerFrame(
                    self.content_frame,
                    self.current_user,
                    self.db_manager
                )
                review_frame.pack(fill="both", expand=True)
                print("✅ 今日复习界面创建成功 - app.py:211")
                return
            except Exception as e:
                print(f"❌ 复习调度界面初始化失败: {e} - app.py:214")
                import traceback
                traceback.print_exc()

        # 备用：显示占位符
        placeholder = ctk.CTkLabel(
            self.content_frame,
            text="今日复习界面\n(开发中...)",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        placeholder.pack(expand=True)
        print("⚠️ 使用今日复习界面占位符 - app.py:225")

    def show_analytics(self):
        """显示统计分析界面"""
        self.clear_content_frame()

        from analytics.ui import AnalyticsFrame
        analytics_frame = AnalyticsFrame(
            self.content_frame,
            self.current_user,
            self.db_manager
        )
        analytics_frame.pack(fill="both", expand=True)
    
    # 更改调用
    def show_reminder_settings(self):
        """显示提醒设置界面"""
        self.clear_content_frame()
        
        if not REMINDER_MODULE_AVAILABLE or not self.reminder_service:
            placeholder = ctk.CTkLabel(
                self.content_frame,
                text="提醒设置\n(提醒模块不可用)",
                font=ctk.CTkFont(size=20, weight="bold"),
            )
            placeholder.pack(expand=True)
            return
        
        # 创建提醒设置界面
        settings_frame = ctk.CTkFrame(self.content_frame)
        settings_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 标题
        title_label = ctk.CTkLabel(
            settings_frame,
            text="🔔 系统提醒设置",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=20)
        
        # 服务状态
        status = self.reminder_service.get_service_status()
        status_frame = ctk.CTkFrame(settings_frame)
        status_frame.pack(fill="x", padx=50, pady=10)
        
        status_text = f"服务状态: {'🟢 运行中' if status['is_running'] else '🔴 已停止'}"
        status_label = ctk.CTkLabel(
            status_frame,
            text=status_text,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        status_label.pack(pady=10)
        
        # 系统信息
        info_text = (
            f"检测系统: {status['system']}\n"
            # f"检查间隔: {status['interval_seconds']}秒\n"
            f"当前用户: {self.current_user.username if self.current_user else '未登录'}\n"
            f"通知支持: {'✅ 可用' if status['plyer_available'] else '⚠️ 受限'}"
        )
        
        info_label = ctk.CTkLabel(
            status_frame,
            text=info_text,
            font=ctk.CTkFont(size=14),
            justify="left"
        )
        info_label.pack(pady=10)
        '''
        # 控制按钮
        button_frame = ctk.CTkFrame(settings_frame)
        button_frame.pack(fill="x", padx=50, pady=20)
        
        # 立即检查按钮
        check_btn = ctk.CTkButton(
            button_frame,
            text="立即检查提醒",
            command=self.check_reminders_now,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        check_btn.pack(pady=10)
        
        # 测试通知按钮
        test_btn = ctk.CTkButton(
            button_frame,
            text="发送测试通知",
            command=self.send_test_notification,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        test_btn.pack(pady=10)
        
        # 重启服务按钮
        restart_btn = ctk.CTkButton(
            button_frame,
            text="重启提醒服务",
            command=self.restart_reminder_service,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        restart_btn.pack(pady=10)
        
        # 详细测试按钮
        detailed_test_btn = ctk.CTkButton(
            button_frame,
            text="详细功能测试",
            command=self.run_detailed_tests,
            height=40,
            font=ctk.CTkFont(size=14),
            fg_color="orange",
            hover_color="darkorange"
        )
        detailed_test_btn.pack(pady=10)
        '''
        # 间隔设置
        interval_frame = ctk.CTkFrame(settings_frame)
        interval_frame.pack(fill="x", padx=50, pady=10)
        
        ctk.CTkLabel(
            interval_frame,
            text="提醒检查间隔（秒）:",
            font=ctk.CTkFont(size=14)
        ).pack(pady=5)
        
        interval_buttons_frame = ctk.CTkFrame(interval_frame, fg_color="transparent")
        interval_buttons_frame.pack(pady=5)
        
        intervals = [
            ("30秒（测试）", 30),
            ("1分钟", 60),
            ("5分钟", 300),
            ("10分钟", 600)
        ]
        
        for text, seconds in intervals:
            btn = ctk.CTkButton(
                interval_buttons_frame,
                text=text,
                command=lambda s=seconds: self.set_reminder_interval(s),
                height=35,
                font=ctk.CTkFont(size=12),
                width=100
            )
            btn.pack(side="left", padx=5)

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
        self.logger.info(f"用户 {user.username} 登录成功")
        self.show_main_interface()

    def start_reminder_system(self):
        """启动系统提醒系统"""
        if not REMINDER_MODULE_AVAILABLE or not self.reminder_service:
            self.logger.warning("提醒模块不可用，跳过启动")
            return
        
        try:
            if self.current_user:
                result = self.reminder_service.start_reminder(self.current_user.id)
                if result["success"]:
                    self.logger.info("✅ 系统提醒服务已启动")
                    # 更新导航栏状态显示
                    self.update_reminder_status_display()
                else:
                    self.logger.warning(f"启动提醒服务失败: {result['msg']}")
        except Exception as e:
            self.logger.error(f"启动提醒系统失败: {e}")

    def update_reminder_status_display(self):
        """更新导航栏中的提醒状态显示"""
        if hasattr(self, 'status_label') and self.reminder_service and REMINDER_MODULE_AVAILABLE:
            reminder_status = self.reminder_service.get_service_status()
            
            # 动态显示提醒间隔
            if reminder_status["is_running"]:
                interval_seconds = reminder_status["interval_seconds"]
                # 格式化间隔时间
                if interval_seconds < 60:
                    status_text = f"🔔 提醒: {interval_seconds}秒"
                else:
                    minutes = interval_seconds // 60
                    status_text = f"🔔 提醒: {minutes}分钟"
            else:
                status_text = "🔕 提醒: 已停止"
                
            status_color = "green" if reminder_status["is_running"] else "gray"
            
            # 更新标签文本和颜色
            self.status_label.configure(text=status_text, text_color=status_color)

    def check_reminders_now(self):
        """立即检查并发送提醒"""
        if not REMINDER_MODULE_AVAILABLE or not self.reminder_service:
            self.show_error_dialog("错误", "提醒服务不可用")
            return
        
        try:
            # 手动触发提醒检查
            self.reminder_service._check_and_send_reminders()
            self.show_info_dialog("成功", "已立即检查并发送提醒")
        except Exception as e:
            self.show_error_dialog("错误", f"检查提醒失败: {e}")

    def send_test_notification(self):
        """发送测试通知"""
        if not REMINDER_MODULE_AVAILABLE or not self.reminder_service:
            self.show_error_dialog("错误", "提醒服务不可用")
            return
        
        result = self.reminder_service.send_test_notification()
        if result["success"]:
            self.show_info_dialog("成功", "测试通知已发送")
        else:
            self.show_error_dialog("失败", result["msg"])

    def restart_reminder_service(self):
        """重启提醒服务"""
        if not REMINDER_MODULE_AVAILABLE or not self.reminder_service:
            self.show_error_dialog("错误", "提醒服务不可用")
            return
        
        # 先停止服务
        self.reminder_service.stop_reminder()
        
        # 再启动服务
        if self.current_user:
            result = self.reminder_service.start_reminder(self.current_user.id)
            if result["success"]:
                self.show_info_dialog("成功", "提醒服务已重启")
                # 更新导航栏状态显示
                self.update_reminder_status_display()
                # 刷新界面
                self.show_reminder_settings()
            else:
                self.show_error_dialog("失败", result["msg"])

    def set_reminder_interval(self, interval_seconds: int):
        """设置提醒检查间隔"""
        if not REMINDER_MODULE_AVAILABLE or not self.reminder_service:
            self.show_error_dialog("错误", "提醒服务不可用")
            return
        
        result = self.reminder_service.set_reminder_interval(interval_seconds)
        if result["success"]:
            self.show_info_dialog("成功", f"提醒间隔已设置为 {interval_seconds} 秒")
            # 更新导航栏状态显示
            self.update_reminder_status_display()
        else:
            self.show_error_dialog("失败", result["msg"])

    def run_detailed_tests(self):
        """运行详细功能测试"""
        if not REMINDER_MODULE_AVAILABLE or not self.reminder_service:
            self.show_error_dialog("错误", "提醒服务不可用")
            return
        
        # 创建测试对话框
        test_dialog = ctk.CTkToplevel(self.root)
        test_dialog.title("🔍 详细功能测试")
        test_dialog.geometry("600x500")
        test_dialog.transient(self.root)
        test_dialog.grab_set()
        
        # 居中显示
        test_dialog.update_idletasks()
        x = (self.root.winfo_x() + (self.root.winfo_width() - test_dialog.winfo_width()) // 2)
        y = (self.root.winfo_y() + (self.root.winfo_height() - test_dialog.winfo_height()) // 2)
        test_dialog.geometry(f"+{x}+{y}")
        
        # 测试内容区域
        content_frame = ctk.CTkFrame(test_dialog)
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 标题
        title_label = ctk.CTkLabel(
            content_frame,
            text="详细功能测试",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=10)
        
        # 测试结果文本框
        test_result_text = ctk.CTkTextbox(
            content_frame,
            height=300,
            font=ctk.CTkFont(size=12)
        )
        test_result_text.pack(fill="both", expand=True, pady=10)
        test_result_text.insert("1.0", "测试结果将显示在这里...\n\n")
        
        def append_test_result(message):
            """添加测试结果到文本框"""
            test_result_text.insert("end", f"{message}\n")
            test_result_text.see("end")
            test_dialog.update()
        
        # 测试按钮框架
        test_buttons_frame = ctk.CTkFrame(content_frame)
        test_buttons_frame.pack(fill="x", pady=10)
        
        def test_system_notifier():
            """测试系统通知器"""
            append_test_result("\n🔔 测试系统通知器...")
            try:
                from src.scheduler.reminder import SystemNotifier
                notifier = SystemNotifier()
                append_test_result(f"  系统: {notifier.system_name}")
                
                # 测试简单通知
                success = notifier.notify("测试通知", "这是一条测试通知", timeout=5)
                append_test_result(f"  简单通知: {'✅ 成功' if success else '❌ 失败'}")
                
                # 测试复习提醒格式
                review_notification = notifier.notify(
                    "📚 复习提醒", 
                    "【立即复习】Python基础语法\n内容: 变量、数据类型...\n计划时间: 10:00",
                    timeout=5
                )
                append_test_result(f"  复习提醒: {'✅ 成功' if review_notification else '❌ 失败'}")
                
            except Exception as e:
                append_test_result(f"  ❌ 系统通知器测试失败: {e}")
        
        def test_reminder_service():
            """测试提醒服务"""
            append_test_result("\n🔄 测试提醒服务...")
            try:
                status = self.reminder_service.get_service_status()
                append_test_result(f"  服务状态: {status}")
                
                # 测试待复习计划获取
                pending_reviews = self.reminder_service._get_pending_reviews(self.current_user.id)
                append_test_result(f"  待复习计划数: {len(pending_reviews)}")
                
                for review in pending_reviews[:3]:  # 只显示前3个
                    append_test_result(f"    - {review['title']} ({review['stage_label']})")
                    
            except Exception as e:
                append_test_result(f"  ❌ 提醒服务测试失败: {e}")
        
        def test_all_functionality():
            """测试所有功能"""
            append_test_result("🚀 开始全面测试...")
            test_system_notifier()
            test_reminder_service()
            append_test_result("\n🎉 全面测试完成！")
        
        # 测试按钮
        ctk.CTkButton(
            test_buttons_frame,
            text="测试系统通知器",
            command=test_system_notifier,
            height=35
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            test_buttons_frame,
            text="测试提醒服务",
            command=test_reminder_service,
            height=35
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            test_buttons_frame,
            text="全面测试",
            command=test_all_functionality,
            height=35,
            fg_color="green",
            hover_color="darkgreen"
        ).pack(side="left", padx=5)
        
        # 关闭按钮
        ctk.CTkButton(
            content_frame,
            text="关闭",
            command=test_dialog.destroy,
            height=40,
            font=ctk.CTkFont(size=14)
        ).pack(pady=10)

    def show_info_dialog(self, title, message):
        """显示信息对话框"""
        import tkinter.messagebox as messagebox
        messagebox.showinfo(title, message)
        
    def show_error_dialog(self, title, message):
        """显示错误对话框"""
        import tkinter.messagebox as messagebox
        messagebox.showerror(title, message)
        
    def logout(self):
        """退出登录"""
        # 停止提醒服务
        if self.reminder_service and REMINDER_MODULE_AVAILABLE:
            self.reminder_service.stop_reminder()
            self.logger.info("提醒服务已停止")
            # 更新导航栏状态显示
            self.update_reminder_status_display()
        
        self.current_user = None
        self.show_login()

    def run(self):
        """运行应用"""
        self.root.mainloop()


if __name__ == "__main__":
    app = ReviewAlarmApp()
    app.run()