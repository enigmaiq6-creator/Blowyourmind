@echo off
title Facebook Robot Automator
echo ==========================================
echo      INICIANDO ROBOT DE FACEBOOK...
echo ==========================================
echo.
echo Por favor, no cierres esta ventana.
echo.
cd /d "%~dp0"
node robot.js
echo.
echo ==========================================
echo      TRABAJO TERMINADO (O ERROR)
echo ==========================================
pause
