@echo off
chcp 850 >nul
setlocal enabledelayedexpansion

:: ======================
:: CONFIGURACION BASICA
:: ======================

set SOURCE=C:\Users\Javier\Downloads\CATALOGO_PS2_estable
set FILENAME=catalogo_ps2

:: DESTINOS SIN COMILLAS
set DEST1=C:\Backups_PS2
set DEST2=D:\PS2_Respaldo
set DEST3=G:\PS2_MegaBackup
set DEST5=G:\TERABOX_RESPALDOS

:: Carpeta de logs
set LOGDIR=%~dp0logs
if not exist "%LOGDIR%" mkdir "%LOGDIR%"

:: ======================
:: FECHA
:: ======================
for /f "tokens=1-4 delims=/ " %%a in ("%date%") do (
    set dd=%%a
    set mm=%%b
    set yy=%%c
)
set DATE=%yy%-%mm%-%dd%
set LOGFILE=%LOGDIR%\%DATE%.log

echo [%date% %time%] INICIO >> "%LOGFILE%"

echo Verificando carpetas destino...

:: ======================
:: CREAR CARPETAS SI NO EXISTEN
:: ======================
for %%D in ("%DEST1%" "%DEST2%" "%DEST3%" "%DEST5%") do (
    if not exist %%D (
        echo   Creando carpeta: %%D
        mkdir %%D
    ) else (
        echo   Carpeta OK: %%D
    )
)

echo.
echo ============================
echo   INICIANDO BACKUP PS2
echo ============================
echo.

:: ======================
:: VERSIONADO
:: ======================
set COUNT=1
:version_loop
set VERSION=V!COUNT!
set OUTPUT=%FILENAME%_%DATE%_%VERSION%.zip

if exist "%DEST1%\%OUTPUT%" (
    set /a COUNT+=1
    goto version_loop
)

:: ======================
:: CREAR ZIP
:: ======================
echo Creando ZIP: %OUTPUT%
echo [%date% %time%] ZIP %OUTPUT% >> "%LOGFILE%"

if exist "%TEMP%\%OUTPUT%" del "%TEMP%\%OUTPUT%"

tar.exe -a -c -f "%TEMP%\%OUTPUT%" -C "%SOURCE%" .

if not exist "%TEMP%\%OUTPUT%" (
    echo ERROR: No se pudo crear ZIP.
    echo [%date% %time%] ERROR ZIP >> "%LOGFILE%"
    pause
    exit /b
)

echo ZIP OK.
echo.

:: ======================
:: COPIAR ARCHIVO
:: ======================
for %%D in ("%DEST1%" "%DEST2%" "%DEST3%" "%DEST5%") do (
    echo Copiando a %%D ...

    if exist %%D (
        copy "%TEMP%\%OUTPUT%" "%%D" >nul
        if !errorlevel! == 0 (
            echo   OK
            echo [%date% %time%] COPY OK -> %%D >> "%LOGFILE%"
        ) else (
            echo   ERROR
            echo [%date% %time%] COPY FAIL -> %%D >> "%LOGFILE%"
        )
    ) else (
        echo   DESTINO NO DISPONIBLE
        echo [%date% %time%] NO DESTINO -> %%D >> "%LOGFILE%"
    )
    echo.
)

:: ======================
:: LIMPIEZA
:: ======================
echo Limpiando copias viejas...
echo [%date% %time%] LIMPIEZA >> "%LOGFILE%"

for %%D in ("%DEST1%" "%DEST2%" "%DEST3%" "%DEST5%") do (
    if exist %%D (
        for /f "skip=10 delims=" %%f in ('dir "%%D\%FILENAME%_*.zip" /b /o-d 2^>nul') do (
            del "%%D\%%f"
            echo Eliminado: %%D\%%f
            echo [%date% %time%] DELETE -> %%D\%%f >> "%LOGFILE%"
        )
    )
)

echo.
echo Backup completo.
echo [%date% %time%] FIN >> "%LOGFILE%"

:: ======================
:: CARTEL SIMPLE
:: ======================
powershell -command "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.MessageBox]::Show('Backup completado','PS2',0,64)"

pause
exit
