from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    # Ensure instance folder exists (safe place for sqlite db, uploads, etc.)
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except Exception:
        pass
    
    # Config
    app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'your_random_secret_key')
    env_db = os.getenv('DATABASE_URL')
    # Default sqlite DB goes into %LOCALAPPDATA% to avoid OneDrive sync/locking issues.
    local_appdata = os.getenv("LOCALAPPDATA") or app.instance_path
    default_sqlite_path = Path(local_appdata) / "SHealthcare" / "shealthcare.db"
    try:
        default_sqlite_path.parent.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass
    default_sqlite_uri = f"sqlite:///{default_sqlite_path.as_posix()}"
    if not env_db or env_db.strip() == "" or env_db.strip() == "sqlite:///users.db":
        app.config['SQLALCHEMY_DATABASE_URI'] = default_sqlite_uri
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = env_db
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Import models to ensure they are registered with SQLAlchemy
    from app import models

    # Register Blueprints
    from app.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
