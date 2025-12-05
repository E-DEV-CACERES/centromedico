# Script PowerShell para iniciar la API
# Ejecutar con: .\iniciar_api.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  SISTEMA DE CENTRO MEDICO - API" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Cambiar al directorio del script
Set-Location $PSScriptRoot

# Verificar si existe el entorno virtual
if (-not (Test-Path "venv")) {
    Write-Host "El entorno virtual no existe. Creando entorno virtual..." -ForegroundColor Yellow
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: No se pudo crear el entorno virtual." -ForegroundColor Red
        Write-Host "Verifica que Python este instalado y en el PATH." -ForegroundColor Red
        Read-Host "Presiona Enter para salir"
        exit 1
    }
    Write-Host "Entorno virtual creado exitosamente." -ForegroundColor Green
    Write-Host ""
}

# Activar entorno virtual
Write-Host "Activando entorno virtual..." -ForegroundColor Cyan
try {
    & "venv\Scripts\Activate.ps1"
    if ($LASTEXITCODE -ne 0) {
        throw "Error al activar el entorno virtual"
    }
} catch {
    Write-Host "ERROR: No se pudo activar el entorno virtual." -ForegroundColor Red
    Write-Host "Si es la primera vez, ejecuta: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser" -ForegroundColor Yellow
    Read-Host "Presiona Enter para salir"
    exit 1
}

# Verificar si las dependencias están instaladas
if (-not (Test-Path "venv\Lib\site-packages\fastapi")) {
    Write-Host ""
    Write-Host "Instalando dependencias..." -ForegroundColor Yellow
    python -m pip install --upgrade pip
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: No se pudo actualizar pip." -ForegroundColor Red
        Read-Host "Presiona Enter para salir"
        exit 1
    }
    
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: No se pudieron instalar las dependencias." -ForegroundColor Red
        Read-Host "Presiona Enter para salir"
        exit 1
    }
    Write-Host ""
    Write-Host "Dependencias instaladas exitosamente." -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host "Dependencias ya instaladas." -ForegroundColor Green
    Write-Host ""
}

Write-Host "Iniciando servidor FastAPI..." -ForegroundColor Cyan
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  API disponible en:" -ForegroundColor Cyan
Write-Host "  http://localhost:8000" -ForegroundColor Yellow
Write-Host ""
Write-Host "  Documentacion interactiva:" -ForegroundColor Cyan
Write-Host "  http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host ""
Write-Host "  Documentacion alternativa:" -ForegroundColor Cyan
Write-Host "  http://localhost:8000/redoc" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Presiona Ctrl+C para detener el servidor" -ForegroundColor Yellow
Write-Host ""

# Ejecutar uvicorn usando python -m para evitar problemas de rutas
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
