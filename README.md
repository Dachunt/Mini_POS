# Mini POS — Sistema de Punto de Venta e Inventario

Sistema minimalista de **Punto de Venta (POS)** con gestión de inventario en tiempo real, construido con Flask (Python) y MySQL.

## ✨ Características

- ✅ Interfaz moderna y responsive
- ✅ Listado de productos con búsqueda en tiempo real
- ✅ Carrito de compras dinámico
- ✅ 3 métodos de pago (efectivo, tarjeta, transferencia)
- ✅ Transacciones ACID con lock pesimista (SELECT FOR UPDATE)
- ✅ Stock actualizado automáticamente
- ✅ Recibo de venta generado al finalizar
- ✅ Indicador de estado de conexión a BD
- ✅ Validación exhaustiva de datos
- ✅ Manejo seguro de errores

## 🛠️ Requisitos

- **Python** 3.8 o superior
- **MySQL** 5.7+ o **MariaDB** 10.3+
- **pip** (gestor de paquetes de Python)

## 📋 Instalación Rápida

### 1. Clonar o descargar el proyecto

```bash
cd D:\expo\Mini_POS
```

### 2. Crear entorno virtual (recomendado)

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r backend/requirements.txt
```

### 4. Crear la base de datos

**Opción A: Usando el script Python** (recomendado)
```bash
python init_db.py
```

**Opción B: Manualmente con MySQL**
```bash
mysql -u root < database/schema.sql
```

**Opción C: Desde cliente MySQL**
```sql
-- En tu cliente MySQL:
mysql> SOURCE database/schema.sql;
```

> **Nota:** Si tu MySQL tiene contraseña, ajusta `backend/config.py`:
> ```python
> 'mysql+pymysql://root:tu_contraseña@localhost:3306/pos_inventario'
> ```

### 5. Ejecutar la aplicación

**Opción A: Script automático** (recomendado)
```bash
python run.py
```

**Opción B: Desde terminal**
```bash
cd backend
python app.py
```

### 6. Abrir en navegador

Abre tu navegador y ve a:
```
http://localhost:5000
```

## 🧪 Pruebas

### Test básico en navegador

1. **Listar productos:**
   - Deberías ver 10 productos en el catálogo
   - Busca por nombre (ej: "Coca", "Arroz")

2. **Agregar al carrito:**
   - Haz clic en un producto o en el botón `+`
   - Verifica que el badge del carrito se actualiza

3. **Modificar cantidad:**
   - Usa los botones `−` y `+` en el carrito
   - Verifica que el total se calcula correctamente

4. **Finalizar venta:**
   - Selecciona método de pago
   - Haz clic en "Finalizar Venta"
   - Verifica que aparece el recibo
   - Comprueba que el stock se actualizó

### Test con cURL (desde otra terminal)

**Listar productos:**
```bash
curl http://localhost:5000/api/productos
```

**Crear una venta:**
```bash
curl -X POST http://localhost:5000/api/ventas \
  -H "Content-Type: application/json" \
  -d '{
    "metodo_pago": "efectivo",
    "items": [
      {"producto_id": 1, "cantidad": 2, "precio_unitario": 15.50},
      {"producto_id": 3, "cantidad": 1, "precio_unitario": 22.50}
    ]
  }'
