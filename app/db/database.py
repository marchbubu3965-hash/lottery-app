import sqlite3
import sys
from pathlib import Path
from hashlib import sha256

# ==================================================
# 應用程式名稱（資料夾用）
# ==================================================
APP_NAME = "LotteryApp"

# ==================================================
# 使用者資料目錄（可寫、永久保存）
# macOS: ~/Library/Application Support/LotteryApp
# Windows: C:\Users\xxx\LotteryApp
# ==================================================
def get_app_data_dir() -> Path:
    home = Path.home()

    if sys.platform == "darwin":
        base = home / "Library" / "Application Support"
    elif sys.platform.startswith("win"):
        base = home
    else:
        base = home

    app_dir = base / APP_NAME
    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir


# ==================================================
# 資料庫路徑（永久、可寫）
# ==================================================
DATA_DIR = get_app_data_dir()
DB_PATH = DATA_DIR / "lottery.db"


# ==================================================
# PyInstaller / 開發環境 通用資源路徑
# schema.sql 專用（唯讀）
# ==================================================
def resource_path(relative_path: str) -> Path:
    """
    PyInstaller / 開發環境 通用資源路徑
    """
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / relative_path

    # 開發環境：lottery_app/app/db/schema.sql
    return Path(__file__).resolve().parent / relative_path


# ==================================================
# 取得資料庫連線
# ==================================================
def get_connection():
    """
    建立並回傳 SQLite 連線
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


# ==================================================
# 初始化資料庫（建立資料表）
# ==================================================
def init_db():
    """
    若資料庫不存在，建立資料表
    """
    schema_path = resource_path("schema.sql")

    if not schema_path.exists():
        raise FileNotFoundError(f"schema.sql not found: {schema_path}")

    conn = get_connection()
    cursor = conn.cursor()

    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    cursor.executescript(schema_sql)
    conn.commit()
    conn.close()


# ==================================================
# 初始化預設管理者帳號
# ==================================================
def init_default_admin():
    """
    建立預設管理者帳號（若不存在）
    """
    default_username = "admin"
    default_password = "admin123"  # 建議首次登入後修改
    password_hash = sha256(default_password.encode("utf-8")).hexdigest()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM users WHERE username = ?",
        (default_username,)
    )

    if cursor.fetchone() is None:
        cursor.execute(
            """
            INSERT INTO users (username, password_hash)
            VALUES (?, ?)
            """,
            (default_username, password_hash)
        )
        conn.commit()

    conn.close()


# ==================================================
# 一次性初始化入口（App 啟動時呼叫）
# ==================================================
def setup_database():
    """
    App 啟動時呼叫：
    - DB 不存在 → 建立資料表
    - 建立預設管理者帳號
    """
    if not DB_PATH.exists():
        init_db()

    init_default_admin()
