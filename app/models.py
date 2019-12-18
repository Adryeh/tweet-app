import json
from time import time
from flask_login import AnonymousUserMixin
from datetime import datetime
from app import login_manager, db
from flask_login import UserMixin



class Anonymous(AnonymousUserMixin):
  def __init__(self):
    self.username = 'Guest'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)


class User(db.Model, UserMixin):
    liked = db.relationship(
        'PostLike',
        foreign_keys='PostLike.user_id',
        backref='user', lazy='dynamic')


    def followed_posts(self, max_number_of_posts = None):
        followed = Post.query.join(followers, (followers.c.followed_id == Post.user_id)).filter(
            followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        if max_number_of_posts is None:
            return followed.union(own).order_by(Post.date_posted.desc())
        return followed.union(own).order_by(Post.date_posted.desc()).limit(max_number_of_posts)


    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)


    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)


    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0


    def like_post(self, post):
        if not self.has_liked_post(post):
            like = PostLike(user_id=self.id, post_id=post.id)
            db.session.add(like)


    def unlike_post(self, post):
        if self.has_liked_post(post):
            PostLike.query.filter_by(
                user_id=self.id,
                post_id=post.id).delete()


    def has_liked_post(self, post):
        return PostLike.query.filter(
            PostLike.user_id == self.id,
            PostLike.post_id == post.id).count() > 0


    def post_likes(self, user):
        posts = Post.query.filter_by(user_id=user.id)
        sum = 0
        for post in posts:
            sum += post.get_likes_count(post.id)
        return sum


    def user_follower_list(self, user, limit=None):
        pass


    def get_rank(self, user):
        return user.post_likes(user)


    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    name = db.Column(db.String)
    second_name = db.Column(db.String)
    posts = db.relationship('Post', backref='author', lazy=True)
    last_message_read_time = db.Column(db.DateTime)

    followed = db.relationship('User', secondary=followers,
                                primaryjoin=(followers.c.follower_id == id),
                                secondaryjoin=(followers.c.followed_id == id),
                                backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')


    messages_sent = db.relationship('Message',
                                    foreign_keys='Message.sender_id',
                                    backref='author',
                                    lazy='dynamic')


    messages_received = db.relationship('Message',
                                        foreign_keys='Message.recipient_id',
                                        backref='recipient',
                                        lazy='dynamic')


    def new_messages(self):
        last_read_time = self.last_message_read_time or datetime(1900, 1, 1)
        return Message.query.filter_by(recipient=self).filter(Message.timestamp > last_read_time).count()



    def __repr__(self):
        return '<User {}>'.format(self.username)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String)
    text = db.Column(db.Text)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    picture = db.Column(db.String(20))
    likes = db.relationship('PostLike', backref='post', lazy='dynamic')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def get_likes_count(self, id):
        return PostLike.query.filter(
            PostLike.post_id == id).count()


class PostLike(db.Model):
    __tablename__ = 'post_like'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return f'<Message {self.body}>'

