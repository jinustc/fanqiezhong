"""番茄钟状态机 —— 核心计时逻辑，无 UI 依赖。"""

from enum import Enum


class TimerState(Enum):
    """计时器状态枚举"""
    IDLE = "idle"
    WORKING = "working"
    PAUSED = "paused"
    SHORT_BREAK = "short_break"
    LONG_BREAK = "long_break"


class SessionType(Enum):
    """阶段类型"""
    WORK = "work"
    BREAK = "break"


class PomodoroEngine:
    """番茄钟状态机引擎。

    状态流转：
        IDLE → WORKING → PAUSED → WORKING → ... → SHORT_BREAK → ... → LONG_BREAK
                          ↑                                              |
                          └──────────────────────────────────────────────┘
    每完成 sessions_before_long_break 轮工作后触发一次长休息。
    """

    # 状态 → (时长_分钟, 总秒数) 的映射
    _STATE_DURATION_MAP = {
        TimerState.WORKING: "work_duration",
        TimerState.SHORT_BREAK: "short_break_duration",
        TimerState.LONG_BREAK: "long_break_duration",
        TimerState.IDLE: "work_duration",
    }

    def __init__(
        self,
        work_duration: int = 25,
        short_break_duration: int = 5,
        long_break_duration: int = 15,
        sessions_before_long_break: int = 4,
    ):
        self.work_duration = work_duration
        self.short_break_duration = short_break_duration
        self.long_break_duration = long_break_duration
        self.sessions_before_long_break = sessions_before_long_break

        self.state = TimerState.IDLE
        self.remaining_seconds = work_duration * 60
        self.total_seconds = work_duration * 60
        self.completed_sessions = 0
        self._pre_pause_state = None

        self.on_tick = None
        self.on_state_change = None
        self.on_session_complete = None  # fn(SessionType)

    def _set_state(self, new_state: TimerState):
        """切换状态并重置当前阶段的剩余时间和总时间。"""
        self.state = new_state
        attr_name = self._STATE_DURATION_MAP[new_state]
        duration_minutes = getattr(self, attr_name)
        self.remaining_seconds = duration_minutes * 60
        self.total_seconds = duration_minutes * 60

        if self.on_state_change:
            self.on_state_change(new_state)

    def start(self):
        """从空闲状态开始，或从暂停状态恢复。"""
        if self.state == TimerState.IDLE:
            self._set_state(TimerState.WORKING)
        elif self.state == TimerState.PAUSED and self._pre_pause_state:
            self.state = self._pre_pause_state
            self._pre_pause_state = None
            if self.on_state_change:
                self.on_state_change(self.state)

    def pause(self):
        """暂停当前阶段（工作或休息均可暂停）。"""
        if self.state in (TimerState.WORKING, TimerState.SHORT_BREAK, TimerState.LONG_BREAK):
            self._pre_pause_state = self.state
            self.state = TimerState.PAUSED
            if self.on_state_change:
                self.on_state_change(TimerState.PAUSED)

    def reset(self):
        """重置计时器，清空已完成的轮数。"""
        self.completed_sessions = 0
        self._pre_pause_state = None
        self._set_state(TimerState.IDLE)

    def skip(self):
        """跳过当前阶段。工作中跳过→进入休息，休息中跳过→进入工作。"""
        if self.state == TimerState.WORKING:
            self._complete_work_session()
        elif self.state in (TimerState.SHORT_BREAK, TimerState.LONG_BREAK):
            self._complete_break_session()
        elif self.state == TimerState.PAUSED and self._pre_pause_state:
            # 暂停状态下跳过：先恢复状态再委托给正常逻辑
            self.state = self._pre_pause_state
            self._pre_pause_state = None
            if self.state == TimerState.WORKING:
                self._complete_work_session()
            else:
                self._complete_break_session()

    def tick(self):
        """每秒调用一次，倒数一秒。返回 True 表示状态发生了变化。"""
        if self.state in (TimerState.IDLE, TimerState.PAUSED):
            return False

        self.remaining_seconds -= 1

        if self.on_tick:
            self.on_tick(self.remaining_seconds, self.total_seconds)

        if self.remaining_seconds <= 0:
            self._on_session_end()
            return True

        return False

    def _on_session_end(self):
        """当前阶段倒计时到 0 时的处理。"""
        if self.state == TimerState.WORKING:
            self._complete_work_session()
        elif self.state in (TimerState.SHORT_BREAK, TimerState.LONG_BREAK):
            self._complete_break_session()

    def _complete_work_session(self):
        """完成一轮工作阶段：计数 + 1，触发回调，进入休息。"""
        self.completed_sessions += 1
        if self.on_session_complete:
            self.on_session_complete(SessionType.WORK)
        self._transition_to_break()

    def _complete_break_session(self):
        """完成休息阶段：触发回调，进入下一轮工作。"""
        if self.on_session_complete:
            self.on_session_complete(SessionType.BREAK)
        self._set_state(TimerState.WORKING)

    def _transition_to_break(self):
        """根据已完成轮数决定进入短休息还是长休息。"""
        if self.completed_sessions % self.sessions_before_long_break == 0:
            self._set_state(TimerState.LONG_BREAK)
        else:
            self._set_state(TimerState.SHORT_BREAK)

    def get_state_info(self) -> dict:
        """返回当前计时器完整状态，供 UI 层读取。"""
        return {
            "state": self.state,  # 直接返回枚举，不再泄漏字符串
            "remaining_seconds": self.remaining_seconds,
            "total_seconds": self.total_seconds,
            "completed_sessions": self.completed_sessions,
            "sessions_before_long_break": self.sessions_before_long_break,
        }

    def update_settings(
        self,
        work: int = None,
        short_break: int = None,
        long_break: int = None,
        sessions_before_long: int = None,
    ):
        """更新设置参数。如果当前处于空闲状态，立即重置倒计时。"""
        if work is not None:
            self.work_duration = work
        if short_break is not None:
            self.short_break_duration = short_break
        if long_break is not None:
            self.long_break_duration = long_break
        if sessions_before_long is not None:
            self.sessions_before_long_break = sessions_before_long

        if self.state == TimerState.IDLE:
            self.remaining_seconds = self.work_duration * 60
            self.total_seconds = self.work_duration * 60
