@echo off
REM Copies the previous peas disease model into models_final\peas\disease\ (the app is already pointed there).
cd /d "%~dp0"
if not exist "peas\disease" mkdir "peas\disease"
set "SRC=D:\hacathon\website deployment\CDCNSA\models\peas\disease\Peas_Disease_ResNet50_FROZEN.pth"
if exist "%SRC%" (
  copy /Y "%SRC%" "peas\disease\Peas_Disease_ResNet50_FROZEN.pth" >nul && echo OK  peas\disease\Peas_Disease_ResNet50_FROZEN.pth
) else (
  echo MISSING: %SRC%
)
echo Restart the server so it picks up the peas model.
pause
