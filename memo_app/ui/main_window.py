from __future__ import annotations

from datetime import datetime, timedelta

from PyQt6.QtCore import QTimer, QSize, Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QStyle
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateTimeEdit,
    QFrame,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QSplitter,
    QSystemTrayIcon,
    QVBoxLayout,
    QWidget,
)

from memo_app.data.repository import MemoRepository
from memo_app.models import MemoEvent, now_iso
from memo_app.services.holiday_service import HolidayService
from memo_app.services.scheduler import Scheduler
from memo_app.system.startup import is_startup_enabled, set_startup_enabled
from memo_app.ui.event_card_widget import EventCardWidget
from memo_app.ui.reminder_window import ReminderWindow


RULE_TYPE_MAP = {
    "一次性提醒": "one_time",
    "每周提醒": "weekly",
    "工作日提醒": "workday",
}

RULE_TYPE_LABELS = {
    "one_time": "◉ 一次性",
    "weekly": "◆ 每周",
    "workday": "● 工作日",
}

STATUS_LABELS = {
    "pending": "◌ 待提醒",
    "done": "✓ 已完成",
    "dismissed": "— 已关闭",
}


class MainWindow(QMainWindow):
    def __init__(self, repository: MemoRepository) -> None:
        super().__init__()
        self.repository = repository
        self.holiday_service = HolidayService(repository)
        self.scheduler = Scheduler(self.holiday_service)
        self.current_event_id: int | None = None
        self.active_event_id: int | None = None
        self.dark_mode_enabled = False
        self.reminder_window = ReminderWindow()
        self.poll_timer = QTimer(self)
        self.tray_icon = QSystemTrayIcon(self)
        self.setWindowTitle("Win Memo Tool")
        self.resize(1000, 640)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        self._build_ui()
        self._wire_signals()
        self.refresh_events()

    def _build_ui(self) -> None:
        root = QWidget(self)
        root.setObjectName("root")
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(20, 20, 20, 20)
        root_layout.setSpacing(16)

        header_card = QFrame()
        header_card.setObjectName("headerCard")
        header_layout = QHBoxLayout(header_card)
        header_layout.setContentsMargins(18, 16, 18, 16)
        header_layout.setSpacing(12)

        title_wrap = QVBoxLayout()
        title_wrap.setSpacing(4)
        title = QLabel("桌面备忘录")
        title.setObjectName("pageTitle")
        subtitle = QLabel("轻量记录、定时提醒、悬浮常驻")
        subtitle.setObjectName("pageSubtitle")
        title_wrap.addWidget(title)
        title_wrap.addWidget(subtitle)

        self.theme_checkbox = QCheckBox("暗色模式")
        self.hide_button = QPushButton("隐藏窗口")
        self.hide_button.setObjectName("secondaryButton")
        self.hide_button.clicked.connect(self.hide)
        header_layout.addLayout(title_wrap)
        header_layout.addStretch(1)
        header_layout.addWidget(self.theme_checkbox)
        header_layout.addWidget(self.hide_button)
        root_layout.addWidget(header_card)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setObjectName("mainSplitter")

        list_panel = QFrame(splitter)
        list_panel.setObjectName("panelCard")
        list_layout = QVBoxLayout(list_panel)
        list_layout.setContentsMargins(16, 16, 16, 16)
        list_layout.setSpacing(10)
        list_title = QLabel("事件列表")
        list_title.setObjectName("sectionTitle")
        list_hint = QLabel("按下一次提醒时间排序")
        list_hint.setObjectName("sectionHint")
        list_layout.addWidget(list_title)
        list_layout.addWidget(list_hint)
        self.event_list = QListWidget()
        self.event_list.setObjectName("eventList")
        list_layout.addWidget(self.event_list)
        self.list_summary = QLabel("共 0 个事件")
        self.list_summary.setObjectName("sectionHint")
        list_layout.addWidget(self.list_summary)

        form_panel = QFrame(splitter)
        form_panel.setObjectName("panelCard")
        form_layout = QVBoxLayout(form_panel)
        form_layout.setContentsMargins(16, 16, 16, 16)
        form_layout.setSpacing(10)
        form_title = QLabel("事件编辑")
        form_title.setObjectName("sectionTitle")
        form_hint = QLabel("创建一次性、每周或工作日提醒")
        form_hint.setObjectName("sectionHint")
        form_layout.addWidget(form_title)
        form_layout.addWidget(form_hint)

        basic_group = QFrame()
        basic_group.setObjectName("groupCard")
        basic_layout = QVBoxLayout(basic_group)
        basic_layout.setContentsMargins(14, 14, 14, 14)
        basic_layout.setSpacing(10)
        basic_title = QLabel("基本信息")
        basic_title.setObjectName("groupTitle")
        basic_layout.addWidget(basic_title)
        basic_form = QFormLayout()
        self.title_input = QLineEdit()
        self.rule_type_input = QComboBox()
        self.rule_type_input.addItems(["一次性提醒", "每周提醒", "工作日提醒"])
        basic_form.addRow("标题", self.title_input)
        basic_form.addRow("提醒类型", self.rule_type_input)
        basic_layout.addLayout(basic_form)
        form_layout.addWidget(basic_group)

        time_group = QFrame()
        time_group.setObjectName("groupCard")
        time_layout = QVBoxLayout(time_group)
        time_layout.setContentsMargins(14, 14, 14, 14)
        time_layout.setSpacing(10)
        time_title = QLabel("时间设置")
        time_title.setObjectName("groupTitle")
        time_layout.addWidget(time_title)
        time_form = QFormLayout()
        self.datetime_input = QDateTimeEdit()
        self.datetime_input.setCalendarPopup(True)
        self.datetime_input.setDateTime(datetime.now().replace(microsecond=0))
        self.datetime_input.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.time_input = QDateTimeEdit()
        self.time_input.setDateTime(datetime.now().replace(microsecond=0))
        self.time_input.setDisplayFormat("HH:mm:ss")
        self.weekday_input = QComboBox()
        self.weekday_input.addItems(["周一", "周二", "周三", "周四", "周五", "周六", "周日"])
        time_form.addRow("一次性日期时间", self.datetime_input)
        time_form.addRow("每周时间", self.time_input)
        time_form.addRow("每周星期", self.weekday_input)
        time_layout.addLayout(time_form)
        form_layout.addWidget(time_group)

        content_group = QFrame()
        content_group.setObjectName("groupCard")
        content_layout = QVBoxLayout(content_group)
        content_layout.setContentsMargins(14, 14, 14, 14)
        content_layout.setSpacing(10)
        content_title = QLabel("内容")
        content_title.setObjectName("groupTitle")
        self.notes_input = QPlainTextEdit()
        self.notes_input.setPlaceholderText("输入事件内容")
        content_layout.addWidget(content_title)
        content_layout.addWidget(self.notes_input)
        form_layout.addWidget(content_group)

        actions = QHBoxLayout()
        actions.setSpacing(10)
        self.save_button = QPushButton("保存事件")
        self.save_button.setObjectName("primaryButton")
        self.clear_button = QPushButton("清空表单")
        self.clear_button.setObjectName("secondaryButton")
        self.delete_button = QPushButton("删除事件")
        self.delete_button.setObjectName("dangerButton")
        actions.addWidget(self.save_button, 1)
        actions.addWidget(self.clear_button, 1)
        actions.addWidget(self.delete_button, 0)
        form_layout.addLayout(actions)

        self.startup_checkbox = QCheckBox("开机自动启动")
        self.startup_checkbox.setChecked(is_startup_enabled())
        form_layout.addWidget(self.startup_checkbox)
        form_layout.addStretch(1)

        splitter.addWidget(list_panel)
        splitter.addWidget(form_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        root_layout.addWidget(splitter)

        self.setCentralWidget(root)
        self._apply_styles()

    def _wire_signals(self) -> None:
        self.save_button.clicked.connect(self.save_event)
        self.clear_button.clicked.connect(self.clear_form)
        self.delete_button.clicked.connect(self.delete_selected_event)
        self.event_list.itemSelectionChanged.connect(self.load_selected_event)
        self.rule_type_input.currentIndexChanged.connect(self._update_rule_inputs)
        self.theme_checkbox.toggled.connect(self.toggle_theme)
        self.startup_checkbox.toggled.connect(self.toggle_startup)
        self.reminder_window.dismiss_button.clicked.connect(self.dismiss_active_reminder)
        self.reminder_window.snooze_5_button.clicked.connect(lambda: self.snooze_active_reminder(5))
        self.reminder_window.snooze_10_button.clicked.connect(lambda: self.snooze_active_reminder(10))
        self.reminder_window.snooze_30_button.clicked.connect(lambda: self.snooze_active_reminder(30))
        self.poll_timer.setInterval(30000)
        self.poll_timer.timeout.connect(self.check_due_events)
        self.poll_timer.start()
        self._setup_tray_icon()
        self._update_rule_inputs()

    def _apply_styles(self) -> None:
        if self.dark_mode_enabled:
            stylesheet = """
            QWidget#root { background: #1f1f1f; }
            QFrame#headerCard, QFrame#panelCard, QFrame#groupCard { background: #2b2b2b; border: 1px solid #3c3c3c; border-radius: 12px; }
            QLabel#pageTitle { color: #ffffff; font-size: 24px; font-weight: 700; }
            QLabel#pageSubtitle, QLabel#sectionHint { color: #b8b8b8; font-size: 12px; }
            QLabel#sectionTitle { color: #ffffff; font-size: 16px; font-weight: 600; }
            QLabel#groupTitle { color: #d9d9d9; font-size: 13px; font-weight: 600; }
            QListWidget#eventList { background: #252525; border: 1px solid #3c3c3c; border-radius: 10px; padding: 8px; outline: none; }
            QListWidget#eventList::item { border: none; background: transparent; padding: 0; margin: 4px 0; }
            QListWidget#eventList::item:selected { border: none; background: transparent; }
            QLineEdit, QComboBox, QDateTimeEdit, QPlainTextEdit { background: #202020; border: 1px solid #4a4a4a; border-radius: 8px; padding: 8px 10px; color: #f2f2f2; selection-background-color: #2d5ea8; }
            QLineEdit:focus, QComboBox:focus, QDateTimeEdit:focus, QPlainTextEdit:focus { border: 1px solid #4c8dff; background: #262626; }
            QComboBox::drop-down { border: none; width: 24px; }
            QPushButton { min-height: 36px; border-radius: 8px; padding: 0 14px; font-weight: 600; }
            QPushButton#primaryButton { background: #2563eb; color: white; border: none; }
            QPushButton#primaryButton:hover { background: #3b77f0; }
            QPushButton#secondaryButton { background: #2f2f2f; color: #f2f2f2; border: 1px solid #4a4a4a; }
            QPushButton#secondaryButton:hover { background: #383838; }
            QPushButton#dangerButton { background: #3b2323; color: #ffb8b8; border: 1px solid #7a4343; }
            QPushButton#dangerButton:hover { background: #4a2a2a; }
            QCheckBox { color: #d8d8d8; spacing: 8px; }
            """
        else:
            stylesheet = """
            QWidget#root { background: #f5f6f8; }
            QFrame#headerCard, QFrame#panelCard, QFrame#groupCard { background: #ffffff; border: 1px solid #e2e5ea; border-radius: 12px; }
            QLabel#pageTitle { color: #111111; font-size: 24px; font-weight: 700; }
            QLabel#pageSubtitle, QLabel#sectionHint { color: #6b7280; font-size: 12px; }
            QLabel#sectionTitle { color: #111827; font-size: 16px; font-weight: 600; }
            QLabel#groupTitle { color: #374151; font-size: 13px; font-weight: 600; }
            QListWidget#eventList { background: #fbfbfc; border: 1px solid #e5e7eb; border-radius: 10px; padding: 8px; outline: none; }
            QListWidget#eventList::item { border: none; background: transparent; padding: 0; margin: 4px 0; }
            QListWidget#eventList::item:selected { border: none; background: transparent; }
            QLineEdit, QComboBox, QDateTimeEdit, QPlainTextEdit { background: #ffffff; border: 1px solid #d1d5db; border-radius: 8px; padding: 8px 10px; color: #111827; selection-background-color: #dbeafe; }
            QLineEdit:focus, QComboBox:focus, QDateTimeEdit:focus, QPlainTextEdit:focus { border: 1px solid #3b82f6; background: #ffffff; }
            QComboBox::drop-down { border: none; width: 24px; }
            QPushButton { min-height: 36px; border-radius: 8px; padding: 0 14px; font-weight: 600; }
            QPushButton#primaryButton { background: #2563eb; color: white; border: none; }
            QPushButton#primaryButton:hover { background: #1d4ed8; }
            QPushButton#secondaryButton { background: #ffffff; color: #111827; border: 1px solid #d1d5db; }
            QPushButton#secondaryButton:hover { background: #f9fafb; }
            QPushButton#dangerButton { background: #fff5f5; color: #dc2626; border: 1px solid #fecaca; }
            QPushButton#dangerButton:hover { background: #fee2e2; }
            QCheckBox { color: #374151; spacing: 8px; }
            """
        self.setStyleSheet(stylesheet)
        self.reminder_window.apply_theme(self.dark_mode_enabled)

    def _setup_tray_icon(self) -> None:
        icon = self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogDetailedView)
        self.setWindowIcon(icon)
        self.tray_icon.setIcon(icon)

        menu = QMenu(self)
        show_action = QAction("显示窗口", self)
        hide_action = QAction("隐藏窗口", self)
        quit_action = QAction("退出", self)
        show_action.triggered.connect(self.show_normal)
        hide_action.triggered.connect(self.hide)
        quit_action.triggered.connect(self.close)
        menu.addAction(show_action)
        menu.addAction(hide_action)
        menu.addSeparator()
        menu.addAction(quit_action)
        self.tray_icon.setContextMenu(menu)
        self.tray_icon.setToolTip("Win Memo Tool")
        self.tray_icon.activated.connect(self._on_tray_activated)
        self.tray_icon.show()

    def _on_tray_activated(self, reason) -> None:
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.show_normal()

    def show_normal(self) -> None:
        self.show()
        self.raise_()
        self.activateWindow()

    def toggle_theme(self, checked: bool) -> None:
        self.dark_mode_enabled = checked
        self._apply_styles()

    def toggle_startup(self, checked: bool) -> None:
        set_startup_enabled(checked)

    def _update_rule_inputs(self) -> None:
        rule_type = RULE_TYPE_MAP[self.rule_type_input.currentText()]
        self.weekday_input.setEnabled(rule_type == "weekly")
        self.datetime_input.setEnabled(rule_type == "one_time")
        self.time_input.setEnabled(rule_type in {"weekly", "workday"})

    def refresh_events(self) -> None:
        self.event_list.clear()
        events = sorted(
            self.repository.list_events(),
            key=lambda event: (event.next_trigger_at is None, event.next_trigger_at or "9999-12-31 23:59:59", event.updated_at),
        )
        self.list_summary.setText(f"共 {len(events)} 个事件")
        for event in events:
            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, event.id)
            item.setSizeHint(QSize(0, 96))
            self.event_list.addItem(item)
            card = EventCardWidget(event, self.dark_mode_enabled)
            self.event_list.setItemWidget(item, card)

    def save_event(self) -> None:
        title = self.title_input.text().strip()
        if not title:
            QMessageBox.warning(self, "缺少标题", "请输入事件标题。")
            return

        rule_type = RULE_TYPE_MAP[self.rule_type_input.currentText()]
        timestamp = now_iso()
        event = MemoEvent(
            id=self.current_event_id,
            title=title,
            content=self.notes_input.toPlainText().strip(),
            rule_type=rule_type,
            one_time_at=self.datetime_input.dateTime().toPyDateTime().replace(microsecond=0).isoformat(sep=" ") if rule_type == "one_time" else None,
            weekday=self.weekday_input.currentIndex() if rule_type == "weekly" else None,
            time_of_day=(self.time_input.time().toString("HH:mm:ss") if rule_type in {"weekly", "workday"} else self.datetime_input.time().toString("HH:mm:ss")),
            status="pending",
            snooze_until=None,
            next_trigger_at=None,
            last_triggered_at=None,
            created_at=timestamp,
            updated_at=timestamp,
        )

        if self.current_event_id is None:
            event.next_trigger_at = self.scheduler.compute_next_trigger(event)
            self.repository.create_event(event)
        else:
            existing = self.repository.list_events()
            for saved in existing:
                if saved.id == self.current_event_id:
                    event.created_at = saved.created_at
                    event.last_triggered_at = saved.last_triggered_at
                    event.snooze_until = saved.snooze_until
                    event.status = saved.status
                    break
            event.next_trigger_at = self.scheduler.compute_next_trigger(event)
            self.repository.update_event(event)

        self.refresh_events()
        self.clear_form()

    def load_selected_event(self) -> None:
        item = self.event_list.currentItem()
        if item is None:
            return
        event_id = item.data(Qt.ItemDataRole.UserRole)
        for event in self.repository.list_events():
            if event.id != event_id:
                continue
            self.current_event_id = event.id
            self.title_input.setText(event.title)
            self.notes_input.setPlainText(event.content)
            display_rule = next(label for label, value in RULE_TYPE_MAP.items() if value == event.rule_type)
            self.rule_type_input.setCurrentText(display_rule)
            if event.one_time_at:
                self.datetime_input.setDateTime(self.datetime_input.dateTime().fromString(event.one_time_at, "yyyy-MM-dd HH:mm:ss"))
            if event.weekday is not None:
                self.weekday_input.setCurrentIndex(event.weekday)
            if event.time_of_day:
                self.time_input.setTime(self.time_input.time().fromString(event.time_of_day, "HH:mm:ss"))
            break

    def delete_selected_event(self) -> None:
        item = self.event_list.currentItem()
        if item is None:
            return
        event_id = item.data(Qt.ItemDataRole.UserRole)
        self.repository.delete_event(event_id)
        self.refresh_events()
        self.clear_form()

    def clear_form(self) -> None:
        self.current_event_id = None
        self.event_list.clearSelection()
        self.title_input.clear()
        self.notes_input.clear()
        self.rule_type_input.setCurrentIndex(0)
        self.weekday_input.setCurrentIndex(0)

    def check_due_events(self) -> None:
        now = datetime.now().replace(microsecond=0)
        for event in self.repository.list_events():
            if not event.next_trigger_at:
                continue
            if datetime.fromisoformat(event.next_trigger_at) > now:
                continue
            self.active_event_id = event.id
            self.reminder_window.show_event(event.title, event.content or event.title)
            break

    def dismiss_active_reminder(self) -> None:
        if self.active_event_id is None:
            return
        for event in self.repository.list_events():
            if event.id != self.active_event_id:
                continue
            event.last_triggered_at = now_iso()
            event.snooze_until = None
            event.status = "done" if event.rule_type == "one_time" else "pending"
            event.next_trigger_at = self.scheduler.compute_next_trigger(event, datetime.now().replace(microsecond=0) + timedelta(seconds=1))
            self.repository.update_event(event)
            break
        self.active_event_id = None
        self.reminder_window.hide()
        self.refresh_events()

    def snooze_active_reminder(self, minutes: int) -> None:
        if self.active_event_id is None:
            return
        for event in self.repository.list_events():
            if event.id != self.active_event_id:
                continue
            snooze_at = datetime.now().replace(microsecond=0) + timedelta(minutes=minutes)
            event.snooze_until = snooze_at.isoformat(sep=" ")
            event.status = "pending"
            event.next_trigger_at = event.snooze_until
            self.repository.update_event(event)
            break
        self.active_event_id = None
        self.reminder_window.hide()
        self.refresh_events()
