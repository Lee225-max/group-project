"""
复习调度界面 - 成员C实现
"""

import customtkinter as ctk
from tkinter import messagebox
from .service import SchedulerService
from src.database.models import ReviewSchedule, KnowledgeItem


class ReviewDialog(ctk.CTkToplevel):
    """复习对话框"""

    def __init__(self, parent, review, scheduler_service, db_manager, refresh_callback):
        super().__init__(parent)
        self.review = review
        self.scheduler_service = scheduler_service
        self.db_manager = db_manager
        self.refresh_callback = refresh_callback

        self.title("复习知识点")
        self.geometry("600x500")
        self.resizable(False, False)

        # 设置模态
        self.transient(parent)
        self.grab_set()

        self.knowledge_item = None
        self.recall_score = 0.5  # 默认回忆分数
        
        # 确保review是字典格式
        self.review = self._ensure_dict_format(review)
        
        self.load_knowledge_item()
        self.create_widgets()
        self.center_window()

    def _ensure_dict_format(self, item):
        """确保项目是字典格式"""
        if isinstance(item, dict):
            return item
        elif hasattr(item, '__dict__'):
            return item.__dict__
        else:
            return self._convert_to_dict(item)

    def _convert_to_dict(self, item):
        """将对象转换为字典格式"""
        result = {
            'id': getattr(item, 'id', ''),
            'knowledge_item_id': getattr(item, 'knowledge_item_id', ''),
            'title': getattr(item, 'title', '无标题'),
            'content': getattr(item, 'content', ''),
            'category': getattr(item, 'category', ''),
            'completed': getattr(item, 'completed', False),
            'scheduled_date': getattr(item, 'scheduled_date', ''),
            'interval_index': getattr(item, 'interval_index', 0)
        }
        return result

    def center_window(self):
        """居中显示窗口"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"+{x}+{y}")

    def load_knowledge_item(self):
        """加载知识点内容"""
        session = self.db_manager.get_session()
        try:
            knowledge_item_id = self.review.get('knowledge_item_id') or self.review.get('knowledge_id')
            if not knowledge_item_id:
                print("❌ 无法获取知识点ID - ui.py:77")
                return
                
            self.knowledge_item = (
                session.query(KnowledgeItem)
                .filter(KnowledgeItem.id == knowledge_item_id)
                .first()
            )
            if not self.knowledge_item:
                print(f"❌ 找不到知识点: ID {knowledge_item_id} - ui.py:86")
        except Exception as e:
            print(f"❌ 加载知识点失败: {e} - ui.py:88")
        finally:
            session.close()

    def create_widgets(self):
        """创建对话框组件"""
        if not self.knowledge_item:
            messagebox.showerror("错误", "知识点不存在")
            self.destroy()
            return

        # 主容器
        main_container = ctk.CTkFrame(self)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # 标题
        title_label = ctk.CTkLabel(
            main_container,
            text=self.knowledge_item.title,
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        title_label.pack(pady=(0, 10))

        # 分类信息
        if self.knowledge_item.category:
            category_label = ctk.CTkLabel(
                main_container,
                text=f"分类: {self.knowledge_item.category}",
                font=ctk.CTkFont(size=14),
                text_color="gray",
            )
            category_label.pack(pady=(0, 20))

        # 内容区域
        content_frame = ctk.CTkFrame(main_container)
        content_frame.pack(fill="both", expand=True, pady=10)

        # 内容标签
        ctk.CTkLabel(
            content_frame, text="知识点内容:", font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", pady=(10, 5))

        # 内容显示
        content_text = ctk.CTkTextbox(
            content_frame, wrap="word", font=ctk.CTkFont(size=12)
        )
        content_text.pack(fill="both", expand=True, padx=10, pady=5)
        content_text.insert("1.0", self.knowledge_item.content)
        content_text.configure(state="disabled")  # 只读模式

        # 回忆程度评估
        evaluation_frame = ctk.CTkFrame(main_container)
        evaluation_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(
            evaluation_frame,
            text="回忆程度评估:",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(anchor="w", pady=(10, 5))

        # 回忆程度滑块
        slider_frame = ctk.CTkFrame(evaluation_frame, fg_color="transparent")
        slider_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(slider_frame, text="完全忘记", font=ctk.CTkFont(size=12)).pack(
            side="left"
        )

        self.recall_slider = ctk.CTkSlider(
            slider_frame,
            from_=0,
            to=1,
            number_of_steps=10,
            command=self.on_slider_change,
        )
        self.recall_slider.pack(side="left", fill="x", expand=True, padx=10)
        self.recall_slider.set(0.5)  # 默认值

        ctk.CTkLabel(slider_frame, text="完全记得", font=ctk.CTkFont(size=12)).pack(
            side="left"
        )

        # 分数显示
        self.score_label = ctk.CTkLabel(
            evaluation_frame,
            text="回忆分数: 50%",
            font=ctk.CTkFont(size=12),
            text_color="blue",
        )
        self.score_label.pack(pady=5)

        # 按钮框架
        button_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        button_frame.pack(fill="x", pady=10)

        # 完成复习按钮
        complete_btn = ctk.CTkButton(
            button_frame,
            text="完成复习",
            command=self.complete_review,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        complete_btn.pack(side="left", padx=(0, 10), expand=True)

        # 取消按钮
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="稍后复习",
            command=self.destroy,
            height=40,
            fg_color="gray",
        )
        cancel_btn.pack(side="right", padx=(10, 0), expand=True)

    def on_slider_change(self, value):
        """滑块值改变回调"""
        score_percent = int(value * 100)
        self.recall_score = value
        self.score_label.configure(text=f"回忆分数: {score_percent}%")

    def complete_review(self):
        """完成复习"""
        try:
            # 将回忆分数转换为0-100的范围
            recall_score_percent = int(self.recall_score * 100)
            effectiveness = max(1, min(5, int(self.recall_score * 5)))  # 1-5分
            
            # 获取复习计划ID和知识点ID
            schedule_id = self.review.get('id') or self.review.get('schedule_id')
            knowledge_id = self.review.get('knowledge_item_id') or self.review.get('knowledge_id')
            
            if not schedule_id:
                messagebox.showerror("错误", "无法获取复习计划ID")
                return

            result = self.scheduler_service.complete_review(
                schedule_id,
                knowledge_id,
                effectiveness,
                recall_score_percent
            )

            if result.get("success", False):
                messagebox.showinfo("成功", "复习完成！")
                if self.refresh_callback:
                    self.refresh_callback()
                self.destroy()
            else:
                messagebox.showerror("错误", result.get("msg", "复习完成失败"))

        except Exception as e:
            messagebox.showerror("错误", f"复习完成失败: {str(e)}")


class ReviewSchedulerFrame(ctk.CTkFrame):
    """今日复习计划界面"""

    def __init__(self, parent, current_user, db_manager):
        super().__init__(parent)
        self.current_user = current_user
        self.scheduler_service = SchedulerService(db_manager)
        self.db_manager = db_manager
        
        # 跟踪当前显示的组件
        self.current_widgets = []
        self.empty_label = None
        
        print(f"🎯 今日复习界面初始化完成  用户ID: {self.current_user.id} - ui.py:256")
        
        self.create_widgets()
        print("🎯 今日复习界面组件创建完成 - ui.py:259")
        
        self.load_today_reviews()
        print("🎯 今日复习界面数据加载完成 - ui.py:262")
        
    def create_widgets(self):
        """创建界面组件"""
        # 设置框架背景色便于调试
        self.configure(fg_color=("gray95", "gray10"))
        
        # 顶部工具栏
        toolbar = ctk.CTkFrame(self)
        toolbar.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            toolbar, text="今日复习计划", font=ctk.CTkFont(size=20, weight="bold")
        ).pack(side="left")

        # 统计信息
        self.stats_label = ctk.CTkLabel(
            toolbar, text="加载中...", font=ctk.CTkFont(size=14)
        )
        self.stats_label.pack(side="right")

        # 刷新按钮
        refresh_btn = ctk.CTkButton(
            toolbar, text="刷新", command=self.load_today_reviews, width=80
        )
        refresh_btn.pack(side="right", padx=(10, 0))

        # 内容区域
        content_frame = ctk.CTkFrame(self)
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        print(f"📦 内容框架创建: {content_frame.winfo_exists()} - ui.py:292")

        # 复习列表容器 - 使用ScrollableFrame
        self.review_list_frame = ctk.CTkScrollableFrame(
            content_frame, 
            fg_color=("gray90", "gray13")  # 设置明显背景色便于调试
        )
        self.review_list_frame.pack(fill="both", expand=True, padx=5, pady=5)
        print(f"📦 滚动框架创建: {self.review_list_frame.winfo_exists()} - ui.py:300")

    def clear_widgets(self):
        """安全地清除所有组件"""
        try:
            # 清除当前跟踪的组件
            for widget in self.current_widgets:
                try:
                    widget.destroy()
                except Exception:
                    continue
            self.current_widgets = []
            
            # 清除空状态标签
            if self.empty_label:
                try:
                    self.empty_label.destroy()
                except Exception:
                    pass
                self.empty_label = None
                
            # 清除滚动框架中的所有子组件
            for widget in self.review_list_frame.winfo_children():
                try:
                    widget.destroy()
                except Exception:
                    continue
        except Exception as e:
            print(f"清除组件时出错: {e} - ui.py:328")

    def load_today_reviews(self):
        """加载今日复习计划"""
        print("🔄 今日复习界面开始加载数据 - ui.py:332")
        # 安全地清除现有内容
        self.clear_widgets()

        try:
            print(f"🔍 调用调度器服务获取今日复习计划，用户ID: {self.current_user.id} - ui.py:337")
            
            # 尝试不同的方法名来获取今日复习计划
            today_reviews = []
            
            # 方法1: 尝试 get_today_review_plans
            if hasattr(self.scheduler_service, 'get_today_review_plans'):
                today_reviews = self.scheduler_service.get_today_review_plans(self.current_user.id)
                print("✅ 使用 get_today_review_plans 方法 - ui.py:345")
            # 方法2: 尝试 get_today_reviews
            elif hasattr(self.scheduler_service, 'get_today_reviews'):
                today_reviews = self.scheduler_service.get_today_reviews(self.current_user.id)
                print("✅ 使用 get_today_reviews 方法 - ui.py:349")
            else:
                print("❌ 调度器服务中没有找到获取今日复习计划的方法 - ui.py:351")
                today_reviews = []
        
            print(f"📊 今日复习界面收到 {len(today_reviews)} 个复习计划 - ui.py:354")
            
            # 调试：打印接收到的数据
            for i, review in enumerate(today_reviews):
                print(f"📋 复习计划 {i+1}: {type(review)} - ui.py:358")
                if hasattr(review, '__dict__'):
                    print(f"属性: {review.__dict__} - ui.py:360")
                elif isinstance(review, dict):
                    print(f"数据: {review} - ui.py:362")
                else:
                    print(f"值: {review} - ui.py:364")

            if not today_reviews:
                # 创建空状态提示
                self.empty_label = ctk.CTkLabel(
                    self.review_list_frame,
                    text="今日没有复习计划\n快去添加一些知识点吧！",
                    font=ctk.CTkFont(size=16),
                    text_color="gray",
                )
                self.empty_label.pack(expand=True, pady=50)
                self.stats_label.configure(text="今日无复习任务")
                return

            # 更新统计信息
            completed = sum(1 for review in today_reviews if self._get_completed_status(review))
            total = len(today_reviews)
            self.stats_label.configure(text=f"进度: {completed}/{total}")

            # 显示复习项目
            for review in today_reviews:
                review_item = self.create_review_item(review)
                if review_item:
                    self.current_widgets.append(review_item)
                    
            print(f"✅ 成功创建 {len(self.current_widgets)} 个复习项目 - ui.py:389")

        except Exception as e:
            print(f"❌ 加载复习计划失败: {str(e)} - ui.py:392")
            messagebox.showerror("错误", f"加载复习计划失败: {str(e)}")

    def _get_completed_status(self, review):
        """安全地获取完成状态"""
        if hasattr(review, 'completed'):
            return review.completed
        elif isinstance(review, dict):
            return review.get('completed', False)
        else:
            return False

    def create_review_item(self, review):
        """创建复习项目UI"""
        print(f"🔧 创建复习项目: {type(review)} - ui.py:406")
        
        try:
            # 确保review是字典格式
            review = self._ensure_dict_format(review)
            print(f"🔧 转换后格式: {type(review)} - ui.py:411")
            
            session = self.db_manager.get_session()
            try:
                # 获取知识点ID - 尝试不同的字段名
                knowledge_item_id = (review.get('knowledge_item_id') or 
                                   review.get('knowledge_id'))
                
                if not knowledge_item_id:
                    print("❌ 无法获取知识点ID - ui.py:420")
                    return None

                # 获取知识点信息
                knowledge_item = (
                    session.query(KnowledgeItem)
                    .filter(KnowledgeItem.id == knowledge_item_id)
                    .first()
                )

                if not knowledge_item:
                    print(f"❌ 找不到知识点: ID {knowledge_item_id} - ui.py:431")
                    return None

                # 复习项目卡片
                item_frame = ctk.CTkFrame(self.review_list_frame)
                item_frame.pack(fill="x", padx=5, pady=5)

                # 内容区域
                content_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
                content_frame.pack(fill="x", padx=10, pady=10)

                # 标题和分类
                title_label = ctk.CTkLabel(
                    content_frame,
                    text=knowledge_item.title,
                    font=ctk.CTkFont(size=16, weight="bold"),
                    anchor="w",
                )
                title_label.pack(anchor="w")

                if knowledge_item.category:
                    category_label = ctk.CTkLabel(
                        content_frame,
                        text=f"分类: {knowledge_item.category}",
                        font=ctk.CTkFont(size=12),
                        text_color="gray",
                        anchor="w",
                    )
                    category_label.pack(anchor="w", pady=(2, 0))

                # 复习内容预览
                content_preview = (
                    knowledge_item.content[:100] + "..."
                    if len(knowledge_item.content) > 100
                    else knowledge_item.content
                )
                content_label = ctk.CTkLabel(
                    content_frame,
                    text=content_preview,
                    font=ctk.CTkFont(size=12),
                    anchor="w",
                    justify="left",
                )
                content_label.pack(anchor="w", pady=(5, 0), fill="x")

                # 复习信息
                info_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
                info_frame.pack(fill="x", pady=(10, 0))

                # 使用字典访问方式获取阶段信息
                interval_index = review.get('interval_index', 0)
                stage_label_text = f"第 {interval_index + 1} 次复习"
                
                # 如果有阶段标签，使用阶段标签
                stage_label_text = review.get('stage_label', stage_label_text)
                
                stage_label = ctk.CTkLabel(
                    info_frame,
                    text=stage_label_text,
                    font=ctk.CTkFont(size=12),
                    text_color="blue",
                )
                stage_label.pack(side="left")

                # 使用字典访问方式获取时间信息
                scheduled_date = review.get('scheduled_date', '')
                if hasattr(scheduled_date, 'strftime'):
                    time_str = scheduled_date.strftime('%H:%M')
                elif isinstance(scheduled_date, str) and ' ' in scheduled_date:
                    time_str = scheduled_date.split(' ')[1][:5]  # 提取时间部分
                else:
                    time_str = '未知时间'
                    
                time_label = ctk.CTkLabel(
                    info_frame,
                    text=f"计划时间: {time_str}",
                    font=ctk.CTkFont(size=12),
                    text_color="gray",
                )
                time_label.pack(side="left", padx=(20, 0))

                # 操作按钮
                button_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
                button_frame.pack(fill="x", pady=(10, 0))

                if not review.get('completed', False):
                    # 开始复习按钮
                    review_btn = ctk.CTkButton(
                        button_frame,
                        text="开始复习",
                        command=lambda r=review: self.start_review(r),
                        fg_color="#28a745",
                        hover_color="#218838",
                    )
                    review_btn.pack(side="left")
                else:
                    # 已完成状态
                    completed_label = ctk.CTkLabel(
                        button_frame,
                        text="✅ 已完成",
                        font=ctk.CTkFont(size=12, weight="bold"),
                        text_color="green",
                    )
                    completed_label.pack(side="left")

                # 分隔线
                separator = ctk.CTkFrame(item_frame, height=1, fg_color="lightgray")
                separator.pack(fill="x", padx=10)

                print(f"✅ 成功创建复习项目: {knowledge_item.title} - ui.py:540")
                return item_frame

            except Exception as e:
                print(f"❌ 创建复习项目时出错: {e} - ui.py:544")
                return None
            finally:
                session.close()
                
        except Exception as e:
            print(f"❌ 处理复习项目时出错: {e} - ui.py:550")
            return None

    def _ensure_dict_format(self, item):
        """确保项目是字典格式"""
        if isinstance(item, dict):
            return item
        elif hasattr(item, '__dict__'):
            return item.__dict__
        else:
            return self._convert_to_dict(item)

    def _convert_to_dict(self, item):
        """将对象转换为字典格式"""
        result = {
            'id': getattr(item, 'id', ''),
            'knowledge_item_id': getattr(item, 'knowledge_item_id', ''),
            'knowledge_id': getattr(item, 'knowledge_id', ''),
            'title': getattr(item, 'title', '无标题'),
            'content': getattr(item, 'content', ''),
            'category': getattr(item, 'category', ''),
            'completed': getattr(item, 'completed', False),
            'scheduled_date': getattr(item, 'scheduled_date', ''),
            'interval_index': getattr(item, 'interval_index', 0),
            'stage_label': getattr(item, 'stage_label', '未知阶段'),
            'stage_desc': getattr(item, 'stage_desc', ''),
            'schedule_id': getattr(item, 'schedule_id', '')
        }
        return result

    def start_review(self, review):
        """开始复习"""
        try:
            ReviewDialog(
                self,
                review,
                self.scheduler_service,
                self.db_manager,
                self.load_today_reviews,
            )
        except Exception as e:
            messagebox.showerror("错误", f"打开复习对话框失败: {str(e)}")