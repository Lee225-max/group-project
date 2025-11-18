"""
知识管理界面 - 成员B负责
"""

import customtkinter as ctk
from tkinter import messagebox
from src.knowledge.service import KnowledgeService


class KnowledgeManagementFrame(ctk.CTkFrame):
    """知识管理界面"""

    def __init__(self, parent, current_user, db_manager):
        super().__init__(parent)
        self.current_user = current_user
        self.knowledge_service = KnowledgeService(db_manager)

        self.create_widgets()
        self.load_knowledge_items()

    def create_widgets(self):
        """创建界面组件"""
        # 顶部工具栏
        toolbar = ctk.CTkFrame(self)
        toolbar.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            toolbar, text="知识管理", font=ctk.CTkFont(size=20, weight="bold")
        ).pack(side="left")

        ctk.CTkButton(
            toolbar, text="+ 添加知识点", command=self.add_knowledge_item
        ).pack(side="right", padx=5)

        # 搜索框
        search_frame = ctk.CTkFrame(self)
        search_frame.pack(fill="x", padx=10, pady=5)

        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="搜索知识点...")
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.search_entry.bind("<KeyRelease>", self.on_search)

        ctk.CTkButton(search_frame, text="搜索", width=80, command=self.on_search).pack(
            side="right"
        )

        # 知识列表容器
        self.list_container = ctk.CTkFrame(self)
        self.list_container.pack(fill="both", expand=True, padx=10, pady=10)

        # 创建列表框架
        self.create_list_frame()

    def create_list_frame(self):
        """创建知识列表框架"""
        # 清空容器
        for widget in self.list_container.winfo_children():
            widget.destroy()

        # 列表框架
        list_frame = ctk.CTkFrame(self.list_container)
        list_frame.pack(fill="both", expand=True)

        # 列表头部
        header = ctk.CTkFrame(list_frame)
        header.pack(fill="x", padx=5, pady=5)

        headers = ["标题", "分类", "创建时间", "操作"]
        widths = [300, 150, 150, 200]

        for i, (text, width) in enumerate(zip(headers, widths)):
            label = ctk.CTkLabel(header, text=text, width=width)
            label.pack(side="left")

        # 滚动框架
        self.scrollable_frame = ctk.CTkScrollableFrame(list_frame)
        self.scrollable_frame.pack(fill="both", expand=True)

    def load_knowledge_items(self, items=None):
        """加载知识项列表"""
        if items is None:
            items = self.knowledge_service.get_user_knowledge_items(
                self.current_user.id
            )

        # 清空现有内容
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        if not items:
            # 显示空状态
            empty_label = ctk.CTkLabel(
                self.scrollable_frame,
                text="暂无知识点，点击“添加知识点”开始创建",
                font=ctk.CTkFont(size=16),
            )
            empty_label.pack(pady=50)
            return

        for item in items:
            self.create_item_row(item)

    def create_item_row(self, item):
        """创建知识项行"""
        row = ctk.CTkFrame(self.scrollable_frame)
        row.pack(fill="x", padx=5, pady=2)

        # 标题（可点击查看详情）
        title_label = ctk.CTkLabel(row, text=item.title, width=300, anchor="w")
        title_label.pack(side="left")
        title_label.bind("<Button-1>", lambda e, item=item: self.view_item_detail(item))

        # 分类
        category_label = ctk.CTkLabel(
            row, text=item.category or "未分类", width=150, anchor="w"
        )
        category_label.pack(side="left")

        # 创建时间
        time_label = ctk.CTkLabel(
            row, text=item.created_at.strftime("%Y-%m-%d %H:%M"), width=150, anchor="w"
        )
        time_label.pack(side="left")

        # 操作按钮
        btn_frame = ctk.CTkFrame(row, width=200)
        btn_frame.pack(side="left")
        btn_frame.pack_propagate(False)

        ctk.CTkButton(
            btn_frame,
            text="编辑",
            width=50,
            height=25,
            command=lambda: self.edit_item(item),
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            btn_frame,
            text="删除",
            width=50,
            height=25,
            fg_color="#d9534f",
            hover_color="#c9302c",
            command=lambda: self.delete_item(item),
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            btn_frame,
            text="复习",
            width=50,
            height=25,
            fg_color="#5cb85c",
            hover_color="#4cae4c",
            command=lambda: self.review_item(item),
        ).pack(side="left", padx=2)

    def add_knowledge_item(self):
        """添加知识点"""
        KnowledgeItemDialog(
            self, self.current_user, self.knowledge_service, self.load_knowledge_items
        )

    def edit_item(self, item):
        """编辑知识点"""
        KnowledgeItemDialog(
            self,
            self.current_user,
            self.knowledge_service,
            self.load_knowledge_items,
            item,
        )

    def delete_item(self, item):
        """删除知识点"""
        if messagebox.askyesno("确认删除", f"确定要删除知识点 '{item.title}' 吗？"):
            if self.knowledge_service.delete_knowledge_item(item.id):
                self.load_knowledge_items()
                messagebox.showinfo("成功", "知识点已删除")

    def view_item_detail(self, item):
        """查看知识点详情"""
        KnowledgeItemDetailDialog(self, item)

    def review_item(self, item):
    """复习知识点"""
    try:
        from src.scheduler.ui import ReviewDialog
        ReviewDialog(self, item, self.current_user, self.knowledge_service.db_manager)
    except ImportError:
        messagebox.showinfo("提示", "复习模块尚未实现")
    except Exception as e:
        messagebox.showerror("错误", f"打开复习对话框失败: {str(e)}")
        
    def on_search(self, event=None):
        """搜索功能"""
        search_term = self.search_entry.get().strip()
        if search_term:
            items = self.knowledge_service.search_knowledge_items(
                self.current_user.id, search_term
            )
            self.load_knowledge_items(items)
        else:
            self.load_knowledge_items()


