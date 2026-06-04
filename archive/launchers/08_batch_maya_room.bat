@echo off
chcp 65001 >nul
setlocal EnableExtensions

pushd "%~dp0.."
set "EXIT_CODE=0"
set "DEFAULT_INPUT=assets\2d\svg_clean"
set "DEFAULT_REPORT=outputs\reports\batch_maya_report.json"

echo ============================================================
echo  TuPhuongVoLo-ArtPipeline - Batch Maya nhieu SVG/phong
echo ============================================================
echo.
echo Launcher nay tao report batch cho nhieu file SVG hoac nhieu phong.
echo Input-dir = thu muc chua nhieu SVG sach. Input-file = mot file SVG sach.
echo Mac dinh chay DRY-RUN/report: khong chay Maya, khong ghi manifest,
echo khong sua file nguon, va khong xoa bat ky file nao.
echo.

if not "%~1"=="" set "DEFAULT_INPUT=%~1"

echo Input mac dinh:
echo   "%DEFAULT_INPUT%"
echo.
set /p "INPUT_PATH=Nhap file .svg hoac thu muc SVG, hoac Enter de dung mac dinh: "
if "%INPUT_PATH%"==" " set "INPUT_PATH="
if not defined INPUT_PATH set "INPUT_PATH=%DEFAULT_INPUT%"

if not exist "%INPUT_PATH%" (
    echo.
    echo Loi: Khong tim thay input:
    echo   "%INPUT_PATH%"
    set "EXIT_CODE=1"
    goto :end
)

set "INPUT_MODE="
if exist "%INPUT_PATH%\" (
    set "INPUT_MODE=--input-dir"
) else (
    if /I "%INPUT_PATH:~-4%"==".svg" (
        set "INPUT_MODE=--input-file"
    )
)

if not defined INPUT_MODE (
    echo.
    echo Loi: Input phai la thu muc hoac file .svg.
    echo Pipeline khong xoa va khong sua file nguon.
    set "EXIT_CODE=1"
    goto :end
)

set /p "ALL_ROOMS_CHOICE=Lap job cho tat ca phong trong SVG? [Y/n]: "
if "%ALL_ROOMS_CHOICE%"==" " set "ALL_ROOMS_CHOICE="
set "ALL_ROOMS_ARG=--all-rooms"
if /I "%ALL_ROOMS_CHOICE%"=="n" set "ALL_ROOMS_ARG="
if /I "%ALL_ROOMS_CHOICE%"=="no" set "ALL_ROOMS_ARG="

set /p "DRY_CHOICE=Chi chay dry-run/report truoc? [Y/n]: "
if "%DRY_CHOICE%"==" " set "DRY_CHOICE="
set "DRY_RUN_ARG=--dry-run"
if /I "%DRY_CHOICE%"=="n" set "DRY_RUN_ARG="
if /I "%DRY_CHOICE%"=="no" set "DRY_RUN_ARG="

set /p "RENDER_CHOICE=Lap ke hoach/render PNG preview cho moi job? [y/N]: "
if "%RENDER_CHOICE%"==" " set "RENDER_CHOICE="
set "RENDER_ARG="
if /I "%RENDER_CHOICE%"=="y" set "RENDER_ARG=--render-preview"
if /I "%RENDER_CHOICE%"=="yes" set "RENDER_ARG=--render-preview"

echo.
echo Report JSON mac dinh:
echo   "%DEFAULT_REPORT%"
set /p "REPORT_PATH=Nhap duong dan report JSON, hoac Enter de dung mac dinh: "
if "%REPORT_PATH%"==" " set "REPORT_PATH="
if not defined REPORT_PATH set "REPORT_PATH=%DEFAULT_REPORT%"
for %%R in ("%REPORT_PATH%") do set "REPORT_ABS=%%~fR"

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
    echo python scripts\python\batch_maya_room.py %INPUT_MODE% "%INPUT_PATH%" %ALL_ROOMS_ARG% %DRY_RUN_ARG% %RENDER_ARG% --json-report "%REPORT_PATH%" --maya-path "%MAYAPY_PATH%"
    echo.
    python scripts\python\batch_maya_room.py %INPUT_MODE% "%INPUT_PATH%" %ALL_ROOMS_ARG% %DRY_RUN_ARG% %RENDER_ARG% --json-report "%REPORT_PATH%" --maya-path "%MAYAPY_PATH%"
) else (
    echo python scripts\python\batch_maya_room.py %INPUT_MODE% "%INPUT_PATH%" %ALL_ROOMS_ARG% %DRY_RUN_ARG% %RENDER_ARG% --json-report "%REPORT_PATH%"
    echo.
    python scripts\python\batch_maya_room.py %INPUT_MODE% "%INPUT_PATH%" %ALL_ROOMS_ARG% %DRY_RUN_ARG% %RENDER_ARG% --json-report "%REPORT_PATH%"
)
set "EXIT_CODE=%ERRORLEVEL%"

echo.
echo Bao cao JSON:
echo   "%REPORT_ABS%"
echo.
if "%EXIT_CODE%"=="0" (
    if defined DRY_RUN_ARG (
        echo Hoan tat dry-run batch. Hay mo report de kiem tra job, phong, prop marker, output du kien.
    ) else (
        echo Hoan tat batch Maya. Hay kiem tra outputs\maya\, outputs\preview\, va report JSON.
    )
) else (
    echo Batch bi loi. Hay doc thong bao ben tren; file nguon van duoc giu nguyen.
)

:end
echo.
echo Nhan phim bat ky de dong cua so...
pause >nul
popd
exit /b %EXIT_CODE%
