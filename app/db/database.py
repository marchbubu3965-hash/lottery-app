import sqlite3
from pathlib import Path

# -----------------------------
# 資料庫檔案位置設定
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "lottery.db"

SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"


# -----------------------------
# 取得資料庫連線
# -----------------------------
def get_connection():
    """
    建立並回傳 SQLite 連線
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


# -----------------------------
# 初始化資料庫（建立資料表）
# -----------------------------
def init_db():
    """
    若資料庫或資料表不存在，則建立
    """
    DATA_DIR.mkdir(exist_ok=True)

    conn = get_connection()
    cursor = conn.cursor()

    if not SCHEMA_PATH.exists():
        raise FileNotFoundError("schema.sql not found")

    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    cursor.executescript(schema_sql)
    conn.commit()
    conn.close()


# -----------------------------
# 初始化預設資料
# -----------------------------
def init_default_admin():
    """
    建立預設管理者帳號（若不存在）
    """
    from hashlib import sha256

    default_username = "admin"
    default_password = "admin123"  # 建議第一次登入後修改
    password_hash = sha256(default_password.encode("utf-8")).hexdigest()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM users WHERE username = ?",
        (default_username,)
    )
    exists = cursor.fetchone()

    if not exists:
        cursor.execute(
            """
            INSERT INTO users (username, password_hash)
            VALUES (?, ?)
            """,
            (default_username, password_hash)
        )
        conn.commit()

    conn.close()


# -----------------------------
# 一次性初始化入口
# -----------------------------
def setup_database():
    """
    專案啟動時呼叫：
    - 建立資料庫
    - 建立資料表
    - 建立預設帳號
    """
    init_db()
    init_default_admin()
