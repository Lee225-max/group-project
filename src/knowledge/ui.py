# -*- codeing =utf-8 -*-
# @Time : 2025/11/24 19:58
# @Author: Muncy
# @File : ui.py
# @Software: PyCharm
"""
知识管理界面 - 美化版 + 今日复习联动功能
"""

import customtkinter as ctk
from tkinter import messagebox
from src.knowledge.service import KnowledgeService
from src.scheduler.service import SchedulerService


class KnowledgeManagementFrame(ctk.CTkFrame):
    """知识管理界面 - 支持今日复习联动"""

    def __init__(self, parent, current_user, db_manager):
        super().__init__(parent)
        self.current_user = current_user
        self.knowledge_service = KnowledgeService(db_manager)
        self.db_manager = db_manager
        self.scheduler_service = SchedulerService(db_manager)
        self.show_only_today = False  # 今日复习筛选状态

        # 颜色配置
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

        self.create_widgets()
        self.load_knowledge_items()
        self.update_today_review_count()

    def create_widgets(self):
        """创建界面组件 - 纵向紧凑布局"""
        # 配置网格布局
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # 主控制栏（包含所有控制元素）
        control_frame = ctk.CTkFrame(self, fg_color=self.colors['light'], corner_radius=10)
        control_frame.grid(row=0, column=0, sticky="ew", padx=8, pady=5)
        control_frame.grid_columnconfigure(1, weight=1)

        # 第一行：标题和主要按钮
        header_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, columnspan=3, sticky="ew", padx=10, pady=5)
        header_frame.grid_columnconfigure(1, weight=1)

        # 标题
        title_label = ctk.CTkLabel(
            header_frame,
            text="📚 知识管理",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors['primary']
        )
        title_label.grid(row=0, column=0, sticky="w")

        # 今日复习状态
        self.today_review_label = ctk.CTkLabel(
            header_frame,
            text="今日需复习：加载中...",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=self.colors['dark']
        )
        self.today_review_label.grid(row=0, column=1, sticky="w", padx=15)

        # 添加知识点按钮
        add_btn = ctk.CTkButton(
            header_frame,
            text="➕ 添加",
            command=self.add_knowledge_item,
            width=70,
            height=26,
            fg_color=self.colors['success'],
            hover_color='#139C8B',
            font=ctk.CTkFont(size=10, weight="bold")
        )
        add_btn.grid(row=0, column=2, sticky="e")

        # 第二行：搜索和筛选
        action_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        action_frame.grid(row=1, column=0, columnspan=3, sticky="ew", padx=10, pady=(0, 5))
        action_frame.grid_columnconfigure(0, weight=1)

        # 搜索框
        self.search_entry = ctk.CTkEntry(
            action_frame,
            placeholder_text="🔍 搜索知识点...",
            height=30,
            font=ctk.CTkFont(size=11)
        )
        self.search_entry.grid(row=0, column=0, sticky="ew")
        self.search_entry.bind("<KeyRelease>", self.on_search)

        # 筛选按钮
        self.filter_today_btn = ctk.CTkButton(
            action_frame,
            text="📅 筛选今日",
            command=self.toggle_today_filter,
            width=70,
            height=26,
            fg_color=self.colors['primary'],
            hover_color='#1B6B93',
            font=ctk.CTkFont(size=10, weight="bold")
        )
        self.filter_today_btn.grid(row=0, column=1, sticky="e", padx=(10, 0))

        # 知识列表容器 - 紧贴控制栏
        self.list_container = ctk.CTkFrame(self, corner_radius=10)
        self.list_container.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))
        self.list_container.grid_columnconfigure(0, weight=1)
        self.list_container.grid_rowconfigure(0, weight=1)

        # 创建列表框架
        self.create_list_frame()

    def create_list_frame(self):
        """创建知识列表框架"""
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

    def toggle_today_filter(self):
        """切换今日复习筛选"""
        if self.show_only_today:
            # 取消筛选
            self.show_only_today = False
            self.filter_today_btn.configure(
                text="📅 筛选今日",
                fg_color=self.colors['primary'],
                hover_color='#1B6B93'
            )
            self.update_today_review_count()
        else:
            # 应用筛选
            self.show_only_today = True
            self.filter_today_btn.configure(
                text="❌ 取消筛选",
                fg_color=self.colors['warning'],
                hover_color='#D97B00'
            )
            self.today_review_label.configure(text="🎯 正在显示今日复习")

        self.load_knowledge_items()

    def update_today_review_count(self):
        """更新今日复习计数"""
        try:
            today_count = self.db_manager.get_today_review_count(self.current_user.id)
            overdue_count = self.db_manager.get_overdue_reviews_count(self.current_user.id)

            if overdue_count > 0:
                self.today_review_label.configure(
                    text=f"⚠️ 今日需复习：{today_count}项（{overdue_count}项逾期）",
                    text_color=self.colors['danger']
                )
            elif today_count > 0:
                self.today_review_label.configure(
                    text=f"📖 今日需复习：{today_count}项",
                    text_color=self.colors['primary']
                )
            else:
                self.today_review_label.configure(
                    text="🎉 今日无复习任务",
                    text_color=self.colors['success']
                )
        except Exception as e:
            print(f"更新今日复习计数失败: {e} - ui.py:181")
            self.today_review_label.configure(
                text="❌ 加载失败",
                text_color=self.colors['danger']
            )

    def load_knowledge_items(self, items=None):
        """加载知识项列表 - 支持今日复习筛选"""
        print("🔄 开始加载知识点列表... - ui.py:189")

        # 更新今日复习计数（如果不是筛选模式）
        if not self.show_only_today:
            self.update_today_review_count()

        if items is None:
            print("📝 从数据库查询知识点... - ui.py:196")
            try:
                items = self.knowledge_service.get_user_knowledge(self.current_user.id)
                items = [self._ensure_dict_format(item) for item in items]
            except Exception as e:
                print(f"❌ 获取知识点失败: {e}，回退到基本方法 - ui.py:201")
                items = self.knowledge_service.get_user_knowledge_items(self.current_user.id)
                items = [self._convert_to_dict(item) for item in items]

        # 应用今日复习筛选
        if self.show_only_today:
            items = [item for item in items if item.get('is_today_review', False)]
            print(f"📅 筛选后今日复习知识点: {len(items)}项 - ui.py:208")

        print(f"📊 获取到 {len(items)} 个知识点 - ui.py:210")

        # 清空现有内容
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        if not items:
            # 显示空状态
            empty_text = "📝 暂无知识点\n点击\"添加知识点\"开始创建您的知识库"
            if self.show_only_today:
                empty_text = "🎉 太棒了！\n所有今日复习任务已完成！"

            empty_frame = ctk.CTkFrame(
                self.scrollable_frame,
                fg_color="transparent",
                corner_radius=12
            )
            empty_frame.grid(row=0, column=0, sticky="nsew", pady=50)
            empty_frame.grid_columnconfigure(0, weight=1)

            empty_label = ctk.CTkLabel(
                empty_frame,
                text=empty_text,
                font=ctk.CTkFont(size=16),
                text_color=self.colors['dark']
            )
            empty_label.grid(row=0, column=0, pady=10)
            return

        print(f"🎯 创建 {len(items)} 个知识点卡片 - ui.py:239")
        for i, item in enumerate(items):
            self.create_knowledge_card(item, i)

    def create_knowledge_card(self, item, index):
        """创建美观的知识卡片"""
        item = self._ensure_dict_format(item)
        is_today_review = item.get('is_today_review', False)
        is_urgent = item.get('is_urgent', False)

        # 卡片框架
        card = ctk.CTkFrame(
            self.scrollable_frame,
            fg_color="white",
            border_color=self.colors['today'] if is_today_review else "#E0E0E0",
            border_width=2 if is_today_review else 1,
            corner_radius=12
        )
        card.grid(row=index, column=0, sticky="ew", padx=10, pady=8)
        card.grid_columnconfigure(1, weight=1)

        # 紧急状态指示器
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
            text=f"📖 {item.get('title', '无标题')}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=self.colors['dark'],
            anchor="w"
        )
        title_label.grid(row=0, column=0, sticky="w")

        # 状态标签
        status_text = item.get('review_status', '未知状态')
        status_color = self.colors['today'] if is_today_review else self.colors['primary']

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
        if item.get('category'):
            category_label = ctk.CTkLabel(
                meta_frame,
                text=f"🏷️ {item.get('category')}",
                font=ctk.CTkFont(size=12),
                text_color=self.colors['secondary']
            )
            category_label.grid(row=0, column=0, sticky="w")

        # 时间信息
        time_label = ctk.CTkLabel(
            meta_frame,
            text=f"⏰ {item.get('created_at', '未知时间')}",
            font=ctk.CTkFont(size=11),
            text_color="#666666"
        )
        time_label.grid(row=0, column=1, sticky="w", padx=(20, 0))

        # 下一阶段 & 时间
        next_stage = item.get("next_stage_desc")
        next_review_at = item.get("next_review_at")
        if next_stage and next_review_at:
            ctk.CTkLabel(
                meta_frame,
                text=f"➡️ 下一阶段：{next_stage}",
                font=ctk.CTkFont(size=11),
                text_color=self.colors['primary']
            ).grid(row=2, column=0, sticky="w", pady=(5, 0))
            ctk.CTkLabel(
                meta_frame,
                text=f"🕒 复习时间：{next_review_at}",
                font=ctk.CTkFont(size=11),
                text_color="#666666"
            ).grid(row=2, column=1, sticky="w", padx=(20, 0))
        # 内容预览
        content_preview = item.get('content', '')
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

        # 编辑按钮
        edit_btn = ctk.CTkButton(
            button_frame,
            text="✏️ 编辑",
            command=lambda: self.edit_item(item),
            fg_color=self.colors['primary'],
            hover_color='#1B6B93',
            **btn_style
        )
        edit_btn.pack(side="left", padx=(0, 8))

        # 删除按钮
        delete_btn = ctk.CTkButton(
            button_frame,
            text="🗑️ 删除",
            command=lambda: self.delete_item(item),
            fg_color=self.colors['danger'],
            hover_color='#A63225',
            **btn_style
        )
        delete_btn.pack(side="left", padx=(0, 8))

        # 复习按钮
        review_text = "📚 复习" if not is_today_review else "🎯 立即复习"
        review_color = self.colors['success'] if not is_today_review else self.colors['today']
        review_hover = '#139C8B' if not is_today_review else '#E55A4D'

        review_btn = ctk.CTkButton(
            button_frame,
            text=review_text,
            command=lambda: self.review_item(item),
            fg_color=review_color,
            hover_color=review_hover,
            **btn_style
        )
        review_btn.pack(side="left", padx=(0, 8))

        # 加入今日复习按钮（针对非今日复习的知识点）
        if not is_today_review:
            add_today_btn = ctk.CTkButton(
                button_frame,
                text="⭐ 加入今日",
                command=lambda: self.add_to_today_review(item),
                fg_color=self.colors['warning'],
                hover_color='#D97B00',
                text_color="white",
                **btn_style
            )
            add_today_btn.pack(side="left")

    def _ensure_dict_format(self, item):
        """确保项目是字典格式"""
        if hasattr(item, 'get'):
            return item
        else:
            return self._convert_to_dict(item)

    def _convert_to_dict(self, item):
        """将数据库对象转换为字典格式"""
        if hasattr(item, 'get'):
            return item

        result = {
            'id': getattr(item, 'id', ''),
            'title': getattr(item, 'title', '无标题'),
            'category': getattr(item, 'category', '未分类'),
            'content': getattr(item, 'content', ''),
            'created_at': getattr(item, 'created_at', '未知时间'),
            'review_status': '⏳ 状态未知',
            'is_today_review': False,
            'is_urgent': False
        }

        if hasattr(item, 'created_at') and hasattr(item.created_at, 'strftime'):
            result['created_at'] = item.created_at.strftime("%Y-%m-%d %H:%M")

        return result

    def add_to_today_review(self, item):
        """手动将知识点加入今日复习"""
        try:
            item = self._ensure_dict_format(item)
            print(f"📅 将知识点 '{item.get('title', '无标题')}' 加入今日复习 - ui.py:438")

            result = self.db_manager.add_to_today_review(item['id'], self.current_user.id)

            if result["success"]:
                messagebox.showinfo(
                    "成功",
                    f"✅ 已将知识点 '{item.get('title', '无标题')}' 加入今日复习计划",
                    icon="info"
                )
                self.load_knowledge_items()
            else:
                messagebox.showerror("错误", result["msg"])

        except Exception as e:
            print(f"❌ 加入今日复习失败: {e} - ui.py:453")
            messagebox.showerror("错误", f"加入今日复习失败: {e}")

    def add_knowledge_item(self):
        """添加知识点"""
        print("📝 打开添加知识点对话框... - ui.py:458")
        KnowledgeItemDialog(
            self,
            self.current_user,
            self.knowledge_service,
            self.load_knowledge_items,
            None
        )

    def edit_item(self, item):
        """编辑知识点"""
        item = self._ensure_dict_format(item)
        print(f"✏️ 打开编辑知识点对话框: {item.get('title', '无标题')} - ui.py:470")

        class AdaptedItem:
            def __init__(self, item_dict):
                self.id = item_dict['id']
                self.title = item_dict.get('title', '无标题')
                self.content = item_dict.get('content', '')
                self.category = item_dict.get('category')
                self.created_at = item_dict.get('created_at')

        adapted_item = AdaptedItem(item)
        KnowledgeItemDialog(
            self,
            self.current_user,
            self.knowledge_service,
            self.load_knowledge_items,
            adapted_item,
        )

    def delete_item(self, item):
        """删除知识点"""
        item = self._ensure_dict_format(item)
        title = item.get('title', '无标题')
        if messagebox.askyesno(
                "确认删除",
                f"确定要删除知识点 '{title}' 吗？\n此操作不可恢复！",
                icon="warning"
        ):
            if self.knowledge_service.delete_knowledge_item(item['id']):
                self.load_knowledge_items()
                messagebox.showinfo("成功", "✅ 知识点已删除")

    def review_item(self, item):
        """复习知识点"""
        try:
            from src.scheduler.ui import ReviewDialog

            item = self._ensure_dict_format(item)
            print(f"🔍 调试 知识点对象类型: {type(item)} - ui.py:508")
            print(f"🔍 调试 知识点ID: {item.get('id', 'No id attribute')} - ui.py:509")

            class AdaptedItem:
                def __init__(self, item_dict):
                    self.knowledge_item_id = item_dict['id']
                    self.title = item_dict.get('title', '无标题')
                    self.content = item_dict.get('content', '')
                    self.category = item_dict.get('category')
                    for key, value in item_dict.items():
                        setattr(self, key, value)

            adapted_item = AdaptedItem(item)

            ReviewDialog(
                self,
                adapted_item,
                self.current_user,
                self.scheduler_service,
                self.db_manager,
                # self.knowledge_service.db_manager,
                refresh_callback=self.load_knowledge_items
            )
        except ImportError:
            messagebox.showinfo("提示", "复习模块尚未实现")
        except Exception as e:
            messagebox.showerror("错误", f"打开复习对话框失败: {str(e)}")
            print(f"详细错误信息: {e} - ui.py:533")

    def on_search(self, event=None):
        """搜索功能"""
        search_term = self.search_entry.get().strip()
        print(f"🔍 执行搜索: '{search_term}' 用户ID: {self.current_user.id} - ui.py:538")

        try:
            if search_term:
                print("📝 调用搜索服务... - ui.py:542")
                items = self.knowledge_service.search_knowledge_items(
                    self.current_user.id, search_term
                )
                print(f"📊 搜索返回 {len(items)} 个结果 - ui.py:546")

                items = [self._convert_to_dict(item) for item in items]

                if self.show_only_today:
                    items = [item for item in items if item.get('is_today_review', False)]

                self.load_knowledge_items(items)
            else:
                print("🔄 搜索词为空，显示所有知识点 - ui.py:555")
                self.load_knowledge_items()
        except Exception as e:
            print(f"❌ 搜索过程中出错: {e} - ui.py:558")
            messagebox.showerror("错误", f"搜索失败: {str(e)}")


