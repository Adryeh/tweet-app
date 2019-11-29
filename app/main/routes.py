from flask import render_template, flash, redirect, url_for
from app import db
from app.main import main
from app.models import User, Post, PostLike
from app.posts.forms import CreatePost
from flask_login import current_user, login_required


@main.route('/', methods=['POST', 'GET'])
@login_required
def home_page():
    form = CreatePost()
    user = User.query.filter_by(id=current_user.id).first()
    posts = user.followed_posts()
    if form.validate_on_submit():
        post = Post(title=form.title.data, text=form.text.data, user_id=current_user.id)
        db.session.add(post)
        db.session.commit()
        flash('Posted', 'success')
        return redirect(url_for('main.home_page'))
    return render_template('home.html', title='Home Page', user=user, form=form, posts=posts)