@echo off
chcp 65001 >nul
setlocal EnableExtensions

pushd "%~dp0.."

set "REPORT=outputs\reports\batch_maya_report.json"

echo ============================================================
echo  TuPhuongVoLo-ArtPipeline - Batch Maya nhieu phong/SVG
echo ============================================================
echo.
echo Launcher nay chay DRY-RUN mac dinh de lap ke hoach an toan.
echo Dry-run khong chay Maya, khong cap nhat manifest, khong sua SVG nguon.
echo Bao cao JSON se nam tai: %REPORT%
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
            echo Loi: Hay keo-tha file .svg hoac mot thu muc chua SVG sach.
            echo Khong co file nguon nao bi xoa hoac sua.
            goto :end
        )
    )
)

python scripts\python\batch_maya_room.py %INPUT_MODE% "%INPUT_PATH%" --dry-run --json-report "%REPORT%"
set "EXIT_CODE=%ERRORLEVEL%"

echo.
echo Hoan tat dry-run. Hay mo bao cao JSON tai:
echo %CD%\%REPORT%
echo.
echo De tao Maya .ma that, developer co the chay script Python khong dung --dry-run
echo va truyen --maya-path neu can.

:end
popd
echo.
pause
exit /b %EXIT_CODE%
