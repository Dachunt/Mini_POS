import os

class Config:
    """Configuración segura de la aplicación Flask-POS"""
    
    # Clave secreta para sesiones y seguridad
    SECRET_KEY = os.environ.get('SECRET_KEY', 'clave-secreta-pos-2026-cambiar-en-produccion')
    
    # Configuración de la base de datos MySQL
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'mysql+pymysql://root:@localhost:3306/pos_inventario'
    )
    
    # No alertar sobre cambios en modelos en cada request
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Limitar tamaño de JSON para requests
    MAX_CONTENT_LENGTH = 1024 * 1024  # 1MB
    
    # Habilitar modo debug solo en desarrollo (verificar variable de entorno)
    DEBUG = os.environ.get('FLASK_ENV') == 'development'