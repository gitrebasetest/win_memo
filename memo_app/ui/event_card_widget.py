from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout

from memo_app.models import MemoEvent

STATUS_LABELS = {
    "pending": "待提醒",
    "done": "已完成",
    "dismissed": "已关闭",
}


class EventCardWidget(QFrame):
    def __init__(self, event: MemoEvent, dark_mode_enabled: bool) -> None:
        super().__init__()
        self.event = event
        self.dark_mode_enabled = dark_mode_enabled
        self._build_ui()
        self._apply_theme()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(8)

        header_row = QHBoxLayout()
        header_row.setSpacing(8)
        type_dot = QLabel("●")
        type_dot.setObjectName(f"typeDot_{self.event.rule_type}")
        type_dot.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title = QLabel(self.event.title)
        title.setObjectName("cardTitle")
        header_row.addWidget(type_dot, 0)
        header_row.addWidget(title, 1)

        meta_row = QHBoxLayout()
        meta_row.setSpacing(8)
        schedule = QLabel(f"下次提醒：{self.event.next_trigger_at or self.event.one_time_at or self.event.time_of_day or '未安排'}")
        schedule.setObjectName("cardSchedule")
        status_badge = QLabel(STATUS_LABELS.get(self.event.status, self.event.status))
        status_badge.setObjectName(f"statusBadge_{self.event.status}")
        meta_row.addWidget(schedule, 1)
        meta_row.addWidget(status_badge, 0)

        preview = QLabel(self.event.content.strip() or "暂无备注内容")
        preview.setObjectName("cardPreview")
        preview.setWordWrap(True)

        layout.addLayout(header_row)
        layout.addLayout(meta_row)
        layout.addWidget(preview)

    def _apply_theme(self) -> None:
        if self.dark_mode_enabled:
            stylesheet = """
            QFrame {
                background: #2f2f2f;
                border: 1px solid #3f3f3f;
                border-radius: 10px;
            }
            QLabel#cardTitle {
                color: #ffffff;
                font-size: 15px;
                font-weight: 700;
                background: transparent;
            }
            QLabel#cardSchedule {
                color: #c9ced6;
                font-size: 12px;
                background: transparent;
            }
            QLabel#cardPreview {
                color: #d7dbe1;
                font-size: 12px;
                background: transparent;
            }
            QLabel#typeDot_one_time, QLabel#typeDot_weekly, QLabel#typeDot_workday {
                font-size: 16px;
                font-weight: 700;
                min-width: 16px;
                max-width: 16px;
                background: transparent;
            }
            QLabel#typeDot_one_time { color: #c084fc; }
            QLabel#typeDot_weekly { color: #60a5fa; }
            QLabel#typeDot_workday { color: #4ade80; }
            QLabel#statusBadge_pending, QLabel#statusBadge_done, QLabel#statusBadge_dismissed {
                border-radius: 10px;
                padding: 4px 10px;
                font-size: 11px;
                font-weight: 600;
            }
            QLabel#statusBadge_pending { background: #3a334b; color: #d7ccff; }
            QLabel#statusBadge_done { background: #1f4d3a; color: #9ff0bf; }
            QLabel#statusBadge_dismissed { background: #4b2f35; color: #ffbec3; }
            """
        else:
            stylesheet = """
            QFrame {
                background: #ffffff;
                border: 1px solid #e5e7eb;
                border-radius: 10px;
            }
            QLabel#cardTitle {
                color: #172033;
                font-size: 15px;
                font-weight: 700;
                background: transparent;
            }
            QLabel#cardSchedule {
                color: #6b7890;
                font-size: 12px;
                background: transparent;
            }
            QLabel#cardPreview {
                color: #55637d;
                font-size: 12px;
                background: transparent;
            }
            QLabel#typeDot_one_time, QLabel#typeDot_weekly, QLabel#typeDot_workday {
                font-size: 16px;
                font-weight: 700;
                min-width: 16px;
                max-width: 16px;
                background: transparent;
            }
            QLabel#typeDot_one_time { color: #9333ea; }
            QLabel#typeDot_weekly { color: #0284c7; }
            QLabel#typeDot_workday { color: #16a34a; }
            QLabel#statusBadge_pending, QLabel#statusBadge_done, QLabel#statusBadge_dismissed {
                border-radius: 10px;
                padding: 4px 10px;
                font-size: 11px;
                font-weight: 600;
            }
            QLabel#statusBadge_pending { background: #eef2ff; color: #4f46e5; }
            QLabel#statusBadge_done { background: #dcfce7; color: #166534; }
            QLabel#statusBadge_dismissed { background: #fee2e2; color: #b91c1c; }
            """
        self.setStyleSheet(stylesheet)
