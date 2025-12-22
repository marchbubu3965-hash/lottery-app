import tkinter as tk

from app.ui.main_window import MainWindow


def run_lottery_app():
    """
    抽籤系統主入口
    """
    root = tk.Tk()
    MainWindow(root)
    root.mainloop()


# 允許直接執行此檔案
if __name__ == "__main__":
    run_lottery_app()
