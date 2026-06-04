@echo off
chcp 65001 >nul
setlocal EnableExtensions

pushd "%~dp0.."
set "EXIT_CODE=0"

echo ============================================================
echo  TuPhuongVoLo-ArtPipeline - Package desktop app dev-only
echo ============================================================
echo.
echo Launcher nay in lenh dong goi .exe bang PyInstaller.
echo PyInstaller la cong cu dev-only, khong phai dependency runtime cua artist pipeline.
echo File .exe/build/dist sinh ra chi la output local va khong duoc commit.
echo.

where python >nul 2>nul
if errorlevel 1 (
    echo Loi: Khong tim thay Python trong PATH.
    echo Hay cai Python 3.11+ hoac kich hoat moi truong ao truoc khi chay launcher.
    set "EXIT_CODE=1"
    goto :end
)

echo Dry-run truoc de kiem tra lenh package:
echo.
python scripts\python\package_artist_app.py --dry-run
set "EXIT_CODE=%ERRORLEVEL%"

if not "%EXIT_CODE%"=="0" (
    echo.
    echo Package dry-run bi loi. Hay doc thong bao ben tren.
    goto :end
)

echo.
echo De build that tren may dev da cai PyInstaller, chay:
echo python scripts\python\package_artist_app.py --build
echo.
echo Neu can xoa artifact package local truoc khi build:
echo python scripts\python\package_artist_app.py --clean-output --build

:end
echo.
echo Nhan phim bat ky de dong cua so...
pause >nul
popd
exit /b %EXIT_CODE%
