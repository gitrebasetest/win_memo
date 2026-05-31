# 实现计划：新增与编辑事件的明确区分

## 目标
让用户能够清晰区分"新增事件"和"编辑已有事件"两种模式，避免误操作修改老事件。

## 修改文件
- `memo_app/ui/main_window.py` — 主要 UI 和逻辑改动
- `memo_app/ui/theme.py` — 新增模式徽章的样式

## 具体改动

### 1. 表单标题和提示动态切换

**当前**: `form_title` 固定 "事件编辑"，`form_hint` 固定 "创建一次性、每周或工作日提醒"

**改为**: 将 `form_title` 和 `form_hint` 保存为实例变量（`self.form_title`, `self.form_hint`），新增方法 `_update_form_header()`：

- 新增模式 (`current_event_id is None`):
  - `form_title.setText("新建事件")`
  - `form_hint.setText("创建一次性、每周或工作日提醒")`
- 编辑模式 (`current_event_id is not None`):
  - `form_title.setText("编辑事件")`
  - `form_hint.setText(f"正在编辑: {self.title_input.text()}")`

调用时机: `clear_form()` 和 `load_selected_event()` 中，以及 `title_input` 文本变化时更新编辑模式的 hint。

### 2. 保存按钮文案动态切换

**当前**: 固定 "保存事件"

**改为**: `self.save_button` 文案根据模式切换：
- 新增模式: "添加事件"
- 编辑模式: "更新事件"

在 `_update_form_header()` 中一并处理。

### 3. 删除按钮在新增模式下隐藏

**当前**: `delete_button` 始终可见

**改为**: 在 `_update_form_header()` 中：
- 新增模式: `self.delete_button.setVisible(False)`
- 编辑模式: `self.delete_button.setVisible(True)`

### 4. 增加"新建事件"按钮

在事件列表面板顶部（`list_title` 和 `list_hint` 之后），增加一个 `self.new_event_button`：
- `objectName`: "primaryButton"
- 文案: "+ 新建事件"
- 点击后调用 `clear_form()`（回到新增模式）

位置: `list_layout.addWidget(self.new_event_button)` 在 `list_hint` 之后、`event_list` 之前。

在 `_wire_signals()` 中连接: `self.new_event_button.clicked.connect(self.clear_form)`。

### 5. 删除事件增加确认弹窗

**当前**: `delete_selected_event()` 直接删除，无确认

**改为**: 删除前弹出 `QMessageBox.question()` 确认：
```
确认删除此事件？
此操作无法撤销。
```
只有用户点击"是"才执行删除。

### 6. 编辑模式切换时清空表单的确认（可选但推荐）

**当前**: 点击列表事件立即加载到表单，如果用户之前正在填写新事件内容，这些内容会被覆盖丢失。

**改为**: 在 `load_selected_event()` 中，如果当前表单有内容（`title_input` 不为空）且处于新增模式，先弹出确认：
```
当前表单有未保存的内容，切换到编辑模式将丢弃这些内容。是否继续？
```
只有用户确认后才加载事件数据；否则取消选择，保留当前表单内容。

### 7. 编辑模式徽章样式

在 `form_title` 旁增加一个模式徽章标签 `self.mode_badge`（QLabel）：
- `objectName`: "modeBadge"
- 新增模式: 文案 "新增"，背景色 accent_soft，文字色 accent_text
- 编辑模式: 文案 "编辑"，背景色 warning_soft，文字色 warning_text（复用已有主题色）

在 `theme.py` 的 `build_app_stylesheet` 中增加样式：
```css
QLabel#modeBadge {
    border-radius: 10px;
    padding: 4px 10px;
    font-size: 12px;
    font-weight: 700;
    background: {palette.accent_soft};
    color: {palette.accent_text};
}
QLabel#modeBadge[mode="edit"] {
    background: {palette.warning_soft};
    color: {palette.warning_text};
}
```

徽章放在 `form_title` 同一行（HBoxLayout），标题左、徽章右。

### 8. 弹窗窗口尺寸重置（顺便修复之前分析的棘轮效应问题）

在 `ReminderWindow.show_event()` 中，设置文本后、`show()` 之前，添加：
```python
self.resize(520, 220)
```
确保每次弹出窗口大小一致。

## 调用链总结

- `clear_form()` → 设置 `current_event_id = None` → 调用 `_update_form_header()` → 切换为新增模式外观
- `load_selected_event()` → 设置 `current_event_id = event.id` → 调用 `_update_form_header()` → 切换为编辑模式外观
- `title_input.textChanged` 信号 → 如果处于编辑模式，更新 `form_hint` 显示当前编辑的事件标题
- `new_event_button.clicked` → 调用 `clear_form()`