@echo off
chcp 65001 >nul
setlocal EnableExtensions

pushd "%~dp0.."
set "EXIT_CODE=0"

echo ============================================================
echo  TuPhuongVoLo-ArtPipeline - Dung 1 phong Maya tu SVG sach
echo ============================================================
echo.
echo Launcher nay giup hoa si lap ke hoach hoac tao file Maya .ma.
echo Mac dinh nen chay DRY-RUN truoc: khong chay Maya, khong ghi manifest,
echo khong sua file .ai/.svg goc, va chi in cac duong dan output du kien.
echo.

set "DEFAULT_SVG="
for /f "usebackq delims=" %%F in (`powershell -NoProfile -Command "$roots=@('assets\2d\svg_clean','drops'); Get-ChildItem -Path $roots -Filter '*.svg' -File -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 1 -ExpandProperty FullName"`) do set "DEFAULT_SVG=%%F"

if not "%~1"=="" (
    set "DEFAULT_SVG=%~1"
)

if defined DEFAULT_SVG (
    echo SVG mac dinh:
    echo   "%DEFAULT_SVG%"
    echo.
    set /p "INPUT_PATH=Nhap duong dan SVG sach, hoac Enter de dung mac dinh: "
) else (
    set /p "INPUT_PATH=Nhap duong dan file SVG sach: "
)
if "%INPUT_PATH%"==" " set "INPUT_PATH="
if not defined INPUT_PATH set "INPUT_PATH=%DEFAULT_SVG%"

if not defined INPUT_PATH (
    echo.
    echo Loi: Chua co file SVG. Hay dat SVG vao assets\2d\svg_clean\ hoac drops\.
    set "EXIT_CODE=1"
    goto :end
)

if not exist "%INPUT_PATH%" (
    echo.
    echo Loi: Khong tim thay file SVG:
    echo   "%INPUT_PATH%"
    set "EXIT_CODE=1"
    goto :end
)

if /I not "%INPUT_PATH:~-4%"==".svg" (
    echo.
    echo Loi: Input phai la file .svg sach.
    echo Pipeline khong xoa va khong sua file nguon.
    set "EXIT_CODE=1"
    goto :end
)

set /p "ROOM_NAME=Nhap ten phong/layer [phong_kho]: "
if "%ROOM_NAME%"==" " set "ROOM_NAME="
if not defined ROOM_NAME set "ROOM_NAME=phong_kho"

set /p "DRY_CHOICE=Chay dry-run truoc? [Y/n]: "
if "%DRY_CHOICE%"==" " set "DRY_CHOICE="
set "DRY_RUN_ARG=--dry-run"
if /I "%DRY_CHOICE%"=="n" set "DRY_RUN_ARG="
if /I "%DRY_CHOICE%"=="no" set "DRY_RUN_ARG="

set /p "RENDER_CHOICE=Lap ke hoach/render PNG preview? [y/N]: "
if "%RENDER_CHOICE%"==" " set "RENDER_CHOICE="
set "RENDER_ARG="
if /I "%RENDER_CHOICE%"=="y" set "RENDER_ARG=--render-preview"
if /I "%RENDER_CHOICE%"=="yes" set "RENDER_ARG=--render-preview"

set "MAYAPY_PATH="
if not defined DRY_RUN_ARG (
    echo.
    echo De trong mayapy path de dung config\pipeline.yaml hoac PATH.
    echo Vi du: C:\Program Files\Autodesk\Maya2024\bin\mayapy.exe
    set /p "MAYAPY_PATH=Duong dan mayapy.exe tuy chon: "
)

echo.
echo Lenh se chay:
if defined MAYAPY_PATH (
    echo python scripts\python\build_maya_room.py --input "%INPUT_PATH%" --room "%ROOM_NAME%" --style line_art_green_floor %DRY_RUN_ARG% %RENDER_ARG% --maya-path "%MAYAPY_PATH%"
    echo.
    python scripts\python\build_maya_room.py --input "%INPUT_PATH%" --room "%ROOM_NAME%" --style line_art_green_floor %DRY_RUN_ARG% %RENDER_ARG% --maya-path "%MAYAPY_PATH%"
) else (
    echo python scripts\python\build_maya_room.py --input "%INPUT_PATH%" --room "%ROOM_NAME%" --style line_art_green_floor %DRY_RUN_ARG% %RENDER_ARG%
    echo.
    python scripts\python\build_maya_room.py --input "%INPUT_PATH%" --room "%ROOM_NAME%" --style line_art_green_floor %DRY_RUN_ARG% %RENDER_ARG%
)
set "EXIT_CODE=%ERRORLEVEL%"

echo.
if "%EXIT_CODE%"=="0" (
    if defined DRY_RUN_ARG (
        echo Hoan tat dry-run. Hay kiem tra ten phong, prop marker, duong dan .ma/.png du kien.
    ) else (
        echo Hoan tat job Maya. Neu thanh cong, hay kiem tra outputs\maya\ va outputs\preview\.
    )
) else (
    echo Job bi loi. Hay doc thong bao ben tren; file .ai/.svg goc van duoc giu nguyen.
)

:end
echo.
echo Nhan phim bat ky de dong cua so...
pause >nul
popd
exit /b %EXIT_CODE%
