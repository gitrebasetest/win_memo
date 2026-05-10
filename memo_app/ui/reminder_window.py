from __future__ import annotations

from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, Qt
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget


class ReminderWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("提醒")
        self.setWindowFlag(Qt.WindowType.Tool, True)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        self.resize(420, 220)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        badge = QLabel("到点提醒")
        badge.setObjectName("badge")
        self.title_label = QLabel()
        self.title_label.setObjectName("title")
        self.content_label = QLabel()
        self.content_label.setObjectName("content")
        self.content_label.setWordWrap(True)
        layout.addWidget(badge)
        layout.addWidget(self.title_label)
        layout.addWidget(self.content_label)

        actions = QHBoxLayout()
        actions.setSpacing(8)
        self.dismiss_button = QPushButton("关闭")
        self.dismiss_button.setObjectName("secondaryButton")
        self.snooze_5_button = QPushButton("延后 5 分钟")
        self.snooze_10_button = QPushButton("延后 10 分钟")
        self.snooze_30_button = QPushButton("延后 30 分钟")
        for button in (self.snooze_5_button, self.snooze_10_button, self.snooze_30_button):
            button.setObjectName("primaryButton")
        actions.addWidget(self.dismiss_button)
        actions.addWidget(self.snooze_5_button)
        actions.addWidget(self.snooze_10_button)
        actions.addWidget(self.snooze_30_button)
        layout.addLayout(actions)

        self.apply_theme(False)

        self.animation = QPropertyAnimation(self, b"windowOpacity", self)
        self.animation.setDuration(260)
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)

    def apply_theme(self, dark_mode_enabled: bool) -> None:
        if dark_mode_enabled:
            stylesheet = """
            QWidget { background: rgba(24, 33, 49, 0.96); border: 1px solid rgba(82, 107, 146, 0.45); border-radius: 20px; }
            QLabel#badge { color: #8cb2ff; background: #243552; border-radius: 10px; padding: 6px 10px; font-weight: 600; max-width: 72px; }
            QLabel#title { color: #f8fbff; font-size: 20px; font-weight: 700; }
            QLabel#content { color: #b9c7de; font-size: 13px; line-height: 1.5; }
            QPushButton { min-height: 38px; border-radius: 12px; padding: 0 14px; font-weight: 600; }
            QPushButton#primaryButton { background: #5b8cff; color: white; border: none; }
            QPushButton#primaryButton:hover { background: #76a1ff; }
            QPushButton#secondaryButton { background: #22304a; color: #eef3fb; border: 1px solid #33415c; }
            """
        else:
            stylesheet = """
            QWidget { background: rgba(255, 255, 255, 0.97); border: 1px solid rgba(186, 201, 223, 0.7); border-radius: 20px; }
            QLabel#badge { color: #4f7cff; background: #edf3ff; border-radius: 10px; padding: 6px 10px; font-weight: 600; max-width: 72px; }
            QLabel#title { color: #172033; font-size: 20px; font-weight: 700; }
            QLabel#content { color: #5f6c85; font-size: 13px; line-height: 1.5; }
            QPushButton { min-height: 38px; border-radius: 12px; padding: 0 14px; font-weight: 600; }
            QPushButton#primaryButton { background: #4f7cff; color: white; border: none; }
            QPushButton#primaryButton:hover { background: #3f6ef5; }
            QPushButton#secondaryButton { background: #eef3fb; color: #22304a; border: 1px solid #d6dfeb; }
            """
        self.setStyleSheet(stylesheet)

    def show_event(self, title: str, content: str) -> None:
        self.title_label.setText(title)
        self.content_label.setText(content)
        self.setWindowOpacity(0.0)
        self.show()
        self.raise_()
        self.activateWindow()
        self.animation.start()
