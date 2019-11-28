from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from app.config import Config
from flask_migrate import Migrate


db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.session_protection = "strong"
login_manager.login_message_category = 'info'


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)


    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)


    from app.users.routes import users
    from app.main.routes import main
    from app.posts.routes import posts

    app.register_blueprint(users)
    app.register_blueprint(main)
    app.register_blueprint(posts)

    return app