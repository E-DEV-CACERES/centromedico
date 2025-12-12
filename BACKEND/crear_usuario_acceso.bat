@echo off
REM Script para crear el usuario de acceso al sistema (Windows)

echo ========================================
echo Crear Usuario de Acceso al Sistema
echo ========================================
echo.

REM Cambiar al directorio del script
cd /d "%~dp0"

REM Verificar que Python esté disponible
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no está instalado o no está en el PATH
    echo Por favor, instala Python 3.8 o superior
    pause
    exit /b 1
)

REM Ejecutar el script
python crear_usuario_acceso.py %*

if errorlevel 1 (
    echo.
    echo [ERROR] No se pudo crear el usuario
    pause
    exit /b 1
)

echo.
pause

