# Desktop Tool Dev Skill — PyQt6 桌面工具开发指南

基于「松鼠备忘录」项目的完整开发过程总结，覆盖从零搭建到打包分发全链路。
适用于任何 Python + PyQt6 + SQLite3 + PyInstaller 技术栈的 Windows 桌面小工具开发。

---

## 1. 项目结构

采用**分层 + 模块化**目录布局，避免将所有逻辑堆在单文件里：

```
project/
├── app.py                    # 入口：最小化引导
├── requirements.txt          # PyQt6, requests, PyInstaller
├── memo_app.spec             # PyInstaller 打包配置
├── assets/                   # 静态资源：logo.png 等
├── scripts/build.ps1         # 一键打包脚本
├── README.md / USAGE.md      # 使用与构建说明
└── memo_app/
    ├── __init__.py
    ├── main.py               # 应用启动、初始化数据库、创建主窗口
    ├── config.py             # 路径管理、常量、默认配置
    ├── models.py             # 纯数据 dataclass（不含任何 Qt 依赖）
    ├── data/
    │   ├── database.py       # 数据库连接与建表
    │   └── repository.py     # CRUD 仓储层
    ├── services/
    │   ├── scheduler.py      # 纯业务逻辑：调度计算
    │   └── holiday_service.py # 外部数据：联网 + 缓存
    ├── system/
    │   └── startup.py        # 平台特定：Windows 开机自启
    └── ui/
        ├── theme.py          # 主题系统：调色板 + 全局样式表
        ├── main_window.py    # 主窗口
        ├── reminder_window.py # 提醒弹窗
        ├── event_card_widget.py # 自定义列表卡片组件
        ├── clock_picker.py   # 自绘时钟选时器
        └── clock_time_input.py # 时间输入封装
```

### 关键原则
- **models.py 无 Qt 依赖**：纯 dataclass，可被所有层引用
- **data/ 只管存储**：database.py 负责连接，repository.py 负责查询
- **services/ 只管业务**：不引入任何 `PyQt6` import
- **ui/ 只管视图**：引用 models + data + services + system
- **app.py 极简**：只负责调 main()

---

## 2. 应用启动与生命周期

```python
# main.py
def main() -> int:
    # 1. 确保运行时目录和默认配置文件存在
    ensure_runtime_files()
    paths = get_app_paths()

    # 2. 初始化数据库
    database = Database(paths.database_path)
    database.initialize()
    repository = MemoRepository(database)

    # 3. 创建 QApplication
    app = QApplication(sys.argv)
    app.setApplicationName(DISPLAY_NAME)
    app.setQuitOnLastWindowClosed(False)  # 关闭窗口不退出，托盘常驻

    # 4. 创建主窗口（传入依赖）
    window = MainWindow(repository=repository)
    window.show()

    return app.exec()
```

### venv 注意事项
- 用 `python -m venv .venv` 创建虚拟环境
- `.venv/` 加入 `.gitignore`
- 打包脚本中始终使用 `.venv/Scripts/python.exe`
- **不要用 Windows Store 版 Python 创建 venv**（路径不稳定）

---

## 3. 主题系统设计

### 核心模式：单一 ThemePalette + 全局 stylesheet

```python
# theme.py
@dataclass(frozen=True)
class ThemePalette:
    root_background: str
    card_background: str
    # ... 30+ 语义化颜色 tokens

DARK_PALETTE = ThemePalette(...)
LIGHT_PALETTE = ThemePalette(...)

def get_palette(dark: bool) -> ThemePalette: ...

def build_app_stylesheet(dark: bool) -> str:
    palette = get_palette(dark)
    return f"""
    QWidget#root {{ background: {palette.root_background}; }}
    QPushButton#primaryButton {{ background: {palette.accent}; }}
    ...
    """
```

### 关键经验
- **给控件设 objectName**（如 `#primaryButton`），样式表才能精准命中
- **独立窗口（QMenu、QComboBox 弹出列表、QCalendarWidget、QMessageBox）不继承主窗口 stylesheet**
  - 解决：在 `QApplication` 级别额外 `setStyleSheet`