class KnowledgeItemDialog(ctk.CTkToplevel):
    """知识点编辑对话框"""

    def __init__(self, parent, user, knowledge_service, callback, item=None):
        super().__init__(parent)
        self.user = user
        self.knowledge_service = knowledge_service
        self.callback = callback
        self.item = item

        self.title("编辑知识点" if item else "添加知识点")
        self.geometry("600x500")
        self.resizable(False, False)

        self.create_widgets()
        self.center_window()

    def center_window(self):
        """居中显示窗口"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"+{x}+{y}")

    def create_widgets(self):
        """创建对话框组件"""
        # 主容器
        main_container = ctk.CTkFrame(self)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # 标题
        ctk.CTkLabel(main_container, text="标题:").pack(anchor="w", pady=(0, 5))
        self.title_entry = ctk.CTkEntry(main_container, height=35)
        self.title_entry.pack(fill="x", pady=(0, 15))

        # 分类
        ctk.CTkLabel(main_container, text="分类:").pack(anchor="w", pady=(0, 5))
        self.category_entry = ctk.CTkEntry(main_container, height=35)
        self.category_entry.pack(fill="x", pady=(0, 15))

        # 内容
        ctk.CTkLabel(main_container, text="内容:").pack(anchor="w", pady=(0, 5))
        self.content_text = ctk.CTkTextbox(main_container, height=200)
        self.content_text.pack(fill="both", expand=True, pady=(0, 20))

        # 按钮框架
        button_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        button_frame.pack(fill="x")

        ctk.CTkButton(button_frame, text="保存", command=self.save).pack(
            side="left", padx=(0, 10)
        )

        ctk.CTkButton(button_frame, text="取消", command=self.destroy).pack(side="left")

        # 如果是编辑模式，填充数据
        if self.item:
            self.title_entry.insert(0, self.item.title)
            self.category_entry.insert(0, self.item.category or "")
            self.content_text.insert("1.0", self.item.content)

    def save(self):
        """保存知识点"""
        title = self.title_entry.get().strip()
        category = self.category_entry.get().strip() or None
        content = self.content_text.get("1.0", "end-1c").strip()

        if not title or not content:
            messagebox.showerror("错误", "请填写标题和内容")
            return

        try:
            if self.item:
                # 更新现有项
                self.knowledge_service.update_knowledge_item(
                    self.item.id, title=title, category=category, content=content
                )
            else:
                # 创建新项
                self.knowledge_service.add_knowledge_item(
                    self.user.id, title, content, category
                )

            self.callback()
            self.destroy()
            messagebox.showinfo("成功", "知识点已保存")
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {str(e)}")


class KnowledgeItemDetailDialog(ctk.CTkToplevel):
    """知识点详情对话框"""

    def __init__(self, parent, item):
        super().__init__(parent)
        self.item = item

        self.title(f"知识点详情: {item.title}")
        self.geometry("500x400")

        self.create_widgets()
        self.center_window()

    def center_window(self):
        """居中显示窗口"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"+{x}+{y}")

    def create_widgets(self):
        """创建对话框组件"""
        # 主容器
        main_container = ctk.CTkFrame(self)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # 标题
        title_label = ctk.CTkLabel(
            main_container,
            text=self.item.title,
            font=ctk.CTkFont(size=18, weight="bold"),
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

        # 创建时间
        time_label = ctk.CTkLabel(
            main_container,
            text=f"创建时间: {self.item.created_at.strftime('%Y-%m-%d %H:%M')}",
            font=ctk.CTkFont(size=12),
        )
        time_label.pack(anchor="w", pady=(0, 15))

        # 内容
        content_label = ctk.CTkLabel(
            main_container, text="内容:", font=ctk.CTkFont(size=14, weight="bold")
        )
        content_label.pack(anchor="w", pady=(0, 5))

        content_frame = ctk.CTkFrame(main_container)
        content_frame.pack(fill="both", expand=True)

        content_text = ctk.CTkTextbox(content_frame, wrap="word")
        content_text.pack(fill="both", expand=True, padx=10, pady=10)
        content_text.insert("1.0", self.item.content)
        content_text.configure(state="disabled")
