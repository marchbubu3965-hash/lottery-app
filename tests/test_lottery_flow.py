import pytest

from app.core.lottery_state_machine import (
    LotteryStateMachine,
    LotteryState,
    InvalidStateTransition,
)


def test_normal_lottery_flow():
    """
    正常抽獎流程：
    IDLE → RUNNING → WAIT_NEXT → RUNNING → FINISHED
    """
    sm = LotteryStateMachine()

    # 初始狀態
    assert sm.state == LotteryState.IDLE

    # 開始抽獎
    sm.start()
    assert sm.state == LotteryState.RUNNING

    # 本輪結束，等待下一個獎項
    sm.wait_next()
    assert sm.state == LotteryState.WAIT_NEXT

    # 使用者點「繼續下一個獎項」
    sm.next_round()
    assert sm.state == LotteryState.RUNNING

    # 全部抽完
    sm.finish()
    assert sm.state == LotteryState.FINISHED


def test_pause_and_resume_flow():
    """
    暫停流程：
    RUNNING → PAUSED → RUNNING
    """
    sm = LotteryStateMachine()
    sm.start()

    sm.pause()
    assert sm.state == LotteryState.PAUSED

    sm.resume()
    assert sm.state == LotteryState.RUNNING


def test_finish_from_wait_next():
    """
    允許在 WAIT_NEXT 直接結束
    """
    sm = LotteryStateMachine()
    sm.start()
    sm.wait_next()

    sm.finish()
    assert sm.state == LotteryState.FINISHED


def test_invalid_transitions():
    """
    非法狀態轉換應丟出例外
    """
    sm = LotteryStateMachine()

    # 尚未開始不能 wait_next
    with pytest.raises(InvalidStateTransition):
        sm.wait_next()

    sm.start()

    # RUNNING 不能直接 next_round
    with pytest.raises(InvalidStateTransition):
        sm.next_round()

    sm.wait_next()

    # WAIT_NEXT 不能 pause
    with pytest.raises(InvalidStateTransition):
        sm.pause()
