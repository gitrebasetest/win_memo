from __future__ import annotations

from datetime import datetime, time

from PyQt6.QtCore import Qt, QRectF, QPointF, pyqtSignal, QEvent
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

from memo_app.ui.theme import build_app_stylesheet, get_palette


DARK_MODE = True


def set_clock_dark_mode(enabled: bool) -> None:
    global DARK_MODE
    DARK_MODE = enabled


def _rhu(x: float) -> int:
    """Round half-up away from zero.

    Python's int() truncates toward zero, which is exactly what we need:
    int(3.7) = 3   int(-3.7) = -3.  Adding 0.5 before truncation gives
    standard half-up rounding in all quadrants.
    """
    return int(x + 0.5) if x >= 0 else int(x - 0.5)

class ClockTimePicker(QWidget):
    time_changed = pyqtSignal()

    _STEP_LABELS = {0: "选择小时", 1: "选择分钟", 2: "选择秒"}
    _CLOCK_RADIUS = 108
    _INNER_RADIUS = 60
    _MID_RADIUS = 69

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._step = 0
        self._hour = 12
        self._minute = 0
        self._second = 0
        self._hovered_value = -1
        self.setFixedSize(320, 260)
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

        dark = DARK_MODE
        palette = get_palette(dark)

        # Fill the entire picker with the same card background as ClockTimePopup
        painter.fillRect(self.rect(), QColor(palette.card_background))

        header_h = 28
        cx = self.width() / 2
        cy = header_h + self._CLOCK_RADIUS

        # disc shadow
        shadow = QRadialGradient(QPointF(cx, cy + 4), self._CLOCK_RADIUS + 8)
        shadow.setColorAt(0, QColor(0, 0, 0, 25))
        shadow.setColorAt(1, QColor(0, 0, 0, 0))
        painter.setBrush(QBrush(shadow))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPointF(cx, cy + 4), self._CLOCK_RADIUS + 8, self._CLOCK_RADIUS + 8)

        # disc plate
        painter.setBrush(QBrush(QColor(palette.card_background)))
        painter.setPen(QPen(QColor(palette.border), 1))
        painter.drawEllipse(QPointF(cx, cy), self._CLOCK_RADIUS, self._CLOCK_RADIUS)

        # inner ring for minute/second steps
        if self._step in (1, 2):
            painter.setBrush(QBrush(QColor(palette.panel_background)))
            painter.setPen(QPen(QColor(palette.border), 1))
            painter.drawEllipse(QPointF(cx, cy), self._INNER_RADIUS, self._INNER_RADIUS)

        accent = QColor(palette.accent)
        accent_dim = QColor(palette.accent_soft)
        text_main = QColor(palette.text_primary)
        text_dim = QColor(palette.text_muted)

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
            HX = cx + self._CLOCK_RADIUS * 0.7 * cos(angle)
            HY = cy - self._CLOCK_RADIUS * 0.7 * sin(angle)
            painter.setPen(QPen(accent, 2.5))
            painter.drawLine(QPointF(cx, cy), QPointF(HX, HY))
            painter.setBrush(accent)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QPointF(cx, cy), 5, 5)
        elif self._step == 1:
            angle = pi / 2 - self._minute * 2 * pi / 60
            MX = cx + self._CLOCK_RADIUS * 0.7 * cos(angle)
            MY = cy - self._CLOCK_RADIUS * 0.7 * sin(angle)
            painter.setPen(QPen(accent, 2.5))
            painter.drawLine(QPointF(cx, cy), QPointF(MX, MY))
            painter.setBrush(accent)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QPointF(cx, cy), 5, 5)
        else:
            angle = pi / 2 - self._second * 2 * pi / 60
            SX = cx + self._CLOCK_RADIUS * 0.7 * cos(angle)
            SY = cy - self._CLOCK_RADIUS * 0.7 * sin(angle)
            painter.setPen(QPen(accent, 2.5))
            painter.drawLine(QPointF(cx, cy), QPointF(SX, SY))
            painter.setBrush(accent)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QPointF(cx, cy), 5, 5)

        # top header: step label + time display + dots
        font_title = QFont("Segoe UI", 11, QFont.Weight.Bold)
        painter.setFont(font_title)
        painter.setPen(text_main)
        step_label = self._STEP_LABELS[self._step]
        time_display = f"{self._hour:02d}:{self._minute:02d}:{self._second:02d}"
        painter.drawText(QRectF(16, 0, 280, 20), Qt.AlignmentFlag.AlignLeft, step_label)
        painter.drawText(QRectF(16, 0, 280, 20), Qt.AlignmentFlag.AlignRight, time_display)

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
        # outer ring: 1-12
        for i in range(1, 13):
            angle = pi / 2 - i * 2 * pi / 12
            r = self._CLOCK_RADIUS * 0.73
            x = cx + r * cos(angle) - 13
            y = cy - r * sin(angle) - 11
            is_current = self._hour == i or (i == 12 and self._hour == 0)
            is_hovered = self._hovered_value == i
            painter.save()
            if is_current:
                painter.setBrush(accent)
                painter.setPen(Qt.PenStyle.NoPen)
                circle_rect = QRectF(x - 4, y - 2, 26, 26)
                painter.drawRoundedRect(circle_rect, 13, 13)
                painter.setPen(QColor("#ffffff"))
            elif is_hovered:
                painter.setBrush(accent_dim)
                painter.setPen(Qt.PenStyle.NoPen)
                circle_rect = QRectF(x - 4, y - 2, 26, 26)
                painter.drawRoundedRect(circle_rect, 13, 13)
                painter.setPen(text_main)
            else:
                painter.setPen(text_main)
            font = QFont("Segoe UI", 12, QFont.Weight.Bold if is_current else QFont.Weight.Normal)
            painter.setFont(font)
            painter.drawText(QRectF(x, y, 26, 26), Qt.AlignmentFlag.AlignCenter, str(i))
            painter.restore()

        # inner ring: 0, 13-23
        for i in range(13, 25):
            display = 0 if i == 24 else i
            angle = pi / 2 - (i % 12) * 2 * pi / 12
            r = self._MID_RADIUS * 0.68
            x = cx + r * cos(angle) - 11
            y = cy - r * sin(angle) - 9
            is_current = self._hour == display
            is_hovered = self._hovered_value == display
            painter.save()
            if is_current:
                painter.setBrush(accent)
                painter.setPen(Qt.PenStyle.NoPen)
                circle_rect = QRectF(x - 2, y - 1, 22, 22)
                painter.drawRoundedRect(circle_rect, 11, 11)
                painter.setPen(QColor("#ffffff"))
            elif is_hovered:
                painter.setBrush(accent_dim)
                painter.setPen(Qt.PenStyle.NoPen)
                circle_rect = QRectF(x - 2, y - 1, 22, 22)
                painter.drawRoundedRect(circle_rect, 11, 11)
                painter.setPen(text_main)
            else:
                painter.setPen(text_dim)
            font = QFont("Segoe UI", 10, QFont.Weight.Bold if is_current else QFont.Weight.Normal)
            painter.setFont(font)
            painter.drawText(QRectF(x, y, 22, 22), Qt.AlignmentFlag.AlignCenter, str(display))
            painter.restore()

    def _draw_minutes(self, painter, cx, cy, accent, accent_dim, text_main, text_dim):
        for i in range(0, 60):
            angle = pi / 2 - i * 2 * pi / 60
            is_label = i % 5 == 0
            r_text = self._CLOCK_RADIUS * 0.72
            r_mid = self._CLOCK_RADIUS * 0.62
            r_tick = self._CLOCK_RADIUS * 0.88
            r_tick_inner = self._CLOCK_RADIUS * 0.80
            rx = cos(angle)
            ry = -sin(angle)
            is_current = self._minute == i
            is_hovered = self._hovered_value == i

            if is_label or is_hovered:
                x = cx + r_text * rx - 12
                y = cy + r_text * ry - 10
                if not is_label and is_hovered:
                    # hovered non-label: show number in a small pop pill below the tick
                    x = int(cx + r_mid * rx - 10)
                    y = int(cy + r_mid * ry - 9)
                    painter.save()
                    painter.setBrush(accent)
                    painter.setPen(Qt.PenStyle.NoPen)
                    pill_rect = QRectF(x - 2, y - 1, 20, 18)
                    painter.drawRoundedRect(pill_rect, 9, 9)
                    painter.setPen(QColor("#ffffff"))
                    font = QFont("Segoe UI", 9, QFont.Weight.Bold)
                    painter.setFont(font)
                    painter.drawText(QRectF(x, y, 18, 18), Qt.AlignmentFlag.AlignCenter, str(i))
                    painter.restore()
                else:
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
                    font = QFont("Segoe UI", 11, QFont.Weight.Bold if is_current else QFont.Weight.Normal)
                    painter.setFont(font)
                    painter.drawText(QRectF(x, y, 24, 24), Qt.AlignmentFlag.AlignCenter, str(i))
                    painter.restore()
            else:
                # thin tick mark
                tick_color = accent if is_current else text_dim
                painter.setPen(QPen(tick_color, 1))
                x1 = cx + r_tick_inner * rx
                y1 = cy + r_tick_inner * ry
                x2 = cx + r_tick * rx
                y2 = cy + r_tick * ry
                painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))

    def _draw_seconds(self, painter, cx, cy, accent, accent_dim, text_main, text_dim):
        for i in range(0, 60):
            angle = pi / 2 - i * 2 * pi / 60
            is_label = i % 5 == 0
            r_text = self._CLOCK_RADIUS * 0.72
            r_mid = self._CLOCK_RADIUS * 0.62
            r_tick = self._CLOCK_RADIUS * 0.88
            r_tick_inner = self._CLOCK_RADIUS * 0.80
            rx = cos(angle)
            ry = -sin(angle)
            is_current = self._second == i
            is_hovered = self._hovered_value == i

            if is_label or is_hovered:
                x = cx + r_text * rx - 12
                y = cy + r_text * ry - 10
                if not is_label and is_hovered:
                    x = int(cx + r_mid * rx - 10)
                    y = int(cy + r_mid * ry - 9)
                    painter.save()
                    painter.setBrush(accent)
                    painter.setPen(Qt.PenStyle.NoPen)
                    pill_rect = QRectF(x - 2, y - 1, 20, 18)
                    painter.drawRoundedRect(pill_rect, 9, 9)
                    painter.setPen(QColor("#ffffff"))
                    font = QFont("Segoe UI", 9, QFont.Weight.Bold)
                    painter.setFont(font)
                    painter.drawText(QRectF(x, y, 18, 18), Qt.AlignmentFlag.AlignCenter, str(i))
                    painter.restore()
                else:
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
                    font = QFont("Segoe UI", 11, QFont.Weight.Bold if is_current else QFont.Weight.Normal)
                    painter.setFont(font)
                    painter.drawText(QRectF(x, y, 24, 24), Qt.AlignmentFlag.AlignCenter, str(i))
                    painter.restore()
            else:
                tick_color = accent if is_current else text_dim
                painter.setPen(QPen(tick_color, 1))
                x1 = cx + r_tick_inner * rx
                y1 = cy + r_tick_inner * ry
                x2 = cx + r_tick * rx
                y2 = cy + r_tick * ry
                painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))

    def _disc_center(self) -> tuple[float, float]:
        header_h = 28
        return self.width() / 2, header_h + self._CLOCK_RADIUS

    def _angle_to_clock_index(self, degrees: float) -> int:
        """Map mouse angle to a 12-hour clock index (0=12 o'clock, 1=1 o'clock, ..., 11=11 o'clock)."""
        raw = (90.0 - degrees) / 30.0
        idx = _rhu(raw) % 12
        return idx  # 0..11

    def _angle_to_min_sec(self, degrees: float) -> int:
        """Map mouse angle to 0-59 minute/second value."""
        raw = (90.0 - degrees) / 6.0
        return _rhu(raw) % 60

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        cx, cy = self._disc_center()
        mx = event.position().x()
        my = event.position().y()
        dist = hypot(mx - cx, my - cy)
        angle = atan2(-(my - cy), mx - cx)
        if angle < 0:
            angle += 2 * pi
        degrees = angle * 180 / pi

        if self._step == 0 and dist > self._INNER_RADIUS * 0.35 and dist < self._CLOCK_RADIUS * 1.05:
            is_inner = dist < self._MID_RADIUS
            ci = self._angle_to_clock_index(degrees)
            if is_inner:
                self._hovered_value = 0 if ci == 0 else ci + 12  # inner: 0, 13-23
            else:
                self._hovered_value = 12 if ci == 0 else ci      # outer: 1-12
            self.update()
        elif self._step == 1 and dist > self._CLOCK_RADIUS * 0.3 and dist < self._CLOCK_RADIUS * 1.05:
            self._hovered_value = self._angle_to_min_sec(degrees)
            self.update()
        elif self._step == 2 and dist > self._CLOCK_RADIUS * 0.3 and dist < self._CLOCK_RADIUS * 1.05:
            self._hovered_value = self._angle_to_min_sec(degrees)
            self.update()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        cx, cy = self._disc_center()
        mx = event.position().x()
        my = event.position().y()
        dist = hypot(mx - cx, my - cy)
        angle = atan2(-(my - cy), mx - cx)
        if angle < 0:
            angle += 2 * pi
        degrees = angle * 180 / pi

        if dist > self._CLOCK_RADIUS * 1.05 or dist < self._INNER_RADIUS * 0.35:
            return

        if self._step == 0:
            is_inner = dist < self._MID_RADIUS
            ci = self._angle_to_clock_index(degrees)
            if is_inner:
                self._hour = 0 if ci == 0 else ci + 12
            else:
                self._hour = 12 if ci == 0 else ci
            self._step = 1
            self._hovered_value = -1
            self.update()
        elif self._step == 1:
            self._minute = self._angle_to_min_sec(degrees)
            self._step = 2
            self._hovered_value = -1
            self.update()
        elif self._step == 2:
            self._second = self._angle_to_min_sec(degrees)
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
            Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, False)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._picker = ClockTimePicker(self)
        self._picker.time_changed.connect(self._on_picker_done)
        self.setFixedSize(self._picker.width(), self._picker.height())
        layout.addWidget(self._picker)

        self.adjustSize()
        self.setMouseTracking(True)
        self.installEventFilter(self)

    def paintEvent(self, event) -> None:
        palette = get_palette(DARK_MODE)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QColor(palette.card_background))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(self.rect())
        painter.end()

    def set_time(self, value: time) -> None:
        self._picker.set_time(value)

    def get_time(self) -> time:
        return self._picker.get_time()

    def _on_picker_done(self) -> None:
        self.time_selected.emit(self.get_time())
        self.hide()

    def eventFilter(self, obj, event) -> bool:
        if event.type() == QEvent.Type.Leave and obj is self:
            self.time_selected.emit(self.get_time())
            self.hide()
        return super().eventFilter(obj, event)