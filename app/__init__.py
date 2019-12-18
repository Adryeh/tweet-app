from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from app.config import Config
from flask_migrate import Migrate
from datetime import timedelta
from flask_socketio import SocketIO


db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.refresh_view = 'relogin'
login_manager.needs_refresh_message = (u"Session timedout, please re-login")
login_manager.session_protection = "strong"
login_manager.login_message_category = 'info'
socketio = SocketIO()


def create_app(config_class=Config, debug=False):
    app = Flask(__name__)
    app.config.from_object(Config)
    app.debug = debug

    @app.before_request
    def before_request():
        session.permanent = True
        app.permanent_session_lifetime = timedelta(minutes=15)


    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    socketio.init_app(app)


    from app.users.routes import users
    from app.main.routes import main
    from app.posts.routes import posts
    from app.chat.routes import chat

    app.register_blueprint(users)
    app.register_blueprint(main)
    app.register_blueprint(posts)
    app.register_blueprint(chat)

    return app