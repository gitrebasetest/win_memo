from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout

from memo_app.models import MemoEvent

RULE_LABELS = {
    "one_time": "一次性提醒",
    "weekly": "每周提醒",
    "workday": "工作日提醒",
}


class EventCardWidget(QFrame):
    def __init__(self, event: MemoEvent) -> None:
        super().__init__()
        self.event = event
        self._build_ui()

    def _build_ui(self) -> None:
        self.setObjectName("eventCard")
        self.setProperty("selected", False)

        outer_layout = QHBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        rail = QLabel()
        rail.setObjectName("cardSelectionRail")
        rail.setMinimumHeight(72)
        outer_layout.addWidget(rail, 0)

        body = QFrame()
        body.setObjectName("eventCardBody")
        layout = QVBoxLayout(body)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(8)

        rule_label = QLabel(RULE_LABELS.get(self.event.rule_type, self.event.rule_type))
        rule_label.setObjectName("cardRuleLabel")

        header_row = QHBoxLayout()
        header_row.setSpacing(8)
        type_dot = QLabel("●")
        type_dot.setProperty("typeDot", self.event.rule_type)
        type_dot.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title = QLabel(self.event.title)
        title.setObjectName("cardTitle")
        title.setWordWrap(False)
        header_row.addWidget(type_dot, 0)
        header_row.addWidget(title, 1)

        meta_row = QHBoxLayout()
        meta_row.setSpacing(8)
        schedule = QLabel(f"下次提醒：{self.event.next_trigger_at or self.event.one_time_at or self.event.time_of_day or '未安排'}")
        schedule.setObjectName("cardSchedule")
        schedule.setWordWrap(False)
        meta_row.addWidget(schedule, 1)

        preview = QLabel(self.event.content.strip() or "暂无备注内容")
        preview.setObjectName("cardPreview")
        preview.setWordWrap(False)

        layout.addWidget(rule_label)
        layout.addLayout(header_row)
        layout.addLayout(meta_row)
        layout.addWidget(preview)
        outer_layout.addWidget(body, 1)

    def set_selected(self, selected: bool) -> None:
        self.setProperty("selected", selected)
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()
