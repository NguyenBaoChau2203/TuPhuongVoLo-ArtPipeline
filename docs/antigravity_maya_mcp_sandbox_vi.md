# Quy trình tích hợp và sử dụng an toàn Antigravity + Maya MCP Sandbox

Tài liệu này hướng dẫn chi tiết cách thiết lập, cấu hình và quy trình vận hành an toàn khi kết nối AI Agent (Antigravity) với Autodesk Maya qua Model Context Protocol (MCP) trong dự án game **Tứ Phương Vô Lộ**.

> [!WARNING]
> Việc cho phép AI Agent điều khiển trực tiếp Maya đi kèm rủi ro hư hại dữ liệu thiết kế, thay đổi cấu trúc scene ngoài ý muốn. Quy trình dưới đây bắt buộc phải được tuân thủ nghiêm ngặt.

---

## 1. Tổng quan về Cơ chế hoạt động

- **Antigravity**: AI Agent hỗ trợ lập trình và tự động hóa quy trình sản xuất mỹ thuật game.
- **Model Context Protocol (MCP)**: Giao thức chuẩn hóa kết nối mô hình ngôn ngữ lớn (LLM) với các công cụ cục bộ bên ngoài.
- **Maya MCP Server**: Tiến trình cổng kết nối trung gian (chạy độc lập ngoài repository này) nhận lệnh từ Antigravity và chuyển tiếp lệnh Python/MEL vào Maya.
- **Maya commandPort**: Cổng lắng nghe tích hợp của Autodesk Maya để thực thi lệnh được gửi tới từ cổng kết nối localhost.

## 2. Tại sao phải chạy trong Sandbox 010A?

Vì AI Agent có khả năng thực thi các tác vụ sửa đổi sâu như tạo/xóa đối tượng, thay đổi vật liệu, điều chỉnh thuộc tính mesh hoặc camera, nên:
- **Nguyên tắc cốt lõi**: Agent chỉ được phép truy cập và thực thi trực tiếp trên tệp bản sao làm việc:
  `working/scene_agent_work.ma`
- Bản sao này nằm trong một thư mục phiên làm việc độc lập được tạo tự động bởi công cụ `scripts/python/maya_agent_sandbox.py`.
- Dữ liệu sản xuất gốc, file thiết kế nguồn của artist tuyệt đối không được phép chỉnh sửa trực tiếp.

---

## 3. Điều kiện chuẩn bị (Prerequisites)

