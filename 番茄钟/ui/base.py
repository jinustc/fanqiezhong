"""UI 组件的公共基类。"""

import tkinter as tk

from pomodoro.ui.theme import BG, TEXT, SURFACE, OVERLAY, OVERLAY_HOVER, BLUE, BLUE_HOVER


class BaseDialog(tk.Toplevel):
    """所有模态对话框的基类，统一初始化、居中、样式。"""

    def __init__(self, master, title: str, geometry: str):
        super().__init__(master)
        self.title(title)
        self.geometry(geometry)
        self.resizable(False, False)
        self.configure(bg=BG)
        self.transient(master)
        self.grab_set()
        self._center_on_parent(master)

    def _center_on_parent(self, parent):
        self.update_idletasks()
        px = parent.winfo_rootx() + parent.winfo_width() // 2 - self.winfo_width() // 2
        py = parent.winfo_rooty() + parent.winfo_height() // 2 - self.winfo_height() // 2
        self.geometry(f"+{px}+{py}")

    def _create_title(self, text: str) -> tk.Label:
        from pomodoro.ui.theme import FONT_TITLE
        return tk.Label(self, text=text, font=FONT_TITLE, bg=BG, fg=TEXT)


def create_accent_button(parent, text: str, command, **kwargs) -> tk.Button:
    """强调按钮（蓝底黑字）。"""
    return tk.Button(
        parent, text=text,
        font=("Segoe UI", 11, "bold"),
        bg=BLUE, fg=BG,
        activebackground=BLUE_HOVER, activeforeground=BG,
        borderwidth=0, cursor="hand2", **kwargs,
    )


def create_secondary_button(parent, text: str, command, **kwargs) -> tk.Button:
    """次要按钮（灰底白字）。"""
    return tk.Button(
        parent, text=text,
        font=("Segoe UI", 11),
        bg=OVERLAY, fg=TEXT,
        activebackground=OVERLAY_HOVER, activeforeground=TEXT,
        borderwidth=0, cursor="hand2", **kwargs,
    )
