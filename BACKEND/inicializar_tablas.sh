#!/bin/bash
# Script para inicializar todas las tablas de la base de datos (Linux/Mac)

echo "========================================"
echo "Inicializar Tablas de la Base de Datos"
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
python3 inicializar_tablas.py

if [ $? -ne 0 ]; then
    echo ""
    echo "[ERROR] La inicialización falló"
    exit 1
fi

