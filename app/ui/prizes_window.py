import tkinter as tk
from tkinter import ttk, messagebox
from app.services.prize_service import PrizeService


class PrizesWindow:
    def __init__(self, parent):
        self.win = tk.Toplevel(parent)
        self.win.title("獎項管理")
        self.win.geometry("650x450")
        self.win.resizable(False, False)

        self.service = PrizeService()
        self._build_ui()
        self._load_data()

    def _build_ui(self):
        self.tree = ttk.Treeview(
            self.win,
            columns=("id", "name", "quota", "order", "special"),
            show="headings",
            height=12
        )

        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="名稱")
        self.tree.heading("quota", text="名額")
        self.tree.heading("order", text="順序")
        self.tree.heading("special", text="特別獎")

        self.tree.column("id", width=50, anchor="center")
        self.tree.column("special", width=80, anchor="center")

        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        form = ttk.Frame(self.win)
        form.pack(pady=5)

        ttk.Label(form, text="名稱").grid(row=0, column=0)
        ttk.Label(form, text="名額").grid(row=0, column=2)
        ttk.Label(form, text="順序").grid(row=0, column=4)

        self.name_entry = ttk.Entry(form, width=15)
        self.quota_entry = ttk.Entry(form, width=5)
        self.order_entry = ttk.Entry(form, width=5)

        self.name_entry.grid(row=0, column=1, padx=5)
        self.quota_entry.grid(row=0, column=3, padx=5)
        self.order_entry.grid(row=0, column=5, padx=5)

        self.special_var = tk.IntVar()
        ttk.Checkbutton(form, text="特別獎", variable=self.special_var)\
            .grid(row=0, column=6, padx=5)

        ttk.Button(
            self.win,
            text="儲存修改",
            command=self.save_edit
        ).pack(pady=5)

        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    def _load_data(self):
        self.tree.delete(*self.tree.get_children())

        for row in self.service.get_all_prizes():
            self.tree.insert(
                "",
                "end",
                values=(
                    row["id"],
                    row["name"],
                    row["quota"],
                    row["draw_order"],
                    "是" if row["is_special"] else "否"
                )
            )

    def on_select(self, event):
        item = self.tree.item(self.tree.selection()[0])
        pid, name, quota, order, special = item["values"]

        self.selected_id = pid
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, name)

        self.quota_entry.delete(0, tk.END)
        self.quota_entry.insert(0, quota)

        self.order_entry.delete(0, tk.END)
        self.order_entry.insert(0, order)

        self.special_var.set(1 if special == "是" else 0)

    def save_edit(self):
        if not hasattr(self, "selected_id"):
            messagebox.showwarning("提示", "請選擇獎項")
            return

        self.service.update_prize(
            self.selected_id,
            self.name_entry.get(),
            int(self.quota_entry.get()),
            int(self.order_entry.get()),
            self.special_var.get()
        )

        self._load_data()
