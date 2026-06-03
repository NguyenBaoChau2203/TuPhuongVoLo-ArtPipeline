# Quy trình backup sandbox cho Maya Agent / Antigravity

Tài liệu này dùng cho giai đoạn 010A. Mục tiêu là chuẩn bị một bản sao an
toàn trước khi thử nghiệm agent toàn quyền trong Maya. Giai đoạn này **không**
cài MCP server, **không** cấu hình Antigravity, và **không** thêm AI API.

## Vì sao cần backup?

Agent toàn quyền có thể đổi tên node, xóa object, lưu đè scene, hoặc tạo nhiều
file thử nghiệm. Vì vậy agent không được làm việc trực tiếp trên file gốc của
họa sĩ hoặc file sinh ra từ pipeline chính.

Quy tắc khuyến nghị:

> Full control chỉ được phép bên trong thư mục `working/` của một phiên sandbox.

## Tạo một phiên sandbox

Chạy lệnh từ thư mục repo:

```powershell
python scripts/python/maya_agent_sandbox.py ^
  --maya-scene outputs\maya\tu_phuong_vo_lo_phong_kho_main_maya_v017.ma ^
  --geometry-json outputs\tmp\tu_phuong_vo_lo_phong_kho_main_blockout_v017.json ^
  --source-svg D:\TuPhuongVoLo_ArtistTests\real_svg_test_01\phong_kho.svg ^
  --room phong_kho ^
  --backup-root D:\TuPhuongVoLo_AgentBackups
```

Nếu chưa chắc đường dẫn, có thể chạy thử trước:

```powershell
python scripts/python/maya_agent_sandbox.py ^
  --maya-scene outputs\maya\tu_phuong_vo_lo_phong_kho_main_maya_v017.ma ^
  --room phong_kho ^
  --backup-root D:\TuPhuongVoLo_AgentBackups ^
  --dry-run
```

`--dry-run` chỉ in kế hoạch. Lệnh này không tạo thư mục và không copy file.

## Cấu trúc phiên sandbox

Sau khi tạo, phiên sandbox nằm trong thư mục dạng:

```text
D:\TuPhuongVoLo_AgentBackups\<timestamp>_<room_or_session>\
  original\
    scene_before_agent.ma
    geometry_before_agent.json
    source_svg_snapshot.svg
  working\
    scene_agent_work.ma
  reports\
    agent_session.json
    agent_notes.md
  restore_agent_backup.ps1
```

`original/` là bản chụp để đối chiếu và khôi phục. Không chỉnh sửa các file
trong thư mục này.

`working/` là nơi agent được phép làm việc.

## File Antigravity/MCP được mở

Khi thử nghiệm agent toàn quyền, chỉ trỏ Antigravity/MCP/Maya tới file:

```text
working\scene_agent_work.ma
```

Nếu agent cần lưu kết quả, hãy lưu thành file mới bên trong `working/`, ví dụ:

```text
working\scene_agent_result_v001.ma
```

Không cho agent mở hoặc ghi đè:

- File `.ai` gốc của họa sĩ
- File `.svg` gốc hoặc SVG trong `drops/`, `assets/`, thư mục test của họa sĩ
- File `.ma` gốc trong `outputs/maya/`
- File geometry JSON gốc trong `outputs/tmp/`
- Bất kỳ file production nào ngoài thư mục sandbox

## Cách khôi phục

Mỗi phiên sandbox có script:

```text
restore_agent_backup.ps1
```

Script này copy:

```text
original\scene_before_agent.ma
```

tới đường dẫn restore mà bạn chỉ định.

Ví dụ:

```powershell
powershell -ExecutionPolicy Bypass -File D:\TuPhuongVoLo_AgentBackups\20260603_201500_phong_kho\restore_agent_backup.ps1 ^
  -RestoreTarget D:\TuPhuongVoLo_AgentBackups\restore_test\scene_restored.ma
```

Nên restore ra một file mới để kiểm tra trước. Không restore đè vào file
production nếu chưa chắc chắn.

## Không được làm

- Không commit file `.ma`, `.png`, `.zip`, hoặc nội dung sinh ra trong
  `outputs/`.
- Không commit sandbox backup nếu backup root nằm trong repo.
- Không đưa secrets, `.env`, token, API key, credential, hoặc thông tin đăng
  nhập vào sandbox/report.
- Không cài hoặc vendor MayaMCP trong giai đoạn 010A.
- Không cấu hình Antigravity trong giai đoạn 010A.
- Không thêm AI API hoặc web UI.
- Không triển khai Feature 006 ở bước này.

## Ghi nhớ

File `.ai` và `.svg` gốc là input chỉ đọc của họa sĩ. Maya scene trong sandbox
là bản sao để thử nghiệm. Chỉ sau khi con người kiểm tra kết quả agent tạo ra
mới được cân nhắc đưa thay đổi trở lại pipeline chính.
