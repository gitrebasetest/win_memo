from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class MemoEvent:
    id: Optional[int]
    title: str
    content: str
    rule_type: str
    one_time_at: Optional[str]
    weekday: Optional[int]
    time_of_day: Optional[str]
    status: str
    snooze_until: Optional[str]
    next_trigger_at: Optional[str]
    last_triggered_at: Optional[str]
    created_at: str
    updated_at: str


@dataclass
class HolidayRecord:
    day: str
    status: str
    holiday_name: Optional[str]
    updated_at: str


def now_iso() -> str:
    return datetime.now().replace(microsecond=0).isoformat(sep=" ")
