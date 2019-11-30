from datetime import datetime
from app import login_manager, db
from flask_login import UserMixin, current_user


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


    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    name = db.Column(db.String)
    second_name = db.Column(db.String)
    posts = db.relationship('Post', backref='author', lazy=True)


    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')


    def __repr__(self):
        return '<User {}>'.format(self.username)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String)
    text = db.Column(db.Text)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
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


