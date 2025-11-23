"""
系统级复习提醒模块 - 完整版
支持跨平台系统通知和App弹窗提醒
"""

import platform
import subprocess
import logging
import threading
import time
from datetime import datetime
from typing import List, Optional, Dict, Any

# 尝试导入 plyer，如果不可用则使用备用方案
try:
    from plyer import notification
    PLYER_AVAILABLE = True
except ImportError:
    PLYER_AVAILABLE = False
    print("⚠️  plyer 不可用，将使用备用通知方案 - reminder.py:20")

logger = logging.getLogger(__name__)


class SystemNotifier:
    """跨平台系统通知器"""
    
    def __init__(self):
        self.system_name = platform.system()
        logger.info(f"初始化系统通知器，检测到系统: {self.system_name}")
    
    def notify(self, title: str, message: str, timeout: int = 10) -> bool:
        """
        显示系统通知
        """
        logger.info("🔔 尝试发送系统通知")
        logger.info(f"  系统: {self.system_name}")
        logger.info(f"  标题: {title}")
        logger.info(f"  内容: {message}")
        try:
            if self.system_name == "Darwin":  # macOS
                logger.info("🖥️  使用 macOS 通知方案")
                result = self._mac_notify(title, message)
                logger.info(f"  macOS 通知结果: {'✅ 成功' if result else '❌ 失败'}")
                return result
                
            elif self.system_name == "Windows":
                logger.info("🪟 使用 Windows 通知方案")
                result = self._windows_notify(title, message, timeout)
                logger.info(f"  Windows 通知结果: {'✅ 成功' if result else '❌ 失败'}")
                return result
                
            elif self.system_name == "Linux":
                logger.info("🐧 使用 Linux 通知方案")
                result = self._linux_notify(title, message, timeout)
                logger.info(f"  Linux 通知结果: {'✅ 成功' if result else '❌ 失败'}")
                return result
                
            else:
                logger.warning(f"不支持的操作系统: {self.system_name}")
                result = self._fallback_notify(title, message)
                logger.info(f"  备用方案结果: {'✅ 成功' if result else '❌ 失败'}")
                return result
               
        except Exception as e:
            logger.error(f"显示系统通知失败: {e}")
            return False
    
    def _mac_notify(self, title: str, message: str) -> bool:
        """macOS 系统通知 - 使用 terminal-notifier"""
        try:
            # 清理消息中的特殊字符
            message_clean = message.replace('"', "'").replace('\n', ' ')
        
            # 使用与测试脚本相同的 AppleScript 格式
            script = f'''
            display notification "{message_clean}" with title "📚 智能复习提醒" sound name "default"
            '''
        
            logger.info(f"  执行 AppleScript: {script.strip()}")
            result = subprocess.run([
                "terminal-notifier",
                "-title", title,
                "-message", message_clean,
                "-sound", "default",
                 "-group", "review-alarm"  # 添加分组标识
            ], capture_output=True, timeout=10)          
          
            if result.returncode == 0:
                logger.info("   macOS 通知结果: ✅ 成功")
                return True
            else:
                logger.error(f"   macOS 通知失败: {result.stderr}")
                return False
            
        except Exception as e:
            logger.error(f"  macOS 通知异常: {e}")
            return False
    
    def _windows_notify(self, title: str, message: str, timeout: int) -> bool:
        """Windows 系统通知 - 增强版"""
        try:
            logger.info("  尝试 Windows 通知...")
            
            # 方法1: 使用 ctypes 显示消息框（最可靠）
            try:
                import ctypes
                logger.info("  使用 ctypes 消息框")
                # 使用 MB_SYSTEMMODAL 让对话框置顶
                ctypes.windll.user32.MessageBoxW(0, message, title, 0x1000)  # MB_SYSTEMMODAL
                logger.info("  ctypes 消息框显示成功")
                return True
            except Exception as e:
                logger.error(f"  ctypes 消息框失败: {e}")
                
            # 方法2: 使用 plyer
            if PLYER_AVAILABLE:
                try:
                    logger.info("  使用 plyer 通知")
                    notification.notify(
                        title=title,
                        message=message,
                        timeout=timeout,
                        app_name="智能复习闹钟",
                        toast=True
                    )
                    logger.info("  plyer 通知发送成功")
                    return True
                except Exception as e:
                    logger.error(f"  plyer 通知失败: {e}")
                    
            # 方法3: 使用 win10toast（如果可用）
            try:
                from win10toast import ToastNotifier
                logger.info("  使用 win10toast")
                toaster = ToastNotifier()
                toaster.show_toast(title, message, duration=timeout, threaded=True)
                logger.info("  win10toast 通知发送成功")
                return True
            except ImportError:
                logger.info("  win10toast 不可用")
            except Exception as e:
                logger.error(f"  win10toast 失败: {e}")
                
            logger.error("  所有 Windows 通知方法都失败了")
            return self._fallback_notify(title, message)
            
        except Exception as e:
            logger.error(f"  Windows 通知失败: {e}")
            return False
    
    def _linux_notify(self, title: str, message: str, timeout: int) -> bool:
        """Linux 系统通知（使用 notify-send）- 增强版"""
        try:
            logger.info("  尝试 Linux 通知...")
            
            # 方法1: 使用 plyer
            if PLYER_AVAILABLE:
                try:
                    logger.info("  使用 plyer 通知")
                    notification.notify(
                        title=title,
                        message=message,
                        timeout=timeout,
                        app_name="智能复习闹钟"
                    )
                    logger.info("  plyer 通知发送成功")
                    return True
                except Exception as e:
                    logger.error(f"  plyer 通知失败: {e}")
            
            # 方法2: 使用 notify-send 命令
            try:
                logger.info("  使用 notify-send 命令")
                result = subprocess.run([
                    "notify-send", 
                    title, 
                    message,
                    f"--expire-time={timeout * 1000}",
                    "--urgency=normal",
                    "--app-name=智能复习闹钟",
                    "--icon=dialog-information"
                ], capture_output=True, timeout=5)
                if result.returncode == 0:
                    logger.info("  notify-send 执行成功")
                    return True
                else:
                    logger.error(f"  notify-send 失败: {result.stderr}")
            except FileNotFoundError:
                logger.warning("  未找到 notify-send 命令")
            except Exception as e:
                logger.error(f"  notify-send 异常: {e}")
                    
            # 方法3: 使用 zenity（Gnome 桌面）
            try:
                logger.info("  尝试使用 zenity")
                result = subprocess.run([
                    "zenity",
                    "--info",
                    f"--text={message}",
                    f"--title={title}",
                    f"--timeout={timeout}"
                ], capture_output=True, timeout=5)
                if result.returncode == 0:
                    logger.info("  zenity 执行成功")
                    return True
            except FileNotFoundError:
                logger.info("  zenity 不可用")
            except Exception as e:
                logger.error(f"  zenity 异常: {e}")
                
            logger.error("  所有 Linux 通知方法都失败了")
            return self._fallback_notify(title, message)
            
        except Exception as e:
            logger.error(f"  Linux 通知失败: {e}")
            return False
    
    def _fallback_notify(self, title: str, message: str) -> bool:
        """备用通知方案 - 增强版"""
        try:
            logger.info("  使用备用通知方案")
            
            # 方法1: 使用 tkinter 对话框
            try:
                import tkinter as tk
                from tkinter import messagebox
                
                # 创建隐藏的根窗口
                root = tk.Tk()
                root.withdraw()
                root.attributes('-topmost', True)  # 置顶
                
                messagebox.showinfo(title, message)
                root.destroy()
                logger.info("  tkinter 对话框显示成功")
                return True
            except Exception as e:
                logger.error(f"  tkinter 对话框失败: {e}")
                
            # 方法2: 使用控制台输出
            print(f"\n{'='*50} - reminder.py:242")
            print(f"🔔 {title} - reminder.py:243")
            print(f"{message} - reminder.py:244")
            print(f"{'='*50}\n - reminder.py:245")
            logger.info("  已输出到控制台")
            return True
            
        except Exception as e:
            logger.error(f"  备用通知方案失败: {e}")
            # 最终备用：简单的打印
            print(f"🔔 {title}: {message} - reminder.py:252")
            return True


