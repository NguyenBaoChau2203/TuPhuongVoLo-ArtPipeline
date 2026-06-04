# Launcher hằng ngày

Launcher là file `.bat` để vợ/họa sĩ chạy pipeline mà không cần nhớ lệnh dài.

## Dùng hằng ngày

| File | Khi nào dùng |
| --- | --- |
| `09_artist_desktop_app.bat` | Cách chính: chọn SVG, preflight, dry-run, tạo Maya `.ma`. |
| `00_maya_env_check.bat` | Kiểm tra Python/PyYAML/`mayapy.exe` trước khi chạy Maya thật. |
| `07_build_maya_room.bat` | Fallback CLI thân thiện cho một SVG/một phòng nếu không mở app. |
| `08_create_maya_sandbox.bat` | Fallback tạo Maya sandbox từ file `.ma` đã có nếu muốn làm ngoài app. |

## Quy trình ngắn

1. Vợ export SVG từ Illustrator.
2. Nhấp đúp `09_artist_desktop_app.bat`.
3. Chọn SVG.
4. Bấm `Kiểm tra SVG`.
5. Bấm `Chạy dry-run`.
6. Nếu dry-run ổn, bấm `Chạy Maya thật`.
7. Dùng app tạo Visual Fidelity / Maya sandbox nếu cần.
8. Mở `working\scene_agent_work.ma` trong sandbox để Codex polish.

## Sau khi có `.ma`

Đọc:

```text
docs\WORKFLOW_FOR_WIFE_VI.md
docs\CODEX_PROMPTS_VI.md
```

Nếu muốn Codex polish Maya, hãy tạo sandbox trước rồi chỉ mở:

```text
...\working\scene_agent_work.ma
```

Cách dễ nhất là dùng nút trong app: `Tự tìm output mới nhất` → `Tạo Maya Sandbox` → `Mở working/scene_agent_work.ma`.
Nếu không mở app, dùng `08_create_maya_sandbox.bat`.

## Không dùng hằng ngày

Các launcher cũ cho Blender/isometric, batch, packaging, ingest asset hoặc cleanup thủ công không nằm trong flow mỗi ngày. Nếu cần lại, xem `archive\README.md`.

## Nhắc an toàn

- Dry-run trước khi chạy Maya thật.
- Không ghi đè file `.ai` hoặc `.svg` gốc.
- Không commit file sinh ra trong `outputs\`.
- `mayapy.exe` thường nằm ở:

```text
C:\Program Files\Autodesk\Maya2024\bin\mayapy.exe
```
