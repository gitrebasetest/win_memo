from __future__ import annotations

from datetime import date, datetime, time, timedelta

from memo_app.models import MemoEvent
from memo_app.services.holiday_service import HolidayService


class Scheduler:
    def __init__(self, holiday_service: HolidayService) -> None:
        self.holiday_service = holiday_service

    def compute_next_trigger(self, event: MemoEvent, reference: datetime | None = None) -> str | None:
        now = reference or datetime.now().replace(microsecond=0)
        if event.snooze_until:
            snooze_at = datetime.fromisoformat(event.snooze_until)
            if snooze_at >= now:
                return snooze_at.isoformat(sep=" ")

        if event.rule_type == "one_time":
            if not event.one_time_at:
                return None
            target = datetime.fromisoformat(event.one_time_at)
            return target.isoformat(sep=" ") if target >= now else None

        if not event.time_of_day:
            return None
        trigger_time = time.fromisoformat(event.time_of_day)

        if event.rule_type == "weekly":
            weekday = event.weekday if event.weekday is not None else 0
            return self._next_weekly_trigger(now, weekday, trigger_time).isoformat(sep=" ")

        if event.rule_type == "workday":
            return self._next_workday_trigger(now, trigger_time).isoformat(sep=" ")

        return None

    def _next_weekly_trigger(self, now: datetime, weekday: int, trigger_time: time) -> datetime:
        current = datetime.combine(now.date(), trigger_time)
        days_ahead = (weekday - now.weekday()) % 7
        candidate = current + timedelta(days=days_ahead)
        if candidate < now:
            candidate += timedelta(days=7)
        return candidate

    def _next_workday_trigger(self, now: datetime, trigger_time: time) -> datetime:
        day = now.date()
        candidate = datetime.combine(day, trigger_time)
        if candidate < now:
            day += timedelta(days=1)
        while not self._is_workday(day):
            day += timedelta(days=1)
        return datetime.combine(day, trigger_time)

    def _is_workday(self, day: date) -> bool:
        status = self.holiday_service.get_day_status(day)
        if status == "workday":
            return True
        if status == "holiday":
            return False
        return day.weekday() < 5
