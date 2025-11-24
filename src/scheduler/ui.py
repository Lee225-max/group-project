"""
复习调度界面 - lixinru
"""

import customtkinter as ctk
from tkinter import messagebox
from .service import SchedulerService
from src.database.models import KnowledgeItem


class ReviewDialog(ctk.CTkToplevel):
    """复习对话框 - 采用知识管理页面样式"""

    def __init__(self, parent, review, current_user,scheduler_service, db_manager, refresh_callback):
        super().__init__(parent)
        self.review = review
        self.current_user = current_user
        self.scheduler_service = scheduler_service
        self.db_manager = db_manager
        self.refresh_callback = refresh_callback

        # 颜色配置 - 与知识管理页面保持一致
        self.colors = {
            'primary': '#2E86AB',
            'secondary': '#A23B72',
            'success': '#18A999',
            'warning': '#F18F01',
            'danger': '#C73E1D',
            'light': '#F8F9FA',
            'dark': '#212529',
            'today': '#FF6B6B',
            'completed': '#4ECDC4'
        }

        self.title("🎯 复习知识点")
        self.geometry("700x600")
        self.resizable(True, True)

        # 设置模态
        self.transient(parent)
        self.grab_set()
        self.focus_set()

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
        width = 700
        height = 600
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def load_knowledge_item(self):
        """加载知识点内容"""
        session = self.db_manager.get_session()
        try:
            knowledge_item_id = self.review.get(
                'knowledge_item_id') or self.review.get('knowledge_id')
            if not knowledge_item_id:
                print("❌ 无法获取知识点ID - ui.py:92")
                return

            self.knowledge_item = (
                session.query(KnowledgeItem)
                .filter(KnowledgeItem.id == knowledge_item_id)
                .first()
            )
            if not self.knowledge_item:
                print(f"❌ 找不到知识点: ID {knowledge_item_id} - ui.py:101")
        except Exception as e:
            print(f"❌ 加载知识点失败: {e} - ui.py:103")
        finally:
            session.close()

    def create_widgets(self):
        """创建对话框组件 - 采用知识管理页面样式"""
        if not self.knowledge_item:
            messagebox.showerror("错误", "知识点不存在")
            self.destroy()
            return

        # 主容器
        main_container = ctk.CTkFrame(self, fg_color=self.colors['light'], corner_radius=15)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # 标题
        title_label = ctk.CTkLabel(
            main_container,
            text=f"📖 {self.knowledge_item.title}",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=self.colors['dark']
        )
        title_label.pack(anchor="w", pady=(10, 5), padx=20)

        # 分类信息
        if self.knowledge_item.category:
            category_label = ctk.CTkLabel(
                main_container,
                text=f"🏷️ {self.knowledge_item.category}",
                font=ctk.CTkFont(size=14),
                text_color=self.colors['secondary']
            )
            category_label.pack(anchor="w", pady=(0, 15), padx=20)

        # 内容区域卡片
        content_card = ctk.CTkFrame(main_container, fg_color="white", corner_radius=12)
        content_card.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        content_card.grid_columnconfigure(0, weight=1)
        content_card.grid_rowconfigure(1, weight=1)

        # 内容标签
        ctk.CTkLabel(
            content_card,
            text="📄 内容",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors['dark']
        ).grid(row=0, column=0, sticky="w", padx=15, pady=15)

        # 内容显示
        content_text = ctk.CTkTextbox(
            content_card,
            wrap="word",
            font=ctk.CTkFont(size=13),
            border_width=1,
            border_color="#E0E0E0",
            corner_radius=8
        )
        content_text.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        content_text.insert("1.0", self.knowledge_item.content)
        content_text.configure(state="disabled")  # 只读模式

        # 回忆程度评估卡片
        evaluation_card = ctk.CTkFrame(main_container, fg_color="white", corner_radius=12)
        evaluation_card.pack(fill="x", padx=20, pady=(0, 20))

        ctk.CTkLabel(
            evaluation_card,
            text="🎯 回忆程度评估",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors['dark']
        ).pack(anchor="w", padx=15, pady=15)

        # 回忆程度滑块
        slider_frame = ctk.CTkFrame(evaluation_card, fg_color="transparent")
        slider_frame.pack(fill="x", padx=15, pady=(0, 10))

        ctk.CTkLabel(
            slider_frame,
            text="😵 完全忘记",
            font=ctk.CTkFont(size=12),
            text_color=self.colors['danger']
        ).pack(side="left")

        self.recall_slider = ctk.CTkSlider(
            slider_frame,
            from_=0,
            to=1,
            number_of_steps=10,
            command=self.on_slider_change,
            progress_color=self.colors['primary'],
            button_color=self.colors['primary'],
            button_hover_color=self.colors['secondary']
        )
        self.recall_slider.pack(side="left", fill="x", expand=True, padx=10)
        self.recall_slider.set(0.5)  # 默认值

        ctk.CTkLabel(
            slider_frame,
            text="🤩 完全记得",
            font=ctk.CTkFont(size=12),
            text_color=self.colors['success']
        ).pack(side="left")

        # 分数显示
        self.score_label = ctk.CTkLabel(
            evaluation_card,
            text="回忆分数: 50%",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.colors['primary']
        )
        self.score_label.pack(pady=(0, 15))

        # 按钮框架
        button_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=(0, 10))
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)

        # 完成复习按钮
        complete_btn = ctk.CTkButton(
            button_frame,
            text="✅ 完成复习",
            command=self.complete_review,
            height=45,
            fg_color=self.colors['success'],
            hover_color='#139C8B',
            font=ctk.CTkFont(size=14, weight="bold")
        )
        complete_btn.grid(row=0, column=0, padx=(0, 10))

        # 取消按钮
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="⏰ 稍后复习",
            command=self.destroy,
            height=45,
            fg_color="#6C757D",
            hover_color="#5A6268",
            font=ctk.CTkFont(size=14)
        )
        cancel_btn.grid(row=0, column=1, padx=(10, 0))

    def on_slider_change(self, value):
        """滑块值改变回调"""
        score_percent = int(value * 100)
        self.recall_score = value
        
        # 根据分数改变颜色
        if score_percent >= 80:
            color = self.colors['success']
        elif score_percent >= 60:
            color = self.colors['primary']
        elif score_percent >= 40:
            color = self.colors['warning']
        else:
            color = self.colors['danger']
            
        self.score_label.configure(
            text=f"回忆分数: {score_percent}%",
            text_color=color
        )

    def complete_review(self):
        """完成复习"""
        try:
            # 将回忆分数转换为0-100的范围
            recall_score_percent = int(self.recall_score * 100)
            effectiveness = max(1, min(5, int(self.recall_score * 5)))  # 1-5分

            # 获取复习计划ID和知识点ID
            schedule_id = self.review.get('id') or self.review.get('schedule_id')
            knowledge_id = self.review.get(
                'knowledge_item_id') or self.review.get('knowledge_id')

            if not schedule_id:
                messagebox.showerror("错误", "无法获取复习计划ID")
                return

            result = self.scheduler_service.complete_review(
                schedule_id,
                self.current_user.id,
                effectiveness,
                recall_score_percent
            )

            if result.get("success", False):
                messagebox.showinfo("成功", "🎉 复习完成！")
                if self.refresh_callback:
                    self.refresh_callback()
                self.destroy()
            else:
                messagebox.showerror("错误", result.get("msg", "复习完成失败"))

        except Exception as e:
            messagebox.showerror("错误", f"复习完成失败: {str(e)}")


