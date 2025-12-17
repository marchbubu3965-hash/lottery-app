from hashlib import sha256
from app.db.database import get_connection


class AuthService:
    """
    負責使用者登入驗證
    """

    @staticmethod
    def hash_password(password: str) -> str:
        """
        將密碼轉成 SHA-256 雜湊
        """
        return sha256(password.encode("utf-8")).hexdigest()

    @staticmethod
    def authenticate(username: str, password: str) -> bool:
        """
        驗證帳號密碼是否正確
        """
        password_hash = AuthService.hash_password(password)

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id
            FROM users
            WHERE username = ? AND password_hash = ?
            """,
            (username, password_hash)
        )

        user = cursor.fetchone()
        conn.close()

        return user is not None
