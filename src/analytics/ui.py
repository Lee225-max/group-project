# -*- codeing =utf-8 -*-
# @Time : 2025/11/22 18:12
# @Author: Muncy
# @File : ui.py
# @Software: PyCharm
'''import customtkinter as ctk
from .login_window import LoginWindow
from .knowledge_window import KnowledgeWindow
from .analytics_window import AnalyticsWindow


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("智能复习闹钟")
        self.geometry("1000x700")

        # 设置主题
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.api_client = None  # API客户端实例
        self.current_user = None

        self.create_widgets()

    def create_widgets(self):
        # 创建左侧导航栏
        self.navigation_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(4, weight=1)

        # 导航按钮
        self.knowledge_button = ctk.CTkButton(
            self.navigation_frame,
            text="知识管理",
            command=self.show_knowledge_tab
        )
        self.knowledge_button.grid(row=1, column=0, padx=20, pady=10)

        self.review_button = ctk.CTkButton(
            self.navigation_frame,
            text="今日复习",
            command=self.show_review_tab
        )
        self.review_button.grid(row=2, column=0, padx=20, pady=10)

        self.analytics_button = ctk.CTkButton(
            self.navigation_frame,
            text="学习统计",
            command=self.show_analytics_tab
        )
        self.analytics_button.grid(row=3, column=0, padx=20, pady=10)

        # 主内容区域
        self.main_frame = ctk.CTkFrame(self, corner_radius=0)
        self.main_frame.grid(row=0, column=1, sticky="nsew")
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # 显示登录窗口
        self.show_login()

    def show_login(self):
        # 清理主内容区域
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        LoginWindow(self.main_frame, self.on_login_success)

    def on_login_success(self, user_data, api_client):
        self.current_user = user_data
        self.api_client = api_client
        self.show_knowledge_tab()

    def show_knowledge_tab(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        KnowledgeWindow(self.main_frame, self.api_client)

    def show_analytics_tab(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        AnalyticsWindow(self.main_frame, self.api_client)


# frontend/api_client.py
import requests
import json


class APIClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.token = None

    def login(self, username: str, password: str) -> bool:
        try:
            response = requests.post(
                f"{self.base_url}/auth/login",
                json={"username": username, "password": password}
            )
            if response.status_code == 200:
                self.token = response.json().get("access_token")
                return True
        except requests.RequestException:
            pass
        return False

    def get_knowledge_items(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get(
            f"{self.base_url}/knowledge/items",
            headers=headers
        )
        return response.json() if response.status_code == 200 else []
'''
"""
统计分析界面
"""
import customtkinter as ctk
from ..stats import ReviewStatsAnalyzer
from ..visualization import AnalyticsVisualization
import tkinter as tk
from tkinter import ttk


