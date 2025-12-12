#!/bin/bash

echo ""
echo "========================================"
echo "Creando Usuario Administrador"
echo "========================================"
echo ""

# Cambiar al directorio del script
cd "$(dirname "$0")"

# Ejecutar el script Python
python3 crear_admin.py "$@"

if [ $? -eq 0 ]; then
    echo ""
    echo "Proceso completado exitosamente."
else
    echo ""
    echo "Error al ejecutar el script."
    exit 1
fi
