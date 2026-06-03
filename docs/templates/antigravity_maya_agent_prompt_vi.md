# Hướng dẫn dành cho AI Agent hoạt động trong Maya Sandbox

Chào Agent, bạn đang được cấp quyền truy cập điều khiển Autodesk Maya thông qua cổng kết nối MCP để thực hiện tối ưu hóa hoặc chỉnh sửa scene mỹ thuật của dự án game **Tứ Phương Vô Lộ**.

Để đảm bảo an toàn tuyệt đối cho tài nguyên dự án, bạn phải tuân thủ nghiêm ngặt các chỉ thị dưới đây:

---

## 1. Giới hạn không gian hoạt động (Scope of Work)

- Bạn **chỉ được phép** mở và chỉnh sửa tệp Maya làm việc sau đây:
  `working/scene_agent_work.ma`
- Tuyệt đối **không** được mở, thay đổi hoặc ghi đè lên bất kỳ tệp tin nào ngoài thư mục sandbox này, bao gồm:
  - Tệp gốc Illustrator `.ai` của họa sĩ.
  - Tệp ảnh vector nguồn `.svg`.
  - Tệp scene Maya gốc trong `outputs/maya/`.
  - Bản chụp trạng thái ban đầu trong `original/` (ví dụ: `scene_before_agent.ma`, `geometry_before_agent.json`).
- Không được xóa bất kỳ tệp tin backup nào trong thư mục `original/`.

---

## 2. Quy trình thực thi nhiệm vụ (Execution Flow)

1. **Khảo sát ban đầu (Inspect First)**: 
   Trước khi thực hiện bất kỳ chỉnh sửa nào, bạn phải chạy lệnh truy vấn thông tin để kiểm tra và báo cáo cho người dùng về trạng thái hiện tại của scene:
   - Các nhóm đối tượng hình học (meshes, groups).
   - Danh sách các Layer (display layers).
   - Danh sách vật liệu/chất liệu (materials/shaders) đang được gán.
   - Trạng thái camera và ánh sáng hiện tại.

2. **Thực hiện thay đổi không phá hủy (Non-Destructive Edits)**:
   - Ưu tiên thực hiện các thay đổi không phá hủy (như tạo nhóm mới, gán vật liệu thay vì xóa lưới gốc).
   - Đảm bảo scene sau khi chỉnh sửa vẫn giữ nguyên khả năng biên tập tiếp bởi họa sĩ (ví dụ: giữ nguyên cấu trúc phân cấp node hợp lý, không gộp mesh vô tội vạ).

3. **Lưu kết quả mới (Save as New File)**:
   - Khi hoàn thành công việc, hãy thực hiện lưu kết quả (Save As) thành một tệp `.ma` mới bên trong thư mục `working/`.
   - Quy tắc đặt tên tệp kết quả: `scene_agent_result_v001.ma` (tăng số phiên bản lên nếu lưu nhiều lần).
   - Tuyệt đối không ghi đè trực tiếp lên `scene_before_agent.ma`.

4. **Báo cáo chi tiết (Detailed Report)**:
   Sau khi hoàn tất, hãy viết một báo cáo chi tiết chỉ ra:
   - Những đối tượng/layer nào đã được thêm mới hoặc sửa đổi.
   - Những vật liệu nào đã được gán hoặc thay đổi.
   - Tên tệp tin kết quả bạn đã lưu trong thư mục `working/`.
