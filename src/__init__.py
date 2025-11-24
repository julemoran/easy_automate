from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from src.config import Config
from flask_cors import CORS

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.config['DEBUG'] = True  # Enable debug mode for detailed error output

    db.init_app(app)
    migrate.init_app(app, db)

    CORS(app)

    # Register blueprints here
    from src.blueprints.applications import bp as applications_bp
    app.register_blueprint(applications_bp, url_prefix='/applications')

    from src.blueprints.pages import bp as pages_bp
    app.register_blueprint(pages_bp, url_prefix='/pages')

    from src.blueprints.browser import bp as browser_bp
    app.register_blueprint(browser_bp, url_prefix='/browser')

    # Register socketio blueprint (for organization)
    from src.blueprints.socketio import websocket_bp
    app.register_blueprint(websocket_bp)

    return app

from src import models