- **自绘控件需要主动同步主题**：`clock_picker.py` 通过全局变量 `DARK_MODE` + `set_clock_dark_mode()` 通知
- 颜色用语义化命名（`text_primary`）而非硬编码 `#333333`

---

## 4. SQLite3 数据层

```python
# database.py
class Database:
    def __init__(self, db_path: Path): ...

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row  # 支持按列名访问
        return connection

    def initialize(self) -> None:
        with self.connect() as conn:
            conn.executescript("CREATE TABLE IF NOT EXISTS ...")
```

```python
# repository.py
class MemoRepository:
    def __init__(self, database: Database): ...

    def list_events(self) -> list[MemoEvent]: ...
    def create_event(self, event: MemoEvent) -> MemoEvent: ...
    def update_event(self, event: MemoEvent) -> None: ...
    def delete_event(self, event_id: int) -> None: ...
```

### 要点
- DB 路径放在用户数据目录：`Path(os.environ["APPDATA"]) / "app_name" / "data" / "memo.db"`
- 用 `contextlib` 自动管理连接（`with self.connect() as conn`）
- 模型用 `dataclass`，可以在 Repo 里做 `_row_to_event()` 转换

---

## 5. 定时提醒调度

### 统一模型：`next_trigger_at`

每种提醒类型都只暴露一个可计算的"下一次触发时间"：

```python
class Scheduler:
    def compute_next_trigger(self, event, reference=None) -> str | None:
        # 一次性提醒 → 返回 event.one_time_at
        # 每周提醒   → 计算下一个指定星期几的 HH:mm:ss
        # 工作日提醒 → 计算下一个工作日（跳过节假日）的 HH:mm:ss
        # 延后状态   → 返回 snooze_until
```

### 轮询检测

```python
# 在 MainWindow 中用 QTimer 每 30 秒检查
self.poll_timer = QTimer(self)
self.poll_timer.setInterval(30000)
self.poll_timer.timeout.connect(self.check_due_events)
self.poll_timer.start()

def check_due_events(self):
    now = datetime.now()
    for event in self.repository.list_events():
        if event.next_trigger_at and datetime.fromisoformat(event.next_trigger_at) <= now:
            self.reminder_window.show_event(event.title, event.content)
            break
```

---

## 6. 自绘时钟选时器（Clock Picker）

### 架构
- `ClockTimeInput`：外观像普通输入框，点击弹出 picker
- `ClockTimePopup`：`Qt.Popup | FramelessWindowHint` 弹窗容器
- `ClockTimePicker`：paintEvent 自绘圆形表盘

### 关键技术点

**双圈 24 小时制**：
- 外圈 1-12，内圈 0/13-23
- 通过 `dist < MID_RADIUS` 判断点击内外圈

**60 格分/秒刻度**：
- 每格 1 单位，`range(0, 60)`
- 每 5 格显示数字标签
- 非标签格画细短线
- hover 时弹出彩色小药丸显示数字

**角度映射**（最容易出 bug）：
```python
def _angle_to_clock_index(degrees):
    raw = (90.0 - degrees) / 30.0
    return _rhu(raw) % 12   # 0=12点, 1=1点, ...

def _angle_to_min_sec(degrees):
    raw = (90.0 - degrees) / 6.0
    return _rhu(raw) % 60
```
- 用 `_rhu`（half-up 取整）而非 Python 内置 `round()`（银行家舍入）
- 鼠标角度用 `atan2(-(my - cy), mx - cx)` 从圆心反算

**主题同步**：
- `set_clock_dark_mode(enabled)` 全局变量通知
- picker 和 popup 都在 `paintEvent` 中读取 `get_palette(DARK_MODE)` 取色

---

## 7. 提醒弹窗

```python
class ReminderWindow(QWidget):
    def __init__(self):
        # Qt.Tool | WindowStaysOnTopHint 确保独立置顶
        self.setWindowFlag(Qt.WindowType.Tool, True)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)

        # 淡入动画
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(260)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)

    def show_event(self, title, content):
        self.setWindowOpacity(0.0)
        self.show()
        self.animation.start()
```