class AnalyticsFrame(ctk.CTkFrame):
    """统计分析界面框架"""

    def __init__(self, parent, current_user, db_manager):
        super().__init__(parent)
        self.current_user = current_user
        self.db_manager = db_manager
        self.stats_analyzer = ReviewStatsAnalyzer(db_manager)
        self.visualizer = AnalyticsVisualization(db_manager)

        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        """设置界面布局"""
        # 标题
        title_label = ctk.CTkLabel(
            self,
            text="📊 学习统计分析",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=20)

        # 创建选项卡
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=10)

        # 添加选项卡
        self.overview_tab = self.tabview.add("概览")
        self.stats_tab = self.tabview.add("详细统计")
        self.charts_tab = self.tabview.add("图表分析")

        self.setup_overview_tab()
        self.setup_stats_tab()
        self.setup_charts_tab()

    def setup_overview_tab(self):
        """设置概览选项卡"""
        # 整体统计卡片
        stats_frame = ctk.CTkFrame(self.overview_tab)
        stats_frame.pack(fill="x", padx=20, pady=20)

        ctk.CTkLabel(
            stats_frame,
            text="📈 整体学习统计",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=10)

        # 统计指标网格
        self.stats_grid = ctk.CTkFrame(stats_frame)
        self.stats_grid.pack(fill="x", padx=20, pady=10)

        # 图表预览
        chart_preview_frame = ctk.CTkFrame(self.overview_tab)
        chart_preview_frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            chart_preview_frame,
            text="📋 学习趋势预览",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=10)

        self.chart_label = ctk.CTkLabel(chart_preview_frame, text="图表加载中...")
        self.chart_label.pack(expand=True)

    def setup_stats_tab(self):
        """设置详细统计选项卡"""
        # 创建滚动框架
        self.stats_scrollframe = ctk.CTkScrollableFrame(self.stats_tab)
        self.stats_scrollframe.pack(fill="both", expand=True, padx=20, pady=20)

        # 这里将添加详细的统计表格
        self.stats_content_label = ctk.CTkLabel(
            self.stats_scrollframe,
            text="详细统计数据加载中...",
            font=ctk.CTkFont(size=14)
        )
        self.stats_content_label.pack(pady=20)

    def setup_charts_tab(self):
        """设置图表分析选项卡"""
        # 图表控制按钮
        controls_frame = ctk.CTkFrame(self.charts_tab)
        controls_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkButton(
            controls_frame,
            text="🔄 刷新图表",
            command=self.refresh_charts,
            width=120
        ).pack(side="left", padx=10)

        # 图表显示区域
        self.charts_content_frame = ctk.CTkFrame(self.charts_tab)
        self.charts_content_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.charts_label = ctk.CTkLabel(
            self.charts_content_frame,
            text="图表生成中...",
            font=ctk.CCTkFont(size=14)
        )
        self.charts_label.pack(expand=True)

    def load_data(self):
        """加载统计数据"""
        try:
            # 获取整体统计
            self.overall_stats = self.stats_analyzer.get_overall_review_stats(
                self.current_user.id
            )
            self.mastery_stats = self.stats_analyzer.get_knowledge_mastery(
                self.current_user.id
            )

            self.update_overview_display()
            self.update_stats_display()
            self.update_charts_display()

        except Exception as e:
            self.show_error(f"加载统计数据失败: {e}")

    def update_overview_display(self):
        """更新概览显示"""
        # 清除现有内容
        for widget in self.stats_grid.winfo_children():
            widget.destroy()

        # 创建统计卡片
        stats_data = [
            ("总复习计划", f"{self.overall_stats['total_schedules']} 个", "📚"),
            ("已完成", f"{self.overall_stats['completed_schedules']} 个", "✅"),
            ("完成率", f"{self.overall_stats['completion_rate']}%", "📊"),
            ("近7天复习", f"{self.overall_stats['recent_7d_reviews']} 次", "📅"),
            ("平均效果", f"{self.overall_stats['avg_effectiveness']} 分", "⭐"),
        ]

        # 2列布局
        for i, (title, value, icon) in enumerate(stats_data):
            row = i // 2
            col = i % 2

            stat_card = ctk.CTkFrame(self.stats_grid, width=200, height=80)
            stat_card.grid(row=row, column=col, padx=10, pady=10, sticky="ew")
            stat_card.grid_propagate(False)

            # 图标和数值
            ctk.CTkLabel(
                stat_card,
                text=f"{icon} {value}",
                font=ctk.CTkFont(size=16, weight="bold")
            ).pack(pady=(10, 0))

            # 标题
            ctk.CTkLabel(
                stat_card,
                text=title,
                font=ctk.CTkFont(size=12)
            ).pack(pady=(0, 10))

    def update_stats_display(self):
        """更新详细统计显示"""
        # 清除现有内容
        for widget in self.stats_scrollframe.winfo_children():
            widget.destroy()

        # 知识点掌握情况表格
        ctk.CTkLabel(
            self.stats_scrollframe,
            text="📋 知识点掌握情况",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", pady=(0, 10))

        if self.mastery_stats:
            for item in self.mastery_stats:
                item_frame = ctk.CTkFrame(self.stats_scrollframe)
                item_frame.pack(fill="x", pady=5)

                ctk.CTkLabel(
                    item_frame,
                    text=item["title"],
                    font=ctk.CTkFont(size=12, weight="bold")
                ).pack(side="left", padx=10)

                ctk.CTkLabel(
                    item_frame,
                    text=f"复习次数: {item['review_count']}",
                    font=ctk.CTkFont(size=11)
                ).pack(side="left", padx=20)

                ctk.CTkLabel(
                    item_frame,
                    text=f"平均效果: {item['avg_effect']}",
                    font=ctk.CTkFont(size=11)
                ).pack(side="left", padx=20)
        else:
            ctk.CTkLabel(
                self.stats_scrollframe,
                text="暂无复习记录",
                font=ctk.CTkFont(size=12)
            ).pack(pady=20)

    def update_charts_display(self):
        """更新图表显示"""
        try:
            # 生成图表
            chart_image = self.visualizer.create_memory_statistics_chart(
                self.current_user.id
            )

            # 这里需要将base64图像显示在界面上
            # 由于CTk不支持直接显示base64，暂时显示文字提示
            self.charts_label.configure(
                text=f"图表已生成 (Base64数据长度: {len(chart_image)})"
            )

        except Exception as e:
            self.charts_label.configure(text=f"图表生成失败: {e}")

    def refresh_charts(self):
        """刷新图表"""
        self.update_charts_display()

    def show_error(self, message):
        """显示错误信息"""
        error_label = ctk.CTkLabel(
            self,
            text=f"❌ {message}",
            text_color="red",
            font=ctk.CTkFont(size=12)
        )
        error_label.pack(pady=10)