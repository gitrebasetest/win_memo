import json
import sys

from PyQt6.QtWidgets import QApplication

from memo_app.config import DISPLAY_NAME, DEFAULT_HOLIDAY_API, get_app_paths
from memo_app.data.database import Database
from memo_app.data.repository import MemoRepository
from memo_app.ui.main_window import MainWindow


def ensure_runtime_files() -> None:
    paths = get_app_paths()
    if not paths.config_path.exists():
        paths.config_path.write_text(
            json.dumps(
                {
                    "holiday_api": DEFAULT_HOLIDAY_API,
                    "startup_enabled": False,
                    "poll_interval_ms": 30000,
                    "default_snooze_minutes": [5, 10, 30],
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )


def main() -> int:
    ensure_runtime_files()
    paths = get_app_paths()
    database = Database(paths.database_path)
    database.initialize()
    repository = MemoRepository(database)

    app = QApplication(sys.argv)
    app.setApplicationName(DISPLAY_NAME)
    app.setQuitOnLastWindowClosed(False)

    window = MainWindow(repository=repository)
    window.show()

    return app.exec()
