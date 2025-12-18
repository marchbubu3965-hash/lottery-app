import random
from typing import List, Dict

from app.db.database import get_connection
from app.services.participant_service import ParticipantService


class LotteryService:
    """
    抽籤核心服務：
    - 依獎項順序抽籤
    - 建立 draw_session
    - 寫入 draw_records
    - 控制 participants.is_active
    """

    def __init__(self):
        self.participant_service = ParticipantService()

    # ==================================================
    # 對外主入口：執行整場抽獎
    # ==================================================
    def run_lottery(self) -> List[Dict]:
        """
        依 prizes.draw_order 依序抽獎
        回傳完整抽獎結果
        """
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, name, quota, is_special
            FROM prizes
            ORDER BY draw_order
        """)
        prizes = cursor.fetchall()
        conn.close()

        all_results = []

        for prize in prizes:
            prize_result = self._draw_for_prize(
                prize_id=prize["id"],
                prize_name=prize["name"],
                quota=prize["quota"],
                is_special=prize["is_special"]
            )
            all_results.append(prize_result)

        return all_results

    # ==================================================
    # 單一獎項抽籤
    # ==================================================
    def _draw_for_prize(
        self,
        prize_id: int,
        prize_name: str,
        quota: int,
        is_special: int
    ) -> Dict:
        """
        對單一獎項進行抽籤
        """

        # 特別獎：重置名單
        if is_special:
            self.participant_service.reset_all_participants()

        # 建立抽籤場次
        session_id = self._create_draw_session(prize_id)

        # 取得可抽名單
        candidates = self.participant_service.get_active_participants()

        if not candidates:
            return {
                "prize": prize_name,
                "winners": [],
                "message": "無可抽名單"
            }

        # 若人數不足，全部中獎
        if len(candidates) <= quota:
            selected = candidates
        else:
            selected = random.sample(candidates, quota)

        winners = []

        for participant in selected:
            participant_id = participant["id"]

            self._record_draw(session_id, participant_id)
            self.participant_service.mark_as_selected(participant_id)

            winners.append({
                "id": participant_id,
                "name": participant["name"]
            })

        self._finish_draw_session(session_id)

        return {
            "prize": prize_name,
            "winners": winners
        }

    # ==================================================
    # DB 操作（內部）
    # ==================================================
    def _create_draw_session(self, prize_id: int) -> int:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO draw_sessions (prize_id)
            VALUES (?)
        """, (prize_id,))

        session_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return session_id

    def _record_draw(self, session_id: int, participant_id: int) -> None:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO draw_records (session_id, participant_id)
            VALUES (?, ?)
        """, (session_id, participant_id))

        conn.commit()
        conn.close()

    def _finish_draw_session(self, session_id: int) -> None:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE draw_sessions
            SET finished_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (session_id,))

        conn.commit()
        conn.close()
