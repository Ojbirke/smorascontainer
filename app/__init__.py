from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////app/instance/football_team.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'your_secret_key_here'  # Set the secret key for CSRF protection

    db.init_app(app)
    migrate = Migrate(app, db)

    from app.routes import bp, format_player_name
    app.register_blueprint(bp)

    # Register the custom filter
    app.jinja_env.filters['format_player_name'] = format_player_name

    return app
