@echo off
chcp 65001 >nul
setlocal

pushd "%~dp0.."

set "REPORT=outputs\reports\batch_isometric_report.json"

echo ============================================================
echo  TuPhuongVoLo-ArtPipeline - Batch render nhiều phòng/SVG
echo ============================================================
echo.
echo Launcher này chạy DRY-RUN mặc định để lập kế hoạch an toàn.
echo Nếu máy chưa cài Blender, dry-run vẫn chạy được và không sửa file nguồn.
echo Báo cáo JSON sẽ nằm tại: %REPORT%
echo.

if "%~1"=="" (
    set "INPUT_MODE=--input-dir"
    set "INPUT_PATH=assets\2d\svg_clean"
) else (
    if exist "%~1\" (
        set "INPUT_MODE=--input-dir"
        set "INPUT_PATH=%~1"
    ) else (
        if /I "%~x1"==".svg" (
            set "INPUT_MODE=--input-file"
            set "INPUT_PATH=%~1"
        ) else (
            echo Lỗi: Hãy kéo thả file .svg hoặc một thư mục chứa SVG sạch.
            echo Không có file nguồn nào bị xóa hoặc sửa.
            goto :end
        )
    )
)

python scripts\python\batch_isometric_render.py %INPUT_MODE% "%INPUT_PATH%" --dry-run --json-report "%REPORT%"

echo.
echo Hoàn tất dry-run. Hãy mở báo cáo JSON tại:
echo %CD%\%REPORT%
echo.
echo Để render thật khi Blender đã cài đặt, developer có thể chạy script Python
echo không dùng --dry-run và truyền --blender-path nếu cần.

:end
popd
echo.
pause
