#!/bin/bash

echo "========================================"
echo "  SISTEMA DE CENTRO MEDICO - API"
echo "========================================"
echo ""

# Verificar si existe el entorno virtual
if [ ! -d "venv" ]; then
    echo "El entorno virtual no existe. Creando entorno virtual..."
    python3 -m venv venv
    echo ""
    echo "Entorno virtual creado exitosamente."
    echo ""
fi

echo "Activando entorno virtual..."
source venv/bin/activate

# Verificar si las dependencias están instaladas
if [ ! -d "venv/lib/python*/site-packages/fastapi" ]; then
    echo ""
    echo "Instalando dependencias..."
    pip install -r requirements.txt
    echo ""
    echo "Dependencias instaladas exitosamente."
    echo ""
else
    echo "Dependencias ya instaladas."
    echo ""
fi

echo "Iniciando servidor FastAPI..."
echo ""
echo "========================================"
echo "  API disponible en:"
echo "  http://localhost:8000"
echo ""
echo "  Documentacion interactiva:"
echo "  http://localhost:8000/docs"
echo ""
echo "  Documentacion alternativa:"
echo "  http://localhost:8000/redoc"
echo "========================================"
echo ""
echo "Presiona Ctrl+C para detener el servidor"
echo ""

uvicorn main:app --reload --host 0.0.0.0 --port 8000
