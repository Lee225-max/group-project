# -*- codeing =utf-8 -*-
# @Time : 2025/11/24 0:54
# @Author: Muncy
# @File : ui.py
# @Software: PyCharm
"""
统计分析界面 - 成员D负责
"""

import customtkinter as ctk
from tkinter import messagebox
import threading
from PIL import Image, ImageTk
import base64
from io import BytesIO

from .service import AnalyticsService


class AnalyticsFrame(ctk.CTkFrame):
    """统计分析界面"""

    def __init__(self, parent, current_user, db_manager):
        super().__init__(parent)
        self.current_user = current_user
        self.analytics_service = AnalyticsService(db_manager)

        self.stats_data = None
        self.chart_image = None

        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        """创建界面组件"""
        # 标题
        title_label = ctk.CTkLabel(
            self,
            text="学习统计分析",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=20)

        # 创建选项卡
        self.create_tabview()

    def create_tabview(self):
        """创建选项卡视图"""
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=10)

        # 添加选项卡
        self.tabview.add("学习概览")
        self.tabview.add("趋势分析")
        self.tabview.add("分类统计")
        self.tabview.add("复习效果")

        # 设置各选项卡内容
        self.setup_overview_tab()
        self.setup_trend_tab()
        self.setup_category_tab()
        self.setup_effectiveness_tab()

    def setup_overview_tab(self):
        """设置学习概览选项卡"""
        tab = self.tabview.tab("学习概览")

        # 统计卡片容器
        cards_frame = ctk.CTkFrame(tab)
        cards_frame.pack(fill="x", padx=10, pady=10)

        # 创建统计卡片
        self.stats_cards = {}
        stats_config = [
            ("总知识点", "total_knowledge_items", "📚", "#4CAF50"),
            ("今日复习", "today_review_count", "⏰", "#2196F3"),
            ("已完成复习", "completed_reviews", "✅", "#FF9800"),
            ("记忆保持率", "retention_rate", "🧠", "#9C27B0"),
            ("连续学习", "streak_days", "🔥", "#F44336"),
            ("学习效率", "learning_efficiency", "📊", "#00BCD4")
        ]

        # 创建2行3列的网格布局
        for i, (title, key, icon, color) in enumerate(stats_config):
            row, col = divmod(i, 3)
            card_frame, value_label = self.create_stat_card(cards_frame, title, "加载中...", icon, color)
#            row = i // 3
#            col = i % 3
 #           card = self.create_stat_card(cards_frame, title, "加载中...", icon, color)
