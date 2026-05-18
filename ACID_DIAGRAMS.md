# 📊 DIAGRAMA DE FLUJO ACID - Mini POS

## 🔄 Flujo Completo de Venta con Garantías ACID

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLIENTE (Frontend)                          │
│                                                                     │
│  POST /api/ventas                                                  │
│  {                                                                 │
│    "metodo_pago": "efectivo",                                     │
│    "items": [                                                      │
│      {"producto_id": 1, "cantidad": 2, "precio_unitario": 15.50} │
│    ]                                                               │
│  }                                                                 │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│               SERVIDOR FLASK (backend/routes.py)                    │
│                                                                     │
│  1️⃣ VALIDAR JSON (Consistencia)                                    │
│  ├─ ¿Es JSON válido? ✓                                             │
│  ├─ ¿Tiene metodo_pago? ✓                                          │
│  ├─ ¿metodo_pago es válido? ✓ (efectivo/tarjeta/transferencia)    │
│  └─ ¿Tiene items no vacío? ✓                                       │
│                                                                     │
│  2️⃣ VALIDAR ITEMS (Consistencia)                                   │
│  ├─ Para cada item:                                                │
│  │  ├─ ¿producto_id es número > 0? ✓                             │
│  │  ├─ ¿cantidad es número 1-999? ✓                              │
│  │  └─ ¿precio_unitario > 0? ✓                                   │
│  └─ ❌ Si algo falla → Retorna 400 (SIN TOCAR BD)                │
│                                                                     │
│  3️⃣ INICIAR TRANSACCIÓN (Atomicidad)                              │
│  └─ session.begin() ← BEGIN TRANSACTION                           │
│                                                                     │
│  4️⃣ PARA CADA ITEM (Aislamiento + Atomicidad)                     │
│  │                                                                  │
│  ├─ SELECT ... FOR UPDATE producto WHERE id=? (LOCK)             │
│  │  │                                                              │
│  │  ├─ Producto no existe?                                        │
│  │  │  └─ session.rollback() → ❌ ROLLBACK COMPLETO             │
│  │  │     Retorna 404 (Atomicidad)                               │
│  │  │                                                              │
│  │  ├─ stock_actual < cantidad?                                   │
│  │  │  └─ session.rollback() → ❌ ROLLBACK COMPLETO             │
│  │  │     Retorna 400 (Atomicidad + Consistencia)               │
│  │  │                                                              │
│  │  └─ ✓ Stock OK → Descontar stock                              │
│  │     producto.stock_actual -= cantidad                          │
│  │                                                                  │
│  └─ LIBERAR LOCK (FOR UPDATE se libera)                          │
│                                                                     │
│  5️⃣ CREAR VENTA (Atomicidad)                                       │
│  ├─ INSERT INTO venta (metodo_pago, total, ...)                   │
│  ├─ session.flush() → Obtiene venta.id SIN commitear             │
│  └─ ✓ Venta pendiente de confirmar                               │
│                                                                     │
│  6️⃣ CREAR DETALLES (Atomicidad)                                    │
│  ├─ Para cada item:                                               │
│  │  └─ INSERT INTO detalle_venta (...)                           │
│  └─ ✓ Detalles pendientes de confirmar                           │
│                                                                     │
│  7️⃣ COMMIT TRANSACCIÓN (Durabilidad)                              │
│  └─ ✓ session.commit() (salir de with session.begin())           │
│     ├─ stock_actual actualizado ✓                                 │
│     ├─ venta guardada ✓                                           │
│     ├─ detalle_venta guardado ✓                                   │
│     └─ Datos persisten en MySQL ✓ (DURABILIDAD)                  │
│                                                                     │
│  8️⃣ RETORNAR 201 (Éxito)                                          │
│  └─ { "id": 1, "metodo_pago": "efectivo", ... }                  │
│                                                                     │
└─────────────────────────┬──────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    BASE DE DATOS (MySQL/InnoDB)                     │
│                                                                     │
│  tabla producto:                                                   │
│  ├─ id=1, nombre=Coca-Cola, stock_actual=98 ✓ (ACTUALIZADO)      │
│                                                                     │
│  tabla venta:                                                      │
│  └─ id=1, metodo_pago=efectivo, total=31.00, ✓ (NUEVA)           │
│                                                                     │
│  tabla detalle_venta:                                              │
│  └─ id=1, venta_id=1, producto_id=1, cantidad=2 ✓ (NUEVA)        │
│                                                                     │
│  Redo Log: Transacción registrada en disco ✓ (DURABILIDAD)       │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## ⚠️ Flujo si algo FALLA

