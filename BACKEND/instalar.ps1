# Script de instalación para Windows PowerShell
# Configura automáticamente el entorno del backend

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Instalador del Sistema de Centro Medico" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar que Python esté instalado
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[INFO] Python detectado: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Python no está instalado o no está en el PATH" -ForegroundColor Red
    Write-Host "Por favor, instala Python 3.8 o superior desde https://www.python.org/" -ForegroundColor Yellow
    Read-Host "Presiona Enter para salir"
    exit 1
}

# Cambiar al directorio del script
Set-Location -Path $PSScriptRoot

# Ejecutar el script de instalación
Write-Host ""
Write-Host "[INFO] Iniciando instalación..." -ForegroundColor Cyan
Write-Host ""

python instalar.py $args

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "[ERROR] La instalación falló" -ForegroundColor Red
    Read-Host "Presiona Enter para salir"
    exit 1
}

Write-Host ""
Write-Host "[ÉXITO] Instalación completada" -ForegroundColor Green
Write-Host ""
Write-Host "Para iniciar el servidor, ejecuta: .\iniciar_api.ps1" -ForegroundColor Yellow
Write-Host ""
Read-Host "Presiona Enter para salir"