#            card.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            card_frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            #self.stats_cards[key] = card
            self.stats_cards[key] = value_label
            cards_frame.grid_columnconfigure(col, weight=1)

            # 设置网格权重
        cards_frame.grid_rowconfigure(0, weight=1)
        cards_frame.grid_rowconfigure(1, weight=1)
 #       cards_frame.grid_columnconfigure(col, weight=1)
  #      cards_frame.grid_rowconfigure(row, weight=1)

        # 刷新按钮
        refresh_btn = ctk.CTkButton(
            tab,
            text="刷新数据",
            command=self.load_data,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        refresh_btn.pack(pady=10)

    def create_stat_card(self, parent, title, value, icon, color):
        """创建统计卡片"""
        card = ctk.CTkFrame(parent, border_width=2, border_color=color)

        # 图标和标题
        header_frame = ctk.CTkFrame(card, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=(10, 5))

        ctk.CTkLabel(
            header_frame,
            text=f"{icon} {title}",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left")

        # 数值显示
        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=color
        )
        value_label.pack(pady=10)

        return card, value_label#value_label

    def setup_trend_tab(self):
        """设置趋势分析选项卡"""
        tab = self.tabview.tab("趋势分析")

        # 图表容器
        self.chart_frame = ctk.CTkFrame(tab)
        self.chart_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # 加载提示
        self.chart_label = ctk.CTkLabel(
            self.chart_frame,
            text="图表加载中...",
            font=ctk.CTkFont(size=16)
        )
        self.chart_label.pack(expand=True)

    def setup_category_tab(self):
        """设置分类统计选项卡"""
        tab = self.tabview.tab("分类统计")

        # 分类统计容器
        self.category_frame = ctk.CTkFrame(tab)
        self.category_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.category_label = ctk.CTkLabel(
            self.category_frame,
            text="分类数据加载中...",
            font=ctk.CTkFont(size=16)
        )
        self.category_label.pack(expand=True)

    def setup_effectiveness_tab(self):
        """设置复习效果选项卡"""
        tab = self.tabview.tab("复习效果")

        # 效果统计容器
        self.effectiveness_frame = ctk.CTkFrame(tab)
        self.effectiveness_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.effectiveness_label = ctk.CTkLabel(
            self.effectiveness_frame,
            text="效果数据加载中...",
            font=ctk.CTkFont(size=16)
        )
        self.effectiveness_label.pack(expand=True)

    def load_data(self):
        """加载数据"""
        # 显示加载状态
        for card in self.stats_cards.values():
            card.configure(text="加载中...")

        # 在新线程中加载数据
        thread = threading.Thread(target=self._load_data_thread)
        thread.daemon = True
        thread.start()

    def _load_data_thread(self):
        """在新线程中加载数据"""
        try:
            # 获取统计数据
            self.stats_data = self.analytics_service.get_user_stats(self.current_user.id)

            # 获取图表数据
            self.chart_image = self.analytics_service.create_learning_chart(self.current_user.id)

            # 获取分类统计
            self.category_stats = self.analytics_service.get_category_stats(self.current_user.id)

            # 获取复习效果
            self.effectiveness_stats = self.analytics_service.get_review_effectiveness(self.current_user.id)

            # 在主线程中更新UI
            self.after(0, self._update_ui)

        except Exception as err:#e
            self.after(0,lambda message=str(err): messagebox.showerror("错误", f"加载数据失败: {message}"))
            #self.after(0, lambda: messagebox.showerror("错误", f"加载数据失败: {str(e)}"))

    def _update_ui(self):
        """更新UI显示"""
        if self.stats_data:
            self._update_stats_cards()

        if self.chart_image:
            self._display_chart()

        if self.category_stats:
            self._update_category_display()

        if self.effectiveness_stats:
            self._update_effectiveness_display()

    def _update_stats_cards(self):
        """更新统计卡片"""
        display_config = {
            "total_knowledge_items": lambda x: f"{x} 个",
            "today_review_count": lambda x: f"{x} 个",
            "completed_reviews": lambda x: f"{x} 次",
            "retention_rate": lambda x: f"{x}%",
            "streak_days": lambda x: f"{x} 天",
            "learning_efficiency": lambda x: f"{x}%"
        }

        for key, card in self.stats_cards.items():
            if key in self.stats_data:
                value = self.stats_data[key]
                formatter = display_config.get(key, str)
                card.configure(text=formatter(value))

    def _display_chart(self):
        """显示图表"""
        # 清除原有内容
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        try:
            # 解码base64图片
            image_data = base64.b64decode(self.chart_image.split(',')[1])
            image = Image.open(BytesIO(image_data))

            # 调整图片大小以适应窗口
            width, height = image.size
            new_width = min(800, width)
            new_height = int(height * new_width / width)
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # 转换为PhotoImage
            photo = ImageTk.PhotoImage(image)

            # 创建标签显示图片
            chart_label = ctk.CTkLabel(self.chart_frame, image=photo, text="")
            chart_label.image = photo  # 保持引用
            chart_label.pack(expand=True)

        except Exception as e:
            ctk.CTkLabel(
                self.chart_frame,
                text=f"图表显示失败: {str(e)}",
                font=ctk.CTkFont(size=14)
            ).pack(expand=True)

    def _update_category_display(self):
        """更新分类统计显示"""
        # 清除原有内容
        for widget in self.category_frame.winfo_children():
            widget.destroy()

        if not self.category_stats:
            ctk.CTkLabel(
                self.category_frame,
                text="暂无分类数据",
                font=ctk.CTkFont(size=14)
            ).pack(expand=True)
            return

        # 创建分类统计列表
        scrollable_frame = ctk.CTkScrollableFrame(self.category_frame)
        scrollable_frame.pack(fill="both", expand=True)

        # 按数量排序
        sorted_categories = sorted(
            self.category_stats.items(),
            key=lambda x: x[1],
            reverse=True
        )

        for category, count in sorted_categories:
            category_frame = ctk.CTkFrame(scrollable_frame)
            category_frame.pack(fill="x", padx=5, pady=2)

            ctk.CTkLabel(
                category_frame,
                text=category,
                font=ctk.CTkFont(size=14)
            ).pack(side="left", padx=10)

            ctk.CTkLabel(
                category_frame,
                text=f"{count} 个知识点",
                font=ctk.CTkFont(size=14, weight="bold")
            ).pack(side="right", padx=10)

    def _update_effectiveness_display(self):
        """更新复习效果显示"""
        # 清除原有内容
        for widget in self.effectiveness_frame.winfo_children():
            widget.destroy()

        if not self.effectiveness_stats:
            ctk.CTkLabel(
                self.effectiveness_frame,
                text="暂无复习效果数据",
                font=ctk.CTkFont(size=14)
            ).pack(expand=True)
            return

        # 创建效果统计显示
        scrollable_frame = ctk.CTkScrollableFrame(self.effectiveness_frame)
        scrollable_frame.pack(fill="both", expand=True)

        effectiveness_labels = {
            "优秀": "🟢",
            "良好": "🟡",
            "一般": "🟠",
            "较差": "🔴",
            "困难": "⚫"
        }

        for level, percentage in self.effectiveness_stats.items():
            if level in effectiveness_labels:
                effect_frame = ctk.CTkFrame(scrollable_frame)
                effect_frame.pack(fill="x", padx=5, pady=2)

                ctk.CTkLabel(
                    effect_frame,
                    text=f"{effectiveness_labels[level]} {level}",
                    font=ctk.CTkFont(size=14)
                ).pack(side="left", padx=10)

                # 创建进度条
                progress_bar = ctk.CTkProgressBar(effect_frame)
                progress_bar.pack(side="left", padx=10, fill="x", expand=True)
                progress_bar.set(percentage / 100)

                ctk.CTkLabel(
                    effect_frame,
                    text=f"{percentage:.1f}%",
                    font=ctk.CTkFont(size=12)
                ).pack(side="right", padx=10)