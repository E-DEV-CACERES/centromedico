@echo off
REM Script para inicializar todas las tablas de la base de datos (Windows)

echo ========================================
echo Inicializar Tablas de la Base de Datos
echo ========================================
echo.

REM Cambiar al directorio del script
cd /d "%~dp0"

REM Verificar que Python esté disponible
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no está instalado o no está en el PATH
    pause
    exit /b 1
)

REM Ejecutar el script
python inicializar_tablas.py

if errorlevel 1 (
    echo.
    echo [ERROR] La inicialización falló
    pause
    exit /b 1
)

echo.
pause

