from __future__ import annotations

from datetime import datetime, time

from PyQt6.QtCore import Qt, QTime
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QWidget

from memo_app.ui.clock_picker import ClockTimePopup


class ClockTimeInput(QFrame):
    """A clickable time display field that opens a clock-style time picker popup."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("clockTimeInput")
        self._popup = ClockTimePopup()
        self._popup.time_selected.connect(self._on_time_selected)
        self._current = QTime.fromString("12:00:00", "HH:mm:ss")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(0)
        self._label = QLabel("12:00:00")
        self._label.setObjectName("clockTimeLabel")
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._label)

        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.mousePressEvent = self._on_click

    def _on_click(self, _event) -> None:
        py_time = self._current.toPyTime()
        self._popup.set_time(py_time)
        pos = self.mapToGlobal(self.rect().bottomLeft())
        self._popup.move(pos)
        self._popup.show()

    def _on_time_selected(self, selected: time) -> None:
        self._current = QTime(selected.hour, selected.minute, selected.second)
        self._label.setText(selected.strftime("%H:%M:%S"))

    def time(self) -> QTime:
        return QTime(self._current)

    def setTime(self, qt: QTime) -> None:
        self._current = QTime(qt)
        self._label.setText(qt.toString("HH:mm:ss"))

    def setEnabled(self, enabled: bool) -> None:
        super().setEnabled(enabled)
        self._label.setEnabled(enabled)