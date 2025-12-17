import tkinter as tk
from tkinter import messagebox

from app.services.auth_service import AuthService


class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("抽籤系統 - 登入")
        self.root.geometry("400x300")
        self.root.resizable(False, False)

        self.auth_service = AuthService()

        self._build_ui()

    def _build_ui(self):
        # ===== 標題 =====
        title_label = tk.Label(
            self.root,
            text="抽籤系統登入",
            font=("Arial", 18, "bold")
        )
        title_label.pack(pady=20)

        # ===== 帳號 =====
        username_frame = tk.Frame(self.root)
        username_frame.pack(pady=10)

        tk.Label(username_frame, text="帳號：", font=("Arial", 12)).pack(side=tk.LEFT)
        self.username_entry = tk.Entry(username_frame, width=20)
        self.username_entry.pack(side=tk.LEFT)

        # ===== 密碼 =====
        password_frame = tk.Frame(self.root)
        password_frame.pack(pady=10)

        tk.Label(password_frame, text="密碼：", font=("Arial", 12)).pack(side=tk.LEFT)
        self.password_entry = tk.Entry(password_frame, width=20, show="*")
        self.password_entry.pack(side=tk.LEFT)

        # ===== 登入按鈕 =====
        login_button = tk.Button(
            self.root,
            text="登入",
            width=15,
            command=self.login
        )
        login_button.pack(pady=20)

        # Enter 鍵登入
        self.root.bind("<Return>", lambda event: self.login())

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showwarning("警告", "請輸入帳號與密碼")
            return

        if self.auth_service.authenticate(username, password):
            messagebox.showinfo("成功", "登入成功")
            self.root.destroy()
            self.open_main_window()
        else:
            messagebox.showerror("失敗", "帳號或密碼錯誤")

    def open_main_window(self):
        from app.ui.main_window import MainWindow
        import tkinter as tk

        main_root = tk.Tk()
        MainWindow(main_root)
        main_root.mainloop()

