#!/bin/bash
# Script para reiniciar el servidor

echo "🔄 Reiniciando Amazon Listings Generator..."

# Matar procesos existentes
echo "🛑 Deteniendo procesos existentes..."
pkill -f "python main.py" 2>/dev/null || true
pkill -f "uvicorn" 2>/dev/null || true
sleep 2

# Activar entorno virtual
echo "🔧 Activando entorno virtual..."
source venv/bin/activate

# Iniciar servidor
echo "🚀 Iniciando servidor..."
echo "🌐 Disponible en: http://localhost:8006"
echo "💡 Presiona Ctrl+C para detener"
echo ""

python main.py