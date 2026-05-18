# Mini POS e Inventario (Flask + MySQL)

Proyecto de ejemplo que demuestra un backend transaccional en Flask con MySQL (ACID) y un frontend minimalista.

Requisitos:
- Python 3.8+
- MySQL/MariaDB
- Node no es necesario (frontend estático)

Pasos rápidos:

1) Crear la base de datos y tablas

    mysql -u root -p < database/schema.sql

2) Crear y activar un entorno virtual (Windows PowerShell):

    python -m venv .venv
    .\.venv\Scripts\Activate.ps1

3) Instalar dependencias del backend:

    pip install -r backend/requirements.txt

4) Ajustar la conexión a la base de datos (opcional):

   - Edita `backend/config.py` o exporta la variable de entorno `DATABASE_URL`.
   - Formato: `mysql+pymysql://user:password@host:3306/pos_inventario`

5) Ejecutar la aplicación Flask (desde la carpeta `backend`):

    python app.py

6) Servir el frontend (desde la carpeta `frontend`) — opción rápida:

    python -m http.server 8000

   Luego abre `http://localhost:8000` en el navegador. El frontend hace peticiones a `http://localhost:5000`.

Notas de diseño:
- El endpoint `/api/ventas` usa transacciones y `SELECT ... FOR UPDATE` para garantizar que el stock se valida y reduce de forma segura.
- Si falla cualquiera de las validaciones, la transacción se revierte con `session.rollback()` y la venta no se guarda.

Próximos pasos sugeridos:
- Añadir autenticación y control de usuarios.
- Agregar manejo más fino de errores y logs.
- Implementar tests automáticos de integración que simulen concurrencia.