class KnowledgeItemDialog(ctk.CTkToplevel):
    """知识点编辑对话框 """

    def __init__(self, parent, user, knowledge_service, callback, item=None):
        super().__init__(parent)
        self.user = user
        self.knowledge_service = knowledge_service
        self.callback = callback
        self.item = item

        # 颜色配置
        self.colors = {
            'primary': '#2E86AB',
            'success': '#18A999',
            'light': '#F8F9FA',
            'dark': '#212529'
        }

        self.title("✏️ 编辑知识点" if item else "➕ 添加知识点")
        self.geometry("700x600")
        self.resizable(True, True)

        # 关键修复：设置对话框属性
        self.configure(fg_color="white")  # 设置对话框背景色
        self.transient(parent)  # 设置为主窗口的子窗口
        self.grab_set()  # 设置为模态对话框，阻止主窗口操作
        self.focus_set()  # 获取焦点

        # 绑定窗口关闭事件
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.create_widgets()
        self.center_window()

    def on_close(self):
        """窗口关闭时的处理"""
        self.grab_release()  # 释放模态
        self.destroy()

    def center_window(self):
        """居中显示窗口"""
        self.update_idletasks()
        width = 700
        height = 600
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def create_widgets(self):
        """创建对话框组件"""
        # 主容器
        main_container = ctk.CTkFrame(self, fg_color=self.colors['light'], corner_radius=15)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # 标题
        title_text = "编辑知识点" if self.item else "创建新知识点"
        title_label = ctk.CTkLabel(
            main_container,
            text=title_text,
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=self.colors['dark']
        )
        title_label.pack(anchor="w", pady=(20, 20), padx=20)

        # 表单容器
        form_container = ctk.CTkFrame(main_container, fg_color="white", corner_radius=12)
        form_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        form_container.grid_columnconfigure(0, weight=1)

        # 标题输入
        ctk.CTkLabel(
            form_container,
            text="📝 标题",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.colors['dark']
        ).grid(row=0, column=0, sticky="w", padx=20, pady=(20, 8))

        self.title_entry = ctk.CTkEntry(
            form_container,
            height=45,
            font=ctk.CTkFont(size=13),
            placeholder_text="输入知识点标题..."
        )
        self.title_entry.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 20))

        # 分类输入
        ctk.CTkLabel(
            form_container,
            text="🏷️ 分类",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.colors['dark']
        ).grid(row=2, column=0, sticky="w", padx=20, pady=(0, 8))

        self.category_entry = ctk.CTkEntry(
            form_container,
            height=45,
            font=ctk.CTkFont(size=13),
            placeholder_text="输入分类标签（可选）..."
        )
        self.category_entry.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 20))

        # 内容输入
        ctk.CTkLabel(
            form_container,
            text="📄 内容",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.colors['dark']
        ).grid(row=4, column=0, sticky="w", padx=20, pady=(0, 8))

        self.content_text = ctk.CTkTextbox(
            form_container,
            font=ctk.CTkFont(size=13),
            border_width=1,
            border_color="#E0E0E0"
        )
        self.content_text.grid(row=5, column=0, sticky="nsew", padx=20, pady=(0, 20))
        form_container.grid_rowconfigure(5, weight=1)

        # 按钮框架
        button_frame = ctk.CTkFrame(form_container, fg_color="transparent")
        button_frame.grid(row=6, column=0, sticky="ew", padx=20, pady=20)
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)

        # 保存按钮
        save_btn = ctk.CTkButton(
            button_frame,
            text="💾 保存",
            command=self.save,
            height=40,
            fg_color=self.colors['success'],
            hover_color='#139C8B',
            font=ctk.CTkFont(size=14, weight="bold")
        )
        save_btn.grid(row=0, column=0, padx=(0, 10))

        # 取消按钮
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="❌ 取消",
            command=self.destroy,
            height=40,
            fg_color="#6C757D",
            hover_color="#5A6268",
            font=ctk.CTkFont(size=14)
        )
        cancel_btn.grid(row=0, column=1, padx=(10, 0))

        # 如果是编辑模式，填充数据
        if self.item:
            self.title_entry.insert(0, getattr(self.item, 'title', ''))
            self.category_entry.insert(0, getattr(self.item, 'category', '') or "")
            self.content_text.insert("1.0", getattr(self.item, 'content', ''))

    def save(self):
        """保存知识点"""
        title = self.title_entry.get().strip()
        category = self.category_entry.get().strip() or None
        content = self.content_text.get("1.0", "end-1c").strip()

        if not title:
            messagebox.showerror("错误", "❌ 请填写标题")
            return
        if not content:
            messagebox.showerror("错误", "❌ 请填写内容")
            return

        try:
            if self.item:
                # 更新知识点
                self.knowledge_service.update_knowledge_item(
                    self.item.id, title=title, category=category, content=content
                )
                print(f"✅ 知识点更新成功: {title} - ui.py:734")
            else:
                # 添加新知识点
                self.knowledge_service.add_knowledge_item(
                    self.user.id, title, content, category
                )
                print(f"✅ 知识点创建成功: {title} - ui.py:740")

            # 调用回调函数刷新列表
            if self.callback:
                self.callback()
                print("🔄 回调函数已调用 - ui.py:745")

            messagebox.showinfo("成功", "✅ 知识点已保存")
            self.destroy()

        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {str(e)}")
            print(f"❌ 保存失败: {e} - ui.py:752")


