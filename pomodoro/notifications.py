"""系统通知和声音提示，所有操作均在后台线程执行，不阻塞 UI。"""

import subprocess
import sys
import threading


def send_notification(title: str, message: str):
    """发送系统通知（Windows 用 PowerShell Toast，Linux 用 notify-send）。"""
    threading.Thread(target=_do_send_notification, args=(title, message), daemon=True).start()


def _do_send_notification(title: str, message: str):
    if sys.platform == "win32":
        try:
            script = f'''
            [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] > $null
            $template = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02)
            $textNodes = $template.GetElementsByTagName("text")
            $textNodes.Item(0).AppendChild($template.CreateTextNode("{title}")) > $null
            $textNodes.Item(1).AppendChild($template.CreateTextNode("{message}")) > $null
            $toast = [Windows.UI.Notifications.ToastNotification]::new($template)
            [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("Pomodoro").Show($toast)
            '''
            subprocess.run(
                ["powershell", "-NoProfile", "-Command", script],
                capture_output=True, timeout=5,
            )
        except Exception:
            pass
    elif sys.platform == "linux":
        try:
            subprocess.run(
                ["notify-send", title, message], capture_output=True, timeout=5,
            )
        except Exception:
            pass


def play_sound():
    """播放提示音（后台线程）。"""
    threading.Thread(target=_do_play_sound, daemon=True).start()


def _do_play_sound():
    if sys.platform == "win32":
        try:
            import winsound
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
        except Exception:
            pass
    elif sys.platform == "linux":
        try:
            subprocess.run(
                ["paplay", "/usr/share/sounds/freedesktop/stereo/alarm-clock-elapsed.oga"],
                capture_output=True,
            )
        except Exception:
            pass
