@echo off
echo ========================================
echo   SISTEMA DE CENTRO MEDICO - API
echo ========================================
echo.
echo Activando entorno virtual...
call venv\Scripts\activate.bat
echo.
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
uvicorn main:app --reload --host 0.0.0.0 --port 8000

