@echo off
REM GitHub上传批处理脚本
REM 用于手动触发result.csv文件的上传到GitHub

echo Starting GitHub upload for CFST results...
echo Date: %date% Time: %time%

REM Change to script directory
cd /d "%~dp0"

REM Run the Python upload script
python upload_to_github.py

if %errorlevel% equ 0 (
    echo.
    echo Upload completed successfully!
) else (
    echo.
    echo Upload failed with error code %errorlevel%
)

echo.
echo Date: %date% Time: %time%
pause
