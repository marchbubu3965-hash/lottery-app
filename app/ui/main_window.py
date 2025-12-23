import tkinter as tk
from tkinter import ttk, messagebox
from enum import Enum, auto
import sys
from pathlib import Path

from app.services.lottery_service import LotteryService
from app.services.admin_service import AdminService

from app.ui.history_window import HistoryWindow
from app.ui.participants_window import ParticipantsWindow
from app.ui.prizes_window import PrizesWindow
from app.ui.special_wheel_window import SpecialWheelWindow
from app.core.lottery_state_machine import LotteryStateMachine, LotteryState

# ==================================================
# 主視窗
# ==================================================
class MainWindow:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("抽籤系統")
        self.root.geometry("900x600")
        self.root.resizable(False, False)

        # 狀態
        self.sm = LotteryStateMachine()
        self._after_id = None

        # 抽籤資料
        self._lottery_results = []
        self._current_prize_index = 0

        # 動畫
        self._animation_lines = []
        self._animation_index = 0

        # 背景圖
        base_dir = Path(__file__).resolve().parents[2]
        bg_path = base_dir / "assets" / "images" / "main_background.png"

        self.bg_image = tk.PhotoImage(file=str(bg_path))
        self.bg_label = tk.Label(self.root, image=self.bg_image)
        self.bg_label.place(x=-65, y=-130, width=900, height=600)

        # === 公司 Logo（純視覺）===
        logo_path = base_dir / "assets" / "icons" / "main_logo.png"
        self.logo_image = tk.PhotoImage(file=str(logo_path))
        self.logo_label = tk.Label(
            self.root,
            image=self.logo_image,
            bd=0,
            highlightthickness=0
        )
        self.logo_label.place(x=20, y=10)

        self._build_ui()
        self._sync_ui_with_state()

    # ==================================================
    # UI 建立
    # ==================================================
    def _build_ui(self):
        # 背景圖永遠在最底層
        self.bg_label.lower()
        self.logo_label.lift()


        # 左側管理
        left = ttk.LabelFrame(self.root, text="管理設定")
        left.place(x=20, y=120, width=200, height=160)

        ttk.Button(left, text="獎項管理", command=self.open_prizes)\
            .pack(pady=15)

        ttk.Button(left, text="名單管理",
                   command=lambda: ParticipantsWindow(self.root))\
            .pack(pady=10)

        # 中央控制
        center = ttk.LabelFrame(self.root, text="抽籤控制")
        center.place(x=550, y=40, width=300, height=240)

        self.start_btn = ttk.Button(
            center, text="開始抽籤", width=25, command=self.start_lottery
        )
        self.start_btn.pack(pady=10)

        self.next_btn = ttk.Button(
            center, text="繼續下一個獎項", width=25, command=self.next_prize
        )
        self.next_btn.pack(pady=5)

        self.pause_btn = ttk.Button(
            center, text="暫停", width=25, command=self.toggle_pause
        )
        self.pause_btn.pack(pady=5)

        self.history_btn = ttk.Button(
            center, text="查看歷史中獎", width=25, command=self.open_history
        )
        self.history_btn.pack(pady=10)

        ttk.Button(
            self.root, text="⚠ 清空中獎名單（測試用）",
            command=self.reset_lottery_results
        ).place(x=650, y=240, width=200)

        # 中獎結果
        result = ttk.LabelFrame(self.root, text="中獎結果")
        result.place(x=20, y=340, width=830, height=220)

        self.result_listbox = tk.Listbox(
            result,
            font=("Arial", 14),
            bg="black",
            fg="white",
            selectbackground="#444444",
            selectforeground="white"
        )
        self.result_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 狀態列
        self.status_label = ttk.Label(
            self.root, text="系統就緒",
            relief=tk.SUNKEN, anchor=tk.W
        )
        self.status_label.place(x=0, y=570, width=900)

    # ==================================================
    # 狀態同步
    # ==================================================
    def _refresh_ui(self):
        self._sync_ui_with_state()


    def _sync_ui_with_state(self):
        if self.sm.state == LotteryState.IDLE:
            self._unlock_ui()
            self.next_btn.state(["disabled"])
            self.pause_btn.state(["disabled"])
            self.history_btn.state(["!disabled"])
            self.status_label.config(text="系統就緒")

        elif self.sm.state == LotteryState.RUNNING:
            self._lock_ui()
            self.pause_btn.state(["!disabled"])
            self.history_btn.state(["disabled"])
            self.status_label.config(text="抽籤中...")

        elif self.sm.state == LotteryState.PAUSED:
            self._unlock_ui()
            self.pause_btn.config(text="繼續")
            self.history_btn.state(["disabled"])
            self.status_label.config(text="⏸ 已暫停")

        elif self.sm.state == LotteryState.WAIT_NEXT:
            self._unlock_ui()
            self.next_btn.state(["!disabled"])
            self.pause_btn.state(["disabled"])
            self.history_btn.state(["disabled"])
            self.status_label.config(text="請繼續下一個獎項")

        elif self.sm.state == LotteryState.FINISHED:
            self._unlock_ui()
            self.next_btn.state(["disabled"])
            self.pause_btn.state(["disabled"])
            self.history_btn.state(["!disabled"])
            self.status_label.config(text="🎉 抽籤完成")

    # ==================================================
    # 抽籤流程
    # ==================================================
    def start_lottery(self):
        try:
            self.sm.start()
        except ValueError:
            return

        self._lottery_results = LotteryService().run_lottery()
        if not self._lottery_results:
            messagebox.showwarning("無資料", "目前沒有可抽的獎項")
            self.sm.reset()
            self._refresh_ui()
            return

        self._current_prize_index = 0
        self.result_listbox.delete(0, tk.END)

        self._refresh_ui()
        self._start_next_prize()


    def next_prize(self):
        try:
            self.sm.next_round()
        except ValueError:
            return

        self._refresh_ui()
        self._start_next_prize()



    def _start_next_prize(self):
        prize = self._lottery_results[self._current_prize_index]
        winners = prize.get("winners", [])

        # === 特別獎 → 輪盤 ===
        if prize.get("is_special") and winners:
            SpecialWheelWindow(
                self.root,
                items=[w["name"] for w in winners],
                # on_finish=self._after_special_wheel
                on_finish=lambda winner, p=prize: self._after_special_wheel(p, winner)
            )
            return

        # === 一般獎 ===
        self._animation_lines = []
        self._animation_index = 0

        tag = "🎯 特別獎" if prize.get("is_special") else "一般獎"
        self._animation_lines.append(f"=== {prize['prize']}（{tag}）===")

        if not winners:
            self._animation_lines.append("無中獎者")
        else:
            for w in winners:
                self._animation_lines.append(
                    f"{w['name']}（{w['employee_no']}）"
                )

        self._show_next_line()


    def _after_special_wheel(self, prize, winner_name):
        """
        特別獎輪盤結束後
        """

        self._animation_lines = []
        self._animation_index = 0

        self._animation_lines.append(
            f"=== {prize['prize']}（🎯 特別獎）==="
        )

        # ✅ 只顯示輪盤選中的那一位
        for w in prize.get("winners", []):
            if w["name"] == winner_name:
                self._animation_lines.append(
                    f"{w['name']}（{w['employee_no']}）"
                )
                break

        self._show_next_line()


    def _prepare_animation(self, prize):
        self._animation_lines = []
        self._animation_index = 0

        tag = "🎯 特別獎" if prize.get("is_special") else "一般獎"
        self._animation_lines.append(f"=== {prize['prize']}（{tag}）===")

        winners = prize.get("winners", [])
        if not winners:
            self._animation_lines.append("無中獎者")
        else:
            for w in winners:
                self._animation_lines.append(
                    f"{w['name']}（{w['employee_no']}）"
                )

        self._show_next_line()

    def _show_next_line(self):
        if self.sm.state == LotteryState.PAUSED:
            return

        if self._animation_index >= len(self._animation_lines):
            self._current_prize_index += 1
            if self._current_prize_index >= len(self._lottery_results):
                self.sm.finish()
                self._refresh_ui()
                messagebox.showinfo("完成", "所有獎項已抽完")
            else:
                self.sm.wait_next()
                self._refresh_ui()
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

        self._animation_index += 1
        self._after_id = self.root.after(500, self._show_next_line)

    def toggle_pause(self):
        try:
            if self.sm.state == LotteryState.RUNNING:
                self.sm.pause()
            elif self.sm.state == LotteryState.PAUSED:
                self.sm.resume()
        except ValueError:
            return

        self._refresh_ui()

        if self.sm.state == LotteryState.RUNNING:
            self._show_next_line()


    # ==================================================
    # 其他功能
    # ==================================================
    def open_history(self):
        if self.sm.state not in (LotteryState.IDLE, LotteryState.FINISHED):
            messagebox.showwarning(
                "操作受限",
                "僅能在尚未開始或抽籤完成後查看"
            )
            return
        HistoryWindow(self.root)

    def open_prizes(self):
        PrizesWindow(self.root)

    def reset_lottery_results(self):
        if not messagebox.askyesno("警告", "確定清空所有抽獎資料？"):
            return
        AdminService().reset_lottery_data()
        self._reset_all()
        messagebox.showinfo("完成", "抽獎資料已清空")

    def _reset_all(self):
        self._lottery_results.clear()
        self._current_prize_index = 0
        self._animation_lines.clear()
        self._animation_index = 0
        self.result_listbox.delete(0, tk.END)
        self.sm.reset()
        self._refresh_ui()

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
