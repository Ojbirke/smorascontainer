import os
from flask import Flask
from flask_login import loginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
login_manager = loginManager()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'football_team.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'your_secret_key_here'  # Set the secret key for CSRF protection

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'  # Redirect to login page if not authenticated

    migrate = Migrate(app, db)

    from app.routes import bp, format_player_name
    app.register_blueprint(bp)

    # Register the custom filter
    app.jinja_env.filters['format_player_name'] = format_player_name

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    return app
