import random
from datetime import datetime
from typing import List, Dict

from app.db.database import get_connection


class LotteryService:
    """
    抽籤核心服務（完整版本）
    - 使用 prizes / draw_sessions / draw_records / participants
    """

    # =========================
    # 公開 API
    # =========================
    def run_full_lottery(self) -> List[Dict]:
        """
        依 prizes.draw_order 依序執行所有抽獎
        """
        prizes = self._get_all_prizes_in_order()
        results = []

        for prize in prizes:
            result = self._draw_one_prize(prize)
            results.append(result)

        return results

    def draw_single_prize(self, prize_id: int) -> Dict:
        """
        只抽指定獎項（手動操作用）
        """
        prize = self._get_prize_by_id(prize_id)
        if not prize:
            raise RuntimeError("找不到指定獎項")

        return self._draw_one_prize(prize)

    # =========================
    # 抽獎主流程
    # =========================
    def _draw_one_prize(self, prize) -> Dict:
        """
        抽單一獎項
        """
        if prize["is_special"]:
            self._reset_participants()

        session_id = self._create_draw_session(prize["id"])

        participants = self._get_active_participants()
        if len(participants) < prize["quota"]:
            raise RuntimeError(f"【{prize['name']}】可抽人數不足")

        winners = random.sample(participants, prize["quota"])

        for w in winners:
            self._record_winner(session_id, w["id"])
            self._mark_participant_inactive(w["id"])

        self._finish_draw_session(session_id)

        return {
            "prize_id": prize["id"],
            "prize_name": prize["name"],
            "quota": prize["quota"],
            "winners": [
                {"id": w["id"], "name": w["name"]}
                for w in winners
            ]
        }

    # =========================
    # Prize
    # =========================
    def _get_all_prizes_in_order(self):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, name, quota, draw_order, is_special
            FROM prizes
            ORDER BY draw_order
            """
        )
        rows = cursor.fetchall()
        conn.close()
        return rows

    def _get_prize_by_id(self, prize_id: int):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, name, quota, draw_order, is_special
            FROM prizes
            WHERE id = ?
            """,
            (prize_id,)
        )
        row = cursor.fetchone()
        conn.close()
        return row

    # =========================
    # Draw Session
    # =========================
    def _create_draw_session(self, prize_id: int) -> int:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO draw_sessions (prize_id)
            VALUES (?)
            """,
            (prize_id,)
        )
        session_id = cursor.lastrowid

        conn.commit()
        conn.close()
        return session_id

    def _finish_draw_session(self, session_id: int) -> None:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE draw_sessions
            SET finished_at = ?
            WHERE id = ?
            """,
            (datetime.now().isoformat(timespec="seconds"), session_id)
        )

        conn.commit()
        conn.close()

    # =========================
    # Participants
    # =========================
    def _get_active_participants(self):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, name
            FROM participants
            WHERE is_active = 1
            """
        )
        rows = cursor.fetchall()
        conn.close()
        return rows

    def _mark_participant_inactive(self, participant_id: int) -> None:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE participants
            SET is_active = 0
            WHERE id = ?
            """,
            (participant_id,)
        )

        conn.commit()
        conn.close()

    def _reset_participants(self) -> None:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE participants
            SET is_active = 1
            """
        )

        conn.commit()
        conn.close()

    # =========================
    # Draw Records
    # =========================
    def _record_winner(self, session_id: int, participant_id: int) -> None:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO draw_records (session_id, participant_id)
            VALUES (?, ?)
            """,
            (session_id, participant_id)
        )

        conn.commit()
        conn.close()
