"""统计对话框。"""

import tkinter as tk

from PomoClock.ui.base import BaseDialog, create_secondary_button
from PomoClock.ui.theme import BG, TEXT, SURFACE, BLUE
from PomoClock.storage import load_stats, get_today_stats, get_weekly_stats


class StatsDialog(BaseDialog):
    def __init__(self, master):
        super().__init__(master, "统计", "360x260")
        self._build_ui()

    def _build_ui(self):
        self._create_title("番茄钟统计").pack(pady=(15, 15))

        today = get_today_stats()
        weekly = get_weekly_stats()

        self._stat_card("📅 今日", today["work_sessions"], today["focus_minutes"]).pack(
            fill=tk.X, padx=25, pady=(0, 8))
        self._stat_card("📊 本周", weekly["total_sessions"], weekly["total_minutes"]).pack(
            fill=tk.X, padx=25, pady=(0, 8))

        create_secondary_button(self, "关闭", self.destroy, padx=25).pack(pady=(10, 10))

    def _stat_card(self, label: str, sessions: int, minutes: int) -> tk.Frame:
        frame = tk.Frame(self, bg=SURFACE)
        tk.Label(frame, text=label, font=("Segoe UI", 12, "bold"),
                 bg=SURFACE, fg=BLUE).pack(anchor=tk.W, padx=15, pady=(8, 4))
        tk.Label(
            frame,
            text=f"完成 {sessions} 个番茄  ·  专注 {minutes} 分钟",
            font=("Segoe UI", 11), bg=SURFACE, fg=TEXT,
        ).pack(anchor=tk.W, padx=15, pady=(0, 8))
        return frame
