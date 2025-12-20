import tkinter as tk
from tkinter import ttk, messagebox
from app.ui.history_window import HistoryWindow
from app.ui.participants_window import ParticipantsWindow
from app.ui.prizes_window import PrizesWindow
from app.services.lottery_service import LotteryService
from app.services.participant_service import ParticipantService
from app.services.admin_service import AdminService
import sys




class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("抽籤系統")
        self.root.geometry("900x600")
        self.root.resizable(False, False)
        self._lottery_results = []
        self._current_prize_index = 0
        self._animation_lines = []
        self._animation_index = 0

        self._build_ui()

    def _build_ui(self):
        # =========================
        # 左側：獎項設定
        # =========================
        left_frame = ttk.LabelFrame(self.root, text="管理設定")
        left_frame.place(x=20, y=20, width=400, height=260)

        add_prize_btn = ttk.Button(
            left_frame,
            text="獎項管理",
            command=self.open_prizes
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

        self.next_btn = ttk.Button(
            center_frame,
            text="繼續下一個獎項",
            width=20,
            command=self.start_lottery,
            state="disabled"   # 預設不可按
        )
        self.next_btn.pack(pady=5)

        history_btn = ttk.Button(
            center_frame,
            text="查看歷史中獎",
            width=20,
            command=self.open_history
        )
        history_btn.pack(pady=10)


        reset_btn = ttk.Button(
            center_frame,
            text="重設名單（特別獎）",
            width=20,
            command=self.reset_candidates
        )
        reset_btn.pack(pady=10)

        # =========================
        # 查看資料
        # =========================
        view_frame = ttk.Frame(center_frame)
        view_frame.pack(pady=10)

        ttk.Button(
            left_frame,
            text="名單管理",
            command=lambda: ParticipantsWindow(self.root)
        ).grid(row=3, column=0, columnspan=2, pady=10)

        reset_btn = ttk.Button(
            self.root,
            text="⚠ 清空中獎名單（測試用）",
            command=self.reset_lottery_results
        )
        reset_btn.place(x=650, y=260, width=200)

        # =========================
        # 下方：中獎結果
        # =========================
        result_frame = ttk.LabelFrame(self.root, text="中獎結果")
        result_frame.place(x=20, y=300, width=830, height=230)

        self.result_listbox = tk.Listbox(
            result_frame,
            font=("Arial", 14),
            bg="black",
            fg="white",          # 白字
            selectbackground="#444444",
            selectforeground="white"
        )

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

    def start_lottery(self):
        # 第一次按 → 真正執行抽籤
        if not self._lottery_results:
            self._lock_ui()  # 立刻鎖，避免重複觸發

            svc = LotteryService()
            try:
                self._lottery_results = svc.run_lottery()
            except Exception as e:
                self._unlock_ui()
                messagebox.showerror("錯誤", str(e))
                return

            self._current_prize_index = 0
            self.result_listbox.delete(0, tk.END)

        # 如果還有獎項沒抽
        if self._current_prize_index < len(self._lottery_results):
            self._lock_ui()              # 每個獎項開始前鎖 UI
            self._start_next_prize()
        else:
            self._unlock_ui()
            messagebox.showinfo("完成", "所有獎項已抽完")
            self.status_label.config(text="抽籤完成")


    def _start_next_prize(self):
        prize_result = self._lottery_results[self._current_prize_index]

        prize_name = prize_result["prize"]
        is_special = prize_result.get("is_special", 0)
        tag = "🎯 特別獎" if is_special else "一般獎"

        winners = prize_result.get("winners", [])

        self._animation_lines = []
        self._animation_index = 0

        # 顯示獎項標題
        self._animation_lines.append(f"=== {prize_name}（{tag}）===")

        if not winners:
            self._animation_lines.append("無中獎者")
        else:
            for w in winners:
                self._animation_lines.append(
                    f"{w['name']}（{w['employee_no']}）"
                )

        self.status_label.config(text=f"抽籤中：{prize_name}")
        self._show_next_line()

    def _show_next_line(self):
        if self._animation_index >= len(self._animation_lines):
            self._current_prize_index += 1

            # ===== 判斷是否全部抽完 =====
            if self._current_prize_index >= len(self._lottery_results):
                self.next_btn.state(["disabled"])
                self._unlock_ui()
                self.status_label.config(text="🎉 抽籤完成")
                messagebox.showinfo("完成", "所有獎項已抽完")
            else:
                self.next_btn.state(["!disabled"])
                self.status_label.config(text="請按『繼續下一個獎項』")

            return

        line = self._animation_lines[self._animation_index]
        index = self.result_listbox.size()
        self.result_listbox.insert(tk.END, line)
        self.result_listbox.see(tk.END)

        if "🎯 特別獎" in line:
            self.result_listbox.itemconfig(index, fg="red")
        else:
            self.result_listbox.itemconfig(index, fg="white")

        # 音效、高亮動畫
        self._play_sound()
        self.result_listbox.itemconfig(index, bg="#FFF2CC")
        self.root.after(
            300,
            lambda i=index: self.result_listbox.itemconfig(i, bg="black")
        )

        self._animation_index += 1
        self.root.after(500, self._show_next_line)

    def reset_candidates(self):
        confirm = messagebox.askyesno(
            "確認",
            "此操作將重設所有名單為『可抽狀態』，\n歷史中獎紀錄不會被刪除。\n\n是否繼續？"
        )
        if not confirm:
            return

        try:
            service = ParticipantService()
            count = service.reset_all_participants()

            self.status_label.config(
                text=f"名單已重設，共 {count} 人恢復可抽狀態"
            )
            messagebox.showinfo(
                "完成",
                f"已成功重設 {count} 筆名單"
            )

        except Exception as e:
            messagebox.showerror(
                "錯誤",
                f"重設名單失敗：\n{e}"
            )
    def reset_lottery_results(self):
        confirm = messagebox.askyesno(
            "⚠ 危險操作",
            "此操作將【永久刪除】所有中獎紀錄與抽獎場次，\n"
            "並重設名單狀態。\n\n"
            "⚠ 僅限測試使用，是否繼續？"
        )
        if not confirm:
            return

        try:
            AdminService().reset_lottery_data()
            self._reset_lottery_state()
            self.result_listbox.delete(0, tk.END)
            messagebox.showinfo("完成", "中獎名單已清空")
        except Exception as e:
            messagebox.showerror("錯誤", str(e))

    def _reset_lottery_state(self):
        # 抽籤流程狀態
        self._lottery_results = []
        self._current_prize_index = 0
        self._animation_lines = []
        self._animation_index = 0

        # UI
        self.result_listbox.delete(0, tk.END)
        self.next_btn.state(["disabled"])
        self._unlock_ui()

        self.status_label.config(text="系統已重設，請重新開始抽籤")


    def open_history(self):
        HistoryWindow(self.root)

    def open_participants(self):
        ParticipantsWindow(self.root)

    def open_prizes(self):
        PrizesWindow(self.root)

    def _lock_ui(self):
        self._set_buttons_state(self.root, "disabled")

    def _unlock_ui(self):
        self._set_buttons_state(self.root, "!disabled")

    def _set_buttons_state(self, widget, state):
        for child in widget.winfo_children():
            if isinstance(child, ttk.Button):
                # 👉 排除「繼續下一個獎項」
                if child is self.next_btn:
                    continue
                child.state([state])
            else:
                self._set_buttons_state(child, state)

    def _play_sound(self):
        try:
            if sys.platform.startswith("win"):
                import winsound
                winsound.Beep(1200, 120)  # 頻率, 毫秒
            else:
                self.root.bell()
        except Exception:
            pass

