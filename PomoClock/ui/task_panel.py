"""Task list panel with add/complete/delete functionality."""

import tkinter as tk
from tkinter import messagebox
from datetime import datetime

from PomoClock.storage import load_tasks, save_tasks


class TaskPanel(tk.Frame):
    def __init__(self, master, **kwargs):
        bg_color = kwargs.pop("bg", "#1e1e2e")
        super().__init__(master, bg=bg_color, **kwargs)

        self.tasks: list[dict] = load_tasks()

        # Header
        header = tk.Label(
            self,
            text="任务列表",
            font=("Segoe UI", 12, "bold"),
            bg=bg_color,
            fg="#cdd6f4",
        )
        header.pack(anchor=tk.W, pady=(0, 5))

        # List frame
        list_frame = tk.Frame(self, bg="#313244", highlightthickness=0)
        list_frame.pack(fill=tk.BOTH, expand=True)

        self.listbox = tk.Listbox(
            list_frame,
            font=("Segoe UI", 11),
            bg="#313244",
            fg="#cdd6f4",
            selectbackground="#45475a",
            selectforeground="#cdd6f4",
            activestyle="none",
            borderwidth=0,
            highlightthickness=0,
        )
        scrollbar = tk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.listbox.yview)
        self.listbox.config(yscrollcommand=scrollbar.set)

        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(8, 0), pady=8)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 4), pady=8)

        self.listbox.bind("<Double-1>", self._toggle_complete)
        self.listbox.bind("<Button-3>", self._show_context_menu)

        # Context menu
        self.context_menu = tk.Menu(self, tearoff=0, bg="#313244", fg="#cdd6f4",
                                     activebackground="#45475a", activeforeground="#cdd6f4")
        self.context_menu.add_command(label="删除", command=self._delete_selected)

        # Input frame
        input_frame = tk.Frame(self, bg=bg_color)
        input_frame.pack(fill=tk.X, pady=(8, 0))

        self.entry = tk.Entry(
            input_frame,
            font=("Segoe UI", 11),
            bg="#313244",
            fg="#cdd6f4",
            insertbackground="#cdd6f4",
            relief=tk.FLAT,
        )
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=4)
        self.entry.bind("<Return>", lambda e: self._add_task())

        add_btn = tk.Button(
            input_frame,
            text="+ 添加",
            font=("Segoe UI", 10),
            bg="#89b4fa",
            fg="#1e1e2e",
            activebackground="#74c7ec",
            activeforeground="#1e1e2e",
            borderwidth=0,
            padx=10,
            cursor="hand2",
            command=self._add_task,
        )
        add_btn.pack(side=tk.LEFT, padx=(8, 0))

        self._refresh_list()

    def _add_task(self):
        text = self.entry.get().strip()
        if not text:
            return

        task = {
            "id": datetime.now().isoformat(),
            "text": text,
            "completed": False,
            "created_at": datetime.now().isoformat(),
        }
        self.tasks.append(task)
        self.entry.delete(0, tk.END)
        self._persist()
        self._refresh_list()

    def _toggle_complete(self, event=None):
        selection = self.listbox.curselection()
        if not selection:
            return

        idx = selection[0]
        if idx < len(self.tasks):
            self.tasks[idx]["completed"] = not self.tasks[idx]["completed"]
            self._persist()
            self._refresh_list()

    def _show_context_menu(self, event):
        idx = self.listbox.nearest(event.y)
        if idx >= 0 and idx < len(self.tasks):
            self.listbox.selection_clear(0, tk.END)
            self.listbox.selection_set(idx)
            self.context_menu.tk_popup(event.x_root, event.y_root)

    def _delete_selected(self):
        selection = self.listbox.curselection()
        if not selection:
            return

        idx = selection[0]
        if idx < len(self.tasks):
            del self.tasks[idx]
            self._persist()
            self._refresh_list()

    def _refresh_list(self):
        self.listbox.delete(0, tk.END)
        for task in self.tasks:
            prefix = "✓ " if task["completed"] else "○ "
            display = f"{prefix}{task['text']}"
            self.listbox.insert(tk.END, display)

            idx = self.listbox.size() - 1
            if task["completed"]:
                self.listbox.itemconfig(idx, fg="#6c7086")
            else:
                self.listbox.itemconfig(idx, fg="#cdd6f4")

    def _persist(self):
        save_tasks(self.tasks)