```

**Verificar stock (producto ID 1):**
```bash
curl http://localhost:5000/api/productos/1
```

## 📁 Estructura del Proyecto

```
Mini_POS/
├── backend/
│   ├── app.py              # Aplicación Flask principal
│   ├── config.py           # Configuración (BD, claves, etc.)
│   ├── models.py           # Modelos SQLAlchemy (Producto, Venta, etc.)
│   ├── routes.py           # Endpoints API (/api/productos, /api/ventas)
│   └── requirements.txt    # Dependencias Python
├── frontend/
│   └── index.html          # Interfaz única en HTML/CSS/JS
├── database/
│   └── schema.sql          # Script de creación de BD y datos iniciales
├── .env.example            # Variables de entorno (ejemplo)
├── init_db.py              # Script para inicializar la BD
├── run.py                  # Script para ejecutar la app
├── .gitignore              # Archivos ignorados por git
└── README.md               # Este archivo
```

## ⚙️ Configuración

### Variables de entorno (`.env`)

Copia `.env.example` a `.env`:
```bash
cp .env.example .env
```

Edita `.env` con tus valores:
```env
FLASK_ENV=development
SECRET_KEY=tu-clave-secreta-super-segura
DATABASE_URL=mysql+pymysql://root:contraseña@localhost:3306/pos_inventario
```

## 🔒 Seguridad

- ✅ Validación exhaustiva de entrada (tipos, rangos, campos requeridos)
- ✅ Transacciones ACID con lock pesimista (SELECT FOR UPDATE)
- ✅ Prevención de race conditions en stock
- ✅ Manejo seguro de decimales (Decimal en lugar de float)
- ✅ CORS configurado (ajusta orígenes permitidos en producción)
- ✅ Logging de transacciones importantes
- ✅ Manejo centralizado de errores

## 🐛 Solución de problemas

### "Connection refused" (Puerto 5000)
- Flask ya está corriendo en otro terminal
- Detén todos los servidores Flask
- O cambia el puerto en `app.py`: `app.run(port=5001)`

### "Error de conexión a MySQL"
- Verifica que MySQL está corriendo
  ```bash
  # Windows: verifica en Servicios
  # Linux: sudo systemctl status mysql
  ```
- Verifica credenciales en `backend/config.py`
- Verifica que la BD `pos_inventario` existe:
  ```sql
  SHOW DATABASES;
  ```

### "ModuleNotFoundError: No module named 'flask'"
- Activa el entorno virtual
- Instala dependencias: `pip install -r backend/requirements.txt`

### Datos duplicados en BD
- La tabla `INSERT` se ejecuta cada vez que creas tablas
- Usa `INSERT ... ON DUPLICATE KEY UPDATE` o elimina/crea la BD:
  ```sql
  DROP DATABASE pos_inventario;
  ```

## 📚 Endpoints API

### GET /api/productos
Retorna lista de todos los productos

**Response (200):**
```json
[
  {
    "id": 1,
    "nombre": "Coca-Cola 355ml",
    "precio": 15.50,
    "stock_actual": 98
  }
]
```

### GET /api/productos/{id}
Retorna un producto específico

**Response (200):**
```json
{
  "id": 1,
  "nombre": "Coca-Cola 355ml",
  "precio": 15.50,
  "stock_actual": 98
}
```

### POST /api/ventas
Crea una nueva venta (con transacción ACID)

**Request Body:**
```json
{
  "metodo_pago": "efectivo",
  "items": [
    {
      "producto_id": 1,
      "cantidad": 2,
      "precio_unitario": 15.50
    }
  ]
}
```

**Response (201):**
```json
{
  "id": 1,
  "metodo_pago": "efectivo",
  "total": 31.00,
  "created_at": "2026-05-17T20:30:45.123456",
  "detalles": [
    {
      "id": 1,
      "venta_id": 1,
      "producto_id": 1,
      "cantidad": 2,
      "precio_unitario": 15.50,
      "subtotal": 31.00
    }
  ]
}
```

## 🚀 Próximos pasos sugeridos

- [ ] Autenticación de usuarios (JWT o sesiones)
- [ ] Historial de ventas y reportes
- [ ] Sistema de categorías de productos
- [ ] Devoluciones y descuentos
- [ ] Backup automático de BD
- [ ] Tests automáticos de integración
- [ ] Deployment en servidor (AWS, Heroku, DigitalOcean)
- [ ] Mobile app (React Native, Flutter)

## 📝 Notas de diseño

- Las transacciones usan `SELECT ... FOR UPDATE` para evitar race conditions
- Los precios se calculan del `producto.precio` en tiempo de venta (no se usa el del request)
- El frontend está en HTML5 puro sin frameworks para máxima compatibilidad
- Las validaciones se hacen en backend (no confiar en frontend)

## 📄 Licencia

Proyecto de demostración educativa. Úsalo como referencia.

## ❓ Soporte

Si tienes problemas:
1. Verifica que MySQL está corriendo
2. Revisa los logs en la terminal de Flask
3. Comprueba que `database/schema.sql` se ejecutó correctamente
4. Verifica las credenciales en `backend/config.py`

---

**Versión:** 1.0.0  
**Última actualización:** Mayo 2026

