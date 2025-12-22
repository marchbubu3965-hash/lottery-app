from enum import Enum, auto


class LotteryState(Enum):
    IDLE = auto()
    RUNNING = auto()
    PAUSED = auto()
    WAIT_NEXT = auto()
    FINISHED = auto()


class InvalidStateTransition(Exception):
    pass


class LotteryStateMachine:
    def __init__(self):
        self.state = LotteryState.IDLE

    def start(self):
        if self.state != LotteryState.IDLE:
            raise InvalidStateTransition("只能從 IDLE 開始抽籤")
        self.state = LotteryState.RUNNING

    def pause(self):
        if self.state != LotteryState.RUNNING:
            raise InvalidStateTransition("只能在 RUNNING 暫停")
        self.state = LotteryState.PAUSED

    def resume(self):
        if self.state != LotteryState.PAUSED:
            raise InvalidStateTransition("只能從 PAUSED 繼續")
        self.state = LotteryState.RUNNING

    def wait_next(self):
        if self.state != LotteryState.RUNNING:
            raise InvalidStateTransition("只能從 RUNNING 進入 WAIT_NEXT")
        self.state = LotteryState.WAIT_NEXT

    def finish(self):
        if self.state not in (LotteryState.RUNNING, LotteryState.WAIT_NEXT):
            raise InvalidStateTransition("只能在抽籤過程中完成")
        self.state = LotteryState.FINISHED

    def reset(self):
        self.state = LotteryState.IDLE

    def next_round(self):
        if self.state != LotteryState.WAIT_NEXT:
            raise InvalidStateTransition("只能從 WAIT_NEXT 進入 RUNNING")
        self.state = LotteryState.RUNNING

