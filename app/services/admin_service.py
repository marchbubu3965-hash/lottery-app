# app/services/admin_service.py
from app.db.database import get_connection


class AdminService:

    def reset_lottery_data(self):
        """
        清空所有抽獎相關資料（僅限測試用）
        """
        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("DELETE FROM draw_records")
            cursor.execute("DELETE FROM draw_sessions")
            cursor.execute("""
                UPDATE participants
                SET is_active = 1
            """)

            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
