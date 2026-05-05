@echo off
chcp 65001 >nul
title Kyiv Alert - Web Dashboard

echo ================================================
echo     Kyiv Alert System - WEB DASHBOARD
echo ================================================
echo.

cd /d "C:\kyiv_alert"

set "PY=C:\kyiv_alert\venv\Scripts\python.exe"

echo Запуск веб-інтерфейсу...
"%PY%" -u web_app.py

pause