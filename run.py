#!/usr/bin/env python3
"""
Amazon Listings Generator - Startup Script
"""

import uvicorn
import os
from decouple import config

if __name__ == "__main__":
    # Load configuration from environment
    HOST = config("HOST", default="0.0.0.0")
    PORT = config("PORT", default=8007, cast=int)
    DEBUG = config("DEBUG", default=True, cast=bool)
    
    print("🚀 Iniciando Amazon Listings Generator...")
    print(f"📍 Servidor: http://{HOST}:{PORT}")
    print("📋 Funcionalidades disponibles:")
    print("   • Crear listings con IA")
    print("   • Análisis con Qwen2.5-Coder")
    print("   • Búsqueda de imágenes")
    print("   • Optimización automática")
    print("\n⚡ Asegúrate de que Ollama esté corriendo:")
    print("   ollama serve")
    print("   ollama pull qwen2.5-coder:32b")
    print()
    
    # Run the application
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=DEBUG,
        log_level="info" if DEBUG else "warning"
    )