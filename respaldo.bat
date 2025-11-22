@echo off
setlocal enabledelayedexpansion

:: ===== CONFIGURACIÓN =====
set SOURCE=C:\Users\Javier\Downloads\CATALOGO_PS2_estable
set FILENAME=catalogo_ps2

set DEST1="C:\Backups_PS2"
set DEST2="D:\PS2_Respaldo"
set DEST3="G:\PS2_MegaBackup"
set DEST4="%USERPROFILE%\OneDrive - Personal"
set DEST5="G:\TERABOX RESPALDOS"

:: ===== FECHA =====
for /f "tokens=1-3 delims=/" %%a in ("%date%") do (
    set dd=%%a
    set mm=%%b
    set yy=%%c
)
set DATE=!yy!-!mm!-!dd!

:: ===== VERSIÓN =====
set COUNT=1
:version_loop
set VERSION=V!COUNT!
set OUTPUT=%FILENAME%_%DATE%_%VERSION%.zip

if exist %DEST1%\%OUTPUT% (
    set /a COUNT+=1
    goto version_loop
)

echo ===========================
echo CREANDO ZIP: %OUTPUT%
echo ===========================

:: ===== CREAR ZIP SIN POWERSHELL =====
if exist "%TEMP%\%OUTPUT%" del "%TEMP%\%OUTPUT%"
tar.exe -a -c -f "%TEMP%\%OUTPUT%" -C "%SOURCE%" .

:: ===== COPIAR =====
echo Copiando a C...
copy "%TEMP%\%OUTPUT%" %DEST1% >nul

echo Copiando a D...
copy "%TEMP%\%OUTPUT%" %DEST2% >nul

echo Copiando a G...
copy "%TEMP%\%OUTPUT%" %DEST3% >nul

echo Copiando a OneDrive...
copy "%TEMP%\%OUTPUT%" %DEST4% >nul

echo Copiando a Terabox...
copy "%TEMP%\%OUTPUT%" %DEST5% >nul

echo ===========================
echo BACKUP COMPLETO: %OUTPUT%
echo ===========================

:: ===== LIMPIEZA =====
echo Limpiando copias antiguas...

for %%D in (%DEST1% %DEST2% %DEST3% %DEST4% %DEST5%) do (
    echo Procesando carpeta: %%D
    forfiles /p %%D /m "%FILENAME%_*.zip" /d -30 /c "cmd /c del @path" 2>nul

    for /f "skip=10 delims=" %%f in ('dir %%D\%FILENAME%_*.zip /b /o-d 2^>nul') do (
        del "%%D\%%f" 2>nul
    )
)

echo Limpieza completa.
pause
exit
