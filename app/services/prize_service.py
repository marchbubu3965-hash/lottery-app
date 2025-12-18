from typing import List, Tuple
from app.db.database import get_connection


class PrizeService:

    def create_prize(
        self,
        name: str,
        quota: int,
        draw_order: int,
        is_special: int = 0
    ) -> None:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO prizes (name, quota, draw_order, is_special)
            VALUES (?, ?, ?, ?)
        """, (name, quota, draw_order, is_special))

        conn.commit()
        conn.close()

    def get_all_prizes(self) -> List[Tuple]:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, name, quota, draw_order, is_special
            FROM prizes
            ORDER BY draw_order
        """)

        rows = cursor.fetchall()
        conn.close()
        return rows
