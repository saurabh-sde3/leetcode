# Main application entry point
import os
from app import create_app

# Get configuration from environment variable
config_name = os.environ.get('FLASK_CONFIG', 'development')

# Create Flask application
app = create_app(config_name)

if __name__ == '__main__':
    # Development server settings
    debug_mode = app.config.get('DEBUG', False)
    app.run(
        debug=debug_mode,
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000))
    )
