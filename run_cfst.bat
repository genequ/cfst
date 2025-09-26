@echo off
REM Cloudflare Speed Test Automation Batch Script
REM Run this script manually or schedule it with Windows Task Scheduler

echo Starting Cloudflare Speed Test Automation...
echo Date: %date% Time: %time%

REM Change to script directory
cd /d "%~dp0"

REM Run the Python scheduler
python cfst_scheduler.py --run-once

echo Automation completed.
echo Date: %date% Time: %time%
pause
