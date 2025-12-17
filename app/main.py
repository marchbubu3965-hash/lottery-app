import tkinter as tk

from app.db.database import setup_database
from app.ui.login_window import LoginWindow


def main():
    setup_database()

    root = tk.Tk()
    LoginWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
