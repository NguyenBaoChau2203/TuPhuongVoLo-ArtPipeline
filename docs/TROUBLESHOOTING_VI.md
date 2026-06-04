# Xử lý sự cố

## App không mở

Kiểm tra Python:

```powershell
python --version
```

Nếu Python không có trong `PATH`, cài Python hoặc đặt biến:

```powershell
set TUPHUONGVOLO_PYTHON_EXE=C:\Path\To\python.exe
```

## App không tìm thấy repo

Chạy app từ thư mục repo hoặc đặt:

```powershell
set TUPHUONGVOLO_REPO_ROOT=D:\TuPhuongVoLo-ArtPipeline
```

## Preflight báo FATAL

Thường do:

- file không tồn tại
- file không phải `.svg`
- XML lỗi
- root không phải `<svg>`

Hãy export lại SVG từ Illustrator rồi chạy:

```powershell
python scripts\python\svg_preflight_check.py --input "drops\scene_export.svg"
```

## Dry-run được nhưng chạy Maya thật lỗi

Dry-run không cần Maya. Chạy thật cần `mayapy.exe`.

Kiểm tra:

```powershell
launchers\00_maya_env_check.bat
```

Đường dẫn thường dùng:

```text
C:\Program Files\Autodesk\Maya2024\bin\mayapy.exe
```

## Không có file .ma

Kiểm tra log app hoặc CLI:

- dry-run chỉ in kế hoạch, không tạo `.ma`
- chạy thật phải có `--maya-path`
- Maya trả lỗi thì đọc dòng `ERR_MAYA_FAILED`

Output mong đợi:

```text
outputs\maya\
```

## Không có PNG preview

PNG chỉ tạo khi bật `Render PNG preview` hoặc dùng `--render-preview`.

Output:

```text
outputs\preview\
```

## Scene Maya nhìn đơn giản

Đây là blockout để kiểm tra layout, chưa phải final art.

Làm tiếp:

1. tạo Maya sandbox
2. nhờ Codex tạo Maya Python polish script
3. chạy script trong sandbox
4. bật/tắt group `GRP_agent_*` để review

Xem:

```text
docs\WORKFLOW_FOR_WIFE_VI.md
docs\CODEX_PROMPTS_VI.md
```

## Lỡ chạy script xấu trong Maya

Nếu script chỉ tạo group `GRP_agent_*`, có thể tắt/xóa group đó.

Nếu đã tạo sandbox, rollback bằng:

```text
restore_agent_backup.ps1
```

## Không nên làm

- Không chạy AI/Codex trên file `.ma` gốc trong `outputs\maya\`.
- Không sửa file `.ai` gốc bằng AI.
- Không commit file sinh ra trong `outputs\`.
- Không dùng launcher đã archive trừ khi developer cần lại.
