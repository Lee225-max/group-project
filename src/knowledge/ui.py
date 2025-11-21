"""
知识管理界面 - 成员B负责 + 今日复习联动功能
"""

import customtkinter as ctk
from tkinter import messagebox
from src.knowledge.service import KnowledgeService


class KnowledgeManagementFrame(ctk.CTkFrame):
    """知识管理界面 - 支持今日复习联动"""

    def __init__(self, parent, current_user, db_manager):
        super().__init__(parent)
        self.current_user = current_user
        self.knowledge_service = KnowledgeService(db_manager)
        self.db_manager = db_manager
        self.show_only_today = False  # 今日复习筛选状态

        self.create_widgets()
        self.load_knowledge_items()
        self.update_today_review_count()

    def create_widgets(self):
        """创建界面组件"""
        # 顶部工具栏
        toolbar = ctk.CTkFrame(self)
        toolbar.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            toolbar, text="知识管理", font=ctk.CTkFont(size=20, weight="bold")
        ).pack(side="left")

        # 今日复习状态栏
        self.stats_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        self.stats_frame.pack(side="left", fill="x", expand=True, padx=20)

        self.today_review_label = ctk.CTkLabel(
            self.stats_frame,
            text="今日需复习：加载中...",
            font=ctk.CTkFont(size=12),
            text_color="#FF6B6B"
        )
        self.today_review_label.pack(side="left", padx=(10, 5))

        # 筛选按钮
        self.filter_today_btn = ctk.CTkButton(
            self.stats_frame,
            text="筛选今日复习",
            command=self.toggle_today_filter,
            width=100,
            height=28,
            fg_color="#4ECDC4",
            hover_color="#45B7B0"
        )
        self.filter_today_btn.pack(side="left", padx=5)

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

        headers = ["标题", "分类", "复习状态", "创建时间", "操作"]
        widths = [250, 120, 150, 120, 200]

        for i, (text, width) in enumerate(zip(headers, widths)):
            label = ctk.CTkLabel(header, text=text, width=width)
            label.pack(side="left")

        # 滚动框架
        self.scrollable_frame = ctk.CTkScrollableFrame(list_frame)
        self.scrollable_frame.pack(fill="both", expand=True)

    def toggle_today_filter(self):
        """切换今日复习筛选"""
        if self.show_only_today:
            # 取消筛选
            self.show_only_today = False
            self.filter_today_btn.configure(
                text="筛选今日复习",
                fg_color="#4ECDC4",
                hover_color="#45B7B0"
            )
            self.update_today_review_count()
        else:
            # 应用筛选
            self.show_only_today = True
            self.filter_today_btn.configure(
                text="取消筛选",
                fg_color="#FF6B6B",
                hover_color="#FF5252"
            )
            self.today_review_label.configure(text="正在显示今日复习")

        self.load_knowledge_items()

    def update_today_review_count(self):
        """更新今日复习计数"""
        try:
            today_count = self.db_manager.get_today_review_count(self.current_user.id)
            overdue_count = self.db_manager.get_overdue_reviews_count(
                self.current_user.id)

            if overdue_count > 0:
                self.today_review_label.configure(
                    text=f"今日需复习：{today_count}项（{overdue_count}项逾期）",
                    text_color="#FF5252"
                )
            else:
                self.today_review_label.configure(
                    text=f"今日需复习：{today_count}项",
                    text_color="#FF6B6B" if today_count > 0 else "#888888"
                )
        except Exception as e:
            print(f"更新今日复习计数失败: {e} - ui.py:147")
            self.today_review_label.configure(text="今日需复习：加载失败")

    def load_knowledge_items(self, items=None):
        """加载知识项列表 - 支持今日复习筛选"""
        print("🔄 开始加载知识点列表... - ui.py:152")

        # 更新今日复习计数（如果不是筛选模式）
        if not self.show_only_today:
            self.update_today_review_count()

        if items is None:
            print("📝 从数据库查询知识点... - ui.py:159")
            try:
                # 使用新的方法获取包含复习状态的知识点
                items = self.knowledge_service.get_user_knowledge(self.current_user.id)
                # 确保所有项目都是字典格式
                items = [self._ensure_dict_format(item) for item in items]
            except Exception as e:
                print(f"❌ 获取知识点失败: {e}，回退到基本方法 - ui.py:166")
                # 回退到基本方法
                items = self.knowledge_service.get_user_knowledge_items(
                    self.current_user.id)
                # 将数据库对象转换为字典格式
                items = [self._convert_to_dict(item) for item in items]

        # 应用今日复习筛选
        if self.show_only_today:
            items = [item for item in items if item.get('is_today_review', False)]
            print(f"📅 筛选后今日复习知识点: {len(items)}项 - ui.py:176")

        print(f"📊 获取到 {len(items)} 个知识点 - ui.py:178")

        # 清空现有内容
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        if not items:
            # 显示空状态
            print("📭 没有知识点，显示空状态 - ui.py:186")
            empty_text = "暂无知识点，点击\"添加知识点\"开始创建"
            if self.show_only_today:
                empty_text = "今日暂无复习计划\n所有知识点都已复习完成！🎉"

            empty_label = ctk.CTkLabel(
                self.scrollable_frame,
                text=empty_text,
                font=ctk.CTkFont(size=16),
            )
            empty_label.pack(pady=50)
            return

        print(f"🎯 创建 {len(items)} 个知识点行 - ui.py:199")
        for item in items:
            self.create_item_row(item)
        print("✅ 知识点列表加载完成 - ui.py:202")

    def _ensure_dict_format(self, item):
        """确保项目是字典格式"""
        if hasattr(item, 'get'):
            # 已经是字典
            return item
        else:
            # 转换为字典
            return self._convert_to_dict(item)

    def _convert_to_dict(self, item):
        """将数据库对象转换为字典格式"""

        if hasattr(item, 'get'):
            # 已经是字典，直接返回
            return item

        # 从数据库对象转换为字典
        result = {
            'id': getattr(item, 'id', ''),
            'title': getattr(item, 'title', '无标题'),
            'category': getattr(item, 'category', '未分类'),
            'content': getattr(item, 'content', ''),
            'created_at': getattr(item, 'created_at', '未知时间'),
            'review_status': '⏳ 状态未知',
            'is_today_review': False
        }

        # 处理日期格式
        if hasattr(item, 'created_at') and hasattr(item.created_at, 'strftime'):
            result['created_at'] = item.created_at.strftime("%Y-%m-%d")

        return result

    def create_item_row(self, item):
        """创建知识项行 - 支持今日复习样式"""
        # 确保使用字典访问方式
        item = self._ensure_dict_format(item)

        row = ctk.CTkFrame(self.scrollable_frame)
        row.pack(fill="x", padx=5, pady=2)

        # 如果是今日复习，添加特殊样式
        is_today_review = item.get('is_today_review', False)
        if is_today_review:
            row.configure(border_color="#FF6B6B", border_width=2)

        # 标题（可点击查看详情）
        title_frame = ctk.CTkFrame(row, fg_color="transparent", width=250)
        title_frame.pack(side="left")
        title_frame.pack_propagate(False)

        # 今日复习图标
        if is_today_review:
            icon_label = ctk.CTkLabel(
                title_frame,
                text="📅 ",
                font=ctk.CTkFont(size=12)
            )
            icon_label.pack(side="left")

        title_label = ctk.CTkLabel(
            title_frame, text=item.get(
                'title', '无标题'), anchor="w")
        title_label.pack(side="left", fill="x", expand=True)
        title_label.bind("<Button-1>", lambda e, item=item: self.view_item_detail(item))

        # 分类
        category_label = ctk.CTkLabel(
            row, text=item.get('category', '未分类') or "未分类", width=120, anchor="w"
        )
        category_label.pack(side="left")

        # 复习状态
        status_label = ctk.CTkLabel(
            row,
            text=item.get('review_status', '未知状态'),
            width=150,
            anchor="w",
            text_color="#4ECDC4" if is_today_review else "#888888"
        )
        status_label.pack(side="left")

        # 创建时间
        time_label = ctk.CTkLabel(
            row, text=item.get('created_at', '未知时间'), width=120, anchor="w"
        )
        time_label.pack(side="left")

        # 操作按钮
        btn_frame = ctk.CTkFrame(row, width=200)
        btn_frame.pack(side="left")
        btn_frame.pack_propagate(False)

        ctk.CTkButton(
            btn_frame,
            text="编辑",
            width=45,
            height=25,
            command=lambda: self.edit_item(item),
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            btn_frame,
            text="删除",
            width=45,
            height=25,
            fg_color="#d9534f",
            hover_color="#c9302c",
            command=lambda: self.delete_item(item),
        ).pack(side="left", padx=2)

        # 复习按钮 - 使用不同的颜色标识今日复习
        review_btn = ctk.CTkButton(
            btn_frame,
            text="复习",
            width=45,
            height=25,
            fg_color="#5cb85c" if not is_today_review else "#FF6B6B",
            hover_color="#4cae4c" if not is_today_review else "#FF5252",
            command=lambda: self.review_item(item),
        )
        review_btn.pack(side="left", padx=2)

        # 加入今日复习按钮（针对非今日复习的知识点）
        if not is_today_review:
            add_review_btn = ctk.CTkButton(
                btn_frame,
                text="加入今日",
                width=50,
                height=25,
                fg_color="#FFD93D",
                hover_color="#FFC800",
                text_color="#000000",
                command=lambda: self.add_to_today_review(item)
            )
            add_review_btn.pack(side="left", padx=2)

    def add_to_today_review(self, item):
        """手动将知识点加入今日复习"""
        try:
            item = self._ensure_dict_format(item)
            print(f"📅 将知识点 '{item.get('title', '无标题')}' 加入今日复习 - ui.py:345")

            # 调用数据库管理器的方法
            result = self.db_manager.add_to_today_review(
                item['id'], self.current_user.id)

            if result["success"]:
                messagebox.showinfo(
                    "成功", f"已将知识点 '{item.get('title', '无标题')}' 加入今日复习计划")
                # 刷新列表
                self.load_knowledge_items()
            else:
                messagebox.showerror("错误", result["msg"])

        except Exception as e:
            print(f"❌ 加入今日复习失败: {e} - ui.py:360")
            messagebox.showerror("错误", f"加入今日复习失败: {e}")

    def add_knowledge_item(self):
        """添加知识点"""
        print("📝 打开添加知识点对话框... - ui.py:365")
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
        item = self._ensure_dict_format(item)
        print(f"✏️ 打开编辑知识点对话框: {item.get('title', '无标题')} - ui.py:378")
        print(f"回调函数: {self.load_knowledge_items} - ui.py:379")

        # 需要将字典项转换为适当的对象格式
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
        if messagebox.askyesno("确认删除", f"确定要删除知识点 '{title}' 吗？"):
            if self.knowledge_service.delete_knowledge_item(item['id']):
                self.load_knowledge_items()
                messagebox.showinfo("成功", "知识点已删除")

    def view_item_detail(self, item):
        """查看知识点详情"""
        item = self._ensure_dict_format(item)
        KnowledgeItemDetailDialog(self, item)

    def review_item(self, item):
        """复习知识点"""
        try:
            from src.scheduler.ui import ReviewDialog

            item = self._ensure_dict_format(item)
            print(f"🔍 调试  知识点对象类型: {type(item)} - ui.py:419")
            print(f"🔍 调试  知识点ID: {item.get('id', 'No id attribute')} - ui.py:420")

            # 创建一个适配器对象
            class AdaptedItem:
                def __init__(self, item_dict):
                    self.knowledge_item_id = item_dict['id']
                    self.title = item_dict.get('title', '无标题')
                    self.content = item_dict.get('content', '')
                    self.category = item_dict.get('category')
                    # 复制所有其他属性
                    for key, value in item_dict.items():
                        setattr(self, key, value)

            adapted_item = AdaptedItem(item)

            ReviewDialog(
                self,
                adapted_item,
                self.current_user,
                self.knowledge_service.db_manager,
                refresh_callback=self.load_knowledge_items
            )
        except ImportError:
            messagebox.showinfo("提示", "复习模块尚未实现")
        except Exception as e:
            messagebox.showerror("错误", f"打开复习对话框失败: {str(e)}")
            print(f"详细错误信息: {e} - ui.py:446")

    def on_search(self, event=None):
        """搜索功能"""
        search_term = self.search_entry.get().strip()
        print(f"🔍 执行搜索: '{search_term}'  用户ID: {self.current_user.id} - ui.py:451")

        try:
            if search_term:
                print("📝 调用搜索服务... - ui.py:455")
                # 使用新的搜索方法
                items = self.knowledge_service.search_knowledge_items(
                    self.current_user.id, search_term
                )
                print(f"📊 搜索返回 {len(items)} 个结果 - ui.py:460")

                # 将搜索结果转换为字典格式
                items = [self._convert_to_dict(item) for item in items]

                # 应用今日复习筛选（如果启用）
                if self.show_only_today:
                    items = [
                        item for item in items if item.get(
                            'is_today_review', False)]

                self.load_knowledge_items(items)
            else:
                print("🔄 搜索词为空，显示所有知识点 - ui.py:473")
                self.load_knowledge_items()
        except Exception as e:
            print(f"❌ 搜索过程中出错: {e} - ui.py:476")
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
            self.title_entry.insert(0, getattr(self.item, 'title', ''))
            self.category_entry.insert(0, getattr(self.item, 'category', '') or "")
            self.content_text.insert("1.0", getattr(self.item, 'content', ''))

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
                # 更新知识点
                self.knowledge_service.update_knowledge_item(
                    self.item.id, title=title, category=category, content=content
                )
                print(f"✅ 知识点更新成功: {title} - ui.py:559")
            else:
                # 添加新知识点
                self.knowledge_service.add_knowledge_item(
                    self.user.id, title, content, category
                )
                print(f"✅ 知识点创建成功: {title} - ui.py:565")

            print("🔄 准备调用回调函数刷新列表... - ui.py:567")
            print(f"回调函数: {self.callback} - ui.py:568")

            # 关键修复：确保回调函数被调用
            if self.callback:
                # 立即调用回调函数
                self.callback()
                print("🔄 回调函数已调用 - ui.py:574")
            else:
                print("⚠️ 回调函数不存在，无法刷新列表 - ui.py:576")

            # 先显示成功消息，再关闭对话框
            messagebox.showinfo("成功", "知识点已保存")
            self.destroy()

        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {str(e)}")
            print(f"❌ 保存失败: {e} - ui.py:584")


