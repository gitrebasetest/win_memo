from __future__ import annotations

from datetime import date
import requests

from memo_app.config import DEFAULT_HOLIDAY_API
from memo_app.data.repository import MemoRepository
from memo_app.models import HolidayRecord, now_iso


class HolidayService:
    def __init__(self, repository: MemoRepository, api_base: str = DEFAULT_HOLIDAY_API) -> None:
        self.repository = repository
        self.api_base = api_base.rstrip("/")

    def get_day_status(self, day: date) -> str | None:
        record = self.repository.get_holiday_record(day.isoformat())
        if record is not None:
            return record.status
        try:
            self.fetch_year(day.year)
        except requests.RequestException:
            return None
        record = self.repository.get_holiday_record(day.isoformat())
        return record.status if record else None

    def fetch_year(self, year: int) -> None:
        response = requests.get(f"{self.api_base}/{year}", timeout=10)
        response.raise_for_status()
        payload = response.json()
        holiday_map = payload.get("holiday", {})
        records: list[HolidayRecord] = []
        for day, meta in holiday_map.items():
            status = "workday" if meta.get("holiday") is False else "holiday"
            records.append(
                HolidayRecord(
                    day=day,
                    status=status,
                    holiday_name=meta.get("name"),
                    updated_at=now_iso(),
                )
            )
        if records:
            self.repository.upsert_holiday_records(records)
