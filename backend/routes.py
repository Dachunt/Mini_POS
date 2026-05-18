from flask import Blueprint, request, jsonify
from decimal import Decimal
from sqlalchemy.exc import SQLAlchemyError

from models import db, Producto, Venta, DetalleVenta

api_bp = Blueprint('api_bp', __name__)


@api_bp.route('/api/productos', methods=['GET'])
def listar_productos():
    productos = Producto.query.all()
    return jsonify([p.to_dict() for p in productos])


@api_bp.route('/api/productos/<int:producto_id>', methods=['GET'])
def obtener_producto(producto_id):
    p = Producto.query.get_or_404(producto_id)
    return jsonify(p.to_dict())


@api_bp.route('/api/ventas', methods=['POST'])
def crear_venta():
    payload = request.get_json() or {}
    metodo_pago = payload.get('metodo_pago')
    items = payload.get('items', [])

    if not metodo_pago or not items:
        return jsonify({'error': 'metodo_pago e items son requeridos'}), 400

    session = db.session

    try:
        total = Decimal('0.00')

        # Begin explicit transaction
        with session.begin():
            # Lock and validate stock for each producto
            productos_map = {}
            for it in items:
                pid = int(it.get('producto_id'))
                cantidad = int(it.get('cantidad', 0))
                if cantidad <= 0:
                    session.rollback()
                    return jsonify({'error': 'cantidad inválida para producto {}'.format(pid)}), 400

                producto = session.query(Producto).with_for_update().filter_by(id=pid).first()
                if not producto:
                    session.rollback()
                    return jsonify({'error': f'Producto {pid} no encontrado'}), 400

                if producto.stock_actual < cantidad:
                    session.rollback()
                    return jsonify({'error': f'Stock insuficiente para {producto.nombre}'}), 400

                # reserve stock
                producto.stock_actual -= cantidad
                productos_map[pid] = (producto, cantidad)

                precio = Decimal(str(producto.precio))
                total += precio * cantidad

            # Create Venta
            venta = Venta(metodo_pago=metodo_pago, total=total)
            session.add(venta)
            session.flush()  # obtiene venta.id

            # Create DetalleVenta rows
            for pid, (producto, cantidad) in productos_map.items():
                precio_unitario = Decimal(str(producto.precio))
                subtotal = precio_unitario * cantidad
                detalle = DetalleVenta(
                    venta_id=venta.id,
                    producto_id=pid,
                    cantidad=cantidad,
                    precio_unitario=precio_unitario,
                    subtotal=subtotal,
                )
                session.add(detalle)

        # transaction committed
        return jsonify(venta.to_dict()), 201

    except SQLAlchemyError as e:
        session.rollback()
        return jsonify({'error': 'Error en la base de datos', 'detail': str(e)}), 500
    except Exception as e:
        session.rollback()
        return jsonify({'error': 'Error interno', 'detail': str(e)}), 500
