from __future__ import annotations

import sqlite3
from pathlib import Path


class Database:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def initialize(self) -> None:
        with self.connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL DEFAULT '',
                    rule_type TEXT NOT NULL,
                    one_time_at TEXT,
                    weekday INTEGER,
                    time_of_day TEXT,
                    status TEXT NOT NULL DEFAULT 'pending',
                    snooze_until TEXT,
                    next_trigger_at TEXT,
                    last_triggered_at TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS holiday_cache (
                    day TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    holiday_name TEXT,
                    updated_at TEXT NOT NULL
                );
                """
            )
