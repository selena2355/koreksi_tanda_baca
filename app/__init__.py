from flask import Flask, app
import os

from .config import Config
from .routes.main_routes import main_bp
from .routes.auth_routes import auth_bp
from .routes.riwayat_routes import riwayat_bp
from .extensions import db, migrate



def create_app():
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static",
    )
    app.config.from_object(Config)

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    os.makedirs(app.config["DETECTION_RESULT_FOLDER"], exist_ok=True)
    os.makedirs(app.config["CORRECTION_RESULT_FOLDER"], exist_ok=True)
    if app.config.get("DEBUG_SAVE"):
        os.makedirs(app.config["DEBUG_FOLDER"], exist_ok=True)

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(riwayat_bp)
    
    db.init_app(app)
    migrate.init_app(app, db)

    return app
