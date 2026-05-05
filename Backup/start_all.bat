@echo off
chcp 65001 >nul
cd /d "C:\kyiv_alert\alert_monitor"
set PY=C:\kyiv_alert\venv\Scripts\python.exe

echo [1/3] Starting PLAYER...
start "PLAYER" "%PY%" player_service.py
timeout /t 2 >nul

echo [2/3] Starting SCHEDULER...
start "SCHEDULER" "%PY%" moment_scheduler.py
timeout /t 1 >nul

echo [3/3] Starting MONITOR...
start "MONITOR" "%PY%" monitor.py

echo.
echo ========================================
echo SYSTEM ONLINE ?
echo ========================================
timeout /t 5