```
┌──────────────────────────────────────────────────────────────────────┐
│                    ESCENARIO: Stock insuficiente                     │
└──────────────────────────────────────────────────────────────────────┘

        ┌─────────────────────────────────────────────────────┐
        │ POST /api/ventas                                    │
        │ items: [{"producto_id": 1, "cantidad": 999, ...}] │
        └─────────┬───────────────────────────────────────────┘
                  │
                  ▼
        ✓ JSON válido
        ✓ Items válidos (números, rangos OK)
        │
        ├─ BEGIN TRANSACTION
        │
        ├─ SELECT ... FOR UPDATE producto WHERE id=1
        │  stock_actual = 100
        │  ¿100 < 999? → ❌ SÍ
        │
        ├─ ❌ ERROR VALIDACIÓN
        │  └─ session.rollback()
        │     ├─ Deshace cambios de stock
        │     ├─ Cancela INSERT de venta
        │     ├─ Cancela INSERT de detalles
        │     └─ Transacción: CANCELADA
        │
        └─ Retorna 400
           {
             "error": "Stock insuficiente para 'Coca-Cola'. "
                      "Disponible: 100, Solicitado: 999"
           }

        ✓ RESULTADO:
        ├─ Producto: stock_actual = 100 (SIN CAMBIOS) ✓
        ├─ Venta: NO CREADA ✓
        ├─ Detalles: NO CREADOS ✓
        └─ Base de datos: CONSISTENTE ✓
```

---

## 🚨 Flujo si el SERVIDOR EXPLOTA

```
┌──────────────────────────────────────────────────────────────────────┐
│  ESCENARIO: Flask crash DESPUÉS de validar pero ANTES de COMMIT      │
└──────────────────────────────────────────────────────────────────────┘

        ┌──────────────────────────────────┐
        │ Transacción en progreso         │
        │ BEGIN TRANSACTION ← ACTIVA      │
        │ SELECT ... FOR UPDATE ✓         │
        │ stock = 100                     │
        │ (cambios en memoria, NO en BD)  │
        │                                 │
        │ ❌ FLASK CRASH                 │
        │    (Ctrl+C, power outage, etc) │
        └──────────────────────────────────┘
                    │
                    ▼
        ❌ Transacción NO completada
        ❌ No llegó a session.commit()
        ├─ MySQL detecta conexión perdida
        ├─ Automáticamente ROLLBACK
        └─ Cambios en memoria = DESCARTADOS

        ✓ RESULTADO:
        ├─ Producto: stock_actual = 100 ✓ (NUNCA cambió en BD)
        ├─ Venta: NO CREADA ✓
        ├─ Detalles: NO CREADOS ✓
        └─ Base de datos: CONSISTENTE ✓

        📝 LOG ANTES DEL CRASH:
           "Venta #5 creada: 2 items, total: $31.00, método: efectivo"
           ← Este log NO aparece (no llegó a logger.info())
```

---

## 💾 Flujo si el SERVIDOR EXPLOTA DESPUÉS de COMMIT

```
┌──────────────────────────────────────────────────────────────────────┐
│  ESCENARIO: Flask crash DESPUÉS de COMMIT (ya guardado en BD)        │
└──────────────────────────────────────────────────────────────────────┘

        ┌──────────────────────────────────┐
        │ Transacción completada          │
        │ ✓ session.commit()             │
        │ ✓ Datos escritos en BD         │
        │ ✓ Redo log en disco            │
        │ ✓ logger.info() ejecutado      │
        │ ❌ FLASK CRASH (antes de      │
        │    enviar respuesta HTTP)      │
        └──────────────────────────────────┘
                    │
                    ▼
        ✓ Transacción YA GUARDADA
        ✓ MySQL no la deshace
        ✓ Datos en disco (persisten)
        ├─ Cliente NO recibe respuesta 201
        │  (timeout, conexión cerrada)
        │
        └─ Cliente reinicia el sistema
           ├─ Abre navegador
           ├─ Recarga catálogo
           ├─ ¡Stock ya fue actualizado!
           └─ Puede revertir si quiere

        ✓ RESULTADO:
        ├─ Producto: stock_actual = 98 ✓ (ya cambió)
        ├─ Venta: CREADA ✓ (ya guardada)
        ├─ Detalles: CREADOS ✓ (ya guardados)
        ├─ Base de datos: CONSISTENTE ✓
        └─ Durabilidad: ✓ Datos persistieron
```

