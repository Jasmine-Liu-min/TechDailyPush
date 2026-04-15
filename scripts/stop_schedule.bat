@echo off
schtasks /delete /tn "TechDaily" /f
if %errorlevel%==0 (
    echo OK - Task TechDaily stopped and deleted
) else (
    echo FAILED - Task not found or need Administrator
)
pause
