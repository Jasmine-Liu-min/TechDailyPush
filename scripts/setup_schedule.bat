@echo off
schtasks /create /tn "TechDaily" /tr "python \"%~dp0..\daily.py\"" /sc daily /st 08:00 /f
if %errorlevel%==0 (
    echo OK - Task TechDaily created, runs daily at 08:00
    echo.
    echo View:   double click check_schedule.bat
    echo Run:    double click run_now.bat
    echo Delete: right click stop_schedule.bat as Admin
) else (
    echo FAILED - Please right click and Run as Administrator
)
pause
