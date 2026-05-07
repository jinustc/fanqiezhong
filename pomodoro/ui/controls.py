"""Start/Pause/Reset/Skip control buttons."""

import tkinter as tk

from pomodoro.timer_engine import TimerState


class Controls(tk.Frame):
    def __init__(self, master, on_start, on_pause, on_reset, on_skip, **kwargs):
        bg_color = kwargs.pop("bg", "#1e1e2e")
        super().__init__(master, bg=bg_color, **kwargs)

        self._on_start = on_start
        self._on_pause = on_pause
        self._on_reset = on_reset
        self._on_skip = on_skip

        self.btn_font = ("Segoe UI", 12)
        self.btn_bg = "#313244"
        self.btn_fg = "#cdd6f4"
        self.btn_active_bg = "#45475a"

        self.main_btn = tk.Button(
            self,
            text="▶ 开始",
            font=("Segoe UI", 13, "bold"),
            bg="#89b4fa",
            fg="#1e1e2e",
            activebackground="#74c7ec",
            activeforeground="#1e1e2e",
            width=10,
            height=1,
            borderwidth=0,
            cursor="hand2",
            command=self._on_main_click,
        )
        self.main_btn.pack(side=tk.LEFT, padx=5)

        self.reset_btn = tk.Button(
            self,
            text="↺ 重置",
            font=self.btn_font,
            bg=self.btn_bg,
            fg=self.btn_fg,
            activebackground=self.btn_active_bg,
            activeforeground=self.btn_fg,
            width=8,
            borderwidth=0,
            cursor="hand2",
            command=on_reset,
        )
        self.reset_btn.pack(side=tk.LEFT, padx=5)

        self.skip_btn = tk.Button(
            self,
            text="⏭ 跳过",
            font=self.btn_font,
            bg=self.btn_bg,
            fg=self.btn_fg,
            activebackground=self.btn_active_bg,
            activeforeground=self.btn_fg,
            width=8,
            borderwidth=0,
            cursor="hand2",
            command=on_skip,
        )
        self.skip_btn.pack(side=tk.LEFT, padx=5)

        self._state = TimerState.IDLE

    def _on_main_click(self):
        if self._state == TimerState.WORKING or self._state in (TimerState.SHORT_BREAK, TimerState.LONG_BREAK):
            self._on_pause()
        else:
            self._on_start()

    def update_state(self, state: TimerState):
        self._state = state

        if state == TimerState.IDLE:
            self.main_btn.config(text="▶ 开始", bg="#89b4fa", fg="#1e1e2e", state=tk.NORMAL)
            self.reset_btn.config(state=tk.NORMAL)
            self.skip_btn.config(state=tk.DISABLED)
        elif state == TimerState.WORKING:
            self.main_btn.config(text="⏸ 暂停", bg="#f9e2af", fg="#1e1e2e", state=tk.NORMAL)
            self.reset_btn.config(state=tk.NORMAL)
            self.skip_btn.config(state=tk.NORMAL)
        elif state == TimerState.PAUSED:
            self.main_btn.config(text="▶ 继续", bg="#a6e3a1", fg="#1e1e2e", state=tk.NORMAL)
            self.reset_btn.config(state=tk.NORMAL)
            self.skip_btn.config(state=tk.DISABLED)
        elif state in (TimerState.SHORT_BREAK, TimerState.LONG_BREAK):
            self.main_btn.config(text="⏸ 暂停", bg="#cba6f7", fg="#1e1e2e", state=tk.NORMAL)
            self.reset_btn.config(state=tk.NORMAL)
            self.skip_btn.config(state=tk.NORMAL)
