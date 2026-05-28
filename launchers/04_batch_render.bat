@echo off
chcp 65001 >nul
echo ============================================================
echo  TuPhuongVoLo-ArtPipeline — Render hàng loạt
echo  (Batch Render)
echo ============================================================
echo.
echo ⚠️  PLACEHOLDER: Chưa triển khai (not implemented yet)
echo.
echo Script này sẽ:
echo   1. Quét tất cả file SVG sạch trong assets/2d/svg_clean/
echo   2. Phát hiện tất cả các phòng
echo   3. Render từng phòng thành ảnh PNG isometric
echo   4. Lưu kết quả vào outputs/preview/
echo.
echo TODO: blender --background --python scripts/blender/batch_render_rooms.py -- --input assets/2d/svg_clean/
echo.
echo Xem: specs/004-batch-isometric-render/spec.md
echo ============================================================
pause
