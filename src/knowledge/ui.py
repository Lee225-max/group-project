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
        print("🔄 开始加载知识点列表... - ui.py:81")

        if items is None:
            print("📝 从数据库查询知识点... - ui.py:84")
            items = self.knowledge_service.get_user_knowledge_items(
                self.current_user.id
            )
        print(f"📊 获取到 {len(items)} 个知识点 - ui.py:88")

        # 清空现有内容
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        if not items:
            # 显示空状态
            print("📭 没有知识点，显示空状态 - ui.py:96")
            empty_label = ctk.CTkLabel(
                self.scrollable_frame,
                text="暂无知识点，点击\"添加知识点\"开始创建",
                font=ctk.CTkFont(size=16),
            )
            empty_label.pack(pady=50)
            return

        print(f"🎯 创建 {len(items)} 个知识点行 - ui.py:105")
        for item in items:
            self.create_item_row(item)
        print("✅ 知识点列表加载完成 - ui.py:108")

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
        print("📝 打开添加知识点对话框... - ui.py:167")
        # 打开添加对话框
        KnowledgeItemDialog(
            self,
            self.current_user,
            self.knowledge_service,
            self.load_knowledge_items,
            None  # 没有item表示添加模式
        )

    def edit_item(self, item):
        """编辑知识点"""
        print(f"✏️ 打开编辑知识点对话框: {item.title} - ui.py:179")
        print(f"回调函数: {self.load_knowledge_items} - ui.py:180")
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

            # 修复：添加调试信息并处理可能的属性错误
            print(f"🔍 调试  知识点对象类型: {type(item)} - ui.py:206")
            print(f"🔍 调试  知识点ID: {getattr(item, 'id', 'No id attribute')} - ui.py:207")
            
            # 如果 ReviewDialog 需要 knowledge_item_id 属性，创建一个适配器
            if not hasattr(item, 'knowledge_item_id'):
                # 创建一个简单的适配器对象
                class AdaptedItem:
                    def __init__(self, original_item):
                        self.knowledge_item_id = original_item.id
                        self.title = original_item.title
                        self.content = original_item.content
                        self.category = original_item.category
                        # 复制所有其他属性
                        for attr in dir(original_item):
                            if not attr.startswith('_'):
                                try:
                                    setattr(self, attr, getattr(original_item, attr))
                                except AttributeError:
                                    pass
                
                adapted_item = AdaptedItem(item)
                review_item = adapted_item
            else:
                review_item = item

            ReviewDialog(
                self, 
                review_item, 
                self.current_user, 
                self.knowledge_service.db_manager,
                refresh_callback=self.load_knowledge_items
            )
        except ImportError:
            messagebox.showinfo("提示", "复习模块尚未实现")
        except Exception as e:
            messagebox.showerror("错误", f"打开复习对话框失败: {str(e)}")
            print(f"详细错误信息: {e} - ui.py:242")

    def on_search(self, event=None):
        """搜索功能"""
        search_term = self.search_entry.get().strip()
        print(f"🔍 执行搜索: '{search_term}'  用户ID: {self.current_user.id} - ui.py:247")

        try:
            if search_term:
                print("📝 调用搜索服务... - ui.py:251")
                items = self.knowledge_service.search_knowledge_items(
                    self.current_user.id, search_term
                )
                print(f"📊 搜索返回 {len(items)} 个结果 - ui.py:255")
                self.load_knowledge_items(items)
            else:
                print("🔄 搜索词为空，显示所有知识点 - ui.py:258")
                self.load_knowledge_items()
        except Exception as e:
            print(f"❌ 搜索过程中出错: {e} - ui.py:261")
            messagebox.showerror("错误", f"搜索失败: {str(e)}")


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
                # 更新知识点 - 直接调用方法，不使用返回值
                self.knowledge_service.update_knowledge_item(
                    self.item.id, title=title, category=category, content=content
                )
                print(f"✅ 知识点更新成功: {title} - ui.py:344")
            else:
                # 添加新知识点 - 直接调用方法，不使用返回值
                self.knowledge_service.add_knowledge_item(
                    self.user.id, title, content, category
                )
                print(f"✅ 知识点创建成功: {title} - ui.py:350")

            print("🔄 准备调用回调函数刷新列表... - ui.py:352")
            print(f"回调函数: {self.callback} - ui.py:353")

            # 关键修复：确保回调函数被调用
            if self.callback:
                # 立即调用回调函数
                self.callback()
                print("🔄 回调函数已调用 - ui.py:359")
            else:
                print("⚠️ 回调函数不存在，无法刷新列表 - ui.py:361")

            # 先显示成功消息，再关闭对话框
            messagebox.showinfo("成功", "知识点已保存")
            self.destroy()

        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {str(e)}")
            print(f"❌ 保存失败: {e} - ui.py:369")


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
