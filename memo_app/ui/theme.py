from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ThemePalette:
    root_background: str
    card_background: str
    raised_background: str
    input_background: str
    input_focus_background: str
    panel_background: str
    border: str
    border_strong: str
    shadow_border: str
    text_primary: str
    text_secondary: str
    text_muted: str
    accent: str
    accent_hover: str
    accent_soft: str
    accent_text: str
    danger_background: str
    danger_hover: str
    danger_border: str
    danger_text: str
    success_soft: str
    success_text: str
    warning_soft: str
    warning_text: str
    dismissed_soft: str
    dismissed_text: str
    one_time: str
    weekly: str
    workday: str
    popup_background: str
    popup_border: str


DARK_PALETTE = ThemePalette(
    root_background="#171821",
    card_background="#282a36",
    raised_background="#34384a",
    input_background="#21222c",
    input_focus_background="#262938",
    panel_background="#232530",
    border="#3a3d4d",
    border_strong="#4c5168",
    shadow_border="#20222c",
    text_primary="#f8f8f2",
    text_secondary="#d8dbe8",
    text_muted="#a8afc4",
    accent="#bd93f9",
    accent_hover="#caa9fa",
    accent_soft="#3b3250",
    accent_text="#ece2ff",
    danger_background="#3c2530",
    danger_hover="#4a2d39",
    danger_border="#6e4154",
    danger_text="#ffb6c1",
    success_soft="#233f35",
    success_text="#95f5c7",
    warning_soft="#3b3250",
    warning_text="#ece2ff",
    dismissed_soft="#46303a",
    dismissed_text="#ffcad4",
    one_time="#ff79c6",
    weekly="#8be9fd",
    workday="#50fa7b",
    popup_background="rgba(40, 42, 54, 0.98)",
    popup_border="rgba(128, 134, 166, 0.45)",
)


LIGHT_PALETTE = ThemePalette(
    root_background="#edf1fb",
    card_background="#ffffff",
    raised_background="#f7f8fd",
    input_background="#f5f7ff",
    input_focus_background="#ffffff",
    panel_background="#f3f5fb",
    border="#dbe0ef",
    border_strong="#c5cee6",
    shadow_border="#e4e8f3",
    text_primary="#1d2333",
    text_secondary="#49526b",
    text_muted="#79829b",
    accent="#7c4dff",
    accent_hover="#6d3df4",
    accent_soft="#f1e9ff",
    accent_text="#5c35d6",
    danger_background="#fff1f5",
    danger_hover="#ffe3ec",
    danger_border="#f5bfd0",
    danger_text="#c93b6a",
    success_soft="#ddfbeb",
    success_text="#127548",
    warning_soft="#f1e9ff",
    warning_text="#5c35d6",
    dismissed_soft="#ffe3e8",
    dismissed_text="#bb4760",
    one_time="#e056b5",
    weekly="#2ca9bc",
    workday="#2ca66a",
    popup_background="rgba(255, 255, 255, 0.98)",
    popup_border="rgba(197, 206, 230, 0.92)",
)


def get_palette(dark_mode_enabled: bool) -> ThemePalette:
    return DARK_PALETTE if dark_mode_enabled else LIGHT_PALETTE


