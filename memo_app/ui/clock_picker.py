from __future__ import annotations

from datetime import datetime, time

from PyQt6.QtCore import Qt, QRectF, QPointF, pyqtSignal
from PyQt6.QtGui import (
    QColor,
    QFont,
    QPainter,
    QPen,
    QBrush,
    QMouseEvent,
    QRadialGradient,
    QPaintEvent,
)
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget
from math import pi, cos, sin, hypot, atan2


DARK_MODE = True


def set_clock_dark_mode(enabled: bool) -> None:
    global DARK_MODE
    DARK_MODE = enabled


class ClockTimePicker(QWidget):
    time_changed = pyqtSignal()

    _STEP_LABELS = {0: "选择小时", 1: "选择分钟", 2: "选择秒"}
    _CLOCK_RADIUS = 108
    _INNER_RADIUS = 66

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._step = 0
        self._hour = 12
        self._minute = 0
        self._second = 0
        self._hovered_value = -1
        self._is_minute_ring = False
        self.setFixedSize(320, 400)
        self.setMouseTracking(True)

    def set_time(self, value: time) -> None:
        self._hour = value.hour
        self._minute = value.minute
        self._second = value.second
        self._step = 0
        self.update()

    def get_time(self) -> time:
        return time(self._hour, self._minute, self._second)

    def paintEvent(self, event: QPaintEvent) -> None:  # noqa: ARG002
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        cx = self.width() / 2
        cy = self._CLOCK_RADIUS + 16
        dark = self._is_dark_mode()

        # background
        painter.fillRect(self.rect(), QColor("#1e1f29") if dark else QColor("#f4f6fb"))

        # clock plate shadow
        shadow = QRadialGradient(QPointF(cx, cy + 4), self._CLOCK_RADIUS + 10)
        shadow.setColorAt(0, QColor(0, 0, 0, 30))
        shadow.setColorAt(1, QColor(0, 0, 0, 0))
        painter.setBrush(QBrush(shadow))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPointF(cx, cy + 4), self._CLOCK_RADIUS + 10, self._CLOCK_RADIUS + 10)

        # clock plate
        plate_color = QColor("#2b2c3a") if dark else QColor("#ffffff")
        painter.setBrush(QBrush(plate_color))
        painter.setPen(QPen(QColor("#3a3d4d") if dark else QColor("#dbe0ef"), 1))
        painter.drawEllipse(QPointF(cx, cy), self._CLOCK_RADIUS, self._CLOCK_RADIUS)

        # inner ring for minute/second steps
        if self._step in (1, 2):
            inner_color = QColor("#313445") if dark else QColor("#f0f2fa")
            painter.setBrush(QBrush(inner_color))
            painter.setPen(QPen(QColor("#4c5168") if dark else QColor("#c5cee6"), 1))
            painter.drawEllipse(QPointF(cx, cy), self._INNER_RADIUS, self._INNER_RADIUS)

        accent = QColor("#bd93f9") if dark else QColor("#7c4dff")
        accent_dim = QColor("#3b3250") if dark else QColor("#f1e9ff")
        text_main = QColor("#f8f8f2") if dark else QColor("#1d2333")
        text_dim = QColor("#a8afc4") if dark else QColor("#79829b")

        if self._step == 0:
            self._draw_hours(painter, cx, cy, accent, accent_dim, text_main, text_dim)
        elif self._step == 1:
            self._draw_minutes(painter, cx, cy, accent, accent_dim, text_main, text_dim)
        else:
            self._draw_seconds(painter, cx, cy, accent, accent_dim, text_main, text_dim)

        # clock hands
        if self._step in (1, 2):
            hour_angle = pi / 2 - (self._hour % 12) * 2 * pi / 12
            hx = cx + self._INNER_RADIUS * 0.55 * cos(hour_angle)
            hy = cy - self._INNER_RADIUS * 0.55 * sin(hour_angle)
            painter.setPen(QPen(accent, 2))
            painter.drawLine(QPointF(cx, cy), QPointF(hx, hy))

        if self._step == 2:
            minute_angle = pi / 2 - self._minute * 2 * pi / 60
            mx = cx + self._INNER_RADIUS * 0.55 * cos(minute_angle)
            my = cy - self._INNER_RADIUS * 0.55 * sin(minute_angle)
            painter.setPen(QPen(accent, 2))
            painter.drawLine(QPointF(cx, cy), QPointF(mx, my))

        if self._step == 0:
            angle = pi / 2 - (self._hour % 12) * 2 * pi / 12
            hx = cx + self._CLOCK_RADIUS * 0.7 * cos(angle)
            hy = cy - self._CLOCK_RADIUS * 0.7 * sin(angle)
            painter.setPen(QPen(accent, 2.5))
            painter.drawLine(QPointF(cx, cy), QPointF(hx, hy))
            painter.setBrush(accent)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QPointF(cx, cy), 5, 5)
        elif self._step == 1:
            angle = pi / 2 - self._minute * 2 * pi / 60
            mx = cx + self._CLOCK_RADIUS * 0.7 * cos(angle)
            my = cy - self._CLOCK_RADIUS * 0.7 * sin(angle)
            painter.setPen(QPen(accent, 2.5))
            painter.drawLine(QPointF(cx, cy), QPointF(mx, my))
            painter.setBrush(accent)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QPointF(cx, cy), 5, 5)
        else:
            angle = pi / 2 - self._second * 2 * pi / 60
            sx = cx + self._CLOCK_RADIUS * 0.7 * cos(angle)
            sy = cy - self._CLOCK_RADIUS * 0.7 * sin(angle)
            painter.setPen(QPen(accent, 2.5))
            painter.drawLine(QPointF(cx, cy), QPointF(sx, sy))
            painter.setBrush(accent)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QPointF(cx, cy), 5, 5)

        # step label and time display
        font_title = QFont("Segoe UI", 11, QFont.Weight.Bold)
        painter.setFont(font_title)
        painter.setPen(text_main)
        step_label = self._STEP_LABELS[self._step]
        time_display = f"{self._hour:02d}:{self._minute:02d}:{self._second:02d}"
        painter.drawText(QRectF(16, 6, 280, 22), Qt.AlignmentFlag.AlignLeft, step_label)
        painter.drawText(QRectF(16, 6, 280, 22), Qt.AlignmentFlag.AlignRight, time_display)

        # step indicators
        dot_y = 8
        for i in range(3):
            dx = self.width() // 2 - 20 + i * 20
            dot_r = 4 if i == self._step else 3
            dot_color = accent if i == self._step else text_dim
            painter.setBrush(dot_color)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QPointF(dx, dot_y), dot_r, dot_r)

        painter.end()

    def _draw_hours(self, painter, cx, cy, accent, accent_dim, text_main, text_dim):
        for i in range(1, 13):
            angle = pi / 2 - i * 2 * pi / 12
            r = self._CLOCK_RADIUS * 0.72
            x = cx + r * cos(angle) - 12
            y = cy - r * sin(angle) - 10
            is_current = self._hour % 12 == i % 12
            is_hovered = self._hovered_value == i
            painter.save()
            if is_current:
                painter.setBrush(accent)
                painter.setPen(Qt.PenStyle.NoPen)
                circle_rect = QRectF(x - 4, y - 2, 24, 24)
                painter.drawRoundedRect(circle_rect, 12, 12)
                painter.setPen(QColor("#ffffff"))
            elif is_hovered:
                painter.setBrush(accent_dim)
                painter.setPen(Qt.PenStyle.NoPen)
                circle_rect = QRectF(x - 4, y - 2, 24, 24)
                painter.drawRoundedRect(circle_rect, 12, 12)
                painter.setPen(text_main)
            else:
                painter.setPen(text_main)
            font = QFont("Segoe UI", 13, QFont.Weight.Bold if is_current else QFont.Weight.Normal)
            painter.setFont(font)
            painter.drawText(QRectF(x, y, 24, 24), Qt.AlignmentFlag.AlignCenter, str(i))
            painter.restore()

    def _draw_minutes(self, painter, cx, cy, accent, accent_dim, text_main, text_dim):
        for i in range(0, 60, 5):
            angle = pi / 2 - i * 2 * pi / 60
            r = self._CLOCK_RADIUS * 0.72
            x = cx + r * cos(angle) - 12
            y = cy - r * sin(angle) - 10
            is_current = self._minute // 5 * 5 == i
            is_hovered = self._hovered_value == i
            painter.save()
            if is_current:
                painter.setBrush(accent)
                painter.setPen(Qt.PenStyle.NoPen)
                circle_rect = QRectF(x - 4, y - 2, 24, 24)
                painter.drawRoundedRect(circle_rect, 12, 12)
                painter.setPen(QColor("#ffffff"))
            elif is_hovered:
                painter.setBrush(accent_dim)
                painter.setPen(Qt.PenStyle.NoPen)
                circle_rect = QRectF(x - 4, y - 2, 24, 24)
                painter.drawRoundedRect(circle_rect, 12, 12)
                painter.setPen(text_main)
            else:
                painter.setPen(text_main)
            font = QFont("Segoe UI", 12, QFont.Weight.Bold if is_current else QFont.Weight.Normal)
            painter.setFont(font)
            painter.drawText(QRectF(x, y, 24, 24), Qt.AlignmentFlag.AlignCenter, str(i))
            painter.restore()

    def _draw_seconds(self, painter, cx, cy, accent, accent_dim, text_main, text_dim):
        for i in range(0, 60, 5):
            angle = pi / 2 - i * 2 * pi / 60
            r = self._CLOCK_RADIUS * 0.72
            x = cx + r * cos(angle) - 12
            y = cy - r * sin(angle) - 10
            is_current = self._second // 5 * 5 == i
            is_hovered = self._hovered_value == i
            painter.save()
            if is_current:
                painter.setBrush(accent)
                painter.setPen(Qt.PenStyle.NoPen)
                circle_rect = QRectF(x - 4, y - 2, 24, 24)
                painter.drawRoundedRect(circle_rect, 12, 12)
                painter.setPen(QColor("#ffffff"))
            elif is_hovered:
                painter.setBrush(accent_dim)
                painter.setPen(Qt.PenStyle.NoPen)
                circle_rect = QRectF(x - 4, y - 2, 24, 24)
                painter.drawRoundedRect(circle_rect, 12, 12)
                painter.setPen(text_main)
            else:
                painter.setPen(text_main)
            font = QFont("Segoe UI", 12, QFont.Weight.Bold if is_current else QFont.Weight.Normal)
            painter.setFont(font)
            painter.drawText(QRectF(x, y, 24, 24), Qt.AlignmentFlag.AlignCenter, str(i))
            painter.restore()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        cx = self.width() / 2
        cy = self._CLOCK_RADIUS + 16
        mx = event.position().x()
        my = event.position().y()
        dist = hypot(mx - cx, my - cy)
        angle = atan2(-(my - cy), mx - cx)
        if angle < 0:
            angle += 2 * pi
        degrees = angle * 180 / pi

        if self._step == 0 and dist < self._CLOCK_RADIUS and dist > self._CLOCK_RADIUS * 0.3:
            hour_idx = round(degrees / 30) % 12
            self._hovered_value = 12 if hour_idx == 0 else hour_idx
            self.update()
        elif self._step == 1 and dist < self._CLOCK_RADIUS and dist > self._CLOCK_RADIUS * 0.3:
            self._hovered_value = round(degrees / 6) % 60 // 5 * 5
            self.update()
        elif self._step == 2 and dist < self._CLOCK_RADIUS and dist > self._CLOCK_RADIUS * 0.3:
            self._hovered_value = round(degrees / 6) % 60 // 5 * 5
            self.update()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        cx = self.width() / 2
        cy = self._CLOCK_RADIUS + 16
        mx = event.position().x()
        my = event.position().y()
        dist = hypot(mx - cx, my - cy)
        angle = atan2(-(my - cy), mx - cx)
        if angle < 0:
            angle += 2 * pi
        degrees = angle * 180 / pi

        if dist > self._CLOCK_RADIUS or dist < self._CLOCK_RADIUS * 0.25:
            return

        if self._step == 0:
            hour_idx = round(degrees / 30) % 12
            self._hour = 12 if hour_idx == 0 else hour_idx
            self._step = 1
            self._hovered_value = -1
            self.update()
        elif self._step == 1:
            minute_idx = round(degrees / 6) % 60 // 5 * 5
            self._minute = minute_idx
            self._step = 2
            self._hovered_value = -1
            self.update()
        elif self._step == 2:
            second_idx = round(degrees / 6) % 60 // 5 * 5
            self._second = second_idx
            self._step = 0
            self._hovered_value = -1
            self.time_changed.emit()
            self.update()

    def _is_dark_mode(self) -> bool:
        return DARK_MODE


class ClockTimePopup(QFrame):
    time_selected = pyqtSignal(time)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("clockTimePopup")
        self.setWindowFlags(
            Qt.WindowType.ToolTip | Qt.WindowType.FramelessWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._picker = ClockTimePicker(self)
        self.setFixedSize(self._picker.width(), self._picker.height() + 52)
        layout.addWidget(self._picker)

        footer = QFrame()
        footer.setObjectName("clockFooter")
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(12, 10, 12, 10)
        self._ok_btn = QLabel("确 定")
        self._ok_btn.setObjectName("clockOkButton")
        self._ok_btn.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer_layout.addStretch()
        footer_layout.addWidget(self._ok_btn)
        layout.addWidget(footer)

        self._ok_btn.mousePressEvent = lambda e: self._accept()

        self.adjustSize()

    def set_time(self, value: time) -> None:
        self._picker.set_time(value)

    def get_time(self) -> time:
        return self._picker.get_time()

    def _accept(self) -> None:
        self._picker._step = 0
        self._picker.update()
        self.time_selected.emit(self.get_time())
        self.hide()