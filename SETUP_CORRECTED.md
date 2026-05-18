# 🔧 SETUP CORRECTED — Instrucciones Actualizadas

## ⚡ FORMA MÁS RÁPIDA (Recomendado)

### Opción 1: Script automático corregido
```bash
cd D:\expo\Mini_POS
python start.py
```

**¿Qué hace?**
- Instala dependencias automáticamente si faltan
- Detecta e inicia la aplicación correctamente
- Abre en http://localhost:5000

---

### Opción 2: Manualmente desde la carpeta correcta

```bash
# 1. Ir a la carpeta del proyecto
cd D:\expo\Mini_POS

# 2. Activar entorno virtual (si no está activado)
.venv\Scripts\Activate.ps1

# 3. Instalar dependencias (si no están instaladas)
pip install -r backend/requirements.txt

# 4. Inicializar BD
python init_db.py

# 5. Ejecutar desde la raíz del proyecto
python backend/app.py
```

**Resultado esperado:**
```
INFO:werkzeug:Running on http://0.0.0.0:5000
```

---

### Opción 3: Desde el directorio backend

```bash
cd D:\expo\Mini_POS\backend

# Instalar dependencias si no están
pip install -r requirements.txt

# Ejecutar app
python app.py
```

---

## 🐛 Si sale error "No module named 'app'"

### Causa
El script `run.py` original no estaba agregando correctamente el path de Python.

### Solución
Usa el nuevo script `start.py`:
```bash
python start.py
```

O ejecuta directamente desde la raíz:
```bash
python backend/app.py
```

---

## ✅ Checklist antes de ejecutar

- [ ] MySQL está corriendo (`mysql -u root` debe conectar)
- [ ] Base de datos creada (`python init_db.py`)
- [ ] Entorno virtual activado (`.venv\Scripts\Activate.ps1`)
- [ ] Dependencias instaladas (`pip list | grep flask`)

---

## 🎯 RESUMEN DE COMANDOS

```bash
# Desde D:\expo\Mini_POS

# Crear BD
python init_db.py

# Opción A: Usar nuevo script
python start.py

# Opción B: Ejecutar directamente
python backend/app.py

# Luego abrir navegador
http://localhost:5000
```

---

**¡Listo! El servidor debe iniciar correctamente** 🚀
