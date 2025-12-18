from typing import List, Tuple
from app.db.database import get_connection
import sqlite3


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

    def get_all_prizes(self):
        conn = get_connection()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        cur.execute("""
            SELECT id, name, quota, draw_order, is_special
            FROM prizes
            ORDER BY draw_order
        """)

        rows = cur.fetchall()
        conn.close()
        return rows

    def update_prize(self, prize_id, name, quota, order, is_special):
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            UPDATE prizes
            SET name = ?, quota = ?, draw_order = ?, is_special = ?
            WHERE id = ?
        """, (name, quota, order, is_special, prize_id))

        conn.commit()
        conn.close()
