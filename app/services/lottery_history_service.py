from typing import List, Dict
from app.db.database import get_connection


class LotteryHistoryService:
    """
    歷史中獎紀錄查詢服務
    """

    # ==================================================
    # 1. 查詢所有中獎紀錄
    # ==================================================
    def get_all_records(self) -> List[Dict]:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                dr.id AS record_id,
                p.name AS participant_name,
                pr.name AS prize_name,
                pr.is_special,
                dr.drawn_at
            FROM draw_records dr
            JOIN draw_sessions ds ON dr.session_id = ds.id
            JOIN prizes pr ON ds.prize_id = pr.id
            JOIN participants p ON dr.participant_id = p.id
            ORDER BY dr.drawn_at DESC
        """)

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    # ==================================================
    # 2. 依獎項查詢
    # ==================================================
    def get_records_by_prize(self, prize_id: int) -> List[Dict]:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                dr.id AS record_id,
                p.name AS participant_name,
                dr.drawn_at
            FROM draw_records dr
            JOIN draw_sessions ds ON dr.session_id = ds.id
            JOIN participants p ON dr.participant_id = p.id
            WHERE ds.prize_id = ?
            ORDER BY dr.drawn_at DESC
        """, (prize_id,))

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    # ==================================================
    # 3. 查詢某一次抽籤（session）
    # ==================================================
    def get_records_by_session(self, session_id: int) -> List[Dict]:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                p.name AS participant_name,
                pr.name AS prize_name,
                dr.drawn_at
            FROM draw_records dr
            JOIN draw_sessions ds ON dr.session_id = ds.id
            JOIN prizes pr ON ds.prize_id = pr.id
            JOIN participants p ON dr.participant_id = p.id
            WHERE dr.session_id = ?
        """, (session_id,))

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]
