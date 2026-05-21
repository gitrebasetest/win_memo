from __future__ import annotations

from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, Qt
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from memo_app.ui.theme import build_app_stylesheet


class ReminderWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("reminderWindow")
        self.setWindowTitle("提醒")
        self.setWindowFlag(Qt.WindowType.Tool, True)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        self.resize(520, 220)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        content_card = QFrame()
        content_card.setObjectName("reminderContentCard")
        content_layout = QVBoxLayout(content_card)
        content_layout.setContentsMargins(16, 16, 16, 16)
        content_layout.setSpacing(10)

        top_row = QHBoxLayout()
        top_row.setSpacing(10)
        badge = QLabel("到点提醒")
        badge.setObjectName("badge")
        self.dismiss_button = QPushButton("×")
        self.dismiss_button.setObjectName("reminderCloseButton")
        top_row.addWidget(badge)
        top_row.addStretch(1)
        top_row.addWidget(self.dismiss_button)
        content_layout.addLayout(top_row)

        self.title_label = QLabel()
        self.title_label.setObjectName("title")
        self.content_label = QLabel()
        self.content_label.setObjectName("content")
        self.content_label.setWordWrap(True)
        self.content_label.setMinimumHeight(56)
        content_layout.addWidget(self.title_label)
        content_layout.addWidget(self.content_label)
        layout.addWidget(content_card)

        actions_card = QFrame()
        actions_card.setObjectName("reminderActions")
        actions_layout = QHBoxLayout(actions_card)
        actions_layout.setContentsMargins(14, 14, 14, 14)
        actions_layout.setSpacing(10)

        self.snooze_5_button = QPushButton("延后 5 分钟")
        self.snooze_10_button = QPushButton("延后 10 分钟")
        self.snooze_30_button = QPushButton("延后 30 分钟")
        for button in (self.snooze_5_button, self.snooze_10_button, self.snooze_30_button):
            button.setObjectName("primaryButton")
            actions_layout.addWidget(button)
        layout.addWidget(actions_card)

        self.apply_theme(False)

        self.animation = QPropertyAnimation(self, b"windowOpacity", self)
        self.animation.setDuration(260)
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)

    def apply_theme(self, dark_mode_enabled: bool) -> None:
        self.setStyleSheet(build_app_stylesheet(dark_mode_enabled))

    def show_event(self, title: str, content: str) -> None:
        self.title_label.setText(title)
        self.content_label.setText(content)
        self.setWindowOpacity(0.0)
        self.show()
        self.raise_()
        self.activateWindow()
        self.animation.start()
