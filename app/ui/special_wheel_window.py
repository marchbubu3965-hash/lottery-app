import tkinter as tk
import random
import math


class SpecialWheelWindow:
    def __init__(self, parent, items=None, duration_ms=3000, on_finish=None):
        """
        :param parent: 主視窗 root
        :param duration_ms: 旋轉多久（毫秒）
        :param on_finish: 動畫結束後 callback
        """
        self.items = items or []
        self.on_finish = on_finish
        self.count = len(items)
        self.duration_ms = duration_ms
        self.start_time = None
        self.angle = 0
        self.speed = random.uniform(15, 25)

        self.win = tk.Toplevel(parent)
        self.win.title("🎯 特別獎幸運輪盤")
        self.win.geometry("600x600")
        self.win.transient(parent)
        self.win.grab_set()           # 🔒 鎖定主視窗
        self.win.attributes("-topmost", True)

        self.canvas = tk.Canvas(self.win, width=600, height=600, bg="black")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.center = (300, 300)
        self.radius = 220

        self._draw_static()
        self._draw_pointer()
        self._animate()

    def _draw_static(self):
        # 外圈
        self.canvas.create_oval(
            80, 80, 520, 520,
            outline="gold",
            width=8,
            tags="circle"
        )

        # 中心文字
        self.text_id = self.canvas.create_text(
            300, 300,
            text="SPECIAL\nDRAW",
            fill="red",
            font=("Arial", 36, "bold"),
            justify="center",
            tags="wheel"
        )

    def _animate(self):
        if self.start_time is None:
            self.start_time = self.canvas.winfo_toplevel().tk.call("after", "info")

        # 旋轉文字
        self.angle = (self.angle + self.speed) % 360
        self.canvas.itemconfig(
            self.text_id,
            angle=self.angle
        )

        # 慢慢減速
        self.speed *= 0.97

        if self.speed < 0.5:
            self._stop_and_flash()
            return

        self.win.after(30, self._animate)

    def _draw_pointer(self):
        cx, cy = self.center
        self.canvas.create_polygon(
            cx - 15, cy - self.radius - 10,
            cx + 15, cy - self.radius - 10,
            cx, cy - self.radius + 25,
            fill="red"
        )

    def _stop_and_flash(self):
        step = 360 / self.count
        pointer_angle = (270 - self.angle) % 360
        self.result_index = int(pointer_angle // step)
        self.winner = self.items[self.result_index]
        self.flash_count = 0
        self._flash()

    def _flash(self):
        self.canvas.delete("wheel")

        flash_on = self.flash_count % 2 == 0
        # self._draw_wheel(flash=flash_on)

        self.flash_count += 1

        if self.flash_count < 8:
            self.win.after(180, self._flash)
        else:
            self._reveal()

    def _reveal(self):
        self.canvas.delete("circle")
        # self._draw_wheel(show_text=True, reveal_index=self.result_index)

        self.canvas.create_text(
            300, 300,
            text=f"🎉 {self.winner}",
            fill="gold",
            font=("Arial", 36, "bold"),
            tags="wheel"
        )

        self.win.after(1500, self._close)

    def _close(self):
        self.win.destroy()
        if callable(self.on_finish):
            self.on_finish(self.winner)

    def _finish(self):
        self.win.destroy()
        if callable(self.on_finish):
            self.on_finish()
