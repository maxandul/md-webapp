@echo off
chcp 65001 > nul
cls

echo ================================================
echo   🏢 Mitarbeitergespräche Server
echo   Kanton Zürich - HR
echo ================================================
echo.
echo 📅 %date% %time%
echo.
echo ⚠️  Dieses Fenster NICHT schliessen!
echo.
echo Server startet...
echo.

cd /d "%~dp0"
python app.py

pause