Để thiết lập môi trường hoạt động, cần chuẩn bị:
1. **Antigravity**: Đã cài đặt và sẵn sàng hoạt động trong môi trường làm việc của bạn.
2. **Autodesk Maya**: Đã được cài đặt (ví dụ: Maya 2024).
3. **Python**: Sẵn có phiên bản Python 3.11+ trên máy trạm.
4. **External Maya MCP Server**: Chọn một server MCP hỗ trợ Maya riêng biệt. Server này **không được cài đặt hoặc lưu (vendor)** trực tiếp trong repository này.
5. **Phiên Sandbox 010A**: Đã chạy script để sinh ra thư mục làm việc cách ly bên ngoài repo (ví dụ: trong thư mục `D:\TuPhuongVoLo_AgentBackups\`).

---

## 4. Quy trình vận hành an toàn (10 bước)

1. **Sinh Scene gốc**: Thực hiện quy trình build scene tự động từ ứng dụng chính (Illustrator SVG → Maya blockout).
2. **Tạo Sandbox**: Chạy script sandbox để chụp ảnh trạng thái ban đầu và tạo bản sao làm việc:
   `python scripts/python/maya_agent_sandbox.py --maya-scene outputs/maya/scene.ma --room phong_kho --backup-root D:\TuPhuongVoLo_AgentBackups`
3. **Mở đúng file**: Khởi động Maya và **chỉ mở duy nhất** file bản sao: `working/scene_agent_work.ma` bên trong thư mục sandbox.
4. **Kích hoạt commandPort**: Trong Maya, chạy script `scripts/maya/enable_maya_mcp_command_port.py` từ Script Editor để mở cổng lắng nghe trên localhost (`127.0.0.1:50007`).
5. **Khởi chạy MCP Server**: Bật tiến trình Maya MCP Server bên ngoài repo.
6. **Cấu hình Antigravity**: Thiết lập file cấu hình MCP của Antigravity trỏ đến script server ngoài dựa trên mẫu `docs/templates/antigravity_maya_mcp_config.example.json`.
7. **Khảo sát ban đầu**: Yêu cầu Agent thực hiện thao tác kiểm tra ban đầu (inspect) để liệt kê camera, layers, vật thể hiện có trong scene.
8. **Thực thi thay đổi**: Ra lệnh cho Agent thực hiện các thao tác sửa đổi hoặc tối ưu hóa trên scene làm việc.
9. **Lưu kết quả mới**: Chỉ đạo Agent lưu kết quả thành một file mới trong thư mục sandbox làm việc, ví dụ: `working/scene_agent_result_v001.ma`.
10. **Kiểm tra thủ công**: Người họa sĩ mở file kết quả mới để thẩm định chất lượng mesh/vật liệu trước khi đồng ý đưa thay đổi ngược trở lại dự án chính.

---

## 5. Hành vi bị CẤM (Forbidden Actions)

- ❌ **Không** mở hoặc sửa đổi trực tiếp các file thiết kế gốc `.ai` của Adobe Illustrator.
- ❌ **Không** sửa đổi các file .svg thô hoặc .svg đã làm sạch trong `drops/`, `assets/`, hay các thư mục test.
- ❌ **Không** ghi đè trực tiếp lên các file Maya `.ma` gốc trong thư mục `outputs/maya/`.
- ❌ **Không** cấp quyền đọc/ghi hệ thống file (filesystem MCP tool) mở rộng cho ổ đĩa hệ thống `C:\Users` hay `D:\` (chỉ giới hạn tối đa trong thư mục `working/` của sandbox).
- ❌ **Không** đưa secrets, API keys, file cấu hình `.env` vào không gian làm việc hoặc đẩy lên hệ thống kiểm soát phiên bản (git).
- ❌ **Không** commit các file `.ma`, `.png`, `.zip`, hay thư mục log/backup sinh ra từ sandbox vào git.

---

## 6. Danh sách kiểm tra an toàn (Safety Checklist)

### Trước khi kích hoạt Agent:
- [ ] `git status` ở trạng thái hoàn toàn sạch sẽ (clean), không chứa thay đổi chưa commit.
- [ ] Đã tạo phiên sandbox cách ly thành công (Phase 010A).
- [ ] Maya chỉ đang mở tệp `working/scene_agent_work.ma`.
- [ ] Không gian làm việc của Antigravity giới hạn ở thư mục dự án hoặc thư mục sandbox cụ thể.
- [ ] Quyền truy cập tệp tin (filesystem) của MCP (nếu có) được giới hạn trong thư mục `working/` của sandbox.
- [ ] Cổng kết nối `commandPort` của Maya chỉ mở trên địa chỉ nội bộ `127.0.0.1:50007`. Bắt buộc không được cấu hình mở cổng này cho toàn mạng (wildcard IP `0.0.0.0`), để tránh nguy cơ máy bị hacker bên ngoài dò quét cổng và chạy mã độc từ xa.
- [ ] Không lưu trữ secrets hoặc cấu hình chứa đường dẫn thực tế trong repo.

### Sau khi Agent kết thúc:
- [ ] Đã lưu scene đã chỉnh sửa thành một tệp tin mới (ví dụ: `scene_agent_result_v001.ma`).
- [ ] Đã thực hiện kiểm tra thủ công trực tiếp trong giao diện Maya.
- [ ] Đảm bảo dữ liệu snapshot gốc trong `original/` vẫn an toàn và không bị thay đổi.
- [ ] Tuyệt đối không commit tệp scene đã tạo ra (`.ma`), các tệp kết quả render (`.png`), hoặc file nén (`.zip`) vào repo.
- [ ] Tài liệu hóa/Báo cáo rõ ràng các thay đổi đã được họa sĩ phê duyệt thủ công.
