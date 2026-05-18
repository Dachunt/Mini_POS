# 🛒 Mini POS — Guía Rápida de Inicio

## ⚡ 3 Pasos para Empezar (5 minutos)

### PASO 1: Verificar Requisitos

```bash
# Ejecuta el script de verificación
python check.py
```

Si todo está verde ✅, puedes continuar. Si hay errores ❌, revisa el README.

### PASO 2: Crear Base de Datos

```bash
# Opción A: Usando el script (recomendado)
python init_db.py

# Opción B: Manualmente
mysql -u root < database/schema.sql
```

**Resultado esperado:**
- ✅ Base de datos `pos_inventario` creada
- ✅ Tablas `producto`, `venta`, `detalle_venta` creadas
- ✅ 10 productos precargados (Coca-Cola, Arroz, etc.)

### PASO 3: Ejecutar la Aplicación

```bash
# Opción A: Usar el script automático (recomendado)
python run.py

# Opción B: Manualmente
cd backend
python app.py
```

**Resultado esperado:**
```
🛒 Mini POS — Iniciando servidor...
✅ Todas las dependencias están instaladas
🚀 Iniciando Flask en http://0.0.0.0:5000
   Abre http://localhost:5000 en tu navegador
```

---

## 🌐 Abrir en Navegador

Una vez que Flask esté corriendo, abre tu navegador:

```
http://localhost:5000
```

Deberías ver:
- 📦 Catálogo de productos a la izquierda
- 🛒 Carrito a la derecha
- ✓ Conexión a MySQL indicada en header
- 🕐 Reloj en tiempo real

---

## 🧪 Primeras Pruebas

### 1️⃣ Ver Productos

- [ ] Deberías ver 10 productos con nombre, precio y stock
- [ ] La búsqueda funciona (escribe "coca" o "arroz")
- [ ] El estado de conexión es "MySQL conectado" (punto verde)

### 2️⃣ Agregar al Carrito

- [ ] Haz clic en un producto (ej: Coca-Cola)
- [ ] Deberías verlo en el carrito a la derecha
- [ ] El badge del carrito muestra "1"
- [ ] El total se calcula automáticamente

### 3️⃣ Modificar Cantidad

- [ ] Usa los botones `−` y `+` en el carrito
- [ ] La cantidad cambia
- [ ] El total se actualiza correctamente

### 4️⃣ Finalizar Venta

- [ ] Selecciona método de pago (efectivo, tarjeta, transferencia)
- [ ] Haz clic en "Finalizar Venta"
- [ ] Aparece un modal con el recibo ✅
- [ ] Cierra el modal y verifica que:
  - El carrito se vacía
  - El stock del producto disminuyó

---

## 🔍 Verificar en Base de Datos

Para confirmar que la venta se registró, abre MySQL y ejecuta:

```sql
-- Ver ventas creadas
SELECT * FROM venta;

-- Ver detalles de la última venta
SELECT * FROM detalle_venta ORDER BY id DESC LIMIT 5;

-- Ver stock actualizado
SELECT id, nombre, stock_actual FROM producto;
```

---

## ❌ Problemas Comunes

### "Connection refused" (No se puede conectar)
- ❌ Flask no está corriendo
- ✅ Ejecuta `python run.py` en otra terminal

### "Error en la base de datos"
- ❌ MySQL no está corriendo
- ❌ La base de datos `pos_inventario` no existe
- ✅ Ejecuta `python init_db.py`
- ✅ Verifica MySQL: `mysql -u root -e "SHOW DATABASES;"`

### "Sin conexión" (punto rojo en header)
- ❌ Backend no está corriendo
- ❌ MySQL está desconectado
- ✅ Revisa la consola de Flask para errores

### "ModuleNotFoundError: No module named 'flask'"
- ❌ No instalaste dependencias
- ✅ Ejecuta: `pip install -r backend/requirements.txt`

---

## 📊 Estructura de Archivos Importantes

```
Mini_POS/
├── run.py              ← Ejecutar esto para iniciar
├── check.py            ← Ejecutar esto para verificar requisitos
├── init_db.py          ← Ejecutar esto para crear BD
├── backend/
│   ├── app.py          ← Servidor Flask
│   ├── routes.py       ← Endpoints API
│   └── config.py       ← Configuración
├── frontend/
│   └── index.html      ← Interfaz web
├── database/
│   └── schema.sql      ← Script de BD
└── README.md           ← Documentación completa
```

---

## 🎯 Próximos Pasos

Después de que todo funcione:

1. **Agregar más productos** — Edita `database/schema.sql` con `INSERT`
2. **Cambiar puerto** — En `backend/app.py`: `app.run(port=3000)`
3. **Autenticación** — Agrega login de usuarios
4. **Reportes** — Genera reportes de ventas
5. **Deployment** — Publica en servidor (Heroku, AWS, etc.)

---

## 📞 Necesitas Ayuda?

Revisa el **README.md** completo para más detalles sobre:
- Configuración avanzada
- API endpoints
- Solución de problemas
- Seguridad
- Próximas mejoras sugeridas

---

**¡Listo! Ya tienes Mini POS funcional 🚀**
