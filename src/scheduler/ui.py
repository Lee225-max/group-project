class ReviewDialog(ctk.CTkToplevel):
    """复习对话框"""

    def __init__(self, parent, item, user, db_manager):
        super().__init__(parent)
        self.item = item
        self.user = user
        self.db_manager = db_manager

        self.title(f"复习: {item.title}")
        self.geometry("500x400")
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
