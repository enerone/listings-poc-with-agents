#!/usr/bin/env python3
"""
Script simple para verificar el estado del servidor
"""

import subprocess
import time
import sys

def check_server():
    try:
        # Verificar si el proceso está corriendo
        result = subprocess.run(['pgrep', '-f', 'main.py'], 
                               capture_output=True, text=True)
        
        if result.returncode == 0:
            pids = result.stdout.strip().split('\n')
            print(f"✅ Servidor corriendo (PID: {', '.join(pids)})")
            print("🌐 URL: http://localhost:8006")
            
            # Intentar hacer una petición simple
            try:
                import requests
                response = requests.get('http://localhost:8006', timeout=5)
                if response.status_code == 200:
                    print("✅ Servidor respondiendo correctamente")
                else:
                    print(f"⚠️  Servidor responde con código: {response.status_code}")
            except requests.exceptions.ConnectionError:
                print("⚠️  Servidor no acepta conexiones aún (iniciando...)")
            except Exception as e:
                print(f"⚠️  Error al conectar: {e}")
                
            return True
        else:
            print("❌ Servidor no está corriendo")
            print("💡 Para iniciarlo: ./start.sh")
            return False
            
    except Exception as e:
        print(f"❌ Error verificando servidor: {e}")
        return False

if __name__ == "__main__":
    check_server()