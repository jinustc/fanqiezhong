"""计时器圆环显示组件。"""

import tkinter as tk


class TimerFrame(tk.Frame):
    def __init__(self, master, **kwargs):
        bg_color = kwargs.pop("bg", "#1e1e2e")
        super().__init__(master, bg=bg_color, **kwargs)

        self.canvas_size = 280
        self.ring_width = 12
        self.ring_radius = 110
        self.center = self.canvas_size // 2

        self.canvas = tk.Canvas(
            self,
            width=self.canvas_size,
            height=self.canvas_size,
            bg=bg_color,
            highlightthickness=0,
        )
        self.canvas.pack()

        self._draw_background_ring()
        self._progress_arc_id = self._create_progress_arc(extent=0, color="#313244")

        self.time_text_id = self.canvas.create_text(
            self.center, self.center - 8,
            text="25:00", font=("Segoe UI", 42, "bold"), fill="#cdd6f4",
        )

        self.session_label_id = self.canvas.create_text(
            self.center, 14,
            text="准备开始", font=("Segoe UI", 12), fill="#a6adc8",
        )

        self.dots_y = self.canvas_size - 20
        self.dots: list[int] = []
        self._dots_total = 4
        self._create_dots(4)

        # 缓存上次状态，避免无变化时重绘
        self._last_dots_fill = [None] * 4

    def _draw_background_ring(self):
        x1, y1 = self.center - self.ring_radius, self.center - self.ring_radius
        x2, y2 = self.center + self.ring_radius, self.center + self.ring_radius
        self.canvas.create_arc(
            x1, y1, x2, y2, start=90, extent=-359.9,
            width=self.ring_width, outline="#313244", style="arc",
        )

    def _create_progress_arc(self, extent, color):
        x1, y1 = self.center - self.ring_radius, self.center - self.ring_radius
        x2, y2 = self.center + self.ring_radius, self.center + self.ring_radius
        return self.canvas.create_arc(
            x1, y1, x2, y2, start=90, extent=extent,
            width=self.ring_width, outline=color, style="arc",
        )

    def _create_dots(self, count):
        dot_spacing = 18
        start_x = self.center - (count - 1) * dot_spacing / 2
        for i in range(count):
            x = start_x + i * dot_spacing
            dot = self.canvas.create_oval(
                x - 5, self.dots_y - 5, x + 5, self.dots_y + 5,
                fill="#45475a", outline="",
            )
            self.dots.append(dot)
        self._dots_total = count
        self._last_dots_fill = [None] * count

    def update_display(self, time_str, progress, session_label,
                       completed_sessions, total_sessions, is_working, is_break):
        self.canvas.itemconfig(self.time_text_id, text=time_str)
        self.canvas.itemconfig(self.session_label_id, text=session_label)

        # 用 itemconfig 更新已有圆弧，避免每秒删了重建
        extent = -360 * progress
        if extent > -1:
            extent = -1
        color = "#a6e3a1" if is_break else ("#f38ba8" if is_working else "#89b4fa")
        self.canvas.itemconfig(self._progress_arc_id, extent=extent, outline=color)

        # 只在圆点数量变化时重建
        if total_sessions != self._dots_total:
            for dot in self.dots:
                self.canvas.delete(dot)
            self.dots.clear()
            self._create_dots(total_sessions)

        # 只在颜色变化时更新圆点
        for i in range(total_sessions):
            if i < completed_sessions:
                fill = "#a6e3a1"
            elif i == completed_sessions and is_working:
                fill = "#f38ba8"
            else:
                fill = "#45475a"

            if fill != self._last_dots_fill[i]:
                self.canvas.itemconfig(self.dots[i], fill=fill)
                self._last_dots_fill[i] = fill
