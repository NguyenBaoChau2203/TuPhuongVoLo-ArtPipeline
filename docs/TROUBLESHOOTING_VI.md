# 🔧 Xử lý sự cố — TuPhuongVoLo-ArtPipeline

## Lỗi thường gặp

### ❌ "Python chưa được cài đặt"

**Nguyên nhân**: Python chưa cài hoặc chưa thêm vào PATH.

**Cách sửa**:
1. Tải Python từ [python.org](https://python.org)
2. Khi cài, **tick ✅ "Add Python to PATH"**
3. Khởi động lại máy tính
4. Thử lại

---

### ❌ "Blender không tìm thấy"

**Nguyên nhân**: Blender chưa cài hoặc chưa thêm vào PATH.

**Cách sửa**:
1. Tải Blender từ [blender.org](https://blender.org)
2. Cài đặt bình thường
3. Hoặc: mở file `config/pipeline.yaml` và sửa dòng `blender:` thành đường dẫn đầy đủ, ví dụ:
   ```
   blender: "C:/Program Files/Blender Foundation/Blender 4.0/blender.exe"
   ```

---

### ❌ "Không tìm thấy file SVG"

**Nguyên nhân**: Bạn chưa bỏ file SVG vào đúng thư mục.

**Cách sửa**:
1. Bỏ file SVG vào thư mục `drops/`
2. Hoặc kiểm tra đường dẫn file trong thông báo lỗi

---

### ❌ "SVG không hợp lệ"

**Nguyên nhân**: File SVG không đạt yêu cầu chất lượng.

**Cách sửa**:
1. Đảm bảo file SVG được xuất từ Illustrator (không phải screenshot)
2. Đảm bảo các layer có tên (không phải "Layer 1", "Layer 2")
3. Chạy `02_clean_svg.bat` trước khi dùng các script khác

---

### ❌ Cửa sổ đóng quá nhanh

**Nguyên nhân**: Script chạy xong và đóng ngay.

**Cách sửa**: Các launcher đã có `pause` ở cuối. Nếu vẫn đóng nhanh, mở Command Prompt và chạy file .bat bằng tay:
1. Nhấn `Win + R`, gõ `cmd`, Enter
2. Gõ: `cd D:\TuPhuongVoLo-ArtPipeline`
3. Gõ: `launchers\02_clean_svg.bat`

---

### ❌ Render bị đen / trống

**Nguyên nhân**: Camera không nhìn thấy phòng, hoặc chưa có ánh sáng.

**Cách sửa**:
1. Mở file `.blend` trong Blender
2. Kiểm tra camera có hướng về phòng không
3. Kiểm tra có đèn trong scene không
4. Thử render thủ công trong Blender

---

### ❌ Lỗi tên file tiếng Việt

**Nguyên nhân**: Đường dẫn có ký tự đặc biệt tiếng Việt.

**Cách sửa**:
1. Đặt tên file/thư mục bằng tiếng Anh không dấu
2. Tránh khoảng trắng trong tên file
3. Ví dụ tốt: `kho_storage.svg`, không phải `Kho (lưu trữ).svg`

---

## Vẫn gặp vấn đề?

1. Đọc thông báo lỗi trên màn hình — nó thường gợi ý cách sửa
2. Kiểm tra file log (nếu có) trong thư mục dự án
3. Hỏi developer của dự án
