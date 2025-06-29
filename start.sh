#!/bin/bash
# Script para iniciar Amazon Listings Generator

echo "🚀 Iniciando Amazon Listings Generator..."

# Verificar si el entorno virtual existe
if [ ! -d "venv" ]; then
    echo "❌ Entorno virtual no encontrado. Creando..."
    python -m venv venv
    echo "✅ Entorno virtual creado"
fi

# Activar entorno virtual
echo "🔄 Activando entorno virtual..."
source venv/bin/activate

# Instalar dependencias si es necesario
echo "📦 Verificando dependencias..."
pip install -r requirements.txt > /dev/null 2>&1

# Ejecutar aplicación
echo "🌐 Iniciando servidor en http://localhost:8006"
echo "💡 Presiona Ctrl+C para detener"
echo ""

python main.py