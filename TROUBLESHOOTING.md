# 🐛 Debugging y Troubleshooting — Mini POS

## Logs y Debugging

### Ver logs en la terminal

Cuando ejecutes `python run.py` o `python backend/app.py`, verás logs como:

```
INFO:werkzeug:Running on http://0.0.0.0:5000
INFO:werkzeug:GET /api/productos HTTP/1.1" 200
INFO:werkzeug:POST /api/ventas HTTP/1.1" 201
```

### Habilitar debug más detallado

En `backend/app.py`, busca:
```python
app.run(debug=True, ...)
```

Con `debug=True`:
- ✅ Los cambios en el código se recargan automáticamente
- ✅ Verás trazas de error detalladas
- ⚠️ No usar en producción

---

## Problemas y Soluciones

### 1️⃣ "Address already in use" (Puerto 5000 ocupado)

**Error:**
```
Error: [Errno 48] Address already in use
```

**Soluciones:**

A) Matar el proceso en el puerto:
```bash
# Linux/Mac
lsof -i :5000
kill -9 <PID>

# Windows PowerShell
Get-Process -Id (Get-NetTCPConnection -LocalPort 5000).OwningProcess | Stop-Process
```

B) Usar otro puerto:
```python
# En backend/app.py
app.run(port=5001)  # Cambiar 5000 por otro puerto
```

### 2️⃣ "Cannot find module 'flask'" (Falta instalar)

**Error:**
```
ModuleNotFoundError: No module named 'flask'
```

**Soluciones:**

A) Activar entorno virtual:
```bash
# Windows
.venv\Scripts\activate.bat

# Linux/Mac
source .venv/bin/activate
```

B) Instalar dependencias:
```bash
pip install -r backend/requirements.txt
```

C) Verificar que estamos en el directorio correcto:
```bash
pwd  # o cd en Windows
# Debería terminar en: /D/expo/Mini_POS
```

### 3️⃣ "Connection refused" (MySQL no conecta)

**Error en consola:**
```
Can't connect to MySQL server on 'localhost'
```

**Verificar MySQL:**

```bash
# Ver si MySQL está corriendo
# Windows: Ver en Servicios (services.msc) → MySQL
# Linux
sudo systemctl status mysql

# Conectar manualmente
mysql -u root
```

**Si MySQL no está corriendo:**

```bash
# Windows
net start MySQL80  # o el nombre de tu servicio

# Linux
sudo systemctl start mysql
```

**Verificar credenciales en `backend/config.py`:**
```python
# Por defecto, sin contraseña:
'mysql+pymysql://root:@localhost:3306/pos_inventario'

# Si tienes contraseña:
'mysql+pymysql://root:MI_CONTRASEÑA@localhost:3306/pos_inventario'
```

### 4️⃣ "Unknown database 'pos_inventario'"

**Error:**
```
(pymysql.err.DatabaseError) [1049] Unknown database 'pos_inventario'
```

**Solución — Crear la base de datos:**

```bash
# Opción A: Script Python
python init_db.py

# Opción B: Manualmente
mysql -u root < database/schema.sql

# Opción C: Desde MySQL
mysql -u root
mysql> SOURCE database/schema.sql;
```

### 5️⃣ "Table producto doesn't exist"

**Error:**
```
pymysql.err.ProgrammingError [1146] Table 'pos_inventario.producto' doesn't exist
```

**Solución — Ejecutar schema.sql:**

```bash
mysql -u root -p pos_inventario < database/schema.sql
```

O desde MySQL:
```sql
mysql> USE pos_inventario;
mysql> SOURCE database/schema.sql;
```

### 6️⃣ Frontend dice "⚠️ Sin conexión"

**Error:** Punto rojo en header diciendo "Sin conexión"

**Causas posibles:**

A) Backend no está corriendo
```bash
# En otra terminal
python run.py
```

B) Firewall bloqueando puerto 5000
```bash
# Windows Firewall: Agregar excepción para puerto 5000
```

C) API_BASE incorrecta en `frontend/index.html`
```javascript
// Línea ~278 en index.html
const API_BASE = '';  // Debería estar vacío si Flask sirve el HTML
```

---

## API Testing con cURL

### Listar todos los productos

```bash
curl http://localhost:5000/api/productos
```

**Respuesta esperada:**
```json
[
  {
    "id": 1,
    "nombre": "Coca-Cola 355ml",
    "precio": 15.5,
    "stock_actual": 100
  }
]
```

### Obtener un producto específico

```bash
curl http://localhost:5000/api/productos/1
```

### Crear una venta

