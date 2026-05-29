@echo off
chcp 65001 >nul
setlocal EnableExtensions

cd /d "%~dp0.."

echo ============================================================
echo  TuPhuongVoLo-ArtPipeline - Tao phong Maya tu SVG sach
echo ============================================================
echo.
echo Launcher nay chay DRY-RUN mac dinh de lap ke hoach an toan.
echo Dry-run khong chay Maya, khong cap nhat manifest, khong sua SVG nguon.
echo Muon tao .ma that, hay cau hinh mayapy trong config\pipeline.yaml hoac nho developer chay voi --maya-path.
echo Output Maya se nam trong: outputs\maya
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

if /I not "%INPUT_PATH:~-4%"==".svg" (
    echo Loi: Hay keo-tha mot file .svg sach.
    echo Khong co file nguon nao bi xoa hoac sua.
    echo.
    pause
    exit /b 1
)

echo File SVG input:
echo   "%INPUT_PATH%"
echo.

python scripts\python\build_maya_room.py --input "%INPUT_PATH%" --style line_art_green_floor --dry-run
set "EXIT_CODE=%ERRORLEVEL%"

echo.
if "%EXIT_CODE%"=="0" (
    echo Da lap ke hoach Maya thanh cong.
    echo Day moi la dry-run. File .ma that can Maya/mayapy de tao.
) else (
    echo Khong lap duoc ke hoach Maya. Hay xem thong bao loi phia tren.
)

echo.
pause
exit /b %EXIT_CODE%