class KnowledgeItemDetailDialog(ctk.CTkToplevel):
    """知识点详情对话框"""

    def __init__(self, parent, item):
        super().__init__(parent)
        self.item = item

        self.title(f"知识点详情: {item.get('title', '无标题')}")
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
            text=self.item.get('title', '无标题'),
            font=ctk.CTkFont(size=18, weight="bold"),
        )
        title_label.pack(anchor="w", pady=(0, 10))

        # 分类信息
        if self.item.get('category'):
            category_label = ctk.CTkLabel(
                main_container,
                text=f"分类: {self.item.get('category')}",
                font=ctk.CTkFont(size=12),
            )
            category_label.pack(anchor="w", pady=(0, 10))

        # 创建时间
        time_label = ctk.CTkLabel(
            main_container,
            text="创建时间: {self.item.get('created_at', '未知时间')}",
            font=ctk.CTkFont(size=12),
        )
        time_label.pack(anchor="w", pady=(0, 15))

        # 复习状态
        status_label = ctk.CTkLabel(
            main_container,
            text=f"复习状态: {self.item.get('review_status', '未知状态')}",
            font=ctk.CTkFont(size=12),
            text_color="#4ECDC4" if self.item.get('is_today_review') else "#888888"
        )
        status_label.pack(anchor="w", pady=(0, 15))

        # 内容
        content_label = ctk.CTkLabel(
            main_container, text="内容:", font=ctk.CTkFont(size=14, weight="bold")
        )
        content_label.pack(anchor="w", pady=(0, 5))

        content_frame = ctk.CTkFrame(main_container)
        content_frame.pack(fill="both", expand=True)

        content_text = ctk.CTkTextbox(content_frame, wrap="word")
        content_text.pack(fill="both", expand=True, padx=10, pady=10)
        content_text.insert("1.0", self.item.get('content', '无内容'))
        content_text.configure(state="disabled")
