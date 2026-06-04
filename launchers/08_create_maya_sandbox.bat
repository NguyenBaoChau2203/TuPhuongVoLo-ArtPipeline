@echo off
chcp 65001 >nul
setlocal EnableExtensions

pushd "%~dp0.."
set "EXIT_CODE=0"

echo ============================================================
echo  TuPhuongVoLo-ArtPipeline - Tao Maya sandbox an toan
echo ============================================================
echo.
echo Launcher nay copy file .ma sang sandbox rieng de Codex/agent polish.
echo Khong sua file outputs\maya goc va tao restore_agent_backup.ps1 de rollback.
echo.

where python >nul 2>nul
if errorlevel 1 (
    echo Loi: Khong tim thay Python trong PATH.
    set "EXIT_CODE=1"
    goto :end
)

set "DEFAULT_SCENE="
for /f "usebackq delims=" %%F in (`powershell -NoProfile -Command "Get-ChildItem -Path 'outputs\maya' -Filter '*.ma' -File -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending, Name -Descending | Select-Object -First 1 -ExpandProperty FullName"`) do set "DEFAULT_SCENE=%%F"

if not "%~1"=="" (
    set "DEFAULT_SCENE=%~1"
)

if defined DEFAULT_SCENE (
    echo Maya scene mac dinh:
    echo   "%DEFAULT_SCENE%"
    echo.
    set /p "MAYA_SCENE=Nhap duong dan .ma, hoac Enter de dung mac dinh: "
) else (
    set /p "MAYA_SCENE=Nhap duong dan file Maya .ma: "
)
if "%MAYA_SCENE%"==" " set "MAYA_SCENE="
if not defined MAYA_SCENE set "MAYA_SCENE=%DEFAULT_SCENE%"

if not defined MAYA_SCENE (
    echo.
    echo Loi: Chua co file .ma. Hay chay app tao Maya truoc.
    set "EXIT_CODE=1"
    goto :end
)

if not exist "%MAYA_SCENE%" (
    echo.
    echo Loi: Khong tim thay file .ma:
    echo   "%MAYA_SCENE%"
    set "EXIT_CODE=1"
    goto :end
)

if /I not "%MAYA_SCENE:~-3%"==".ma" (
    echo.
    echo Loi: Input phai la file .ma.
    set "EXIT_CODE=1"
    goto :end
)

set /p "ROOM_NAME=Nhap ten phong/layer [phong_kho]: "
if "%ROOM_NAME%"==" " set "ROOM_NAME="
if not defined ROOM_NAME set "ROOM_NAME=phong_kho"

set "DEFAULT_GEOMETRY="
for /f "usebackq delims=" %%F in (`powershell -NoProfile -Command "Get-ChildItem -Path 'outputs\tmp' -Filter '*.json' -File -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending, Name -Descending | Select-Object -First 1 -ExpandProperty FullName"`) do set "DEFAULT_GEOMETRY=%%F"

if defined DEFAULT_GEOMETRY (
    echo.
    echo Geometry JSON mac dinh:
    echo   "%DEFAULT_GEOMETRY%"
    set /p "GEOMETRY_JSON=Nhap geometry JSON, Enter de dung mac dinh, hoac nhap NONE de bo qua: "
) else (
    echo.
    set /p "GEOMETRY_JSON=Nhap geometry JSON tuy chon, hoac Enter de bo qua: "
)
if "%GEOMETRY_JSON%"==" " set "GEOMETRY_JSON="
if not defined GEOMETRY_JSON set "GEOMETRY_JSON=%DEFAULT_GEOMETRY%"
if /I "%GEOMETRY_JSON%"=="NONE" set "GEOMETRY_JSON="
set "GEOMETRY_ARG="
if defined GEOMETRY_JSON (
    if not exist "%GEOMETRY_JSON%" (
        echo.
        echo Loi: Khong tim thay geometry JSON:
        echo   "%GEOMETRY_JSON%"
        set "EXIT_CODE=1"
        goto :end
    )
    set "GEOMETRY_ARG=--geometry-json ^"%GEOMETRY_JSON%^""
)

set "DEFAULT_SVG="
for /f "usebackq delims=" %%F in (`powershell -NoProfile -Command "$roots=@('drops','assets\2d\svg_clean'); Get-ChildItem -Path $roots -Filter '*.svg' -File -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending, Name -Descending | Select-Object -First 1 -ExpandProperty FullName"`) do set "DEFAULT_SVG=%%F"

if defined DEFAULT_SVG (
    echo.
    echo Source SVG snapshot mac dinh:
    echo   "%DEFAULT_SVG%"
    set /p "SOURCE_SVG=Nhap source SVG, Enter de dung mac dinh, hoac nhap NONE de bo qua: "
) else (
    echo.
    set /p "SOURCE_SVG=Nhap source SVG tuy chon, hoac Enter de bo qua: "
)
if "%SOURCE_SVG%"==" " set "SOURCE_SVG="
if not defined SOURCE_SVG set "SOURCE_SVG=%DEFAULT_SVG%"
if /I "%SOURCE_SVG%"=="NONE" set "SOURCE_SVG="
set "SOURCE_ARG="
if defined SOURCE_SVG (
    if not exist "%SOURCE_SVG%" (
        echo.
        echo Loi: Khong tim thay source SVG:
        echo   "%SOURCE_SVG%"
        set "EXIT_CODE=1"
        goto :end
    )
    set "SOURCE_ARG=--source-svg ^"%SOURCE_SVG%^""
)

set "BACKUP_ROOT=D:\TuPhuongVoLo_AgentBackups"
if not exist D:\ set "BACKUP_ROOT=%USERPROFILE%\TuPhuongVoLo_AgentBackups"
set /p "BACKUP_INPUT=Thu muc backup sandbox [%BACKUP_ROOT%]: "
if "%BACKUP_INPUT%"==" " set "BACKUP_INPUT="
if defined BACKUP_INPUT set "BACKUP_ROOT=%BACKUP_INPUT%"

echo.
echo Lenh se chay:
echo python scripts\python\maya_agent_sandbox.py --maya-scene "%MAYA_SCENE%" --room "%ROOM_NAME%" --backup-root "%BACKUP_ROOT%" %GEOMETRY_ARG% %SOURCE_ARG%
echo.
python scripts\python\maya_agent_sandbox.py --maya-scene "%MAYA_SCENE%" --room "%ROOM_NAME%" --backup-root "%BACKUP_ROOT%" %GEOMETRY_ARG% %SOURCE_ARG%
set "EXIT_CODE=%ERRORLEVEL%"

echo.
if "%EXIT_CODE%"=="0" (
    echo Da tao Maya sandbox. Hay mo file working\scene_agent_work.ma trong thu muc backup vua in ra.
) else (
    echo Tao sandbox bi loi. Hay doc thong bao ben tren; file .ma goc van duoc giu nguyen.
)

:end
echo.
echo Nhan phim bat ky de dong cua so...
pause >nul
popd
exit /b %EXIT_CODE%
