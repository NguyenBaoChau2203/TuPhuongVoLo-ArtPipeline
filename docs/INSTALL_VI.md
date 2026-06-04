# Cài đặt nhanh

## Cần có

- Windows 10/11
- Python 3.11+
- Adobe Illustrator để vẽ/chạy JSX
- Autodesk Maya 2024+ nếu muốn tạo `.ma` thật

Blender là legacy/fallback, không bắt buộc cho workflow hằng ngày.

## Kiểm tra Python

Mở PowerShell:

```powershell
python --version
```

Nếu chưa có Python, cài từ `python.org` và tick `Add Python to PATH`.

## Cài dependency Python

```powershell
cd D:\TuPhuongVoLo-ArtPipeline
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Kiểm tra Maya/mayapy

```powershell
launchers\00_maya_env_check.bat
```

Đường dẫn thường dùng:

```text
C:\Program Files\Autodesk\Maya2024\bin\mayapy.exe
```

## Mở app

```powershell
launchers\09_artist_desktop_app.bat
```

## Đọc tiếp

```text
docs\WORKFLOW_FOR_WIFE_VI.md
docs\CODEX_PROMPTS_VI.md
docs\TROUBLESHOOTING_VI.md
```
