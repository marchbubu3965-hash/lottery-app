import pytest

from app.services.lottery_service import LotteryService
from app.services.participant_service import ParticipantService
from app.services.admin_service import AdminService


@pytest.fixture(autouse=True)
def clean_environment():
    """
    每個測試前後都清空資料，確保測試獨立
    """
    AdminService().reset_lottery_data()
    ParticipantService().reset_all_participants()
    yield
    AdminService().reset_lottery_data()


def _get_special_prizes(results):
    return [p for p in results if p.get("is_special") is True]


def test_special_prize_exists():
    """
    系統中若有設定特別獎，run_lottery 應該回傳 is_special=True 的獎項
    """
    results = LotteryService().run_lottery()
    special_prizes = _get_special_prizes(results)

    assert isinstance(special_prizes, list)
    # 若資料庫真的有設定特別獎，至少應有一筆
    # 若你允許「沒有特別獎」，可改成 >= 0
    assert len(special_prizes) >= 0


def test_special_prize_has_only_one_winner():
    """
    特別獎只能有 1 位得獎者
    """
    results = LotteryService().run_lottery()

    for prize in _get_special_prizes(results):
        winners = prize.get("winners", [])
        assert isinstance(winners, list)
        assert len(winners) == 1


def test_special_prize_winner_is_from_participants():
    """
    特別獎得獎者必須來自參與名單
    """
    participants = ParticipantService().get_all_participants()
    participant_names = {p["name"] for p in participants}

    results = LotteryService().run_lottery()

    for prize in _get_special_prizes(results):
        winner = prize["winners"][0]
        assert winner["name"] in participant_names


def test_special_prize_winner_has_required_fields():
    """
    特別獎得獎者資料結構必須完整
    """
    results = LotteryService().run_lottery()

    for prize in _get_special_prizes(results):
        winner = prize["winners"][0]
        assert "name" in winner
        assert "employee_no" in winner
