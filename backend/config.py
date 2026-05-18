import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'clave-secreta-pos-2026')
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'mysql+pymysql://root:@localhost:3306/pos_inventario'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False