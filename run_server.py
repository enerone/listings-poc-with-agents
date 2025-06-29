#!/usr/bin/env python3
"""
Script simplificado para ejecutar el servidor
"""

import uvicorn
import sys
import os

# Asegurar que estamos en el directorio correcto
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

print("🚀 Amazon Listings Generator")
print("=" * 40)
print(f"📁 Directorio: {script_dir}")
print(f"🐍 Python: {sys.executable}")
print(f"🌐 URL: http://localhost:8007")
print("💡 Presiona Ctrl+C para detener")
print("=" * 40)

if __name__ == "__main__":
    try:
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8007,
            reload=False,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Servidor detenido")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)