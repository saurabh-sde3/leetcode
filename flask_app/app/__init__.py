# Application factory pattern
from flask import Flask, render_template, jsonify
from datetime import datetime
import os

def create_app(config_name='default'):
    """Application factory function"""
    app = Flask(__name__)
    
    # Load configuration
    from config import config
    app.config.from_object(config[config_name])
    
    # Initialize database
    from app.models import DatabaseManager
    with app.app_context():
        DatabaseManager.init_database()
    
    # Register blueprints
    from app.routes import api_bp
    app.register_blueprint(api_bp)
    
    # Main routes
    @app.route('/')
    def home():
        return render_template('home.html')
    
    @app.route('/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'message': 'ECommerce API is running',
            'environment': config_name,
            'version': '2.0.0',
            'timestamp': datetime.now().isoformat()
        })
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 'Resource not found'
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500
    
    return app
