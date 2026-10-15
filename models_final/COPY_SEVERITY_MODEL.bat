@echo off
REM Copies the severity (lesion segmentation) model from training\results into models_final\severity\
cd /d "%~dp0"
if not exist "severity" mkdir "severity"
set S=..\training\results\cdcnsa_severity_export
if exist "%S%\lesion_seg_unet_r34.ts" (
  copy /Y "%S%\lesion_seg_unet_r34.ts" "severity\lesion_seg_unet_r34.ts" >nul && echo OK  severity\lesion_seg_unet_r34.ts
) else (
  echo MISSING: %S%\lesion_seg_unet_r34.ts
)
copy /Y "%S%\severity_config.json" "severity\severity_config.json" >nul && echo OK  severity\severity_config.json
echo.
echo Now test it:  python test_severity.py "path\to\a\leaf_photo.jpg" tomato "Early Blight"
pause
