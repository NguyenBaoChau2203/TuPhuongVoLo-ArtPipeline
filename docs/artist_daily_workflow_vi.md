# Daily workflow cho artist/operator

Tài liệu chính đã được gom lại tại:

```text
docs\WORKFLOW_FOR_WIFE_VI.md
```

Đường làm việc hiện tại:

```text
Ảnh mẫu + mô tả tiếng Việt
-> Codex tạo JSX draft
-> vợ chỉnh Illustrator và export SVG
-> app kiểm SVG / dry-run / tạo Maya .ma
-> Visual Fidelity nếu cần
-> Maya sandbox
-> Codex tạo Maya Python polish script
-> vợ bật/tắt group review, giữ hoặc rollback
```

## Lệnh mở app

```powershell
launchers\09_artist_desktop_app.bat
```

## Lệnh CLI tối thiểu

```powershell
python scripts\python\svg_preflight_check.py --input "drops\scene_export.svg"

python scripts\python\build_maya_room.py `
  --input "drops\scene_export.svg" `
  --room phong_kho `
  --dry-run
```

Chạy Maya thật sau khi dry-run ổn:

```powershell
python scripts\python\build_maya_room.py `
  --input "drops\scene_export.svg" `
  --room phong_kho `
  --maya-path "C:\Program Files\Autodesk\Maya2024\bin\mayapy.exe" `
  --render-preview
```

## Prompt và template

```text
docs\CODEX_PROMPTS_VI.md
scripts\illustrator\templates\reference_to_layout_draft.jsx
scripts\maya\agent_polish_templates\agent_polish_additive_template.py
```

## Sau khi đã dựng Maya `.ma`

Trong app, bấm `Tự tìm output mới nhất` để app tự điền scene Maya và geometry JSON mới nhất.

Sau đó:

1. Nếu cần kiểm tra chất lượng hình khối, bấm `Tạo Visual Fidelity`.
2. Trước khi nhờ Codex polish Maya, bấm `Tạo Maya Sandbox`.
3. Khi sandbox đã tạo xong, bấm `Mở working/scene_agent_work.ma` và chỉ làm việc trên file đó.

Nếu không mở app được, có thể dùng launcher:

```powershell
launchers\08_create_maya_sandbox.bat
```

## Nhắc an toàn

- Không cho AI sửa file `.ai` gốc.
- Không cho AI sửa file `.ma` gốc trong `outputs\maya\`.
- Chỉ polish Maya trên `working\scene_agent_work.ma` trong sandbox.
- Không commit file sinh ra: `.ma`, `.svg`, `.json`, `.png`, `.zip`, `.exe`, sandbox backup.
- Illustrator MCP/Antigravity vẫn là beta nếu chưa smoke test khỏe; đường ổn định là Codex tạo JSX để vợ chạy thủ công trong Illustrator.
