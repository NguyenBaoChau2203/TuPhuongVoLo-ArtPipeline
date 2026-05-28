@echo off
chcp 65001 >nul
echo ============================================================
echo  TuPhuongVoLo-ArtPipeline — Cài đặt công cụ
echo  (Install Tools)
echo ============================================================
echo.
echo Bước 1: Kiểm tra Python...
python --version 2>nul
if errorlevel 1 (
    echo ❌ Python chưa được cài đặt!
    echo    Vui lòng cài Python 3.10+ từ https://python.org
    echo.
    pause
    exit /b 1
)
echo ✅ Python đã cài đặt
echo.

echo Bước 2: Tạo môi trường ảo (virtual environment)...
echo ⚠️  PLACEHOLDER: Chưa triển khai
echo    TODO: python -m venv .venv
echo.

echo Bước 3: Cài đặt thư viện Python...
echo ⚠️  PLACEHOLDER: Chưa triển khai
echo    TODO: pip install -r requirements.txt
echo.

echo Bước 4: Kiểm tra Blender (tùy chọn)...
blender --version 2>nul
if errorlevel 1 (
    echo ⚠️  Blender chưa được cài đặt (không bắt buộc cho bước đầu)
) else (
    echo ✅ Blender đã cài đặt
)
echo.

echo ============================================================
echo  Hoàn tất kiểm tra. Xem kết quả ở trên.
echo ============================================================
pause
