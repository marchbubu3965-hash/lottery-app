import pytest
from app.core.lottery_state_machine import (
    LotteryStateMachine,
    LotteryState,
    InvalidStateTransition
)


def test_initial_state():
    sm = LotteryStateMachine()
    assert sm.state == LotteryState.IDLE


def test_start_from_idle():
    sm = LotteryStateMachine()
    sm.start()
    assert sm.state == LotteryState.RUNNING


def test_start_invalid_state():
    sm = LotteryStateMachine()
    sm.start()
    with pytest.raises(InvalidStateTransition):
        sm.start()


def test_pause_and_resume():
    sm = LotteryStateMachine()
    sm.start()
    sm.pause()
    assert sm.state == LotteryState.PAUSED

    sm.resume()
    assert sm.state == LotteryState.RUNNING


def test_pause_invalid():
    sm = LotteryStateMachine()
    with pytest.raises(InvalidStateTransition):
        sm.pause()


def test_wait_next_flow():
    sm = LotteryStateMachine()
    sm.start()
    sm.wait_next()
    assert sm.state == LotteryState.WAIT_NEXT

    sm.next_round()
    assert sm.state == LotteryState.RUNNING


def test_finish_from_running():
    sm = LotteryStateMachine()
    sm.start()
    sm.finish()
    assert sm.state == LotteryState.FINISHED


def test_finish_from_wait_next():
    sm = LotteryStateMachine()
    sm.start()
    sm.wait_next()
    sm.finish()
    assert sm.state == LotteryState.FINISHED


def test_invalid_finish():
    sm = LotteryStateMachine()
    with pytest.raises(InvalidStateTransition):
        sm.finish()
