@echo off
chcp 65001 >nul
setlocal EnableExtensions

cd /d "%~dp0.."

echo ============================================================
echo  TuPhuongVoLo-ArtPipeline - Tao phong isometric
echo ============================================================
echo.

if "%~1"=="" (
    echo Dang tim SVG sach moi nhat trong assets\2d\svg_clean ...
    for /f "usebackq delims=" %%F in (`powershell -NoProfile -Command "Get-ChildItem -Path 'assets\2d\svg_clean' -Filter '*.svg' -File -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 1 -ExpandProperty FullName"`) do set "INPUT_PATH=%%F"
) else (
    set "INPUT_PATH=%~1"
)

if not defined INPUT_PATH (
    echo Khong tim thay SVG sach nao.
    echo Hay chay launchers\02_clean_svg.bat truoc, hoac keo-tha file .svg sach vao launcher nay.
    echo.
    pause
    exit /b 1
)

echo File SVG input:
echo   "%INPUT_PATH%"
echo.

python scripts\python\build_isometric_room.py --input "%INPUT_PATH%" --style line_art_green_floor
set "EXIT_CODE=%ERRORLEVEL%"

echo.
if "%EXIT_CODE%"=="0" (
    echo Da tao output thanh cong.
    echo PNG preview nam trong: outputs\preview
    echo File Blender nam trong: outputs\blender
) else (
    echo Khong tao duoc phong isometric.
    echo Neu thong bao noi khong tim thay Blender, hay cai Blender 4.x hoac sua tool_paths.blender trong config\pipeline.yaml.
)

echo.
pause
exit /b %EXIT_CODE%
