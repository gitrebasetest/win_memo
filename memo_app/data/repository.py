from __future__ import annotations

from typing import Iterable

from memo_app.data.database import Database
from memo_app.models import HolidayRecord, MemoEvent, now_iso


class MemoRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def list_events(self) -> list[MemoEvent]:
        with self.database.connect() as conn:
            rows = conn.execute(
                """
                SELECT *
                FROM events
                ORDER BY COALESCE(next_trigger_at, '9999-12-31 23:59:59'), updated_at DESC
                """
            ).fetchall()
        return [self._row_to_event(row) for row in rows]

    def create_event(self, event: MemoEvent) -> MemoEvent:
        with self.database.connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO events (
                    title, content, rule_type, one_time_at, weekday, time_of_day,
                    status, snooze_until, next_trigger_at, last_triggered_at,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event.title,
                    event.content,
                    event.rule_type,
                    event.one_time_at,
                    event.weekday,
                    event.time_of_day,
                    event.status,
                    event.snooze_until,
                    event.next_trigger_at,
                    event.last_triggered_at,
                    event.created_at,
                    event.updated_at,
                ),
            )
            event.id = int(cursor.lastrowid)
        return event

    def update_event(self, event: MemoEvent) -> None:
        with self.database.connect() as conn:
            conn.execute(
                """
                UPDATE events
                SET title = ?, content = ?, rule_type = ?, one_time_at = ?, weekday = ?,
                    time_of_day = ?, status = ?, snooze_until = ?, next_trigger_at = ?,
                    last_triggered_at = ?, updated_at = ?
                WHERE id = ?
                """,
                (
                    event.title,
                    event.content,
                    event.rule_type,
                    event.one_time_at,
                    event.weekday,
                    event.time_of_day,
                    event.status,
                    event.snooze_until,
                    event.next_trigger_at,
                    event.last_triggered_at,
                    now_iso(),
                    event.id,
                ),
            )

    def delete_event(self, event_id: int) -> None:
        with self.database.connect() as conn:
            conn.execute("DELETE FROM events WHERE id = ?", (event_id,))

    def upsert_holiday_records(self, records: Iterable[HolidayRecord]) -> None:
        with self.database.connect() as conn:
            conn.executemany(
                """
                INSERT INTO holiday_cache (day, status, holiday_name, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(day) DO UPDATE SET
                    status = excluded.status,
                    holiday_name = excluded.holiday_name,
                    updated_at = excluded.updated_at
                """,
                [(record.day, record.status, record.holiday_name, record.updated_at) for record in records],
            )

    def get_holiday_record(self, day: str) -> HolidayRecord | None:
        with self.database.connect() as conn:
            row = conn.execute("SELECT * FROM holiday_cache WHERE day = ?", (day,)).fetchone()
        if row is None:
            return None
        return HolidayRecord(
            day=row["day"],
            status=row["status"],
            holiday_name=row["holiday_name"],
            updated_at=row["updated_at"],
        )

    @staticmethod
    def _row_to_event(row) -> MemoEvent:
        return MemoEvent(
            id=row["id"],
            title=row["title"],
            content=row["content"],
            rule_type=row["rule_type"],
            one_time_at=row["one_time_at"],
            weekday=row["weekday"],
            time_of_day=row["time_of_day"],
            status=row["status"],
            snooze_until=row["snooze_until"],
            next_trigger_at=row["next_trigger_at"],
            last_triggered_at=row["last_triggered_at"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
