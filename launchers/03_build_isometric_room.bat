@echo off
chcp 65001 >nul
echo ============================================================
echo  TuPhuongVoLo-ArtPipeline — Tạo phòng isometric
echo  (Build Isometric Room)
echo ============================================================
echo.
echo ⚠️  PLACEHOLDER: Chưa triển khai (not implemented yet)
echo.
echo Script này sẽ:
echo   1. Đọc file SVG sạch
echo   2. Phát hiện các phòng trong bản vẽ
echo   3. Tạo cảnh 3D isometric trong Blender
echo   4. Render ảnh preview PNG
echo   5. Lưu file .blend để chỉnh sửa
echo.
echo TODO: blender --background --python scripts/blender/build_isometric_room.py -- --input assets/2d/svg_clean/floorplan.svg
echo.
echo Xem: specs/001-floorplan-to-isometric-room/spec.md
echo ============================================================
pause
