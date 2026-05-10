from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os
import sys


APP_NAME = "win_memo_tool"
DISPLAY_NAME = "Win Memo Tool"
DEFAULT_HOLIDAY_API = "https://timor.tech/api/holiday/year"


@dataclass(frozen=True)
class AppPaths:
    base_dir: Path
    data_dir: Path
    database_path: Path
    config_path: Path
    log_dir: Path


def get_app_paths() -> AppPaths:
    if sys.platform == "win32":
        root = Path(os.environ.get("APPDATA", Path.home() / "AppData/Roaming")) / APP_NAME
    else:
        root = Path.home() / f".{APP_NAME}"

    data_dir = root / "data"
    log_dir = root / "logs"
    data_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)
    return AppPaths(
        base_dir=root,
        data_dir=data_dir,
        database_path=data_dir / "memo.db",
        config_path=root / "settings.json",
        log_dir=log_dir,
    )
