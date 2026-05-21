from __future__ import annotations

from datetime import datetime, timedelta, time

from PyQt6.QtCore import QTimer, QSize, QTime, Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QApplication, QStyle
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
from memo_app.ui.clock_time_input import ClockTimeInput
from memo_app.ui.clock_picker import set_clock_dark_mode
from memo_app.ui.theme import build_app_stylesheet


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
        self.resize(1000, 600)
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
        header_layout.setContentsMargins(22, 18, 22, 18)
        header_layout.setSpacing(14)

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
        list_layout.setContentsMargins(18, 18, 18, 18)
        list_layout.setSpacing(12)
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
        form_layout.setContentsMargins(18, 18, 18, 18)
        form_layout.setSpacing(12)
        form_title = QLabel("事件编辑")
        form_title.setObjectName("sectionTitle")
        form_hint = QLabel("创建一次性、每周或工作日提醒")
        form_hint.setObjectName("sectionHint")
        form_layout.addWidget(form_title)
        form_layout.addWidget(form_hint)

        editor_group = QFrame()
        editor_group.setObjectName("groupCard")
        editor_layout = QVBoxLayout(editor_group)
        editor_layout.setContentsMargins(12, 12, 12, 12)
        editor_layout.setSpacing(10)

        basic_row = QHBoxLayout()
        basic_row.setSpacing(10)
        title_block = QVBoxLayout()
        title_block.setSpacing(4)
        basic_title = QLabel("标题")
        basic_title.setObjectName("groupTitle")
        self.title_input = QLineEdit()
        title_block.addWidget(basic_title)
        title_block.addWidget(self.title_input)

        type_block = QVBoxLayout()
        type_block.setSpacing(4)
        type_title = QLabel("提醒类型")
        type_title.setObjectName("groupTitle")
        self.rule_type_input = QComboBox()
        self.rule_type_input.addItems(["一次性提醒", "每周提醒", "工作日提醒"])
        type_block.addWidget(type_title)
        type_block.addWidget(self.rule_type_input)

        basic_row.addLayout(title_block, 3)
        basic_row.addLayout(type_block, 2)
        editor_layout.addLayout(basic_row)

        time_group = QFrame()
        time_group.setObjectName("groupCard")
        time_layout = QVBoxLayout(time_group)
        time_layout.setContentsMargins(12, 12, 12, 12)
        time_layout.setSpacing(8)
        time_title = QLabel("时间设置")
        time_title.setObjectName("groupTitle")
        self.time_mode_hint = QLabel()
        self.time_mode_hint.setObjectName("timeModeHint")
        self.date_input = QDateTimeEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDateTime(datetime.now().replace(microsecond=0))
        self.date_input.setDisplayFormat("yyyy-MM-dd")
        self.date_input.setCurrentSection(QDateTimeEdit.Section.DaySection)

        self.datetime_input = ClockTimeInput()
        self.time_input = ClockTimeInput()
        self.weekday_input = QComboBox()
        self.weekday_input.addItems(["周一", "周二", "周三", "周四", "周五", "周六", "周日"])

        self.datetime_row = QFrame()
        self.datetime_row.setObjectName("timeOptionRow")
        self.datetime_row.setProperty("mode", "datetime")
        datetime_row_layout = QVBoxLayout(self.datetime_row)
        datetime_row_layout.setContentsMargins(10, 8, 10, 8)
        datetime_row_layout.setSpacing(6)
        self.datetime_label = QLabel("日期和时间")
        self.datetime_label.setObjectName("timeOptionLabel")
        self.datetime_note = QLabel("先选日期，再单独调整时、分、秒。")
        self.datetime_note.setObjectName("timeOptionHint")
        datetime_fields_row = QHBoxLayout()
        datetime_fields_row.setSpacing(8)
        datetime_fields_row.addWidget(self.date_input, 1)
        datetime_fields_row.addWidget(self.datetime_input, 1)
        datetime_row_layout.addWidget(self.datetime_label)
        datetime_row_layout.addLayout(datetime_fields_row)
        datetime_row_layout.addWidget(self.datetime_note)

        self.time_row = QFrame()
        self.time_row.setObjectName("timeOptionRow")
        time_row_layout = QHBoxLayout(self.time_row)
        time_row_layout.setContentsMargins(10, 8, 10, 8)
        time_row_layout.setSpacing(8)
        self.time_label = QLabel("提醒时间")
        self.time_label.setObjectName("timeOptionLabel")
        time_row_layout.addWidget(self.time_label)
        time_row_layout.addWidget(self.time_input, 1)

        self.weekday_row = QFrame()
        self.weekday_row.setObjectName("timeOptionRow")
        weekday_row_layout = QHBoxLayout(self.weekday_row)
        weekday_row_layout.setContentsMargins(10, 8, 10, 8)
        weekday_row_layout.setSpacing(8)
        self.weekday_label = QLabel("星期")
        self.weekday_label.setObjectName("timeOptionLabel")
        weekday_row_layout.addWidget(self.weekday_label)
        weekday_row_layout.addWidget(self.weekday_input, 1)

        weekly_compact_row = QHBoxLayout()
        weekly_compact_row.setSpacing(8)
        weekly_compact_row.addWidget(self.weekday_row, 1)
        weekly_compact_row.addWidget(self.time_row, 1)

        time_layout.addWidget(time_title)
        time_layout.addWidget(self.time_mode_hint)
        time_layout.addWidget(self.datetime_row)
        time_layout.addLayout(weekly_compact_row)
        editor_layout.addWidget(time_group)

        content_group = QFrame()
        content_group.setObjectName("groupCard")
        content_layout = QVBoxLayout(content_group)
        content_layout.setContentsMargins(12, 12, 12, 12)
        content_layout.setSpacing(8)
        content_title = QLabel("内容")
        content_title.setObjectName("groupTitle")
        self.notes_input = QPlainTextEdit()
        self.notes_input.setPlaceholderText("输入事件内容")
        self.notes_input.setMinimumHeight(84)
        content_layout.addWidget(content_title)
        content_layout.addWidget(self.notes_input)

        footer_row = QHBoxLayout()
        footer_row.setSpacing(10)
        self.startup_checkbox = QCheckBox("开机自动启动")
        self.startup_checkbox.setChecked(is_startup_enabled())
        footer_row.addWidget(self.startup_checkbox)
        footer_row.addStretch(1)

        self.save_button = QPushButton("保存事件")
        self.save_button.setObjectName("primaryButton")
        self.clear_button = QPushButton("清空表单")
        self.clear_button.setObjectName("secondaryButton")
        self.delete_button = QPushButton("删除事件")
        self.delete_button.setObjectName("dangerButton")
        footer_row.addWidget(self.save_button)
        footer_row.addWidget(self.clear_button)
        footer_row.addWidget(self.delete_button)

        content_layout.addLayout(footer_row)
        editor_layout.addWidget(content_group)
        form_layout.addWidget(editor_group)
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
        self.event_list.itemSelectionChanged.connect(self._handle_event_selection_changed)
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
        self.setStyleSheet(build_app_stylesheet(self.dark_mode_enabled))
        self.reminder_window.apply_theme(self.dark_mode_enabled)
        self.refresh_events()

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
        quit_action.triggered.connect(self.quit_application)
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
        set_clock_dark_mode(checked)
        self._apply_styles()

    def quit_application(self) -> None:
        self.tray_icon.hide()
        self.reminder_window.close()
        QApplication.instance().quit()

    def toggle_startup(self, checked: bool) -> None:
        set_startup_enabled(checked)

    def _update_rule_inputs(self) -> None:
        rule_type = RULE_TYPE_MAP[self.rule_type_input.currentText()]
        is_one_time = rule_type == "one_time"
        is_weekly = rule_type == "weekly"
        is_workday = rule_type == "workday"

        self.date_input.setEnabled(is_one_time)
        self.datetime_input.setEnabled(is_one_time)
        self.time_input.setEnabled(is_weekly or is_workday)
        self.weekday_input.setEnabled(is_weekly)

        self.datetime_row.setVisible(is_one_time)
        self.time_row.setVisible(is_weekly or is_workday)
        self.weekday_row.setVisible(is_weekly)

        self.datetime_row.setProperty("active", is_one_time)
        self.time_row.setProperty("active", is_weekly or is_workday)
        self.weekday_row.setProperty("active", is_weekly)

        if is_one_time:
            self.time_mode_hint.setText("当前填写日期时间即可。")
        elif is_weekly:
            self.time_mode_hint.setText("当前填写星期和提醒时间。")
        else:
            self.time_mode_hint.setText("当前只填写提醒时间，默认按工作日循环。")

        for row in (self.datetime_row, self.time_row, self.weekday_row):
            self.style().unpolish(row)
            self.style().polish(row)
            row.update()

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
            item.setSizeHint(QSize(0, 128))
            self.event_list.addItem(item)
            card = EventCardWidget(event)
            self.event_list.setItemWidget(item, card)
        self._update_card_selection_states()

    def save_event(self) -> None:
        title = self.title_input.text().strip()
        if not title:
            QMessageBox.warning(self, "缺少标题", "请输入事件标题。")
            return

        rule_type = RULE_TYPE_MAP[self.rule_type_input.currentText()]
        one_time_value = None
        if rule_type == "one_time":
            dt_time = self.datetime_input.time().toPyTime()
            one_time_value = datetime.combine(
                self.date_input.date().toPyDate(),
                dt_time,
            )
            if one_time_value <= datetime.now().replace(microsecond=0):
                QMessageBox.warning(self, "提醒时间无效", "一次性提醒时间必须晚于当前时间。")
                return

        timestamp = now_iso()
        event = MemoEvent(
            id=self.current_event_id,
            title=title,
            content=self.notes_input.toPlainText().strip(),
            rule_type=rule_type,
            one_time_at=(one_time_value.isoformat(sep=" ") if one_time_value is not None else None),
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

    def _handle_event_selection_changed(self) -> None:
        self._update_card_selection_states()
        self.load_selected_event()

    def _update_card_selection_states(self) -> None:
        current_item = self.event_list.currentItem()
        for index in range(self.event_list.count()):
            item = self.event_list.item(index)
            card = self.event_list.itemWidget(item)
            if card is None:
                continue
            card.set_selected(item is current_item)

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
                one_time_value = datetime.fromisoformat(event.one_time_at)
                self.date_input.setDateTime(self.date_input.dateTime().fromString(one_time_value.strftime("%Y-%m-%d"), "yyyy-MM-dd"))
                self.datetime_input.setTime(QTime(one_time_value.hour, one_time_value.minute, one_time_value.second))
            if event.weekday is not None:
                self.weekday_input.setCurrentIndex(event.weekday)
            if event.time_of_day:
                h, m, s = map(int, event.time_of_day.split(":"))
                self.time_input.setTime(QTime(h, m, s))
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
            if event.rule_type == "one_time":
                self.repository.delete_event(event.id)
                break
            event.last_triggered_at = now_iso()
            event.snooze_until = None
            event.status = "pending"
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
