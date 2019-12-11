from app import create_app, socketio, db
from app.models import User, Post, Message


app = create_app(debug=True)


if __name__ == '__main__':
    app.run()