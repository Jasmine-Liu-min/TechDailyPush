@echo off
schtasks /query /tn "TechDaily" /fo list
if %errorlevel% neq 0 (
    echo Task TechDaily not found
)
pause
