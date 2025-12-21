import tkinter as tk
from tkinter import ttk, messagebox
from enum import Enum, auto
import sys

from app.ui.history_window import HistoryWindow
from app.ui.participants_window import ParticipantsWindow
from app.ui.prizes_window import PrizesWindow
from app.services.lottery_service import LotteryService
from app.services.participant_service import ParticipantService
from app.services.admin_service import AdminService


# =========================
# 狀態機定義
# =========================
class LotteryState(Enum):
    IDLE = auto()
    RUNNING = auto()
    PAUSED = auto()
    WAIT_NEXT = auto()
    FINISHED = auto()


class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("抽籤系統")
        self.root.geometry("900x600")
        self.root.resizable(False, False)

        self.state = LotteryState.IDLE
        self._after_id = None

        self._lottery_results = []
        self._current_prize_index = 0
        self._animation_lines = []
        self._animation_index = 0

        self._build_ui()
        self._sync_ui_with_state()

    # ==================================================
    # UI
    # ==================================================
    def _build_ui(self):
        # 左側
        left_frame = ttk.LabelFrame(self.root, text="管理設定")
        left_frame.place(x=20, y=20, width=400, height=260)

        ttk.Button(
            left_frame,
            text="獎項管理",
            command=self.open_prizes
        ).grid(row=0, column=0, columnspan=2, pady=15)

        ttk.Button(
            left_frame,
            text="名單管理",
            command=lambda: ParticipantsWindow(self.root)
        ).grid(row=1, column=0, columnspan=2, pady=10)

        # 中央
        center_frame = ttk.LabelFrame(self.root, text="抽籤控制")
        center_frame.place(x=450, y=20, width=400, height=260)

        ttk.Button(
            center_frame,
            text="開始抽籤",
            width=25,
            command=self.start_lottery
        ).pack(pady=10)

        self.next_btn = ttk.Button(
            center_frame,
            text="繼續下一個獎項",
            width=25,
            command=self.next_prize
        )
        self.next_btn.pack(pady=5)

        self.pause_btn = ttk.Button(
            center_frame,
            text="暫停",
            width=25,
            command=self.toggle_pause
        )
        self.pause_btn.pack(pady=5)

        self.history_btn = ttk.Button(
            center_frame,
            text="查看歷史中獎",
            width=25,
            command=self.open_history
        )
        self.history_btn.pack(pady=10)

        ttk.Button(
            center_frame,
            text="重設名單（特別獎）",
            width=25,
            command=self.reset_candidates
        ).pack(pady=5)

        ttk.Button(
            self.root,
            text="⚠ 清空中獎名單（測試用）",
            command=self.reset_lottery_results
        ).place(x=650, y=260, width=200)

        # 中獎結果
        result_frame = ttk.LabelFrame(self.root, text="中獎結果")
        result_frame.place(x=20, y=300, width=830, height=230)

        self.result_listbox = tk.Listbox(
            result_frame,
            font=("Arial", 14),
            bg="black",
            fg="white",
            selectbackground="#444444",
            selectforeground="white"
        )
        self.result_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 狀態列
        self.status_label = ttk.Label(
            self.root,
            text="系統就緒",
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_label.place(x=0, y=570, width=900)

    # ==================================================
    # 狀態控制
    # ==================================================
    def _set_state(self, new_state: LotteryState):
        self.state = new_state
        self._sync_ui_with_state()

    def _sync_ui_with_state(self):
        if self.state == LotteryState.IDLE:
            self._unlock_ui()
            self.next_btn.state(["disabled"])
            self.pause_btn.state(["disabled"])
            self.history_btn.state(["!disabled"])
            self.status_label.config(text="系統就緒")

        elif self.state == LotteryState.RUNNING:
            self._lock_ui()
            self.pause_btn.state(["!disabled"])
            self.history_btn.state(["disabled"])
            self.status_label.config(text="抽籤中...")

        elif self.state == LotteryState.PAUSED:
            self._unlock_ui()
            self.pause_btn.config(text="繼續")
            self.history_btn.state(["disabled"])
            self.status_label.config(text="⏸ 已暫停")

        elif self.state == LotteryState.WAIT_NEXT:
            self._unlock_ui()
            self.next_btn.state(["!disabled"])
            self.pause_btn.state(["disabled"])
            self.history_btn.state(["disabled"])
            self.status_label.config(text="請按『繼續下一個獎項』")

        elif self.state == LotteryState.FINISHED:
            self._unlock_ui()
            self.next_btn.state(["disabled"])
            self.pause_btn.state(["disabled"])
            self.history_btn.state(["!disabled"])
            self.status_label.config(text="🎉 抽籤完成")

    # ==================================================
    # 抽籤流程
    # ==================================================
    def start_lottery(self):
        if self.state != LotteryState.IDLE:
            return

        self._lottery_results = LotteryService().run_lottery()
        if not self._lottery_results:
            messagebox.showwarning("無資料", "目前沒有可抽的獎項")
            return

        self._current_prize_index = 0
        self.result_listbox.delete(0, tk.END)

        self._set_state(LotteryState.RUNNING)
        self._start_next_prize()

    def next_prize(self):
        if self.state != LotteryState.WAIT_NEXT:
            return

        self._set_state(LotteryState.RUNNING)
        self._start_next_prize()

    def _start_next_prize(self):
        prize = self._lottery_results[self._current_prize_index]

        self._animation_lines = []
        self._animation_index = 0

        tag = "🎯 特別獎" if prize.get("is_special") else "一般獎"
        self._animation_lines.append(f"=== {prize['prize']}（{tag}）===")

        winners = prize.get("winners", [])
        if not winners:
            self._animation_lines.append("無中獎者")
        else:
            for w in winners:
                self._animation_lines.append(f"{w['name']}（{w['employee_no']}）")

        self._show_next_line()

    def _show_next_line(self):
        if self.state == LotteryState.PAUSED:
            return

        if self._animation_index >= len(self._animation_lines):
            self._current_prize_index += 1
            if self._current_prize_index >= len(self._lottery_results):
                self._set_state(LotteryState.FINISHED)
                messagebox.showinfo("完成", "所有獎項已抽完")
            else:
                self._set_state(LotteryState.WAIT_NEXT)
            return

        line = self._animation_lines[self._animation_index]
        idx = self.result_listbox.size()
        self.result_listbox.insert(tk.END, line)
        self.result_listbox.see(tk.END)

        self.result_listbox.itemconfig(
            idx,
            fg="red" if "🎯 特別獎" in line else "white"
        )

        self._play_sound()
        self.result_listbox.itemconfig(idx, bg="#333333")
        self.root.after(300, lambda i=idx: self.result_listbox.itemconfig(i, bg="black"))

        self._animation_index += 1
        self._after_id = self.root.after(500, self._show_next_line)

    def toggle_pause(self):
        if self.state == LotteryState.RUNNING:
            if self._after_id:
                self.root.after_cancel(self._after_id)
                self._after_id = None
            self._set_state(LotteryState.PAUSED)

        elif self.state == LotteryState.PAUSED:
            self.pause_btn.config(text="暫停")
            self._set_state(LotteryState.RUNNING)
            self._show_next_line()

    # ==================================================
    # 其他功能
    # ==================================================
    def open_history(self):
        if self.state not in (LotteryState.IDLE, LotteryState.FINISHED):
            messagebox.showwarning(
                "操作受限",
                "僅能在『尚未開始』或『抽籤完成』狀態下查看中獎紀錄"
            )
            return
        HistoryWindow(self.root)

    def open_prizes(self):
        PrizesWindow(self.root)

    def reset_candidates(self):
        if messagebox.askyesno("確認", "確定重設名單？"):
            count = ParticipantService().reset_all_participants()
            messagebox.showinfo("完成", f"已重設 {count} 筆")

    def reset_lottery_results(self):
        if not messagebox.askyesno("⚠ 警告", "確定清空所有抽獎資料？"):
            return
        AdminService().reset_lottery_data()
        self._reset_state()
        messagebox.showinfo("完成", "抽獎資料已清空")

    def _reset_state(self):
        self._lottery_results = []
        self._current_prize_index = 0
        self._animation_lines = []
        self._animation_index = 0
        self.result_listbox.delete(0, tk.END)
        self._set_state(LotteryState.IDLE)

    # ==================================================
    # UI Lock
    # ==================================================
    def _lock_ui(self):
        self._set_buttons_state(self.root, "disabled")

    def _unlock_ui(self):
        self._set_buttons_state(self.root, "!disabled")

    def _set_buttons_state(self, widget, state):
        for c in widget.winfo_children():
            if isinstance(c, ttk.Button):
                if c in (self.next_btn, self.pause_btn, self.history_btn):
                    continue
                c.state([state])
            else:
                self._set_buttons_state(c, state)

    def _play_sound(self):
        try:
            if sys.platform.startswith("win"):
                import winsound
                winsound.Beep(1200, 120)
            else:
                self.root.bell()
        except Exception:
            pass
