@echo off
title ROBOT PRO - PROGRAMADOR MASIVO
echo ==========================================
echo      INICIANDO ROBOT PRO (80 VIDEOS)
echo ==========================================
echo.
echo  MODO: Meta Business Suite
echo  PROGRAMACION: 2 videos/dia (1 PM y 6 PM)
echo.
echo  1. Se abrira el navegador.
echo  2. Si te pide login, entra a Facebook.
echo  3. El robot ira a Business Suite y empezara.
echo.
cd /d "%~dp0"
node robot_pro.js
echo.
echo ==========================================
echo      TRABAJO TERMINADO
echo ==========================================
pause
