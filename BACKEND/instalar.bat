@echo off
REM Script de instalación para Windows
REM Configura automáticamente el entorno del backend

echo ========================================
echo Instalador del Sistema de Centro Medico
echo ========================================
echo.

REM Verificar que Python esté instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no está instalado o no está en el PATH
    echo Por favor, instala Python 3.8 o superior desde https://www.python.org/
    pause
    exit /b 1
)

echo [INFO] Python detectado
python --version

REM Cambiar al directorio del script
cd /d "%~dp0"

REM Ejecutar el script de instalación
echo.
echo [INFO] Iniciando instalación...
echo.

python instalar.py %*

if errorlevel 1 (
    echo.
    echo [ERROR] La instalación falló
    pause
    exit /b 1
)

echo.
echo [EXITO] Instalación completada
echo.
echo Para iniciar el servidor, ejecuta: iniciar_api.bat
echo.
pause

