# 📋 Quy trình SDD — Phát triển Hướng Đặc tả

## SDD là gì?

**SDD** (Spec-Driven Development — Phát triển Hướng Đặc tả) là quy trình đảm bảo mọi công việc coding đều có kế hoạch rõ ràng trước khi bắt đầu.

Tóm tắt: **Viết kế hoạch trước → Rồi mới code**

---

## Quy trình

### 1. Đặc tả (spec.md)
- Mô tả feature muốn làm
- Liệt kê yêu cầu
- Xác định tiêu chí thành công
- Ở đâu: `specs/NNN-feature/spec.md`

### 2. Kế hoạch (plan.md)
- Thiết kế kỹ thuật
- Chọn công cụ/thư viện
- Xác định cấu trúc code
- Ở đâu: `specs/NNN-feature/plan.md`

### 3. Danh sách việc (tasks.md)
- Chia nhỏ công việc
- Đánh dấu hoàn thành
- Theo dõi tiến độ
- Ở đâu: `specs/NNN-feature/tasks.md`

### 4. Triển khai
- Code theo task list
- Tham chiếu task ID trong commit
- Chạy test sau mỗi thay đổi

### 5. Kiểm tra (quickstart.md)
- Làm theo hướng dẫn quickstart để xác nhận
- Kiểm tra kết quả đầu ra
- Ở đâu: `specs/NNN-feature/quickstart.md`

---

## Các Feature hiện có

| # | Feature | Trạng thái |
|---|---------|-----------|
| 001 | Chuyển đổi mặt bằng → phòng isometric | 📋 Đặc tả xong |
| 002 | Xuất SVG sạch từ Illustrator | 📋 Đặc tả xong |
| 003 | Đặt tên và quản lý tài sản | 📋 Đặc tả xong |
| 004 | Render hàng loạt isometric | 📋 Đặc tả xong |
| 005 | Tích hợp Maya (tùy chọn) | 📋 Đặc tả xong |
| 006 | Điều khiển bằng ngôn ngữ tự nhiên | 📋 Đặc tả xong (tương lai) |

---

## Thứ tự triển khai khuyến nghị

1. **Feature 002** — Xuất SVG sạch (nền tảng cho tất cả)
2. **Feature 003** — Đặt tên tự động
3. **Feature 001** — Tạo phòng isometric
4. **Feature 004** — Render hàng loạt
5. **Feature 005** — Maya (nếu cần)
6. **Feature 006** — Điều khiển ngôn ngữ tự nhiên (tương lai)

---

## Dành cho họa sĩ

Bạn không cần hiểu chi tiết SDD. Điều quan trọng:
- Mỗi tính năng đều có tài liệu đầy đủ trước khi code
- Bạn có thể đọc `spec.md` để hiểu tính năng sẽ làm gì
- Bạn có thể đọc `quickstart.md` để biết cách sử dụng
