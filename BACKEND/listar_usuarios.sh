#!/bin/bash
# Script para listar usuarios del sistema (Linux/Mac)

echo "========================================"
echo "Listar Usuarios del Sistema"
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
python3 listar_usuarios.py "$@"