---

## 8. 系统托盘

```python
# 托盘图标
logo_path = Path(__file__).resolve().parents[2] / "assets" / "logo.png"
icon = QIcon(str(logo_path))
self.setWindowIcon(icon)

# 托盘图标 – 64x64 缩放
pixmap = QPixmap(str(logo_path)).scaled(64, 64,
    Qt.AspectRatioMode.KeepAspectRatio,
    Qt.TransformationMode.SmoothTransformation)
self.tray_icon.setIcon(QIcon(pixmap))

# 右键菜单
menu = QMenu()
menu.addAction(QAction("显示窗口", triggered=self.show_normal))
menu.addAction(QAction("隐藏窗口", triggered=self.hide))
menu.addSeparator()
menu.addAction(QAction("退出", triggered=self.quit_application))
self.tray_icon.setContextMenu(menu)
```

---

## 9. Windows 开机自启

```python
# system/startup.py
import winreg

RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"

def set_startup_enabled(enabled: bool) -> None:
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, RUN_KEY) as key:
        if enabled:
            winreg.SetValueEx(key, "AppName", 0, winreg.REG_SZ, executable_path)
        else:
            winreg.DeleteValue(key, "AppName")
```
- 使用 `HKEY_CURRENT_USER`，不需要管理员权限

---

## 10. PyInstaller 打包

```python
# memo_app.spec
a = Analysis(
    ['app.py'],
    datas=[('assets/logo.png', 'assets')],  # ⚠️ 必须显式声明资源文件
    hiddenimports=collect_submodules('PyQt6'),
    ...
)

exe = EXE(
    pyz, a.scripts, a.binaries, a.datas, [],
    name='win-memo-tool',
    console=False,       # Windows GUI 应用关终端
)
```

打包命令：
```powershell
.venv\Scripts\python.exe -m PyInstaller --clean --noconfirm memo_app.spec
```

### 常见问题
- **资源文件丢失**：`.spec` 中 `datas` 必须显式添加
- **Python 版本不兼容**：PyQt6 6.7+ 要求 Python 3.9+
- **打包体积大**：PyQt6 自带了 ~80MB 的 Qt6 运行时

---

## 11. PyQt6 / PyQt5 兼容注意

| 项目 | PyQt5 | PyQt6 |
|------|-------|-------|
| QAction import | `from PyQt5.QtWidgets import QAction` | `from PyQt6.QtGui import QAction` |
| 枚举 | `Qt.Horizontal`, `Qt.AlignCenter` | `Qt.Orientation.Horizontal`, `Qt.AlignmentFlag.AlignCenter` |
| QEasingCurve | `QEasingCurve.OutCubic` | `QEasingCurve.Type.OutCubic` |
| QSystemTrayIcon::Trigger | `QSystemTrayIcon.Trigger` | `QSystemTrayIcon.ActivationReason.Trigger` |

---

## 12. 开发流程建议

1. **先用 OpenSpec 规划**：proposal → design → specs → tasks，明确做哪些功能、怎么设计
2. **数据结构先行**：先建 models.py 和 database.py，确保存储层正确
3. **服务层无 UI 测试**：scheduler 和 holiday_service 用纯 Python 可以独立测试
4. **UI 逐层迭代**：骨架 → 表单 → 列表 → 主题 → 动画 → 精修
5. **主题统一做最后一轮**：检查所有独立弹窗（QMenu、日历、提醒弹窗、时钟弹窗）是否跟主题
6. **打包验证**：在干净机器上启动打包产物，确认资源加载和数据库路径正确

---

## 触发条件
当用户提到以下关键词组合时，优先使用本 skill：
- PyQt6 / PyQt5 桌面应用开发
- Windows 桌面工具、备忘录、提醒、定时器
- Python + SQLite3 本地存储
- 系统托盘、悬浮窗、开机自启
- 自绘控件、主题系统、暗色模式
- PyInstaller 打包分发

## 不适用场景
- Web 前端 / Electron 应用
- 移动端应用
- 纯命令行工具