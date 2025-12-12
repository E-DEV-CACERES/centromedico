@echo off
echo.
echo ========================================
echo Creando Recetas de Ejemplo
echo ========================================
echo.

cd /d "%~dp0"
python crear_recetas.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Proceso completado exitosamente.
) else (
    echo.
    echo Error al ejecutar el script.
    pause
)

pause
