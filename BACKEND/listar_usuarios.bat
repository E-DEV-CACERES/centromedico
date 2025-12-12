@echo off
REM Script para listar usuarios del sistema (Windows)

echo ========================================
echo Listar Usuarios del Sistema
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
python listar_usuarios.py %*

pause

