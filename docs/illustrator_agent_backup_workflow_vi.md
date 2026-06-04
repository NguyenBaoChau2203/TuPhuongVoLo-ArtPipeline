# Quy trình backup sandbox cho Illustrator Agent

Tài liệu này dùng cho giai đoạn 011A. Mục tiêu là chuẩn bị một bản sao an toàn
trước khi thử nghiệm AI hoặc Illustrator MCP trên artwork. Quy trình này mirrors
010A Maya sandbox: agent chỉ được làm việc trong sandbox, còn file gốc của họa
sĩ luôn là nguồn chỉ đọc.

## Vì sao Illustrator cần sandbox?

File Illustrator thường chứa layer, group, tên đối tượng, màu, symbol, và bản
export mà họa sĩ cần giữ nguyên. AI hoặc MCP có thể vô tình save đè, đổi tên,
flatten layer, merge artwork, hoặc export vào nhầm thư mục. Vì vậy trước mọi
chỉnh sửa có hỗ trợ AI, cần tạo một sandbox riêng và chỉ mở bản sao làm việc.

## Quy trình an toàn

1. Bắt đầu từ file gốc của họa sĩ: `.ai`, `.svg`, hoặc `.png`.
2. Chạy `scripts/python/illustrator_agent_sandbox.py` để tạo phiên backup.
3. Trong Illustrator/Antigravity MCP, chỉ mở `working/scene_agent_work.ai`.
4. Kiểm tra naming, layer, group, và cấu trúc artwork trước.
5. Chỉ sau đó mới cho phép chỉnh sửa trong sandbox.
6. Nếu export SVG từ sandbox, chỉ export vào thư mục `working/`.
7. Chạy app/Maya pipeline hiện có bằng sandbox SVG đã được chấp nhận.
8. Họa sĩ review thủ công trước khi chấp nhận thay đổi vào production.

## Lệnh ví dụ

Chạy từ thư mục repo:

```powershell
python scripts/python/illustrator_agent_sandbox.py ^
  --source-ai D:\TuPhuongVoLo_ArtistTests\real_svg_test_01\phong_kho.ai ^
  --source-svg D:\TuPhuongVoLo_ArtistTests\real_svg_test_01\phong_kho.svg ^
  --room phong_kho ^
  --backup-root D:\TuPhuongVoLo_IllustratorAgentBackups
```

Nếu chỉ muốn xem kế hoạch, thêm `--dry-run`. Lệnh dry-run không tạo thư mục và
không copy file.

## Cấu trúc sandbox

```text
D:\TuPhuongVoLo_IllustratorAgentBackups\<timestamp>_<label>\
  original\
    source_ai_before_agent.ai
    source_svg_before_agent.svg
    source_png_before_agent.png
  working\
    scene_agent_work.ai
    scene_agent_work.svg
    scene_agent_work.png
  reports\
    illustrator_agent_session.json
    agent_notes.md
  restore_illustrator_backup.ps1
```

Nếu một input không được cung cấp, sandbox sẽ không tạo file giả cho input đó.

## Hành động bị cấm

- Không chỉnh sửa file `.ai` gốc.
- Không chỉnh sửa source SVG gốc.
- Không ghi đè PNG/export gốc.
- Không xóa, flatten, merge layer, hoặc đổi tên layer/artwork nếu chưa được phê
  duyệt rõ ràng.
- Không cho agent truy cập rộng vào `D:\` hoặc `C:\Users`.
- Không commit `.ai`, `.svg`, `.png`, `.ma`, `.zip`, `outputs/`, backups, hoặc
  secrets.

## Ghi nhớ

Sandbox chỉ là vùng thử nghiệm. Chỉ sau khi họa sĩ kiểm tra và chấp nhận, file
SVG trong `working/` mới được dùng làm input cho pipeline app/Maya hiện có.
