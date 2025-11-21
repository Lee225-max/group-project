"""系统提醒服务：支持App弹窗+邮件提醒"""
from src.database.manager import DatabaseManager
import smtplib
from email.mime.text import MIMEText
from plyer import notification
from datetime import datetime
import threading
import time


class ReminderService:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.reminder_interval = 60  # 每60秒检查一次提醒
        self.is_running = False

    def start_reminder(self):
        """启动提醒服务（后台线程）"""
        if self.is_running:
            return {"success": False, "msg": "提醒服务已在运行"}
        self.is_running = True
        # 启动后台线程
        reminder_thread = threading.Thread(target=self._reminder_loop, daemon=True)
        reminder_thread.start()
        return {"success": True, "msg": "提醒服务已启动"}

    def stop_reminder(self):
        """停止提醒服务"""
        self.is_running = False
        return {"success": True, "msg": "提醒服务已停止"}

    def _reminder_loop(self):
        """提醒循环：定时检查并发送提醒"""
        while self.is_running:
            self._check_and_send_reminders()
            time.sleep(self.reminder_interval)

    def _check_and_send_reminders(self):
        """检查待提醒计划并发送"""
        pending_reminders = self.db_manager.get_pending_reminders()
        for reminder in pending_reminders:
            title = "⏰ 艾宾浩斯复习提醒"
            message = (
                f"知识点：《{reminder['knowledge_title']}》\n"
                f"计划复习时间：{reminder['scheduled_date']}\n"
                f"请及时复习以巩固记忆～"
            )
            # 根据提醒渠道发送
            if reminder["reminder_channel"] == "app":
                self._send_app_notification(title, message)
            elif reminder["reminder_channel"] == "email":
                self._send_email_notification(reminder["user_email"], title, message)

    def _send_app_notification(self, title, message):
        """发送App桌面通知"""
        try:
            notification.notify(
                title=title,
                message=message,
                app_name="知识复习系统",
                timeout=15  # 通知显示15秒
            )
            print(f"App提醒发送成功：{title} - reminder.py:63")
        except Exception as e:
            print(f"App提醒发送失败：{str(e)} - reminder.py:65")

    def _send_email_notification(self, to_email, title, message):
        """发送邮件通知（需配置SMTP）"""
        # 配置你的SMTP信息（示例为QQ邮箱）
        SMTP_CONFIG = {
            "server": "smtp.qq.com",
            "port": 587,
            "from_email": "你的QQ邮箱@qq.com",
            "password": "你的邮箱授权码"  # 不是登录密码，是SMTP授权码
        }
        try:
            # 构建邮件
            msg = MIMEText(message, "plain", "utf-8")
            msg["Subject"] = title
            msg["From"] = SMTP_CONFIG["from_email"]
            msg["To"] = to_email

            # 发送邮件
            with smtplib.SMTP(SMTP_CONFIG["server"], SMTP_CONFIG["port"]) as server:
                server.starttls()
                server.login(SMTP_CONFIG["from_email"], SMTP_CONFIG["password"])
                server.send_message(msg)
            print(f"邮件提醒发送成功：{to_email} - reminder.py:88")
        except Exception as e:
            print(f"邮件提醒发送失败：{to_email}  {str(e)} - reminder.py:90")