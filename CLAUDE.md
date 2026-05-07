# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Desktop Pomodoro timer built with Python 3 + tkinter. Catppuccin Mocha dark theme, zero external dependencies.

## Commands

```
# Launch the app
"C:\Users\jinus\AppData\Local\Programs\Python\Python313\python.exe" -c "import sys; sys.path.insert(0, r'C:\Users\jinus\Desktop\first-cc'); from pomodoro.main import main; main()"

# Or double-click the launcher
启动番茄钟.bat
```

## Architecture

**State machine** (`timer_engine.py`): `IDLE → WORKING → (PAUSED | SHORT_BREAK | LONG_BREAK)`. Every 4th completed work session triggers a long break. The engine is pure logic with no tkinter dependency — driven by `root.after(1000, tick)`.

**Data flow**: `PomodoroApp` (tk.Tk) owns the `PomodoroEngine`, wires callbacks (`on_tick`, `on_state_change`, `on_session_complete`), and bridges engine → UI components → storage.

**Persistence** (`storage.py`): JSON files in `%APPDATA%/pomodoro/` — `settings.json`, `tasks.json`, `stats.json`. Stats are keyed by ISO date, recording `work_sessions` and `focus_minutes` per day.

**Notifications** (`notifications.py`): Uses PowerShell `ToastNotificationManager` for Windows toast notifications, `winsound.MessageBeep` for audio alerts. Both degrade silently on failure.

**UI layout** (top to bottom, ~420×600 fixed window):
- Menu bar: 选项 → Settings / Stats
- `TimerFrame`: Canvas arc progress ring + center time text + session dots
- `Controls`: Main button (start/pause/resume), Reset, Skip
- `TaskPanel`: Listbox with double-click toggle complete, right-click delete, entry+button to add

## Key Design Decisions

- `PomodoroEngine._pre_pause_state` tracks what state to resume to after PAUSED — enables pausing during breaks too.
- `skip()` fires `on_session_complete` callbacks so skipped work sessions are still recorded to stats.
- Timer tick continues every second regardless of state; `engine.tick()` returns early for IDLE/PAUSED.
- Settings changes in IDLE state reset the countdown to the new work duration immediately.
