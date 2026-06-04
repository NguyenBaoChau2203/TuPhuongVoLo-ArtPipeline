@echo off
chcp 65001 >nul
setlocal

cd /d "%~dp0\.."

set "INPUT_PATH=%~1"
if "%INPUT_PATH%"=="" set "INPUT_PATH=drops"
set "OUTPUT_PATH=assets\2d\svg_clean"

echo ============================================================
echo  TuPhuongVoLo-ArtPipeline - Làm sạch SVG
echo ============================================================
echo.
echo Hãy đặt file SVG vào một trong hai nơi:
echo   - drops\
echo   - assets\2d\svg_raw\
echo.
echo Input đang dùng: %INPUT_PATH%
echo Output sẽ ở:    %OUTPUT_PATH%
echo.

python scripts\python\clean_svg_paths.py --input "%INPUT_PATH%" --output "%OUTPUT_PATH%" --verbose
if errorlevel 1 (
    echo.
    echo Lỗi: Không làm sạch được SVG. File gốc vẫn được giữ nguyên.
    echo Gợi ý: kiểm tra xem thư mục input có file .svg hay chưa.
    echo.
    pause
    exit /b 1
)

echo.
echo Đang kiểm tra các SVG sạch vừa tạo / đang có trong thư mục output...
python scripts\python\validate_svg_contract.py --input "%OUTPUT_PATH%" --strict
if errorlevel 1 (
    echo.
    echo Cảnh báo: Có SVG chưa đạt kiểm tra. Hãy đọc dòng "Lỗi" ở trên.
    echo File gốc vẫn không bị thay đổi.
    echo.
    pause
    exit /b 1
)

echo.
echo Hoàn tất. Kết quả nằm trong: %OUTPUT_PATH%
echo File gốc trong drops\ hoặc assets\2d\svg_raw\ không bị xóa hoặc ghi đè.
echo.
pause
