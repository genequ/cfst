@echo off
REM Cloudflare Speed Test with CFST Repository Upload
REM 运行CFST测试并将结果推送到genequ/cfst仓库

echo Starting Cloudflare Speed Test with CFST upload...
echo Date: %date% Time: %time%

REM Change to script directory
cd /d "%~dp0"

REM Run the Python scheduler with --run-once flag
python cfst_scheduler.py --schedule

if %errorlevel% equ 0 (
    echo.
    echo CFST test and upload completed successfully!
) else (
    echo.
    echo CFST test or upload failed with error code %errorlevel%
)

echo.
echo Date: %date% Time: %time%
pause
