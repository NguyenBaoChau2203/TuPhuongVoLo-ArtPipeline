@echo off
chcp 65001 >nul
setlocal EnableExtensions

pushd "%~dp0.."
set "EXIT_CODE=0"

echo ============================================================
echo  TuPhuongVoLo-ArtPipeline - Desktop app cho hoa si
echo ============================================================
echo.
echo App nay boc pipeline Maya da kiem chung. App khong sua file SVG goc,
echo khong xoa output, va khong thay the Autodesk Maya.
echo.

where python >nul 2>nul
if errorlevel 1 (
    echo Loi: Khong tim thay Python trong PATH.
    echo Hay cai Python 3.11+ hoac kich hoat moi truong ao truoc khi chay launcher.
    set "EXIT_CODE=1"
    goto :end
)

python scripts\python\artist_desktop_app.py
set "EXIT_CODE=%ERRORLEVEL%"

if not "%EXIT_CODE%"=="0" (
    echo.
    echo App khoi dong bi loi. Hay doc thong bao ben tren.
    goto :end
)

popd
exit /b 0

:end
echo.
echo Nhan phim bat ky de dong cua so...
pause >nul
popd
exit /b %EXIT_CODE%

