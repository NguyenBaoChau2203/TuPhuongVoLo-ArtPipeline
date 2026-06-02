# Checklist kiểm tra SVG thật trước khi dựng Maya

> Dành cho họa sĩ và người vận hành pipeline Tứ Phương Vô Lộ.

Mục tiêu của checklist này là giúp thử file SVG thật từ Illustrator một cách an toàn trước khi tạo scene Maya `.ma`.

## Quy tắc an toàn

- Không bao giờ sửa, xóa, hoặc ghi đè file `.ai` gốc.
- Luôn làm việc từ một bản copy/export riêng, không chạy pipeline trực tiếp trên file gốc của họa sĩ.
- Không commit SVG thật, file `.ma`, PNG preview, thư mục `outputs/`, file build, file zip, hoặc artifact sinh ra từ máy artist.
- Nếu phát hiện lỗi thật từ file artist, ghi lại vấn đề để sửa pipeline hoặc sửa quy trình export, không sửa file gốc vội.

## Quy trình đề xuất

1. Mở file `.ai` gốc trong Illustrator và export một bản clean SVG riêng.
2. Đặt bản SVG copy vào thư mục thử nghiệm phù hợp, ví dụ `drops/`.
3. Chạy preflight read-only:

```powershell
python scripts/python/svg_preflight_check.py --input drops/ten_file.svg
```

4. Nếu muốn lưu báo cáo để gửi cho developer, ghi JSON vào `outputs/reports/`:

```powershell
python scripts/python/svg_preflight_check.py --input drops/ten_file.svg --json-output outputs/reports/svg_preflight_report.json
```

5. Nếu preflight báo `FATAL`, dừng lại và sửa nguyên nhân: thiếu file, XML hỏng, hoặc root không phải `<svg>`.
6. Nếu preflight báo `WARNING`, đọc cảnh báo trước. Có thể tiếp tục dry-run nếu cảnh báo không chặn mục tiêu test.
7. Chạy Maya dry-run trước, chưa tạo `.ma` thật:

```powershell
python scripts/python/build_maya_room.py --input drops/ten_file.svg --room ten_phong --dry-run
```

8. Chỉ chạy Maya thật sau khi dry-run thành công và đường dẫn output đúng:

```powershell
python scripts/python/build_maya_room.py --input drops/ten_file.svg --room ten_phong --maya-path "C:\Program Files\Autodesk\Maya2024\bin\mayapy.exe"
```

## Marker cửa và cửa sổ

- Nếu SVG có cửa/cửa sổ, đặt tên group/layer bắt đầu bằng `door_` hoặc `window_`, ví dụ
  `door_main`, `door_left`, `window_small`, `window_back_01`.
- Phase 005.3S chỉ tạo marker hình khối đơn giản trong group `openings` của Maya. Pipeline chưa khoét
  tường, chưa boolean, và chưa tạo lỗ thật.
- Sau khi build `.ma`, mở Maya và kiểm tra marker trong `openings` trước khi polish thủ công.

## Ghi lại vấn đề thật

Khi test SVG thật, hãy ghi lại:

- Tên file copy/export đang test.
- Illustrator version và cách export SVG.
- Preflight báo `OK`, `WARNING`, hay `FATAL`.
- Cảnh báo về element rủi ro như `image`, `use`, `text`, `clipPath`, `mask`, `circle`, `ellipse`, hoặc `line`.
- Marker phát hiện được: `prop_`, `item_`, `object_`, `door_`, `window_`, `rot90`, `rot180`, `rot270`, `mat_`, `material_`, `color_`.
- Kết quả dry-run Maya và lỗi cụ thể nếu có.

Luôn giữ file thật và output sinh ra ở ngoài commit cho đến khi developer tạo fixture tối giản, đã được làm sạch, phù hợp để đưa vào `tests/in/`.