class ReviewSchedulerFrame(ctk.CTkFrame):
    """今日复习计划界面 - 采用知识管理页面样式"""

    def __init__(self, parent, current_user, db_manager):
        super().__init__(parent)
        self.current_user = current_user
        self.scheduler_service = SchedulerService(db_manager)
        self.db_manager = db_manager

        # 使用相同的颜色配置
        self.colors = {
            'primary': '#2E86AB',
            'secondary': '#A23B72',
            'success': '#18A999',
            'warning': '#F18F01',
            'danger': '#C73E1D',
            'light': '#F8F9FA',
            'dark': '#212529',
            'today': '#FF6B6B',
            'completed': '#4ECDC4'
        }

        # 跟踪当前显示的组件
        self.current_widgets = []
        self.empty_label = None

        print(f"🎯 今日复习界面初始化完成  用户ID: {self.current_user.id} - ui.py:326")

        self.create_widgets()
        print("🎯 今日复习界面组件创建完成 - ui.py:329")

        self.load_today_reviews()
        print("🎯 今日复习界面数据加载完成 - ui.py:332")

    def create_widgets(self):
        """创建界面组件 - 采用知识管理页面样式"""
        # 配置网格布局
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # 主控制栏（与知识管理页面一致）
        control_frame = ctk.CTkFrame(self, fg_color=self.colors['light'], corner_radius=10)
        control_frame.grid(row=0, column=0, sticky="ew", padx=8, pady=5)
        control_frame.grid_columnconfigure(1, weight=1)

        # 第一行：标题和统计信息
        header_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, columnspan=3, sticky="ew", padx=10, pady=5)
        header_frame.grid_columnconfigure(1, weight=1)

        # 标题
        title_label = ctk.CTkLabel(
            header_frame,
            text="📅 今日复习",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors['primary']
        )
        title_label.grid(row=0, column=0, sticky="w")

        # 统计信息
        self.stats_label = ctk.CTkLabel(
            header_frame,
            text="今日复习：加载中...",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=self.colors['dark']
        )
        self.stats_label.grid(row=0, column=1, sticky="w", padx=15)

        # 刷新按钮
        refresh_btn = ctk.CTkButton(
            header_frame,
            text="🔄 刷新",
            command=self.load_today_reviews,
            width=70,
            height=26,
            fg_color=self.colors['primary'],
            hover_color='#1B6B93',
            font=ctk.CTkFont(size=10, weight="bold")
        )
        refresh_btn.grid(row=0, column=2, sticky="e")

        # 复习列表容器 - 紧贴控制栏
        self.list_container = ctk.CTkFrame(self, corner_radius=10)
        self.list_container.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))
        self.list_container.grid_columnconfigure(0, weight=1)
        self.list_container.grid_rowconfigure(0, weight=1)

        # 创建滚动框架
        self.create_list_frame()

    def create_list_frame(self):
        """创建复习列表框架"""
        # 清空容器
        for widget in self.list_container.winfo_children():
            widget.destroy()

        # 滚动框架
        self.scrollable_frame = ctk.CTkScrollableFrame(
            self.list_container,
            fg_color=self.colors['light'],
            corner_radius=12
        )
        self.scrollable_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

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
            for widget in self.scrollable_frame.winfo_children():
                try:
                    widget.destroy()
                except Exception:
                    continue
        except Exception as e:
            print(f"清除组件时出错: {e} - ui.py:431")

    def load_today_reviews(self):
        """加载今日复习计划"""
        print("🔄 今日复习界面开始加载数据 - ui.py:435")
        # 安全地清除现有内容
        self.clear_widgets()

        try:
            print(f"🔍 调用调度器服务获取今日复习计划，用户ID: {self.current_user.id} - ui.py:440")

            # 尝试不同的方法名来获取今日复习计划
            today_reviews = []

            # 方法1: 尝试 get_today_review_plans
            if hasattr(self.scheduler_service, 'get_today_review_plans'):
                today_reviews = self.scheduler_service.get_today_review_plans(
                    self.current_user.id)
                print("✅ 使用 get_today_review_plans 方法 - ui.py:449")
            # 方法2: 尝试 get_today_reviews
            elif hasattr(self.scheduler_service, 'get_today_reviews'):
                today_reviews = self.scheduler_service.get_today_reviews(
                    self.current_user.id)
                print("✅ 使用 get_today_reviews 方法 - ui.py:454")
            else:
                print("❌ 调度器服务中没有找到获取今日复习计划的方法 - ui.py:456")
                today_reviews = []

            print(f"📊 今日复习界面收到 {len(today_reviews)} 个复习计划 - ui.py:459")

            if not today_reviews:
                # 创建空状态提示 - 采用知识管理页面样式
                empty_frame = ctk.CTkFrame(
                    self.scrollable_frame,
                    fg_color="transparent",
                    corner_radius=12
                )
                empty_frame.grid(row=0, column=0, sticky="nsew", pady=50)
                empty_frame.grid_columnconfigure(0, weight=1)

                self.empty_label = ctk.CTkLabel(
                    empty_frame,
                    text="🎉 太棒了！\n所有今日复习任务已完成！",
                    font=ctk.CTkFont(size=16),
                    text_color=self.colors['dark']
                )
                self.empty_label.grid(row=0, column=0, pady=10)
                
                self.stats_label.configure(
                    text="🎉 今日无复习任务",
                    text_color=self.colors['success']
                )
                return

            # 更新统计信息
            completed = sum(
                1 for review in today_reviews if self._get_completed_status(review))
            total = len(today_reviews)
            
            # 根据完成情况设置统计信息颜色
            if completed == total:
                stats_color = self.colors['success']
                stats_text = f"🎉 全部完成: {completed}/{total}"
            elif completed > 0:
                stats_color = self.colors['primary']
                stats_text = f"📊 进度: {completed}/{total}"
            else:
                stats_color = self.colors['warning']
                stats_text = f"⏳ 待开始: {completed}/{total}"
                
            self.stats_label.configure(
                text=stats_text,
                text_color=stats_color
            )

            # 显示复习项目
            for i, review in enumerate(today_reviews):
                review_item = self.create_review_item(review, i)
                if review_item:
                    self.current_widgets.append(review_item)

            print(f"✅ 成功创建 {len(self.current_widgets)} 个复习项目 - ui.py:512")

        except Exception as e:
            print(f"❌ 加载复习计划失败: {str(e)} - ui.py:515")
            messagebox.showerror("错误", f"加载复习计划失败: {str(e)}")

    def _get_completed_status(self, review):
        """安全地获取完成状态"""
        if hasattr(review, 'completed'):
            return review.completed
        elif isinstance(review, dict):
            return review.get('completed', False)
        else:
            return False

    def create_review_item(self, review, index):
        """创建复习项目UI - 采用知识管理页面卡片样式"""
        print(f"🔧 创建复习项目: {type(review)} - ui.py:529")

        try:
            # 确保review是字典格式
            review = self._ensure_dict_format(review)

            session = self.db_manager.get_session()
            try:
                # 获取知识点ID - 尝试不同的字段名
                knowledge_item_id = (review.get('knowledge_item_id') or
                                     review.get('knowledge_id'))

                if not knowledge_item_id:
                    print("❌ 无法获取知识点ID - ui.py:542")
                    return None

                # 获取知识点信息
                knowledge_item = (
                    session.query(KnowledgeItem)
                    .filter(KnowledgeItem.id == knowledge_item_id)
                    .first()
                )

                if not knowledge_item:
                    print(f"❌ 找不到知识点: ID {knowledge_item_id} - ui.py:553")
                    return None

                is_completed = review.get('completed', False)
                is_urgent = not is_completed  # 未完成的视为紧急

                # 复习项目卡片 - 采用知识管理页面样式
                card = ctk.CTkFrame(
                    self.scrollable_frame,
                    fg_color="white",
                    border_color=self.colors['today'] if not is_completed else "#E0E0E0",
                    border_width=2 if not is_completed else 1,
                    corner_radius=12
                )
                card.grid(row=index, column=0, sticky="ew", padx=10, pady=8)
                card.grid_columnconfigure(1, weight=1)

                # 紧急状态指示器（未完成时显示）
                if is_urgent:
                    urgency_indicator = ctk.CTkFrame(
                        card,
                        fg_color=self.colors['danger'],
                        width=6,
                        corner_radius=3
                    )
                    urgency_indicator.grid(row=0, column=0, rowspan=3, sticky="ns", padx=(10, 5), pady=10)

                # 内容区域
                content_frame = ctk.CTkFrame(card, fg_color="transparent")
                content_frame.grid(row=0, column=1, sticky="ew", padx=10, pady=12)
                content_frame.grid_columnconfigure(0, weight=1)

                # 标题和状态
                title_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
                title_frame.grid(row=0, column=0, sticky="ew", pady=(0, 8))
                title_frame.grid_columnconfigure(0, weight=1)

                title_label = ctk.CTkLabel(
                    title_frame,
                    text=f"📖 {knowledge_item.title}",
                    font=ctk.CTkFont(size=16, weight="bold"),
                    text_color=self.colors['dark'],
                    anchor="w"
                )
                title_label.grid(row=0, column=0, sticky="w")

                # 状态标签
                if is_completed:
                    status_text = "✅ 已完成"
                    status_color = self.colors['completed']
                else:
                    # 使用字典访问方式获取阶段信息
                    interval_index = review.get('interval_index', 0)
                    status_text = f"第 {interval_index + 1} 次复习"
                    # 如果有阶段标签，使用阶段标签
                    status_text = review.get('stage_label', status_text)
                    status_color = self.colors['today']
                
                status_label = ctk.CTkLabel(
                    title_frame,
                    text=status_text,
                    font=ctk.CTkFont(size=11, weight="bold"),
                    text_color="white",
                    fg_color=status_color,
                    corner_radius=8,
                    padx=8,
                    pady=2
                )
                status_label.grid(row=0, column=1, sticky="e", padx=(10, 0))

                # 元信息
                meta_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
                meta_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))

                # 分类
                if knowledge_item.category:
                    category_label = ctk.CTkLabel(
                        meta_frame,
                        text=f"🏷️ {knowledge_item.category}",
                        font=ctk.CTkFont(size=12),
                        text_color=self.colors['secondary']
                    )
                    category_label.grid(row=0, column=0, sticky="w")

                # 时间信息
                scheduled_date = review.get('scheduled_date', '')
                if hasattr(scheduled_date, 'strftime'):
                    time_str = scheduled_date.strftime('%H:%M')
                elif isinstance(scheduled_date, str) and ' ' in scheduled_date:
                    time_str = scheduled_date.split(' ')[1][:5]  # 提取时间部分
                else:
                    time_str = '未知时间'

                time_label = ctk.CTkLabel(
                    meta_frame,
                    text=f"⏰ {time_str}",
                    font=ctk.CTkFont(size=11),
                    text_color="#666666"
                )
                time_label.grid(row=0, column=1, sticky="w", padx=(20, 0))

                # 内容预览
                content_preview = knowledge_item.content
                if content_preview:
                    if len(content_preview) > 120:
                        content_preview = content_preview[:120] + "..."
                    
                    content_label = ctk.CTkLabel(
                        content_frame,
                        text=content_preview,
                        font=ctk.CTkFont(size=12),
                        text_color="#555555",
                        wraplength=400,
                        justify="left"
                    )
                    content_label.grid(row=2, column=0, sticky="w", pady=(0, 12))

                # 操作按钮区域
                button_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
                button_frame.grid(row=3, column=0, sticky="ew")

                # 按钮样式
                btn_style = {
                    'width': 80,
                    'height': 30,
                    'font': ctk.CTkFont(size=11, weight="bold"),
                    'corner_radius': 8
                }

                if not is_completed:
                    # 开始复习按钮
                    review_btn = ctk.CTkButton(
                        button_frame,
                        text="🎯 开始复习",
                        command=lambda r=review: self.start_review(r),
                        fg_color=self.colors['today'],
                        hover_color='#E55A4D',
                        **btn_style
                    )
                    review_btn.pack(side="left", padx=(0, 8))
                else:
                    # 查看详情按钮
                    detail_btn = ctk.CTkButton(
                        button_frame,
                        text="👀 查看详情",
                        command=lambda: self.show_item_detail(knowledge_item),
                        fg_color=self.colors['primary'],
                        hover_color='#1B6B93',
                        **btn_style
                    )
                    detail_btn.pack(side="left", padx=(0, 8))

                print(f"✅ 成功创建复习项目: {knowledge_item.title} - ui.py:705")
                return card

            except Exception as e:
                print(f"❌ 创建复习项目时出错: {e} - ui.py:709")
                return None
            finally:
                session.close()

        except Exception as e:
            print(f"❌ 处理复习项目时出错: {e} - ui.py:715")
            return None

    def show_item_detail(self, knowledge_item):
        """显示知识点详情"""
        try:
            from src.knowledge.ui import KnowledgeItemDetailDialog
            
            # 将知识点对象转换为字典格式
            item_dict = {
                'id': knowledge_item.id,
                'title': knowledge_item.title,
                'content': knowledge_item.content,
                'category': knowledge_item.category,
                'created_at': knowledge_item.created_at.strftime("%Y-%m-%d %H:%M") if hasattr(knowledge_item.created_at, 'strftime') else '未知时间',
                'review_status': '✅ 已完成复习',
                'is_today_review': False
            }
            
            KnowledgeItemDetailDialog(self, item_dict)
        except Exception as e:
            messagebox.showerror("错误", f"打开详情失败: {str(e)}")

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
                self.current_user,
                self.scheduler_service,
                self.db_manager,
                self.load_today_reviews,
            )
        except Exception as e:
            messagebox.showerror("错误", f"打开复习对话框失败: {str(e)}")