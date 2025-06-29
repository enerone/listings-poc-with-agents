# 🔍 INSTRUCCIONES PARA DEBUGGING

## 📋 **Pasos para debuggear el problema:**

### 1️⃣ **Preparar el entorno:**
```bash
# 1. Abrir terminal y ir al directorio
cd /home/fabi/code/listings-amazon

# 2. Activar entorno virtual
source venv/bin/activate

# 3. Iniciar servidor
python -m uvicorn main:app --host 0.0.0.0 --port 8007

# Dejar esta terminal abierta con el servidor corriendo
```

### 2️⃣ **Abrir navegador con herramientas de desarrollador:**
1. **Abrir Chrome/Firefox**
2. **Ir a**: http://localhost:8007
3. **Presionar F12** (o clic derecho → Inspeccionar)
4. **Ir a la pestaña "Console"** (Consola)
5. **Dejar la consola abierta**

### 3️⃣ **Probar creación de listing:**
1. **Ir a "Crear Listing"** en la web
2. **Completar EXACTAMENTE esto**:
   - **Título**: `Producto Debug Test 123`
   - **Descripción**: `Este es un producto de prueba para debuggear el sistema. Incluye características avanzadas y funcionalidades especiales.`
   - **Imágenes**: NO subir ninguna (para ir más rápido)
3. **Hacer clic en "Crear Listing"**
4. **OBSERVAR la consola del navegador** mientras se procesa

### 4️⃣ **Qué deberías ver en la consola:**
```
🚀 Iniciando proceso de creación...
📝 Datos del listing: {original_title: "Producto Debug Test 123", ...}
📡 Respuesta crear listing: 200
✅ Listing creado: {id: X, original_title: "...", ...}
🤖 Iniciando análisis IA...
📡 Respuesta análisis: 200
✅ Análisis completado: true
🖼️ Buscando imágenes...
📡 Respuesta imágenes: 200
✅ Búsqueda completada: true
⚡ Optimizando...
📡 Respuesta optimización: 200
✅ Optimización completada: true
🎉 Proceso completado exitosamente!
📋 ID del listing creado: X
🔍 Verificando que el listing existe...
✅ Listing verificado: optimized
💬 Mostrando mensaje de éxito...
🔄 Redirigiendo a /listings en 1 segundo...
🌐 Ejecutando redirección...
```

### 5️⃣ **Qué hacer si hay errores:**

**Si ves algún error en la consola:**
1. **Tomar screenshot** del error
2. **Copiar el mensaje de error completo**
3. **Anotar en qué paso se detuvo**

**Si NO aparece el mensaje de éxito:**
1. **Verificar en la terminal del servidor** si hay errores
2. **Anotar qué es lo último que aparece en la consola**

**Si aparece el mensaje pero NO redirige:**
1. **Verificar si aparece el mensaje "🌐 Ejecutando redirección..."**
2. **Probar ir manualmente** a http://localhost:8007/listings

### 6️⃣ **Verificación manual:**

**Después del proceso, verificar manualmente:**
```bash
# En otra terminal (sin cerrar el servidor)
curl -s http://localhost:8007/api/listings/ | python -m json.tool
```

**Esto debería mostrar tu listing recién creado.**

### 7️⃣ **Casos posibles:**

**✅ CASO 1: Todo funciona**
- Ves todos los logs en la consola
- Aparece mensaje de éxito
- Se redirige automáticamente
- El listing aparece en /listings

**❌ CASO 2: Se crea pero no aparece en la interfaz**
- Los logs muestran éxito
- El curl muestra el listing
- Pero no aparece en la página /listings
- → Problema en el frontend de la lista

**❌ CASO 3: Falla en algún paso**
- Los logs se detienen en algún punto
- Hay error en la consola
- → Problema en ese paso específico

**❌ CASO 4: No se crea nada**
- Error 400/500 en crear listing
- → Problema en el backend

### 📊 **Reporte del resultado:**

**Después de la prueba, reporta:**
1. ¿Qué logs aparecieron en la consola?
2. ¿En qué paso se detuvo (si se detuvo)?
3. ¿Apareció mensaje de éxito?
4. ¿Se redirigió automáticamente?
5. ¿El listing aparece en /listings?
6. ¿Qué muestra el comando curl?

**Con esta información podremos identificar exactamente dónde está el problema.**

---

🎯 **El objetivo es ver EXACTAMENTE qué está pasando paso a paso para identificar dónde se rompe el flujo.**