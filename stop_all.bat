@echo off
chcp 65001 >nul
title Kyiv Alert - Зупинка системи

echo Зупиняємо всі процеси Kyiv Alert...

taskkill /fi "WINDOWTITLE eq PLAYER*" /f >nul 2>&1
taskkill /fi "WINDOWTITLE eq SCHEDULER*" /f >nul 2>&1
taskkill /fi "WINDOWTITLE eq MONITOR*" /f >nul 2>&1
taskkill /fi "WINDOWTITLE eq WEB*" /f >nul 2>&1
taskkill /fi "WINDOWTITLE eq Kyiv Alert*" /f >nul 2>&1

echo.
echo Усі процеси зупинено.
echo.
pause