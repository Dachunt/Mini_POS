from flask import Blueprint, request, jsonify
from decimal import Decimal, InvalidOperation
from sqlalchemy.exc import SQLAlchemyError
import logging

from models import db, Producto, Venta, DetalleVenta

logger = logging.getLogger(__name__)

api_bp = Blueprint('api_bp', __name__)


@api_bp.route('/api/productos', methods=['GET', 'HEAD'])
def listar_productos():
    """
    GET /api/productos
    Retorna lista de todos los productos con stock actual.
    HEAD /api/productos - para health check
    """
    try:
        productos = Producto.query.all()
        
        if request.method == 'HEAD':
            return '', 200
            
        return jsonify([p.to_dict() for p in productos]), 200
    except Exception as e:
        logger.error(f"Error listando productos: {e}")
        return jsonify({'error': 'Error al obtener productos'}), 500


@api_bp.route('/api/productos/<int:producto_id>', methods=['GET'])
def obtener_producto(producto_id):
    """
    GET /api/productos/<id>
    Retorna un producto específico con sus detalles.
    """
    try:
        producto = Producto.query.get_or_404(producto_id)
        return jsonify(producto.to_dict()), 200
    except Exception as e:
        logger.error(f"Error obteniendo producto {producto_id}: {e}")
        return jsonify({'error': f'Producto {producto_id} no encontrado'}), 404


@api_bp.route('/api/ventas', methods=['POST'])
def crear_venta():
    """
    POST /api/ventas
    
    Crea una nueva venta con transacción ACID garantizada.
    
    Request body:
    {
        "metodo_pago": "efectivo|tarjeta|transferencia",
        "items": [
            {
                "producto_id": 1,
                "cantidad": 5,
                "precio_unitario": 15.50
            },
            ...
        ]
    }
    
    Response (201):
    {
        "id": 1,
        "metodo_pago": "efectivo",
        "total": 77.50,
        "created_at": "2026-05-17T...",
        "detalles": [...]
    }
    """
    
    # Validar Content-Type
    if not request.is_json:
        return jsonify({
            'error': 'Content-Type debe ser application/json'
        }), 400
    
    payload = request.get_json() or {}
    
    # Validar campos requeridos
    metodo_pago = payload.get('metodo_pago', '').strip().lower()
    items = payload.get('items', [])
    
    if not metodo_pago:
        return jsonify({'error': 'metodo_pago es requerido'}), 400
    
    if metodo_pago not in ['efectivo', 'tarjeta', 'transferencia']:
        return jsonify({
            'error': 'metodo_pago debe ser: efectivo, tarjeta o transferencia'
        }), 400
    
    if not isinstance(items, list) or not items:
        return jsonify({'error': 'items debe ser un array no vacío'}), 400
    
    session = db.session
    
    try:
        total = Decimal('0.00')
        productos_map = {}
        
        # Validar todos los items antes de la transacción
        for idx, it in enumerate(items):
            # Validar estructura del item
            if not isinstance(it, dict):
                return jsonify({
                    'error': f'Item {idx} no es un objeto'
                }), 400
            
            try:
                pid = int(it.get('producto_id', 0))
                cantidad = int(it.get('cantidad', 0))
                precio_unitario = Decimal(str(it.get('precio_unitario', 0)))
            except (ValueError, InvalidOperation, TypeError):
                return jsonify({
                    'error': f'Item {idx}: valores numéricos inválidos'
                }), 400
            
            if pid <= 0:
                return jsonify({
                    'error': f'Item {idx}: producto_id debe ser > 0'
                }), 400
            
            if cantidad <= 0 or cantidad > 999:
                return jsonify({
                    'error': f'Item {idx}: cantidad debe estar entre 1 y 999'
                }), 400
            
            if precio_unitario <= 0:
                return jsonify({
                    'error': f'Item {idx}: precio_unitario debe ser > 0'
                }), 400
        
        # Ejecutar transacción con lock pesimista
        with session.begin():
            for idx, it in enumerate(items):
                pid = int(it.get('producto_id'))
                cantidad = int(it.get('cantidad'))
                
                # Lock SELECT FOR UPDATE para evitar race conditions
                producto = session.query(Producto).with_for_update().filter_by(
                    id=pid
                ).first()
                
                if not producto:
                    session.rollback()
                    return jsonify({
                        'error': f'Producto {pid} no encontrado'
                    }), 404
                
                # Validar stock disponible
                if producto.stock_actual < cantidad:
                    session.rollback()
                    return jsonify({
                        'error': (
                            f'Stock insuficiente para "{producto.nombre}". '
                            f'Disponible: {producto.stock_actual}, '
                            f'Solicitado: {cantidad}'
                        )
                    }), 400
                
                # Descontar stock
                producto.stock_actual -= cantidad
                productos_map[pid] = (producto, cantidad)
                
                # Calcular total
                precio_calc = Decimal(str(producto.precio))
                total += precio_calc * cantidad
            
            # Crear registro de venta
            venta = Venta(metodo_pago=metodo_pago, total=total)
            session.add(venta)
            session.flush()  # Obtener venta.id sin commitear
            
            # Crear detalles de venta
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
        
        # Transacción commiteada exitosamente
        logger.info(
            f"Venta #{venta.id} creada: {len(items)} items, "
            f"total: ${total}, método: {metodo_pago}"
        )
        return jsonify(venta.to_dict()), 201
        
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Error de BD al crear venta: {e}")
        return jsonify({
            'error': 'Error en la base de datos'
        }), 500
    except Exception as e:
        session.rollback()
        logger.error(f"Error inesperado al crear venta: {e}")
        return jsonify({
            'error': 'Error interno del servidor'
        }), 500

