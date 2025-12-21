import random
import sqlite3
from typing import List, Dict, Any

from app.db.database import get_connection


class LotteryService:
    """
    抽籤核心服務（修正版）：
    - 同一獎項內「絕不重複中獎」
    - 一般獎：中獎即停用 participant
    - 特別獎：不影響 is_active
    - 每個獎項一個 transaction
    """

    # ==================================================
    # 對外主入口
    # ==================================================
    def run_lottery(self) -> List[Dict[str, Any]]:
        conn = get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, name, quota, is_special
            FROM prizes
            ORDER BY draw_order
        """)
        prizes = cursor.fetchall()

        results: List[Dict[str, Any]] = []

        for prize in prizes:
            result = self._draw_for_prize(conn, prize)
            results.append(result)

        conn.close()
        return results

    # ==================================================
    # 單一獎項抽籤
    # ==================================================
    def _draw_for_prize(
        self,
        conn: sqlite3.Connection,
        prize: sqlite3.Row
    ) -> Dict[str, Any]:

        cursor = conn.cursor()

        prize_id = prize["id"]
        prize_name = prize["name"]
        quota = prize["quota"]
        is_special = prize["is_special"]

        try:
            # ---------- 建立抽籤場次 ----------
            cursor.execute("""
                INSERT INTO draw_sessions (prize_id)
                VALUES (?)
            """, (prize_id,))
            session_id = cursor.lastrowid

            # ---------- 取得候選名單 ----------
            if is_special:
                cursor.execute("""
                    SELECT id, name, employee_no
                    FROM participants
                """)
            else:
                cursor.execute("""
                    SELECT id, name, employee_no
                    FROM participants
                    WHERE is_active = 1
                """)

            candidates = list(cursor.fetchall())

            if not candidates:
                conn.commit()
                return {
                    "session_id": session_id,
                    "prize": prize_name,
                    "is_special": is_special,
                    "winners": [],
                    "message": "無可抽名單"
                }

            # ---------- 抽籤（不重複） ----------
            remaining = candidates.copy()
            winners: List[Dict[str, Any]] = []

            while remaining and len(winners) < quota:
                p = random.choice(remaining)
                remaining.remove(p)  # ⚠️ 立刻移除，避免重複

                cursor.execute("""
                    INSERT INTO draw_records (session_id, participant_id, drawn_at)
                    VALUES (?, ?, datetime('now', '+8 hours'))
                """, (session_id, p["id"]))

                # 一般獎項 → 停用
                if not is_special:
                    cursor.execute("""
                        UPDATE participants
                        SET is_active = 0
                        WHERE id = ?
                    """, (p["id"],))

                winners.append({
                    "id": p["id"],
                    "name": p["name"],
                    "employee_no": p["employee_no"] or ""
                })

            # ---------- 結束場次 ----------
            cursor.execute("""
                UPDATE draw_sessions
                SET finished_at = datetime('now', '+8 hours')
                WHERE id = ?
            """, (session_id,))

            conn.commit()

            return {
                "session_id": session_id,
                "prize": prize_name,
                "is_special": is_special,
                "winners": winners,
                "message": (
                    "人數不足，全部中獎"
                    if len(candidates) < quota
                    else ""
                )
            }

        except Exception:
            conn.rollback()
            raise
