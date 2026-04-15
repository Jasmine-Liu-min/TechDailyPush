@echo off
schtasks /run /tn "TechDaily"
if %errorlevel%==0 (
    echo OK - TechDaily is running now
) else (
    echo FAILED - Task not found, run setup_schedule.bat first
)
pause
