# Win Memo Tool

## 运行

```powershell
python -m pip install -r requirements.txt
python app.py
```

## 功能

- 悬浮主窗口与托盘恢复
- 一次性提醒
- 每周固定时间提醒
- 每个工作日提醒
- 节假日联网获取与本地缓存
- 提醒关闭与延后
- 开机自动启动开关

## 节假日数据

默认通过 `https://timor.tech/api/holiday/year/<year>` 获取节假日数据。
网络不可用时，会优先使用本地 SQLite 缓存。

## 打包

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build.ps1
```

打包产物默认位于 `dist/win-memo-tool/` 或对应 PyInstaller 输出目录。
