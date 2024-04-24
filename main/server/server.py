from flask import Flask
from api import api as api_blueprint  # Import the Blueprint

def create_app():
    app = Flask(__name__)

    # Register blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')

    # Configurations
    app.config['DEBUG'] = True
    app.config['SECRET_KEY'] = 'your-secret-key'

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='localhost', port=5000)

