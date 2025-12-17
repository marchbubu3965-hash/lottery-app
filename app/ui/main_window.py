import tkinter as tk
from tkinter import ttk, messagebox


class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("抽籤系統")
        self.root.geometry("900x600")
        self.root.resizable(False, False)

        self._build_ui()

    def _build_ui(self):
        # =========================
        # 左側：獎項設定
        # =========================
        left_frame = ttk.LabelFrame(self.root, text="獎項設定")
        left_frame.place(x=20, y=20, width=400, height=260)

        ttk.Label(left_frame, text="獎項名稱").grid(row=0, column=0, padx=10, pady=10)
        self.prize_name_entry = ttk.Entry(left_frame, width=20)
        self.prize_name_entry.grid(row=0, column=1)

        ttk.Label(left_frame, text="名額").grid(row=1, column=0, padx=10, pady=10)
        self.prize_quota_entry = ttk.Entry(left_frame, width=20)
        self.prize_quota_entry.grid(row=1, column=1)

        add_prize_btn = ttk.Button(
            left_frame,
            text="新增獎項",
            command=self.add_prize
        )
        add_prize_btn.grid(row=2, column=0, columnspan=2, pady=15)

        # =========================
        # 中央：抽籤控制
        # =========================
        center_frame = ttk.LabelFrame(self.root, text="抽籤控制")
        center_frame.place(x=450, y=20, width=400, height=260)

        start_btn = ttk.Button(
            center_frame,
            text="開始抽籤",
            width=20,
            command=self.start_lottery
        )
        start_btn.pack(pady=20)

        reset_btn = ttk.Button(
            center_frame,
            text="重設名單（特別獎）",
            width=20,
            command=self.reset_candidates
        )
        reset_btn.pack(pady=10)

        # =========================
        # 下方：中獎結果
        # =========================
        result_frame = ttk.LabelFrame(self.root, text="中獎結果")
        result_frame.place(x=20, y=300, width=830, height=230)

        self.result_listbox = tk.Listbox(result_frame, font=("Arial", 12))
        self.result_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # =========================
        # 系統訊息
        # =========================
        self.status_label = ttk.Label(
            self.root,
            text="系統就緒",
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_label.place(x=0, y=570, width=900)

    # =========================
    # 行為（暫時是骨架）
    # =========================
    def add_prize(self):
        name = self.prize_name_entry.get().strip()
        quota = self.prize_quota_entry.get().strip()

        if not name or not quota:
            messagebox.showwarning("警告", "請輸入獎項名稱與名額")
            return

        self.status_label.config(text=f"已新增獎項：{name}（名額 {quota}）")

    def start_lottery(self):
        messagebox.showinfo("提示", "抽籤功能尚未實作")
        self.status_label.config(text="開始抽籤")

    def reset_candidates(self):
        confirm = messagebox.askyesno(
            "確認",
            "此操作將重設所有名單，是否繼續？"
        )
        if confirm:
            self.status_label.config(text="名單已重設（特別獎模式）")
