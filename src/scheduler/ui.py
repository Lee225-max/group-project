<<<<<<< HEAD
# -*- codeing =utf-8 -*-
# @Time : 2025/11/18 13:44
# @Author: Muncy
# @File : ui.py.py
# @Software: PyCharm
"""
复习调度界面 - 成员C实现
"""

import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from .service import SchedulerService
from src.database.models import ReviewSchedule, KnowledgeItem


class ReviewSchedulerFrame(ctk.CTkFrame):
    """今日复习计划界面"""

    def __init__(self, parent, current_user, db_manager):
        super().__init__(parent)
        self.current_user = current_user
        self.scheduler_service = SchedulerService(db_manager)
        self.db_manager = db_manager

        self.create_widgets()
        self.load_today_reviews()

    def create_widgets(self):
        """创建界面组件"""
        # 顶部工具栏
        toolbar = ctk.CTkFrame(self)
        toolbar.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            toolbar,
            text="今日复习计划",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(side="left")

        # 统计信息
        self.stats_label = ctk.CTkLabel(
            toolbar,
            text="加载中...",
            font=ctk.CTkFont(size=14)
        )
        self.stats_label.pack(side="right")

        # 刷新按钮
        refresh_btn = ctk.CTkButton(
            toolbar,
            text="刷新",
            command=self.load_today_reviews,
            width=80
        )
        refresh_btn.pack(side="right", padx=(10, 0))

        # 内容区域
        content_frame = ctk.CTkFrame(self)
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # 复习列表容器
        self.review_list_frame = ctk.CTkScrollableFrame(content_frame)
        self.review_list_frame.pack(fill="both", expand=True)

        # 空状态提示
        self.empty_label = ctk.CTkLabel(
            self.review_list_frame,
            text="今日没有复习计划\n快去添加一些知识点吧！",
            font=ctk.CTkFont(size=16),
            text_color="gray"
        )

    def load_today_reviews(self):
        """加载今日复习计划"""
        # 清空现有内容
        for widget in self.review_list_frame.winfo_children():
            widget.destroy()

        try:
            today_reviews = self.scheduler_service.get_today_reviews(self.current_user.id)

            if not today_reviews:
                self.empty_label.pack(expand=True, pady=50)
                self.stats_label.configure(text="今日无复习任务")
                return

            # 更新统计信息
            completed = sum(1 for review in today_reviews if review.completed)
            total = len(today_reviews)
            self.stats_label.configure(text=f"进度: {completed}/{total}")

            # 显示复习项目
            for review in today_reviews:
                self.create_review_item(review)

        except Exception as e:
            messagebox.showerror("错误", f"加载复习计划失败: {str(e)}")

    def create_review_item(self, review: ReviewSchedule):
        """创建复习项目UI"""
        session = self.db_manager.get_session()
        try:
            # 获取知识点信息
            knowledge_item = session.query(KnowledgeItem).filter(
                KnowledgeItem.id == review.knowledge_item_id
            ).first()

            if not knowledge_item:
                return

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
                anchor="w"
            )
            title_label.pack(anchor="w")

            if knowledge_item.category:
                category_label = ctk.CTkLabel(
                    content_frame,
                    text=f"分类: {knowledge_item.category}",
                    font=ctk.CTkFont(size=12),
                    text_color="gray",
                    anchor="w"
                )
                category_label.pack(anchor="w", pady=(2, 0))

            # 复习内容预览
            content_preview = knowledge_item.content[:100] + "..." if len(
                knowledge_item.content) > 100 else knowledge_item.content
            content_label = ctk.CTkLabel(
                content_frame,
                text=content_preview,
                font=ctk.CTkFont(size=12),
                anchor="w",
                justify="left"
            )
            content_label.pack(anchor="w", pady=(5, 0), fill="x")

            # 复习信息
            info_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
            info_frame.pack(fill="x", pady=(10, 0))

            stage_label = ctk.CTkLabel(
                info_frame,
                text=f"第 {review.review_stage + 1} 次复习",
                font=ctk.CTkFont(size=12),
                text_color="blue"
            )
            stage_label.pack(side="left")

            time_label = ctk.CTkLabel(
                info_frame,
                text=f"计划时间: {review.scheduled_date.strftime('%H:%M')}",
                font=ctk.CTkFont(size=12),
                text_color="gray"
            )
            time_label.pack(side="left", padx=(20, 0))

            # 操作按钮
            button_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
            button_frame.pack(fill="x", pady=(10, 0))

            if not review.completed:
                # 开始复习按钮
                review_btn = ctk.CTkButton(
                    button_frame,
                    text="开始复习",
                    command=lambda r=review: self.start_review(r),
                    fg_color="#28a745",
                    hover_color="#218838"
                )
                review_btn.pack(side="left")
            else:
                # 已完成状态
                completed_label = ctk.CTkLabel(
                    button_frame,
                    text="✅ 已完成",
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color="green"
                )
                completed_label.pack(side="left")

            # 分隔线
            separator = ctk.CTkFrame(item_frame, height=1, fg_color="lightgray")
            separator.pack(fill="x", padx=10)

        finally:
            session.close()

    def start_review(self, review: ReviewSchedule):
        """开始复习"""
        ReviewDialog(self, review, self.scheduler_service, self.db_manager, self.load_today_reviews)
