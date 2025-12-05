@echo off
echo.
echo ========================================
echo Creando Pacientes de Ejemplo
echo ========================================
echo.

cd /d "%~dp0"
python crear_pacientes.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Proceso completado exitosamente.
) else (
    echo.
    echo Error al ejecutar el script.
    pause
)

pause