class ReminderService:
    """复习提醒服务 - 整合系统通知和App弹窗"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.system_notifier = SystemNotifier()
        self.reminder_interval = 30  # 每30秒检查一次提醒（测试用）
        self.is_running = False
        self.reminder_thread = None
        self.logger = logging.getLogger(__name__)
        self.current_user_id = None
        
    def start_reminder(self, user_id: Optional[int] = None) -> Dict[str, Any]:
        """启动提醒服务（后台线程）"""
        if self.is_running:
            return {"success": False, "msg": "提醒服务已在运行"}
        
        self.is_running = True
        self.current_user_id = user_id
        
        # 启动后台线程
        self.reminder_thread = threading.Thread(
            target=self._reminder_loop, 
            daemon=True,
            name="ReminderService"
        )
        self.reminder_thread.start()
        
        self.logger.info(f"提醒服务已启动，用户ID: {user_id}，检查间隔: {self.reminder_interval}秒")
        return {"success": True, "msg": "提醒服务已启动"}
    
    def stop_reminder(self) -> Dict[str, Any]:
        """停止提醒服务"""
        self.is_running = False
        if self.reminder_thread and self.reminder_thread.is_alive():
            self.reminder_thread.join(timeout=5.0)
        
        self.logger.info("提醒服务已停止")
        return {"success": True, "msg": "提醒服务已停止"}
    
    def set_reminder_interval(self, interval_seconds: int) -> Dict[str, Any]:
        """设置提醒检查间隔"""
        if interval_seconds < 10:
            return {"success": False, "msg": "间隔时间不能少于10秒"}
        
        self.reminder_interval = interval_seconds
        self.logger.info(f"提醒检查间隔已设置为: {interval_seconds}秒")
        return {"success": True, "msg": f"提醒间隔已设置为{interval_seconds}秒"}
    
    def _reminder_loop(self):
        """提醒循环：定时检查并发送提醒"""
        self.logger.info("提醒服务循环开始运行")
        
        while self.is_running:
            try:
                self._check_and_send_reminders()
                # 等待指定间隔
                for _ in range(self.reminder_interval):
                    if not self.is_running:
                        break
                    time.sleep(1)
            except Exception as e:
                self.logger.error(f"提醒循环异常: {e}")
                time.sleep(60)  # 出错后等待1分钟
        
        self.logger.info("提醒服务循环结束")
    
    def _check_and_send_reminders(self):
        """检查待提醒计划并发送"""
        try:
            if not self.current_user_id:
                self.logger.debug("未设置用户ID，跳过提醒检查")
                return
            
            pending_reviews = self._get_pending_reviews(self.current_user_id)
            
            if not pending_reviews:
                self.logger.debug("没有待复习的计划")
                return
            
            self.logger.info(f"找到 {len(pending_reviews)} 个待复习计划")
            
            # 为每个待复习项发送提醒
            for review in pending_reviews:
                self.logger.info(f"准备发送提醒: {review['title']}")
                self._send_reminder_notification(review)
                
        except Exception as e:
            self.logger.error(f"检查提醒失败: {e}")
    
    def _get_pending_reviews(self, user_id: int) -> List[Dict[str, Any]]:
        """获取待复习的计划"""
        try:
            session = self.db_manager.get_session()
            
            # 获取当前时间
            now = datetime.now()
            
            # 查询待复习的计划（计划时间已到且未完成）
            from src.database.models import ReviewSchedule, KnowledgeItem
            
            pending_reviews = (
                session.query(ReviewSchedule, KnowledgeItem)
                .join(KnowledgeItem, ReviewSchedule.knowledge_item_id == KnowledgeItem.id)
                .filter(
                    ReviewSchedule.user_id == user_id,
                    ReviewSchedule.scheduled_date <= now,
                    ~ReviewSchedule.completed
                )
                .order_by(ReviewSchedule.scheduled_date.asc())
                .all()
            )
            
            result = []
            for schedule, knowledge in pending_reviews:
                result.append({
                    'schedule_id': schedule.id,
                    'knowledge_id': knowledge.id,
                    'title': knowledge.title,
                    'content': knowledge.content[:100] + '...' if len(knowledge.content) > 100 else knowledge.content,
                    'scheduled_date': schedule.scheduled_date,
                    'stage_label': self._get_stage_label(schedule.interval_index),
                    'reminder_channel': 'system'  # 默认使用系统通知
                })
            
            session.close()
            return result
            
        except Exception as e:
            self.logger.error(f"获取待复习计划失败: {e}")
            return []
    
    def _get_stage_label(self, interval_index: int) -> str:
        """获取阶段标签"""
        stages = {
            0: "立即复习",
            1: "1小时后",
            2: "睡前复习", 
            3: "第2天",
            4: "第4天",
            5: "第7天",
            6: "第15天"
        }
        return stages.get(interval_index, f"第{interval_index + 1}阶段")
    
    def _send_reminder_notification(self, review: Dict[str, Any]):
        """发送复习提醒通知"""
        try:
            title = "📚 智能复习提醒"
            # 格式化时间
            scheduled_date = review['scheduled_date']
            if hasattr(scheduled_date, 'strftime'):
                time_str = scheduled_date.strftime('%H:%M')
            else:
                time_str = str(scheduled_date)
        
            message = (f"【{review['stage_label']}】{review['title']}\n"f"内容: {review['content']}\n"f"计划时间: {time_str}\n"f"请及时复习以巩固记忆～")
            
            # 根据提醒渠道发送
            if review.get("reminder_channel") == "app" and PLYER_AVAILABLE:
                success = self._send_app_notification(title, message)
            else:
                # 默认使用系统通知
                success = self.system_notifier.notify(title, message, timeout=15)
            
            if success:
                self.logger.info(f"✅ 已发送复习提醒: {review['title']}")
            else:
                self.logger.warning(f"❌ 发送复习提醒失败: {review['title']}")
                
        except Exception as e:
            self.logger.error(f"发送提醒通知失败: {e}")
    
    def _send_app_notification(self, title: str, message: str) -> bool:
        """发送App桌面通知（使用plyer）"""
        try:
            if not PLYER_AVAILABLE:
                self.logger.warning("plyer 不可用，无法发送App通知")
                return False
                
            notification.notify(
                title=title,
                message=message,
                app_name="智能复习闹钟",
                timeout=15,  # 通知显示15秒
                toast=False
            )
            self.logger.debug(f"App提醒发送成功: {title}")
            return True
        except Exception as e:
            self.logger.error(f"App提醒发送失败: {str(e)}")
            return False
    
    def send_test_notification(self) -> Dict[str, Any]:
        """发送测试通知"""
        try:
            title = "🔔 测试通知"
            message = (
                "这是一条测试系统通知！\n"
                "智能复习闹钟提醒服务运行正常。\n"
                "系统将按时提醒您复习知识点。"
            )
            
            success = self.system_notifier.notify(title, message, timeout=10)
            
            if success:
                return {"success": True, "msg": "测试通知发送成功"}
            else:
                return {"success": False, "msg": "测试通知发送失败"}
                
        except Exception as e:
            return {"success": False, "msg": f"测试通知异常: {str(e)}"}
    
    def get_service_status(self) -> Dict[str, Any]:
        """获取服务状态"""
        return {
            "success": True,
            "is_running": self.is_running,
            "interval_seconds": self.reminder_interval,
            "user_id": self.current_user_id,
            "system": platform.system(),
            "plyer_available": PLYER_AVAILABLE
        }


# 全局提醒服务实例
_global_reminder_service = None


def get_reminder_service(db_manager) -> ReminderService:
    """获取全局提醒服务实例"""
    global _global_reminder_service
    if _global_reminder_service is None:
        _global_reminder_service = ReminderService(db_manager)
    return _global_reminder_service


def test_notification():
    """测试通知功能"""
    notifier = SystemNotifier()
    success = notifier.notify(
        "🔔 测试通知", 
        "这是一条测试系统通知！\n智能复习闹钟提醒您按时复习。"
    )
    print(f"通知测试: {'✅ 成功' if success else '❌ 失败'} - reminder.py:500")
    return success


if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 测试通知功能
    print("🔔 测试系统提醒功能... - reminder.py:512")
    test_notification()