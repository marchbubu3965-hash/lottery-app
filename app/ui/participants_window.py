import tkinter as tk
from tkinter import ttk ,messagebox, filedialog
from app.services.participant_service import ParticipantService


class ParticipantsWindow:
    def __init__(self, parent):
        self.win = tk.Toplevel(parent)
        self.win.title("名單管理")
        self.win.geometry("750x500")
        self.win.resizable(False, False)

        self.service = ParticipantService()
        self._build_ui()
        self._load_data()

    def _build_ui(self):
        # ===== TreeView =====
        self.tree = ttk.Treeview(
            self.win,
            columns=("id", "name", "employee_no", "active"),
            show="headings",
            height=15
        )

        for col, text, width in [
            ("id", "ID", 50),
            ("name", "姓名", 180),
            ("employee_no", "員工編號", 150),
            ("active", "啟用", 80),
        ]:
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width, anchor="center")

        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        # ===== 表單 =====
        form = ttk.Frame(self.win)
        form.pack(pady=5)

        ttk.Label(form, text="姓名").grid(row=0, column=0)
        ttk.Label(form, text="員工編號").grid(row=0, column=2)

        self.name_entry = ttk.Entry(form, width=15)
        self.emp_entry = ttk.Entry(form, width=15)

        self.name_entry.grid(row=0, column=1, padx=5)
        self.emp_entry.grid(row=0, column=3, padx=5)

        # ===== 按鈕 =====
        btn_frame = ttk.Frame(self.win)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="新增", command=self.add).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="修改", command=self.update).grid(row=0, column=1, padx=5)
        ttk.Button(btn_frame, text="刪除", command=self.delete).grid(row=0, column=2, padx=5)
        ttk.Button(btn_frame, text="切換啟用", command=self.toggle).grid(row=0, column=3, padx=5)
        ttk.Button(btn_frame, text="Excel 匯入", command=self.import_excel)\
            .grid(row=0, column=4, padx=5)

    def _load_data(self):
        self.tree.delete(*self.tree.get_children())
        for row in self.service.get_all_participants():
            self.tree.insert(
                "",
                "end",
                values=(
                    row["id"],
                    row["name"],
                    row["employee_no"],
                    "是" if row["is_active"] else "否"
                )
            )

    def on_select(self, event):
        item = self.tree.item(self.tree.selection()[0])
        self.selected_id = item["values"][0]

        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, item["values"][1])

        self.emp_entry.delete(0, tk.END)
        self.emp_entry.insert(0, item["values"][2] or "")

    def add(self):
        if not self.name_entry.get():
            messagebox.showwarning("錯誤", "姓名不可空白")
            return

        self.service.add(
            self.name_entry.get(),
            self.emp_entry.get()
        )
        self._load_data()

    def update(self):
        if not self.selected_id:
            return

        self.service.update(
            self.selected_id,
            self.name_entry.get(),
            self.emp_entry.get()
        )
        self._load_data()

    def delete(self):
        if not self.selected_id:
            return

        if messagebox.askyesno("確認", "確定刪除？"):
            self.service.delete(self.selected_id)
            self._load_data()

    # def toggle_active(self):
    #     selected = self.tree.selection()
    #     if not selected:
    #         messagebox.showwarning("提示", "請選擇一筆資料")
    #         return

    #     item = self.tree.item(selected[0])
    #     pid, _, _, active_text = item["values"]

    #     new_status = active_text != "是"
    #     self.service.set_active(pid, new_status)
    #     self._load_data()

    def toggle(self):
        if not self.selected_id:
            return

        item = self.tree.item(self.tree.selection()[0])
        active = item["values"][3] == "是"
        self.service.set_active(self.selected_id, not active)
        self._load_data()

    def import_excel(self):
        path = filedialog.askopenfilename(
            filetypes=[("Excel Files", "*.xlsx")]
        )
        if not path:
            return

        count = self.service.import_from_excel(path)
        messagebox.showinfo("完成", f"成功匯入 {count} 筆")
        self._load_data()