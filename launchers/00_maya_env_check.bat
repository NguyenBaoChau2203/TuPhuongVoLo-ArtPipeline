@echo off
chcp 65001 >nul
setlocal EnableExtensions

pushd "%~dp0.."

echo ============================================================
echo  TuPhuongVoLo-ArtPipeline - Kiem tra moi truong Maya
echo ============================================================
echo.
echo File nay chi kiem tra moi truong. Khong tao output, khong sua file nguon,
echo khong xoa file, va khong chay git.
echo.

echo Repo root:
echo   %CD%
echo.

echo [1/4] Kiem tra Python...
where python >nul 2>nul
if errorlevel 1 (
    echo   Loi: Khong tim thay python trong PATH.
    echo   Hay cai Python 3.11+ hoac kich hoat virtual environment.
) else (
    for /f "delims=" %%V in ('python --version 2^>^&1') do echo   %%V
)
echo.

echo [2/4] Kiem tra PyYAML...
python -c "import yaml; print('  PyYAML OK')" 2>nul
if errorlevel 1 (
    echo   Loi: No module named yaml.
    echo   Cach xu ly: kich hoat venv hoac chay pip install -r requirements.txt.
)
echo.

echo [3/4] Kiem tra mayapy trong PATH...
where mayapy >nul 2>nul
if errorlevel 1 (
    echo   Chua tim thay mayapy trong PATH.
) else (
    for /f "delims=" %%M in ('where mayapy') do echo   %%M
)
echo.

echo [4/4] Goi y duong dan mayapy pho bien...
if exist "C:\Program Files\Autodesk\Maya2025\bin\mayapy.exe" echo   C:\Program Files\Autodesk\Maya2025\bin\mayapy.exe
if exist "C:\Program Files\Autodesk\Maya2024\bin\mayapy.exe" echo   C:\Program Files\Autodesk\Maya2024\bin\mayapy.exe
if exist "C:\Program Files\Autodesk\Maya2023\bin\mayapy.exe" echo   C:\Program Files\Autodesk\Maya2023\bin\mayapy.exe
echo   Neu mayapy khong nam trong PATH, co the dien duong dan nay vao launcher
echo   hoac cap nhat tool_paths.mayapy trong config\pipeline.yaml.
echo.

echo Hoan tat kiem tra moi truong.
echo Nhan phim bat ky de dong cua so...
pause >nul
popd
exit /b 0
