@echo off
schtasks /delete /tn "TechDaily" /f >nul 2>&1
schtasks /create /tn "TechDaily" /tr "\"D:\Program Files\Python\python313\python.exe\" \"C:\Users\AS\TechDailyPush\daily.py\"" /sc daily /st 09:00 /rl highest /f
if %errorlevel%==0 (
    echo OK - Task TechDaily created, runs daily at 09:00
    echo.
    echo View:   double click check_schedule.bat
    echo Run:    double click run_now.bat
    echo Delete: right click stop_schedule.bat as Admin
) else (
    echo FAILED - Please right click and Run as Administrator
)
pause
