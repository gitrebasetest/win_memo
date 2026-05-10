from __future__ import annotations

from pathlib import Path
import os
import sys
import winreg

RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
APP_KEY_NAME = "WinMemoTool"


def get_start_command() -> str:
    executable = Path(sys.executable)
    if executable.name.lower().endswith("python.exe"):
        app_entry = Path(__file__).resolve().parents[2] / "app.py"
        return f'"{executable}" "{app_entry}"'
    return f'"{executable}"'


def is_startup_enabled() -> bool:
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY) as key:
            winreg.QueryValueEx(key, APP_KEY_NAME)
            return True
    except FileNotFoundError:
        return False


def set_startup_enabled(enabled: bool) -> None:
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, RUN_KEY) as key:
        if enabled:
            winreg.SetValueEx(key, APP_KEY_NAME, 0, winreg.REG_SZ, get_start_command())
        else:
            try:
                winreg.DeleteValue(key, APP_KEY_NAME)
            except FileNotFoundError:
                pass
