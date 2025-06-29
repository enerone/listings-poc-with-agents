# 🔧 Solución de Problemas - Amazon Listings Generator

## ❓ **PROBLEMA: "Le cargué todo pero no me lo procesó"**

### ✅ **Verificación rápida:**

1. **¿El servidor está corriendo?**
   ```bash
   python test_web_interface.py
   ```

2. **¿Los listings se están creando?**
   ```bash
   curl -s http://localhost:8007/api/listings/ | python -m json.tool
   ```

3. **¿Ollama está funcionando?**
   ```bash
   curl -s http://localhost:11434/api/tags
   ```

### 🎯 **Lo que debería pasar cuando creas un listing:**

1. **Completas el formulario** → Título + Descripción + Fotos
2. **Haces clic en "Crear Listing"** → Aparece modal de procesamiento
3. **Pasos automáticos**:
   - ✅ Subir imágenes (si las hay)
   - ✅ Crear listing inicial
   - ✅ Analizar con DeepSeek-R1
   - ✅ Buscar imágenes similares
   - ✅ Optimizar resultado
4. **Te muestra mensaje de éxito** → Te redirige a /listings
5. **Ves tu listing procesado** → Con contenido generado por IA

### 🚨 **Posibles problemas y soluciones:**

#### **Problema 1: Modal de procesamiento no aparece**
```bash
# Revisar la consola del navegador (F12)
# Buscar errores JavaScript
```

#### **Problema 2: Se queda en "Procesando..."**
```bash
# Verificar logs del servidor
# El servidor debería mostrar las peticiones en la terminal
```

#### **Problema 3: "Error creando listing"**
```bash
# Verificar que el servidor esté corriendo
ps aux | grep uvicorn

# Si no está corriendo:
cd /home/fabi/code/listings-amazon
source venv/bin/activate
python -m uvicorn main:app --host 0.0.0.0 --port 8007
```

#### **Problema 4: Ollama no responde**
```bash
# Verificar Ollama
ollama serve

# En otra terminal:
ollama pull deepseek-r1
```

#### **Problema 5: Timeout en análisis IA**
```bash
# El análisis puede tomar 30-60 segundos
# Espera a que termine el proceso
```

### 🧪 **Test manual paso a paso:**

1. **Abre el navegador** en: http://localhost:8007
2. **Ve a "Crear Listing"**
3. **Completa EXACTAMENTE esto**:
   - Título: `Test iPhone 15 Pro`
   - Descripción: `Smartphone Apple con cámara avanzada, chip A17 Pro, pantalla Super Retina XDR, disponible en varios colores.`
4. **NO subas fotos por ahora** (para ir más rápido)
5. **Haz clic en "Crear Listing"**
6. **Deberías ver**:
   - Modal con progreso
   - Pasos 1-6 ejecutándose
   - Mensaje de éxito
   - Redirección a /listings

### 📋 **Verificar resultado:**

1. **Ve a "Mis Listings"**
2. **Busca tu listing** (debería aparecer al final)
3. **Haz clic en "Ver"**
4. **Deberías ver**:
   - Título original: `Test iPhone 15 Pro`
   - Título generado: `[Algo optimizado por IA]`
   - Descripción generada
   - Bullet points
   - Keywords
   - Status: "analyzed" o "optimized"

### 🆘 **Si NADA funciona:**

```bash
# 1. Reiniciar todo
pkill -f uvicorn
cd /home/fabi/code/listings-amazon
source venv/bin/activate
python -m uvicorn main:app --host 0.0.0.0 --port 8007

# 2. En otra terminal, probar:
python debug_creation.py

# 3. Si sigue fallando, cambiar puerto:
# Editar main.py línea 33: port=8008
```

### ✅ **Signos de que TODO funciona:**

- ✅ Puedes ver http://localhost:8007
- ✅ El formulario envía datos
- ✅ Aparece modal de procesamiento
- ✅ Los pasos se ejecutan uno por uno
- ✅ Te redirige a /listings
- ✅ Ves tu listing con contenido generado

### 💡 **Tips:**

1. **Usa títulos descriptivos**: "iPhone 15 Pro", "MacBook Air M3", etc.
2. **Descripción detallada**: Incluye características, beneficios, usos
3. **Paciencia**: El análisis IA puede tomar 30-60 segundos
4. **Revisa la consola**: F12 → Console para ver errores JavaScript

¡El sistema funciona correctamente según nuestras pruebas! 🚀