#!/bin/bash
# Script de instalación para Linux/Mac
# Configura automáticamente el entorno del backend

echo "========================================"
echo "Instalador del Sistema de Centro Medico"
echo "========================================"
echo ""

# Verificar que Python esté instalado
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 no está instalado"
    echo "Por favor, instala Python 3.8 o superior"
    exit 1
fi

echo "[INFO] Python detectado"
python3 --version

# Cambiar al directorio del script
cd "$(dirname "$0")"

# Ejecutar el script de instalación
echo ""
echo "[INFO] Iniciando instalación..."
echo ""

python3 instalar.py "$@"

if [ $? -ne 0 ]; then
    echo ""
    echo "[ERROR] La instalación falló"
    exit 1
fi

echo ""
echo "[ÉXITO] Instalación completada"
echo ""
echo "Para iniciar el servidor, ejecuta: ./iniciar_api.sh"
echo ""

