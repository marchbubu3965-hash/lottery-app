import tkinter as tk
from tkinter import ttk, messagebox
from app.services.prize_service import PrizeService


class PrizesWindow:
    def __init__(self, parent):
        self.win = tk.Toplevel(parent)
        self.win.title("獎項管理")
        self.win.geometry("750x500")
        self.win.resizable(False, False)

        self.service = PrizeService()
        self.selected_id = None

        self._build_ui()
        self.load_data()

    def _build_ui(self):
        # ===== TreeView =====
        self.tree = ttk.Treeview(
            self.win,
            columns=("id", "name", "quota", "order", "special"),
            show="headings",
            height=15
        )

        for col, text, width in [
            ("id", "ID", 50),
            ("name", "獎項名稱", 180),
            ("quota", "名額", 80),
            ("order", "順序", 80),
            ("special", "特別獎", 80),
        ]:
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width, anchor="center")

        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        # ===== 表單 =====
        form = ttk.Frame(self.win)
        form.pack(pady=5)

        ttk.Label(form, text="名稱").grid(row=0, column=0)
        ttk.Label(form, text="名額").grid(row=0, column=2)
        ttk.Label(form, text="順序").grid(row=1, column=0)

        self.name_entry = ttk.Entry(form, width=15)
        self.quota_entry = ttk.Entry(form, width=15)
        self.order_entry = ttk.Entry(form, width=15)

        self.name_entry.grid(row=0, column=1, padx=5)
        self.quota_entry.grid(row=0, column=3, padx=5)
        self.order_entry.grid(row=1, column=1, padx=5)

        self.special_var = tk.IntVar()
        ttk.Checkbutton(
            form,
            text="特別獎",
            variable=self.special_var
        ).grid(row=1, column=3)

        # ===== 按鈕 =====
        btn_frame = ttk.Frame(self.win)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="新增", command=self.add).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="修改", command=self.update).grid(row=0, column=1, padx=5)
        ttk.Button(btn_frame, text="刪除", command=self.delete).grid(row=0, column=2, padx=5)

    # =========================
    # 行為
    # =========================
    def load_data(self):
        # ⭐ 關鍵修正 1：重載資料時清空選取狀態
        self.selected_id = None

        self.tree.delete(*self.tree.get_children())
        for r in self.service.get_all():
            self.tree.insert("", "end", values=(
                r["id"],
                r["name"],
                r["quota"],
                r["draw_order"],
                "是" if r["is_special"] else "否"
            ))

    def on_select(self, event):
        # ⭐ 關鍵修正 2：防止 selection 為空
        selected = self.tree.selection()
        if not selected:
            return

        item = self.tree.item(selected[0])
        values = item.get("values")
        if not values:
            return

        self.selected_id = values[0]

        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, values[1])

        self.quota_entry.delete(0, tk.END)
        self.quota_entry.insert(0, values[2])

        self.order_entry.delete(0, tk.END)
        self.order_entry.insert(0, values[3])

        self.special_var.set(1 if values[4] == "是" else 0)

    def add(self):
        if not self.name_entry.get().strip():
            messagebox.showwarning("錯誤", "名稱不可空白")
            return

        try:
            self.service.add(
                self.name_entry.get().strip(),
                int(self.quota_entry.get()),
                int(self.order_entry.get()),
                self.special_var.get()
            )
        except ValueError:
            messagebox.showerror("錯誤", "名額與順序必須是數字")
            return

        self.load_data()

    def update(self):
        if not self.selected_id:
            messagebox.showwarning("提示", "請先選擇一筆資料")
            return

        try:
            self.service.update(
                self.selected_id,
                self.name_entry.get().strip(),
                int(self.quota_entry.get()),
                int(self.order_entry.get()),
                self.special_var.get()
            )
        except ValueError:
            messagebox.showerror("錯誤", "名額與順序必須是數字")
            return

        self.load_data()

    def delete(self):
        if not self.selected_id:
            messagebox.showwarning("提示", "請先選擇一筆資料")
            return

        if messagebox.askyesno("確認", "確定刪除該獎項？"):
            self.service.delete(self.selected_id)
            self.load_data()