=======
"""
复习调度器界面 - 成员C负责
"""

import customtkinter as ctk
from datetime import datetime, timedelta
>>>>>>> ceab570 (feat: add ReviewDialog for knowledge review)


class ReviewDialog(ctk.CTkToplevel):
    """复习对话框"""

<<<<<<< HEAD
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
        self.load_knowledge_item()
=======
    def __init__(self, parent, item, user, db_manager):
        super().__init__(parent)
        self.item = item
        self.user = user
        self.db_manager = db_manager
        
        self.title(f"复习: {item.title}")
        self.geometry("500x400")
        self.resizable(False, False)
        
>>>>>>> ceab570 (feat: add ReviewDialog for knowledge review)
        self.create_widgets()
        self.center_window()

    def center_window(self):
        """居中显示窗口"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
<<<<<<< HEAD
        self.geometry(f'+{x}+{y}')

    def load_knowledge_item(self):
        """加载知识点内容"""
        session = self.db_manager.get_session()
        try:
            self.knowledge_item = session.query(KnowledgeItem).filter(
                KnowledgeItem.id == self.review.knowledge_item_id
            ).first()
        finally:
            session.close()

    def create_widgets(self):
        """创建对话框组件"""
        if not self.knowledge_item:
            messagebox.showerror("错误", "知识点不存在")
            self.destroy()
            return

=======
        self.geometry(f"+{x}+{y}")

    def create_widgets(self):
        """创建对话框组件"""
>>>>>>> ceab570 (feat: add ReviewDialog for knowledge review)
        # 主容器
        main_container = ctk.CTkFrame(self)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

<<<<<<< HEAD
        # 标题
        title_label = ctk.CTkLabel(
            main_container,
            text=self.knowledge_item.title,
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=(0, 10))

        # 分类信息
        if self.knowledge_item.category:
            category_label = ctk.CTkLabel(
                main_container,
                text=f"分类: {self.knowledge_item.category}",
                font=ctk.CTkFont(size=14),
                text_color="gray"
            )
            category_label.pack(pady=(0, 20))

        # 内容区域
        content_frame = ctk.CTkFrame(main_container)
        content_frame.pack(fill="both", expand=True, pady=10)

        # 内容标签
        ctk.CTkLabel(
            content_frame,
            text="知识点内容:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", pady=(10, 5))

        # 内容显示
        content_text = ctk.CTkTextbox(
            content_frame,
            wrap="word",
            font=ctk.CTkFont(size=12)
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
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", pady=(10, 5))

        # 回忆程度滑块
        slider_frame = ctk.CTkFrame(evaluation_frame, fg_color="transparent")
        slider_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(slider_frame, text="完全忘记", font=ctk.CTkFont(size=12)).pack(side="left")

        self.recall_slider = ctk.CTkSlider(
            slider_frame,
            from_=0,
            to=1,
            number_of_steps=10,
            command=self.on_slider_change
        )
        self.recall_slider.pack(side="left", fill="x", expand=True, padx=10)
        self.recall_slider.set(0.5)  # 默认值

        ctk.CTkLabel(slider_frame, text="完全记得", font=ctk.CTkFont(size=12)).pack(side="left")

        # 分数显示
        self.score_label = ctk.CTkLabel(
            evaluation_frame,
            text="回忆分数: 50%",
            font=ctk.CTkFont(size=12),
            text_color="blue"
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
            font=ctk.CTkFont(size=14, weight="bold")
        )
        complete_btn.pack(side="left", padx=(0, 10), expand=True)

        # 取消按钮
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="稍后复习",
            command=self.destroy,
            height=40,
            fg_color="gray"
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
            success = self.scheduler_service.complete_review(
                self.review.id,
                self.recall_score
            )

            if success:
                messagebox.showinfo("成功", "复习完成！")
                self.refresh_callback()
                self.destroy()
            else:
                messagebox.showerror("错误", "复习完成失败")

        except Exception as e:
            messagebox.showerror("错误", f"复习完成失败: {str(e)}")
=======
        # 知识点标题
        title_label = ctk.CTkLabel(
            main_container,
            text=self.item.title,
            font=ctk.CTkFont(size=16, weight="bold"),
            wraplength=400,
        )
        title_label.pack(anchor="w", pady=(0, 10))

        # 分类信息
        if self.item.category:
            category_label = ctk.CTkLabel(
                main_container,
                text=f"分类: {self.item.category}",
                font=ctk.CTkFont(size=12),
            )
            category_label.pack(anchor="w", pady=(0, 10))

        # 内容显示区域
        content_label = ctk.CTkLabel(
            main_container, text="内容:", font=ctk.CTkFont(size=14, weight="bold")
        )
        content_label.pack(anchor="w", pady=(0, 5))

        content_frame = ctk.CTkFrame(main_container)
        content_frame.pack(fill="both", expand=True, pady=(0, 15))

        content_text = ctk.CTkTextbox(content_frame, wrap="word")
        content_text.pack(fill="both", expand=True, padx=10, pady=10)
        content_text.insert("1.0", self.item.content)
        content_text.configure(state="disabled")

        # 复习难度选择
        difficulty_frame = ctk.CTkFrame(main_container)
        difficulty_frame.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(
            difficulty_frame, text="复习难度:", font=ctk.CTkFont(size=12, weight="bold")
        ).pack(anchor="w", pady=(0, 5))

        self.difficulty_var = ctk.StringVar(value="medium")

        difficulties = [
            ("困难", "hard"),
            ("中等", "medium"),
            ("简单", "easy"),
        ]

        for text, value in difficulties:
            ctk.CTkRadioButton(
                difficulty_frame,
                text=text,
                variable=self.difficulty_var,
                value=value,
            ).pack(side="left", padx=(0, 10))

        # 按钮框架
        button_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        button_frame.pack(fill="x")

        ctk.CTkButton(
            button_frame,
            text="完成复习",
            fg_color="#5cb85c",
            hover_color="#4cae4c",
            command=self.complete_review,
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(button_frame, text="稍后提醒", command=self.snooze_review).pack(
            side="left", padx=(0, 10)
        )

        ctk.CTkButton(button_frame, text="取消", command=self.destroy).pack(side="left")

    def complete_review(self):
        """完成复习"""
        # 这里应该调用调度算法更新下一次复习时间
        try:
            # 模拟更新复习记录
            next_review = self.calculate_next_review()
            
            # 在实际实现中，这里应该调用scheduler服务来更新复习计划
            # self.scheduler_service.update_review_schedule(...)
            
            from tkinter import messagebox
            messagebox.showinfo("成功", f"复习完成！下次复习时间: {next_review}")
            self.destroy()
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("错误", f"复习记录更新失败: {str(e)}")

    def snooze_review(self):
        """稍后提醒"""
        # 设置一段时间后再次提醒
        from tkinter import messagebox
        messagebox.showinfo("提示", "将在1小时后再次提醒您复习")
        self.destroy()

    def calculate_next_review(self):
        """计算下一次复习时间（基于SM-2算法简化版）"""
        difficulty = self.difficulty_var.get()
        
        # 简单的间隔计算（实际应该基于SM-2算法）
        intervals = {
            "easy": timedelta(days=7),
            "medium": timedelta(days=3),
            "hard": timedelta(days=1),
        }
        
        next_review = datetime.now() + intervals.get(difficulty, timedelta(days=3))
        return next_review.strftime("%Y-%m-%d %H:%M")
>>>>>>> ceab570 (feat: add ReviewDialog for knowledge review)
