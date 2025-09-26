@echo off
echo Starting automatic result.csv commit to GitHub...
echo.

REM Run the CFST automation script
python cfst_scheduler.py --run-once

echo.
echo Automation completed. Check the output above for details.
pause
