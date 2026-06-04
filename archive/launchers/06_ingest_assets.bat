@echo off
chcp 65001 >nul
setlocal

cd /d "%~dp0\.."

set "INPUT_PATH=%~1"
if "%INPUT_PATH%"=="" set "INPUT_PATH=drops"

echo ============================================================
echo  TuPhuongVoLo-ArtPipeline - Ingest asset
echo ============================================================
echo.
echo Hãy bỏ file vào thư mục drops\ rồi chạy launcher này.
echo Mặc định launcher sẽ COPY file, không xóa file gốc.
echo.
echo Input đang dùng: %INPUT_PATH%
echo Manifest: outputs\manifest\asset_manifest.json
echo.

python scripts\python\asset_agent.py ingest --input "%INPUT_PATH%" --stage raw --variant main
if errorlevel 1 (
    echo.
    echo Lỗi: Không ingest được một hoặc nhiều file.
    echo File gốc trong drops\ vẫn được giữ nguyên.
    echo Gợi ý: kiểm tra định dạng file. Hỗ trợ: .svg .png .jpg .jpeg .webp
    echo.
    pause
    exit /b 1
)

echo.
echo Hoàn tất. File đã được copy vào thư mục asset/output đúng quy ước.
echo Manifest đã được tạo hoặc cập nhật tại outputs\manifest\asset_manifest.json
echo File gốc trong drops\ không bị xóa.
echo.
pause
