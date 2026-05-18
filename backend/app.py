from flask import Flask, send_from_directory
from flask_cors import CORS
import os

from config import Config
from models import db
from routes import api_bp


def create_app():
    app = Flask(__name__, static_folder='../frontend', static_url_path='/static')
    app.config.from_object(Config)
    CORS(app)

    db.init_app(app)
    app.register_blueprint(api_bp)

    # Servir index.html en la raíz
    @app.route('/')
    def index():
        return send_from_directory(os.path.join(os.path.dirname(__file__), '..', 'frontend'), 'index.html')

    with app.app_context():
        db.create_all()

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