def build_app_stylesheet(dark_mode_enabled: bool) -> str:
    palette = get_palette(dark_mode_enabled)
    return f"""
    QWidget#root {{
        background: {palette.root_background};
    }}
    QFrame#headerCard, QFrame#panelCard, QFrame#groupCard {{
        background: {palette.card_background};
        border: 1px solid {palette.border};
        border-radius: 20px;
    }}
    QFrame#panelCard {{
        background: {palette.panel_background};
    }}
    QFrame#groupCard {{
        background: {palette.card_background};
        border-radius: 16px;
    }}
    QFrame#headerCard {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 {palette.card_background}, stop:0.55 {palette.raised_background}, stop:1 {palette.card_background});
    }}
    QSplitter::handle {{
        background: transparent;
        width: 12px;
    }}
    QLabel#pageTitle {{
        color: {palette.text_primary};
        font-size: 32px;
        font-weight: 700;
    }}
    QLabel#pageSubtitle, QLabel#sectionHint {{
        color: {palette.text_muted};
        font-size: 13px;
    }}
    QLabel#sectionTitle {{
        color: {palette.text_primary};
        font-size: 18px;
        font-weight: 700;
    }}
    QLabel#groupTitle {{
        color: {palette.text_secondary};
        font-size: 15px;
        font-weight: 700;
    }}
    QLabel#groupHint {{
        color: {palette.text_muted};
        font-size: 12px;
        background: transparent;
    }}
    QLabel#timeModeHint {{
        color: {palette.accent};
        font-size: 13px;
        font-weight: 700;
        background: transparent;
    }}
    QFrame#timeOptionRow {{
        background: {palette.raised_background};
        border: 1px solid {palette.border};
        border-radius: 12px;
    }}
    QFrame#timeOptionRow[mode="datetime"] {{
        background: {palette.card_background};
        border: 1px solid {palette.border_strong};
    }}
    QFrame#timeOptionRow[active="true"] {{
        border: 1px solid {palette.accent};
        background: {palette.card_background};
    }}
    QLabel#timeOptionLabel {{
        color: {palette.text_primary};
        font-size: 13px;
        font-weight: 700;
        background: transparent;
    }}
    QLabel#timeOptionHint {{
        color: {palette.text_muted};
        font-size: 12px;
        background: transparent;
    }}
    QLabel#cardRuleLabel {{
        color: {palette.text_muted};
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.5px;
        background: transparent;
    }}
    QListWidget#eventList {{
        background: {palette.raised_background};
        border: 1px solid {palette.border};
        border-radius: 16px;
        padding: 12px;
        outline: none;
    }}
    QListWidget#eventList::item {{
        border: none;
        background: transparent;
        padding: 0;
        margin: 6px 0;
    }}
    QListWidget#eventList::item:selected {{
        border: none;
        background: transparent;
    }}
    QLineEdit, QComboBox, QDateTimeEdit, QPlainTextEdit {{
        background: {palette.input_background};
        border: 1px solid {palette.border};
        border-radius: 12px;
        padding: 8px 10px;
        color: {palette.text_primary};
        font-size: 13px;
        selection-background-color: {palette.accent};
    }}
    QLineEdit:focus, QComboBox:focus, QDateTimeEdit:focus, QPlainTextEdit:focus {{
        background: {palette.input_focus_background};
        border: 1px solid {palette.accent};
    }}
    QComboBox::drop-down {{
        border: none;
        width: 26px;
    }}
    QPushButton {{
        min-height: 38px;
        border-radius: 12px;
        padding: 0 14px;
        font-size: 13px;
        font-weight: 700;
        border: 1px solid transparent;
    }}
    QPushButton#primaryButton {{
        background: {palette.accent};
        color: #ffffff;
    }}
    QPushButton#primaryButton:hover {{
        background: {palette.accent_hover};
    }}
    QPushButton#primaryButton:pressed {{
        background: {palette.accent_hover};
    }}
    QPushButton#secondaryButton {{
        background: {palette.raised_background};
        color: {palette.text_secondary};
        border: 1px solid {palette.border};
    }}
    QPushButton#secondaryButton:hover {{
        border-color: {palette.border_strong};
    }}
    QPushButton#dangerButton {{
        background: {palette.danger_background};
        color: {palette.danger_text};
        border: 1px solid {palette.danger_border};
    }}
    QPushButton#dangerButton:hover {{
        background: {palette.danger_hover};
    }}
    QCheckBox {{
        color: {palette.text_secondary};
        font-size: 13px;
        spacing: 8px;
    }}
    QLabel#cardTitle {{
        color: {palette.text_primary};
        font-size: 16px;
        font-weight: 700;
        background: transparent;
    }}
    QLabel#cardSchedule {{
        color: {palette.text_muted};
        font-size: 13px;
        background: transparent;
    }}
    QLabel#cardPreview {{
        color: {palette.text_secondary};
        font-size: 13px;
        background: transparent;
    }}
    QFrame#eventCard {{
        background: {palette.card_background};
        border: 1px solid {palette.border};
        border-radius: 16px;
    }}
    QFrame#eventCardBody {{
        background: transparent;
        border: none;
    }}
    QFrame#eventCard[selected="true"] {{
        border: 1px solid {palette.accent};
        background: {palette.raised_background};
    }}
    QLabel#cardSelectionRail {{
        background: {palette.border};
        border-radius: 3px;
        min-width: 6px;
        max-width: 6px;
    }}
    QFrame#eventCard[selected="true"] QLabel#cardSelectionRail {{
        background: {palette.accent};
    }}
    QLabel[typeDot="one_time"] {{
        color: {palette.one_time};
        font-size: 16px;
        font-weight: 700;
        min-width: 16px;
        max-width: 16px;
        background: transparent;
    }}
    QLabel[typeDot="weekly"] {{
        color: {palette.weekly};
        font-size: 16px;
        font-weight: 700;
        min-width: 16px;
        max-width: 16px;
        background: transparent;
    }}
    QLabel[typeDot="workday"] {{
        color: {palette.workday};
        font-size: 16px;
        font-weight: 700;
        min-width: 16px;
        max-width: 16px;
        background: transparent;
    }}
    QWidget#reminderWindow {{
        background: {palette.popup_background};
        border: 1px solid {palette.popup_border};
        border-radius: 24px;
    }}
    QWidget#reminderWindow QPushButton#primaryButton {{
        min-width: 108px;
    }}
    QPushButton#reminderCloseButton {{
        min-width: 28px;
        max-width: 28px;
        min-height: 28px;
        max-height: 28px;
        padding: 0;
        border-radius: 14px;
        background: transparent;
        color: {palette.text_muted};
        border: 1px solid {palette.border};
        font-size: 15px;
        font-weight: 700;
    }}
    QPushButton#reminderCloseButton:hover {{
        background: {palette.raised_background};
        color: {palette.text_primary};
        border-color: {palette.border_strong};
    }}
    QLabel#badge {{
        color: {palette.accent_text};
        background: {palette.accent_soft};
        border-radius: 10px;
        padding: 6px 10px;
        font-weight: 700;
        max-width: 72px;
    }}
    QFrame#reminderContentCard, QFrame#reminderActions {{
        background: {palette.card_background};
        border: 1px solid {palette.border};
        border-radius: 16px;
    }}
    QLabel#title {{
        color: {palette.text_primary};
        font-size: 22px;
        font-weight: 700;
        background: transparent;
    }}
    QLabel#content {{
        color: {palette.text_secondary};
        font-size: 13px;
        line-height: 1.5;
        background: transparent;
    }}
    QFrame#clockTimeInput {{
        background: {palette.input_background};
        border: 1px solid {palette.border};
        border-radius: 12px;
        min-height: 38px;
    }}
    QLabel#clockTimeLabel {{
        color: {palette.text_primary};
        font-size: 14px;
        font-weight: 600;
        background: transparent;
        padding: 0 4px;
    }}
    QFrame#clockFooter {{
        background: {palette.card_background};
        border-top: 1px solid {palette.border};
        border-bottom-left-radius: 14px;
        border-bottom-right-radius: 14px;
    }}
    QLabel#clockOkButton {{
        background: {palette.accent};
        color: #ffffff;
        border-radius: 8px;
        padding: 6px 18px;
        font-size: 12px;
        font-weight: 700;
    }}
    QLabel#clockOkButton:hover {{
        background: {palette.accent_hover};
    }}
    QFrame#clockTimePopup {{
        background: {palette.card_background};
        border: 1px solid {palette.border};
        border-radius: 16px;
    }}
    """
