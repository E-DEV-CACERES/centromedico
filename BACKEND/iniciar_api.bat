@echo off
REM Cambiar al directorio del script
cd /d "%~dp0"

echo ========================================
echo   SISTEMA DE CENTRO MEDICO - API
echo ========================================
echo.

REM Verificar si existe el entorno virtual en BACKEND
if not exist "venv\" (
    echo El entorno virtual no existe. Creando entorno virtual...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: No se pudo crear el entorno virtual.
        echo Verifica que Python este instalado y en el PATH.
        pause
        exit /b 1
    )
    echo.
    echo Entorno virtual creado exitosamente.
    echo.
)

echo Activando entorno virtual...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: No se pudo activar el entorno virtual.
    pause
    exit /b 1
)

REM Verificar si las dependencias están instaladas
if not exist "venv\Lib\site-packages\fastapi" (
    echo.
    echo Instalando dependencias...
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: No se pudieron instalar las dependencias.
        pause
        exit /b 1
    )
    echo.
    echo Dependencias instaladas exitosamente.
    echo.
) else (
    echo Dependencias ya instaladas.
    echo.
)

echo Iniciando servidor FastAPI...
echo.
echo ========================================
echo   API disponible en:
echo   http://localhost:8000
echo.
echo   Documentacion interactiva:
echo   http://localhost:8000/docs
echo.
echo   Documentacion alternativa:
echo   http://localhost:8000/redoc
echo ========================================
echo.
echo Presiona Ctrl+C para detener el servidor
echo.

REM Ejecutar uvicorn usando python -m para evitar problemas de rutas
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

pause
