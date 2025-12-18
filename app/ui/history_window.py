import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from app.services.lottery_history_service import LotteryHistoryService
import openpyxl
from datetime import datetime



class HistoryWindow(tk.Toplevel):
    """
    歷史中獎紀錄視窗
    """

    def __init__(self, master=None):
        super().__init__(master)

        self.title("歷史中獎紀錄")
        self.geometry("700x400")

        self.history_service = LotteryHistoryService()

        self._build_ui()
        self._load_data()

    # ==================================================
    # UI
    # ==================================================
    def _build_ui(self):
        top_frame = ttk.Frame(self)
        top_frame.pack(fill=tk.X, padx=10, pady=5)

        export_btn = ttk.Button(
            top_frame,
            text="匯出 Excel",
            command=self.export_to_excel
        )
        export_btn.pack(side=tk.RIGHT)
        columns = ("prize", "special", "name", "time")

        self.tree = ttk.Treeview(
            self,
            columns=columns,
            show="headings"
        )
        self.tree.tag_configure(
            "special",
            background="#FFF2CC"  # 淡黃色（特別獎）
        )
        self.tree.heading("prize", text="獎項")
        self.tree.heading("special", text="特別獎")
        self.tree.heading("name", text="中獎者")
        self.tree.heading("time", text="抽籤時間")

        self.tree.column("prize", width=150)
        self.tree.column("special", width=80, anchor="center")
        self.tree.column("name", width=150)
        self.tree.column("time", width=180)

        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 捲軸
        scrollbar = ttk.Scrollbar(
            self,
            orient="vertical",
            command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # ==================================================
    # 資料載入
    # ==================================================
    def _load_data(self):
        records = self.history_service.get_all_records()

        for row in records:
            tag = "special" if row["is_special"] else ""
            self.tree.insert(
                "",
                tk.END,
                values=(
                    row["prize_name"],
                    "是" if row["is_special"] else "否",
                    row["participant_name"],
                    row["drawn_at"]
                ),
                tags=(tag,)
            )


    def export_to_excel(self):
        records = self.history_service.get_all_records()

        if not records:
            messagebox.showinfo("提示", "目前沒有中獎紀錄")
            return

        today = datetime.now().strftime("%Y%m%d")
        default_filename = f"lottery_history_{today}.xlsx"

        file_path = filedialog.asksaveasfilename(
            initialfile=default_filename,
            defaultextension=".xlsx",
            filetypes=[("Excel 檔案", "*.xlsx")]
        )

        if not file_path:
            return

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "歷史中獎紀錄"

        ws.append(["獎項", "特別獎", "中獎者", "抽籤時間"])

        for r in records:
            ws.append([
                r["prize_name"],
                "是" if r["is_special"] else "否",
                r["participant_name"],
                r["drawn_at"]
            ])

        wb.save(file_path)

        messagebox.showinfo("完成", "Excel 匯出完成")


