"""设置对话框。"""

import tkinter as tk

from PomoClock.ui.base import BaseDialog, create_accent_button, create_secondary_button
from PomoClock.ui.theme import BG, TEXT, SURFACE


class SettingsDialog(BaseDialog):
    def __init__(self, master, current_settings: dict, on_save):
        super().__init__(master, "设置", "340x340")
        self._on_save = on_save
        self._settings = dict(current_settings)
        self._build_ui()

    def _build_ui(self):
        self._create_title("番茄钟设置").pack(pady=(15, 15))

        fields = [
            ("工作时长 (分钟):", "work_duration", 1, 120),
            ("短休息时长 (分钟):", "short_break_duration", 1, 60),
            ("长休息时长 (分钟):", "long_break_duration", 1, 60),
            ("长休息间隔 (轮数):", "sessions_before_long_break", 1, 10),
        ]

        self._spinvars = {}

        for label_text, key, min_val, max_val in fields:
            row = tk.Frame(self, bg=BG)
            row.pack(fill=tk.X, padx=25, pady=4)

            tk.Label(row, text=label_text, font=("Segoe UI", 11), bg=BG, fg=TEXT).pack(side=tk.LEFT)

            var = tk.IntVar(value=self._settings[key])
            self._spinvars[key] = var

            tk.Spinbox(
                row, from_=min_val, to=max_val, textvariable=var,
                font=("Segoe UI", 11), bg=SURFACE, fg=TEXT,
                buttonbackground="#45475a", width=5,
                justify=tk.CENTER, relief=tk.FLAT,
            ).pack(side=tk.RIGHT)

        # 复选框
        check_frame = tk.Frame(self, bg=BG)
        check_frame.pack(fill=tk.X, padx=25, pady=(10, 4))

        self.always_on_top_var = tk.BooleanVar(value=self._settings.get("always_on_top", False))
        tk.Checkbutton(
            check_frame, text="窗口置顶", variable=self.always_on_top_var,
            font=("Segoe UI", 11), bg=BG, fg=TEXT, selectcolor=BG,
            activebackground=BG, activeforeground=TEXT,
        ).pack(side=tk.LEFT)

        self.sound_var = tk.BooleanVar(value=self._settings.get("sound_enabled", True))
        tk.Checkbutton(
            check_frame, text="启用提示音", variable=self.sound_var,
            font=("Segoe UI", 11), bg=BG, fg=TEXT, selectcolor=BG,
            activebackground=BG, activeforeground=TEXT,
        ).pack(side=tk.LEFT, padx=(20, 0))

        # 按钮
        btn_frame = tk.Frame(self, bg=BG)
        btn_frame.pack(pady=(15, 10))
        create_secondary_button(btn_frame, "取消", self.destroy, padx=20).pack(side=tk.LEFT, padx=8)
        create_accent_button(btn_frame, "保存", self._save, padx=20).pack(side=tk.LEFT, padx=8)

    def _save(self):
        new_settings = {key: var.get() for key, var in self._spinvars.items()}
        new_settings["always_on_top"] = self.always_on_top_var.get()
        new_settings["sound_enabled"] = self.sound_var.get()
        self._on_save(new_settings)
        self.destroy()
