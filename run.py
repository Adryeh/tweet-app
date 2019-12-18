from app import create_app, socketio, db
from app.models import User, Post, Message
from app.chat.events import *


app = create_app(debug=True)


if __name__ == '__main__':
    socketio.run(app)