from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
import os
import logging

from config import Config
from models import db
from routes import api_bp

# Configurar logging básico
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_app():
    """Factory para crear y configurar la aplicación Flask"""
    
    app = Flask(
        __name__,
        static_folder='../frontend',
        static_url_path='/static'
    )
    
    # Cargar configuración
    app.config.from_object(Config)
    
    # Configurar CORS con restricciones básicas (ajusta según necesites)
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:*", "http://127.0.0.1:*"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type"]
        }
    })
    
    # Inicializar base de datos
    db.init_app(app)
    
    # Registrar blueprints
    app.register_blueprint(api_bp)
    
    # Servir index.html en la raíz
    @app.route('/')
    def index():
        return send_from_directory(
            os.path.join(os.path.dirname(__file__), '..', 'frontend'),
            'index.html'
        )
    
    # Manejador para archivos estáticos del frontend
    @app.route('/static/<path:filename>')
    def static_files(filename):
        return send_from_directory(
            os.path.join(os.path.dirname(__file__), '..', 'frontend'),
            filename
        )
    
    # Manejador de errores 404
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Ruta no encontrada'}), 404
    
    # Manejador de errores 500
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Error interno: {error}")
        return jsonify({'error': 'Error interno del servidor'}), 500
    
    # Crear contexto de aplicación e inicializar BD
    with app.app_context():
        db.create_all()
        logger.info("Base de datos inicializada")
    
    return app


if __name__ == '__main__':
    app = create_app()
    logger.info("Iniciando servidor Flask en http://0.0.0.0:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)

