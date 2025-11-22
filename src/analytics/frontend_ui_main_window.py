# -*- codeing =utf-8 -*-
# @Time : 2025/11/22 18:12
# @Author: Muncy
# @File : frontend_ui_main_window.py.py
# @Software: PyCharm
import customtkinter as ctk
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