class KnowledgeItemDetailDialog(ctk.CTkToplevel):
    """知识点详情对话框 - 美化版"""

    def __init__(self, parent, item):
        super().__init__(parent)
        self.item = item

        # 颜色配置
        self.colors = {
            'primary': '#2E86AB',
            'success': '#18A999',
            'warning': '#F18F01',
            'light': '#F8F9FA',
            'dark': '#212529'
        }

        self.title(f"📖 知识点详情: {item.get('title', '无标题')}")
        self.geometry("600x500")
        self.resizable(False, False)

        self.create_widgets()
        self.center_window()

    def center_window(self):
        """居中显示窗口"""
        self.update_idletasks()
        width = 600
        height = 500
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def create_widgets(self):
        """创建对话框组件"""
        # 主容器
        main_container = ctk.CTkFrame(self, fg_color=self.colors['light'], corner_radius=15)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # 标题
        title_label = ctk.CTkLabel(
            main_container,
            text=self.item.get('title', '无标题'),
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=self.colors['dark']
        )
        title_label.pack(anchor="w", pady=(20, 15), padx=20)

        # 信息卡片
        info_card = ctk.CTkFrame(main_container, fg_color="white", corner_radius=12)
        info_card.pack(fill="x", padx=20, pady=(0, 20))
        info_card.grid_columnconfigure(1, weight=1)

        # 分类信息
        if self.item.get('category'):
            category_frame = ctk.CTkFrame(info_card, fg_color="transparent")
            category_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=15, pady=10)

            ctk.CTkLabel(
                category_frame,
                text="🏷️ 分类:",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=self.colors['dark']
            ).pack(side="left")

            ctk.CTkLabel(
                category_frame,
                text=self.item.get('category'),
                font=ctk.CTkFont(size=12),
                text_color=self.colors['primary']
            ).pack(side="left", padx=(5, 0))

        # 创建时间
        time_frame = ctk.CTkFrame(info_card, fg_color="transparent")
        time_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=15, pady=5)

        ctk.CTkLabel(
            time_frame,
            text="⏰ 创建时间:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.colors['dark']
        ).pack(side="left")

        ctk.CTkLabel(
            time_frame,
            text=self.item.get('created_at', '未知时间'),
            font=ctk.CTkFont(size=12),
            text_color="#666666"
        ).pack(side="left", padx=(5, 0))

        # 复习状态
        status_frame = ctk.CTkFrame(info_card, fg_color="transparent")
        status_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=15, pady=10)

        ctk.CTkLabel(
            status_frame,
            text="📊 复习状态:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.colors['dark']
        ).pack(side="left")

        status_color = self.colors['warning'] if self.item.get('is_today_review') else self.colors['success']
        status_label = ctk.CTkLabel(
            status_frame,
            text=self.item.get('review_status', '未知状态'),
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="white",
            fg_color=status_color,
            corner_radius=8,
            padx=8,
            pady=2
        )
        status_label.pack(side="left", padx=(5, 0))

        # 内容区域
        content_frame = ctk.CTkFrame(main_container, fg_color="white", corner_radius=12)
        content_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        ctk.CTkLabel(
            content_frame,
            text="📄 内容",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=self.colors['dark']
        ).pack(anchor="w", padx=15, pady=15)

        content_text = ctk.CTkTextbox(
            content_frame,
            wrap="word",
            font=ctk.CTkFont(size=12),
            border_width=0
        )
        content_text.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        content_text.insert("1.0", self.item.get('content', '无内容'))
        content_text.configure(state="disabled")