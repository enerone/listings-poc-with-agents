# 🚀 Amazon Listings Generator - INSTRUCCIONES DE USO

## ✅ Estado: PROYECTO FUNCIONANDO

### 📋 Para iniciar el servidor:

**Opción 1 (Recomendada):**
```bash
cd /home/fabi/code/listings-amazon
source venv/bin/activate
python -m uvicorn main:app --host 0.0.0.0 --port 8007
```

**Opción 2:**
```bash
cd /home/fabi/code/listings-amazon
./start.sh
```

**Opción 3:**
```bash
cd /home/fabi/code/listings-amazon
source venv/bin/activate
python run_server.py
```

### 🌐 URLs importantes:

- **Página principal**: http://localhost:8007
- **Crear listing**: http://localhost:8007/create  
- **Ver listings**: http://localhost:8007/listings
- **API**: http://localhost:8007/api/listings/

### 🎯 Cómo usar:

1. **Iniciar servidor** (ver comandos arriba)
2. **Abrir navegador** en http://localhost:8007
3. **Ir a "Crear Listing"**
4. **Completar formulario**:
   - Título del producto
   - Descripción detallada
   - Subir imágenes (opcional)
5. **Hacer clic en "Crear Listing"**
6. **Esperar procesamiento IA** (automático)
7. **Ver resultado** en "Mis Listings"

### 🤖 Funcionalidades IA:

- **Agente Analizador**: Usa DeepSeek-R1 para optimizar contenido
- **Buscador de Imágenes**: Encuentra imágenes similares  
- **Optimizador**: Mejora según reglas de Amazon

### 🔧 Solución de problemas:

**Si el puerto está ocupado:**
```bash
# Cambiar puerto en main.py línea 33
uvicorn.run(app, host="0.0.0.0", port=8008)  # Usar 8008 u otro
```

**Si hay errores de dependencias:**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

**Verificar que funciona:**
```bash
python quick_test.py
```

### 📱 Ejemplo de uso:

1. Título: "Audífonos Bluetooth Sony WH-1000XM4"
2. Descripción: "Audífonos premium con cancelación de ruido..."
3. Subir 2-3 fotos del producto
4. ¡Dejar que la IA haga el resto!

### 🎉 ¡Tu generador está listo!

El sistema procesará automáticamente tu producto y generará:
- Título optimizado para Amazon
- Descripción persuasiva  
- Bullet points efectivos
- Keywords para SEO
- Imágenes adicionales sugeridas

**¡Disfruta creando listings profesionales con IA!** 🚀