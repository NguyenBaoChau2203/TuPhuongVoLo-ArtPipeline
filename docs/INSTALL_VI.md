# 🛠️ Hướng dẫn cài đặt — TuPhuongVoLo-ArtPipeline

## Yêu cầu hệ thống

| Phần mềm | Phiên bản | Bắt buộc? | Tải về |
|-----------|-----------|-----------|--------|
| Windows | 10 hoặc 11 | ✅ Có | — |
| Python | 3.10 trở lên | ✅ Có | [python.org](https://python.org) |
| Adobe Illustrator | CC 2020+ | ✅ Có (để vẽ) | Đã cài sẵn |
| Blender | 4.x | ⚡ Cần cho render | [blender.org](https://blender.org) |
| Autodesk Maya | 2024+ | ❌ Tùy chọn | Nếu cần Maya |

---

## Bước 1: Cài đặt Python

1. Tải Python từ [python.org](https://www.python.org/downloads/)
2. **QUAN TRỌNG**: Tick ✅ "Add Python to PATH" khi cài đặt
3. Mở Command Prompt và kiểm tra:
   ```
   python --version
   ```
   Phải hiện "Python 3.10.x" hoặc cao hơn.

---

## Bước 2: Cài đặt Blender (nếu cần render)

1. Tải Blender từ [blender.org](https://www.blender.org/download/)
2. Cài đặt bình thường
3. Kiểm tra: mở Command Prompt, gõ `blender --version`

---

## Bước 3: Tải dự án

Nếu đã có thư mục dự án, bỏ qua bước này.

```
git clone <đường-dẫn-repo>
cd TuPhuongVoLo-ArtPipeline
```

---

## Bước 4: Chạy kiểm tra cài đặt

Nhấp đúp vào file:
```
launchers\01_install_tools.bat
```

Nó sẽ kiểm tra:
- ✅ Python đã cài chưa
- ✅ Blender đã cài chưa (tùy chọn)

---

## Bước 5: Xong!

Bạn đã sẵn sàng sử dụng pipeline.
Xem tiếp: [Hướng dẫn sử dụng](HOW_TO_USE_FOR_ARTIST_VI.md)

---

## Gặp vấn đề?

Xem: [Xử lý sự cố](TROUBLESHOOTING_VI.md)
