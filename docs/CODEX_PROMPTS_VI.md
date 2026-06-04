# Prompt mẫu cho Codex

Tài liệu này dùng để copy/paste khi nhờ Codex phụ vợ tạo bản nháp Illustrator hoặc polish Maya.

## 1. Prompt tạo JSX từ ảnh mẫu

Gửi ảnh mẫu kèm prompt:

```text
Bạn đang hỗ trợ pipeline Tứ Phương Vô Lộ.

Nhiệm vụ:
Dựa trên ảnh mẫu tôi gửi, tạo một file Illustrator JSX draft.

Mục tiêu:
- Tạo bản vẽ top-down/layout có thể chỉnh trong Illustrator.
- Không cần final art đẹp hoàn hảo, nhưng phải đủ tốt để vợ tôi sửa ít hoặc export SVG nếu cảnh đơn giản.
- Tạo ranh phòng/map, cửa/cửa sổ, vị trí đồ lớn, flow di chuyển, vài shape chính.
- Đặt tên layer/group đúng pipeline để app đọc SVG sang Maya.

Tên cảnh:
[ví dụ: phong_kho]

Những thứ bắt buộc:
[liệt kê: cửa chính bên trái, 3 kệ sát tường phải, 2 thùng gỗ giữa phòng...]

Style mong muốn:
[ví dụ: kho cũ, nhà gỗ Việt Nam, đảo nhỏ, hành lang motel...]

Yêu cầu naming:
- room_[ten_phong]
- door_[ten]
- window_[ten]
- prop_[ten_do]_[so]
- flow_[ten]

Yêu cầu file:
- Xuất nội dung là JSX hoàn chỉnh.
- Dùng template scripts/illustrator/templates/reference_to_layout_draft.jsx làm phong cách.
- JSX không tự overwrite file .ai gốc.
- JSX không tự export SVG ở bản đầu; để vợ tôi review/chỉnh trong Illustrator trước.
- Có note text nhỏ trong Illustrator để vợ tôi biết phần nào cần chỉnh.
```

## 2. Prompt sửa JSX sau khi vợ review

```text
Đây là JSX draft trước đó và feedback của vợ tôi.

Feedback:
[ví dụ: phòng rộng hơn, cửa lệch xuống, kệ nhỏ lại, flow đi vòng qua giữa phòng]

Hãy chỉnh lại JSX:
- giữ naming pipeline
- không đổi mục tiêu export SVG
- chỉ sửa layout/shape cần thiết
- trả về file JSX hoàn chỉnh
```

## 3. Prompt kiểm SVG trước khi chạy app

```text
Tôi có SVG export từ Illustrator.
Hãy kiểm tra xem naming/layout có phù hợp pipeline không.

Tôi muốn biết:
- room group có đúng không
- door/window marker có còn tên không
- prop marker có đủ không
- có element rủi ro không
- room name nên nhập vào app là gì

Không sửa file gốc nếu chưa hỏi.
```

Sau đó chạy:

```powershell
python scripts\python\svg_preflight_check.py --input "drops\scene_export.svg"
```

## 4. Prompt tạo Maya Python polish script

Chỉ dùng sau khi đã tạo sandbox Maya và mở:

```text
...\working\scene_agent_work.ma
```

Prompt:

```text
Bạn đang hỗ trợ Maya sandbox cho Tứ Phương Vô Lộ.

Scene được phép thao tác:
[dán đường dẫn working\scene_agent_work.ma]

Sandbox:
[dán thư mục sandbox]

Rollback:
[dán đường dẫn restore_agent_backup.ps1]

Yêu cầu của vợ tôi:
[ví dụ: làm phòng kho cũ hơn, thêm kệ gỗ, vài thùng gỗ, ánh sáng vàng, sàn hơi bẩn]

Quy tắc bắt buộc:
- Chỉ tạo Maya Python script, không dùng pyautogui.
- Không đổi tường/cửa/layout gốc.
- Không xóa mesh gốc.
- Mọi object mới phải nằm trong group: GRP_agent_polish_v001
- Tạo material đơn giản, light/camera review nếu cần.
- Tạo note trong scene ghi script đã thêm gì.
- Script phải có guard/nhắc operator chỉ chạy trên sandbox working scene.
- Dùng template scripts/maya/agent_polish_templates/agent_polish_additive_template.py làm mẫu.

Output mong muốn:
- Trả về một file Python hoàn chỉnh để paste vào Maya Script Editor.
- Giải thích ngắn cách vợ tôi bật/tắt group để review.
```

## 5. Prompt sửa polish sau review

```text
Vợ tôi đã chạy script Maya polish và review.

Feedback:
[ví dụ: kệ quá cao, ánh sáng vàng quá mạnh, thùng gỗ che flow đi lại]

Hãy tạo script chỉnh tiếp:
- chỉ chỉnh object trong GRP_agent_polish_v001
- không đụng tường/cửa/layout gốc
- giữ khả năng bật/tắt group để review
- nếu cần, tạo group version mới GRP_agent_polish_v002
```

## 6. Mẫu mô tả ngắn cho vợ

```text
Ảnh này là [loại cảnh].
Tôi muốn giữ [3 thứ quan trọng].
Có thể đơn giản hóa [chi tiết không quan trọng].
Ưu tiên [giống ảnh / dễ sửa / đúng pipeline Maya].
```

Ví dụ:

```text
Ảnh này là phòng kho cũ nhìn top-down.
Tôi muốn giữ bố cục phòng dài, cửa bên trái, kệ sát tường phải.
Có thể đơn giản hóa chi tiết thùng nhỏ.
Ưu tiên đúng pipeline Maya và dễ sửa trong Illustrator.
```