```bash
curl -X POST http://localhost:5000/api/ventas \
  -H "Content-Type: application/json" \
  -d '{
    "metodo_pago": "efectivo",
    "items": [
      {"producto_id": 1, "cantidad": 2, "precio_unitario": 15.50},
      {"producto_id": 2, "cantidad": 1, "precio_unitario": 18.00}
    ]
  }'
```

**Respuesta esperada (201):**
```json
{
  "id": 1,
  "metodo_pago": "efectivo",
  "total": 49.00,
  "created_at": "2026-05-17T20:35:10.123456",
  "detalles": [...]
}
```

### Verificar que el stock se actualizó

```bash
curl http://localhost:5000/api/productos/1
```

Deberías ver `"stock_actual": 98` (era 100, compramos 2)

---

## Verificar Base de Datos

### Conectar a MySQL

```bash
mysql -u root
```

### Ver todas las bases de datos

```sql
SHOW DATABASES;
```

Deberías ver `pos_inventario`

### Usar la base de datos

```sql
USE pos_inventario;
```

### Ver tabla de productos

```sql
SELECT * FROM producto;
```

### Ver tabla de ventas

```sql
SELECT * FROM venta;
```

### Ver detalles de ventas

```sql
SELECT * FROM detalle_venta;
```

### Verificar stock después de una venta

```sql
SELECT id, nombre, stock_actual FROM producto WHERE id = 1;
```

---

## Problemas Avanzados

### Race condition en stock (Producto)

Si múltiples clientes compran simultáneamente el mismo producto:

**Solución ya implementada:**
- Routes.py usa `SELECT ... FOR UPDATE` (lock pesimista)
- La transacción es ACID
- El stock siempre es correcto

**Verificar:**
```sql
-- Ver locks activos en MySQL
SHOW ENGINE INNODB STATUS;
```

### Transacción abortada

Si ves "Transaction was aborted" en el navegador:

Causas posibles:
- Producto no existe (`producto_id` inválido)
- Stock insuficiente
- Cantidad inválida (≤ 0)
- Precio negativo

**Verificar:** Revisa los logs en la consola de Flask

### Base de datos muy lenta

Si las consultas son lentas:

**Verificar índices:**
```sql
SHOW INDEXES FROM producto;
SHOW INDEXES FROM venta;
SHOW INDEXES FROM detalle_venta;
```

**Schema.sql ya incluye índices en:**
- `producto.nombre`
- `producto.stock_actual`
- `venta.created_at`
- `venta.metodo_pago`
- `detalle_venta.venta_id`
- `detalle_venta.producto_id`

---

## Performance Monitoring

### Ver número de ventas por hora

```sql
SELECT DATE_FORMAT(created_at, '%Y-%m-%d %H:00:00') AS hora,
       COUNT(*) AS num_ventas,
       SUM(total) AS ingresos
FROM venta
GROUP BY hora
ORDER BY hora DESC;
```

### Productos más vendidos

```sql
SELECT 
  p.nombre,
  SUM(dv.cantidad) AS total_vendido,
  SUM(dv.subtotal) AS ingresos
FROM detalle_venta dv
JOIN producto p ON dv.producto_id = p.id
GROUP BY p.id
ORDER BY total_vendido DESC;
```

---

## Seguridad: Verificar Protecciones

### ✅ Validaciones en Backend (routes.py)

- [x] Valida que `metodo_pago` es uno de: efectivo, tarjeta, transferencia
- [x] Valida que `cantidad` > 0 y ≤ 999
- [x] Valida que `precio_unitario` > 0
- [x] Valida que el producto existe
- [x] Valida stock disponible
- [x] Usa transacciones ACID
- [x] Usa locks pesimistas (SELECT FOR UPDATE)

### ✅ CORS (app.py)

- [x] Configurado para aceptar solo `localhost` por defecto
- [x] Personalizable en producción

### ✅ Logging (routes.py)

- [x] Registra ventas creadas exitosamente
- [x] Registra errores de BD
- [x] Registra errores inesperados

---

## Checkpoints para Validar Todo

- [ ] `python check.py` — Todos los requisitos OK
- [ ] `python init_db.py` — BD creada
- [ ] `python run.py` — Flask corriendo sin errores
- [ ] `http://localhost:5000` — Página carga
- [ ] "MySQL conectado" — Punto verde en header
- [ ] 10 productos visibles en catálogo
- [ ] Búsqueda funciona
- [ ] Agregar al carrito funciona
- [ ] Modificar cantidad funciona
- [ ] Finalizar venta crea recibo
- [ ] Stock se actualiza
- [ ] `SELECT * FROM venta;` muestra la venta creada

---

**¡Si todo esto pasa, tu Mini POS está completamente funcional! 🎉**
