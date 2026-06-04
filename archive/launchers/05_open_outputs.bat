@echo off
chcp 65001 >nul
echo ============================================================
echo  TuPhuongVoLo-ArtPipeline — Mở thư mục kết quả
echo  (Open Outputs Folder)
echo ============================================================
echo.
echo Đang mở thư mục outputs/...
echo.

set "OUTPUTS_DIR=%~dp0..\outputs"

if exist "%OUTPUTS_DIR%" (
    explorer "%OUTPUTS_DIR%"
    echo ✅ Đã mở thư mục kết quả
) else (
    echo ❌ Thư mục outputs/ không tồn tại!
    echo    Chạy một trong các script trước để tạo kết quả.
)

echo.
pause
