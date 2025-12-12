#!/bin/bash
# Script para crear el usuario de acceso al sistema (Linux/Mac)

echo "========================================"
echo "Crear Usuario de Acceso al Sistema"
echo "========================================"
echo ""

# Cambiar al directorio del script
cd "$(dirname "$0")"

# Verificar que Python esté disponible
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 no está instalado"
    exit 1
fi

# Ejecutar el script
python3 crear_usuario_acceso.py "$@"

if [ $? -ne 0 ]; then
    echo ""
    echo "[ERROR] No se pudo crear el usuario"
    exit 1
fi

