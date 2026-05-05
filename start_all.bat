@echo off
chcp 65001 >nul
title Kyiv Alert System - Запуск усіх сервісів

echo ================================================
echo     Kyiv Alert System - ЗАПУСК СИСТЕМИ
echo ================================================
echo.

set "BASE_DIR=C:\kyiv_alert\alert_monitor"
set "PY=C:\kyiv_alert\venv\Scripts\python.exe"

cd /d "%BASE_DIR%"

echo [1/4] Перевірка віртуального середовища...
if not exist "%PY%" (
    echo [ERROR] Python з venv не знайдено: %PY%
    echo Перевірте, чи створено віртуальне середовище.
    pause
    exit /b 1
)

echo [2/4] Очищення старих lock-файлів і флагів...
del /q "%BASE_DIR%\player_lock.lock" 2>nul
del /q "%BASE_DIR%\*.flag" 2>nul
del /q "%BASE_DIR%\current_alert_start.tmp" 2>nul

echo [3/4] Запуск сервісів...

:: Запускаємо в окремому вікні з назвою
start "🔊 PLAYER"     "%PY%" -u player_service.py
timeout /t 2 >nul

start "⏰ SCHEDULER"  "%PY%" -u moment_scheduler.py
timeout /t 1 >nul

start "📡 MONITOR"    "%PY%" -u monitor.py
timeout /t 2 >nul

echo.
echo ================================================
echo     Усі сервіси запущено!
echo ================================================
echo.
echo Відкрий браузер і перейди за адресою:
echo http://localhost:5000
echo.
echo Натисни будь-яку клавішу, щоб закрити це вікно...
pause >nul