---

## 🔀 Flujo Paralelo (Dos Clientes Simultáneos)

```
CLIENTE A                          CLIENTE B
┌──────────────────┐             ┌──────────────────┐
│ POST /ventas     │             │ POST /ventas     │
│ producto_id: 1  │             │ producto_id: 1  │
│ cantidad: 50    │             │ cantidad: 40    │
└────────┬─────────┘             └────────┬─────────┘
         │                                │
         ▼                                ▼
    BEGIN TRANSACTION              BEGIN TRANSACTION
         │                                │
         ▼                                ▼
    SELECT ... FOR UPDATE          SELECT ... FOR UPDATE
    producto WHERE id=1            producto WHERE id=1
         │                                │
    ✓ LOCK ADQUIRIDO ✓            ❌ ESPERA LOCK ❌
    stock = 100                        │
    100 < 50? → NO ✓                   │
         │                                │
    stock = 50                          │ (esperando...)
         │                                │
    INSERT venta...                     │
    INSERT detalle...                   │
         │                                │
    COMMIT ← LIBERA LOCK                 │
         │                                ▼
         │                          ✓ LOCK ADQUIRIDO ✓
         │                          stock = 50 (no 100!)
         │                          50 < 40? → NO ✓
         │                                │
         │                          stock = 10
         │                                │
         │                          INSERT venta...
         │                          INSERT detalle...
         │                                │
         │                          COMMIT
         │                                │
         ▼                                ▼
    Base de datos:
    ├─ stock_actual = 10 ✓ (CORRECTO: 100 - 50 - 40)
    ├─ 2 ventas creadas ✓
    ├─ 2 detalles creados ✓
    └─ SIN RACE CONDITIONS ✓ (por SELECT FOR UPDATE)
```

---

## 📋 Tabla Comparativa: CON vs SIN ACID

| Operación | SIN ACID ❌ | CON ACID (Mini POS) ✅ |
|-----------|-----------|-----|
| **Compra 1: stock=100, quiero 50** |  |  |
| Paso 1: Validar | ✓ | ✓ |
| Paso 2: Restar stock | ✓ | ✓ |
| Paso 2.5: **CRASH** | 💥 | 💥 |
| Resultado | Stock=-50 ❌ | Stock=100 ✓ |
| | *Inconsistente* | *Consistente (ROLLBACK)* |
| **Dos clientes simultáneamente** |  |  |
| Cliente A: stock=100, quiero 100 | Race condition | Lock FOR UPDATE |
| Cliente B: stock=100, quiero 100 | Race condition | Espera turno |
| Resultado A | stock=0 ✓ | stock=0 ✓ |
| Resultado B | stock=0 ❌ | stock=-100 ❌ |
| | *Ambos reciben OK* | *B recibe error 400* |
| | *Stock negativo* | *Stock siempre >= 0* |
| **Producto no existe** |  |  |
| Consulta BD | Falla silenciosa | Validación clara |
| Resultado | Excepción | Error 404 + Rollback |
| Stock | Posiblemente cambiado | SIN CAMBIOS |
| | *Inconsistente* | *Consistente* |
| **Servidor crash después de guardar** |  |  |
| Datos guardados | ? | ✓ En disco |
| Recuperación | Posible corrupción | Íntegro |
| Replay transacción | Difícil | Imposible (ya está) |

---

## ✅ GARANTÍAS ACID EN MINI POS

### ATOMICIDAD ✅
- `with session.begin()` crea transacción explícita
- `session.rollback()` deshace TODO si algo falla
- No hay estados intermedios

### CONSISTENCIA ✅
- Validaciones previas previenen datos inválidos
- Uso de `Decimal` para dinero exacto
- Foreign keys con integridad referencial
- Nunca stock negativo

### AISLAMIENTO ✅
- `.with_for_update()` lock pesimista
- Previene race conditions
- Múltiples clientes sin interferencia

### DURABILIDAD ✅
- `session.commit()` persiste en disk
- MySQL InnoDB redo/undo logs
- Recuperación de crashes automática

---

**Mini POS implementa 100% ACID**  
**Seguro para operaciones financieras ✅**
