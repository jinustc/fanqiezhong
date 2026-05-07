"""主应用窗口。"""

import tkinter as tk

from pomodoro.timer_engine import PomodoroEngine, TimerState, SessionType
from pomodoro.storage import load_settings, save_settings, record_work_session
from pomodoro.notifications import send_notification, play_sound
from pomodoro.ui.timer_frame import TimerFrame
from pomodoro.ui.controls import Controls
from pomodoro.ui.task_panel import TaskPanel
from pomodoro.ui.settings_dialog import SettingsDialog
from pomodoro.ui.stats_dialog import StatsDialog


# 不依赖实例状态的映射表，提为模块常量
_SESSION_LABELS = {
    TimerState.IDLE: "准备开始",
    TimerState.WORKING: "专注工作",
    TimerState.PAUSED: "已暂停",
    TimerState.SHORT_BREAK: "短休息",
    TimerState.LONG_BREAK: "长休息",
}


def _state_title(state: TimerState, time_str: str) -> str:
    """根据状态生成窗口标题。"""
    titles = {
        TimerState.IDLE: "番茄钟 - Pomodoro",
        TimerState.WORKING: f"🍅 {time_str} - 专注中",
        TimerState.PAUSED: f"⏸ {time_str} - 已暂停",
        TimerState.SHORT_BREAK: f"☕ {time_str} - 休息",
        TimerState.LONG_BREAK: f"☕ {time_str} - 长休息",
    }
    return titles.get(state, "番茄钟 - Pomodoro")


class PomodoroApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.settings = load_settings()
        self.engine = PomodoroEngine(
            work_duration=self.settings["work_duration"],
            short_break_duration=self.settings["short_break_duration"],
            long_break_duration=self.settings["long_break_duration"],
            sessions_before_long_break=self.settings["sessions_before_long_break"],
        )

        self.title("番茄钟 - Pomodoro")
        self.geometry("420x600")
        self.resizable(False, False)
        self.configure(bg="#1e1e2e")

        if self.settings.get("always_on_top", False):
            self.wm_attributes("-topmost", True)

        self.engine.on_tick = self._on_tick
        self.engine.on_state_change = self._on_state_change
        self.engine.on_session_complete = self._on_session_complete

        self._last_state = None  # 缓存，避免更新无变化的状态

        self._build_menu()
        self._build_ui()
        self._start_tick()

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_menu(self):
        menubar = tk.Menu(self, bg="#313244", fg="#cdd6f4",
                          activebackground="#45475a", activeforeground="#cdd6f4")
        self.config(menu=menubar)

        options_menu = tk.Menu(menubar, tearoff=0, bg="#313244", fg="#cdd6f4",
                               activebackground="#45475a")
        menubar.add_cascade(label="选项", menu=options_menu)
        options_menu.add_command(label="设置...", command=self._open_settings)
        options_menu.add_command(label="统计", command=self._open_stats)
        options_menu.add_separator()
        options_menu.add_command(label="退出", command=self._on_close)

    def _build_ui(self):
        self.timer_frame = TimerFrame(self, bg="#1e1e2e")
        self.timer_frame.pack(pady=(30, 10))

        self.controls = Controls(
            self, bg="#1e1e2e",
            on_start=self._on_start, on_pause=self._on_pause,
            on_reset=self._on_reset, on_skip=self._on_skip,
        )
        self.controls.pack(pady=(0, 15))

        self.task_panel = TaskPanel(self, bg="#1e1e2e")
        self.task_panel.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 15))

        self._update_display()

    def _on_start(self):
        self.engine.start()

    def _on_pause(self):
        self.engine.pause()

    def _on_reset(self):
        self.engine.reset()

    def _on_skip(self):
        self.engine.skip()
        self._update_display()

    def _on_tick(self, remaining, total):
        self._update_display()

    def _on_state_change(self, new_state):
        self._update_display()

    def _on_session_complete(self, session_type: SessionType):
        if self.settings.get("sound_enabled", True):
            play_sound()

        if session_type == SessionType.WORK:
            send_notification("🍅 番茄钟", "工作时段结束！休息一下～")
            record_work_session(self.settings["work_duration"])
        else:
            send_notification("☕ 休息结束", "休息时间结束，开始新的番茄！")

        self._update_display()

    def _update_display(self):
        info = self.engine.get_state_info()
        state = info["state"]  # 直接是 TimerState 枚举
        remaining = info["remaining_seconds"]
        total = info["total_seconds"]
        completed = info["completed_sessions"]
        sessions_before = info["sessions_before_long_break"]

        progress = remaining / total if total > 0 else 1.0

        mins = remaining // 60
        secs = remaining % 60
        time_str = f"{mins:02d}:{secs:02d}"

        self.timer_frame.update_display(
            time_str=time_str,
            progress=progress,
            session_label=_SESSION_LABELS.get(state, ""),
            completed_sessions=completed % sessions_before,
            total_sessions=sessions_before,
            is_working=state == TimerState.WORKING,
            is_break=state in (TimerState.SHORT_BREAK, TimerState.LONG_BREAK),
        )

        # 只在状态变化时更新按钮，避免无变化 config
        if state != self._last_state:
            self.controls.update_state(state)
            self._last_state = state

        self.title(_state_title(state, time_str))

    def _start_tick(self):
        self.engine.tick()
        self.after(1000, self._start_tick)

    def _open_settings(self):
        def on_save(new_settings):
            self.settings = new_settings
            save_settings(new_settings)
            self.engine.update_settings(
                work=new_settings["work_duration"],
                short_break=new_settings["short_break_duration"],
                long_break=new_settings["long_break_duration"],
                sessions_before_long=new_settings["sessions_before_long_break"],
            )
            self.wm_attributes("-topmost", new_settings.get("always_on_top", False))
            self._update_display()

        SettingsDialog(self, self.settings, on_save)

    def _open_stats(self):
        StatsDialog(self)

    def _on_close(self):
        self.engine.reset()
        self.destroy()
