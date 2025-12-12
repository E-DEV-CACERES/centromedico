@echo off
echo.
echo ========================================
echo Creando Usuario Administrador
echo ========================================
echo.

cd /d "%~dp0"
python crear_admin.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Proceso completado exitosamente.
) else (
    echo.
    echo Error al ejecutar el script.
    pause
)

pause
