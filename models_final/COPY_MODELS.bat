@echo off
REM Copies the verified model files from training\results into models_final\<crop>\disease\
REM (registry_snippet.json and final_report.json are already there). Rice: add it yourself.
setlocal
cd /d "%~dp0"
set R=..\training\results
call :one corn     "cdcnsa_corn_export"        corn_disease_densenet121_srcsplit.pt
call :one cotton   "cdcnsa_cotton_export (2)"  cotton_disease_resnet50_srcsplit.pt
call :one apple    "cdcnsa_apple_export (2)"   apple_disease_dinov2_srcsplit.ts
call :one cucumber "cdcnsa_cucumber_export"    cucumber_disease_resnet50_srcsplit.pt
call :one eggplant "cdcnsa_eggplant_export"    eggplant_disease_efficientnet_b0_srcsplit.pt
call :one grape    "cdcnsa_grape_export (1)"   grape_disease_dinov2_srcsplit.ts
call :one mango    "cdcnsa_mango_export"       mango_disease_dinov2_srcsplit.ts
call :one tomato   "cdcnsa_tomato_export"      tomato_disease_dinov2_srcsplit.ts
echo.
echo Fixing cucumber confidence calibration ...
python fix_cucumber_temperature.py
echo.
echo ===== models_final now contains: =====
dir /s /b *.pt *.ts
echo.
echo Done. (Rice: copy its model + registry_snippet.json + final_report.json into rice\disease\ yourself.)
pause
exit /b

:one
if not exist "%~1\disease" mkdir "%~1\disease"
if exist "%R%\%~2\%~3" (
  copy /Y "%R%\%~2\%~3" "%~1\disease\%~3" >nul && echo OK      %~1  ^<-  %~3
) else (
  echo MISSING %~1  - not found: %R%\%~2\%~3
)
exit /b
