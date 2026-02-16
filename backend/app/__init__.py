# backend/app/__init__.py
from flask import Flask
from flask_cors import CORS
from app.api.correlations import correlations_bp
import logging

def create_app(config_name='development'):
    app = Flask(__name__)
    
    # Configuración
    if config_name == 'development':
        app.config['DEBUG'] = True
    else:
        app.config['DEBUG'] = False
    
    # Habilitar CORS
    CORS(app)
    
    # Registrar blueprints
    app.register_blueprint(correlations_bp)
    
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    @app.route('/')
    def index():
        return {
            'message': 'FTRT-Cambrian Correlation Project API',
            'version': '1.0.0',
            'endpoints': [
                '/api/correlations',
                '/api/cosmic-events',
                '/api/evolutionary-events'
            ]
        }
    
    return app
