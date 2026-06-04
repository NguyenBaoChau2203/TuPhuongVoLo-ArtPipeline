# Hướng dẫn sử dụng cho họa sĩ

Tài liệu chính nên đọc mỗi ngày:

```text
docs\WORKFLOW_FOR_WIFE_VI.md
```

## Quy trình hiện tại

```text
Ảnh mẫu + mô tả
-> Codex tạo JSX draft
-> vợ mở trong Illustrator, chỉnh, export SVG
-> app kiểm SVG / dry-run / tạo Maya .ma
-> Maya sandbox
-> Codex tạo script polish
-> vợ review/rollback
```

## Mở app

Nhấp đúp:

```text
launchers\09_artist_desktop_app.bat
```

Trong app:

1. chọn SVG
2. nhập room, ví dụ `phong_kho`
3. bấm `Kiểm tra SVG`
4. bấm `Chạy dry-run`
5. nếu ổn, bấm `Chạy Maya thật`

## CLI nếu không dùng app

```powershell
python scripts\python\svg_preflight_check.py --input "drops\scene_export.svg"

python scripts\python\build_maya_room.py `
  --input "drops\scene_export.svg" `
  --room phong_kho `
  --dry-run
```

Chạy Maya thật:

```powershell
python scripts\python\build_maya_room.py `
  --input "drops\scene_export.svg" `
  --room phong_kho `
  --maya-path "C:\Program Files\Autodesk\Maya2024\bin\mayapy.exe" `
  --render-preview
```

## Output ở đâu?

```text
outputs\maya\       file .ma
outputs\preview\    ảnh PNG preview
outputs\tmp\        geometry JSON
outputs\reports\    report kiểm tra
```

## Nhờ Codex phụ

Prompt mẫu:

```text
docs\CODEX_PROMPTS_VI.md
```

Template Codex dùng để tạo file mới:

```text
scripts\illustrator\templates\reference_to_layout_draft.jsx
scripts\maya\agent_polish_templates\agent_polish_additive_template.py
```

## Không cần cho workflow hằng ngày

- Blender/isometric cũ
- AI preview fal/mock
- batch nhiều file
- packaging `.exe`
- Illustrator MCP/Antigravity nếu chưa smoke test khỏe

Các phần đó nằm ngoài luồng chính. Xem thêm `archive\README.md` nếu cần tra cứu.
