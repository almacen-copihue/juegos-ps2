@echo off
title Actualizando catálogo de PS2...

echo ===============================
echo   Generando catalogo PS2...
echo ===============================
echo.

:: Ir a la carpeta del script
cd /d "%~dp0"

:: Ejecutar Python
python genera_web.py

echo.
echo ===============================
echo   Catálogo actualizado con éxito
echo ===============================
echo.

pause
