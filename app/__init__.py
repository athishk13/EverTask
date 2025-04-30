from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_dance.contrib.github import make_github_blueprint, github
from config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    # GitHub OAuth
    github_bp = make_github_blueprint(
        client_id=app.config['GITHUB_OAUTH_CLIENT_ID'],
        client_secret=app.config['GITHUB_OAUTH_CLIENT_SECRET'],
    )
    app.register_blueprint(github_bp, url_prefix='/login')

    # Blueprints
    from .auth import auth_bp
    from .routes import main_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    return app
