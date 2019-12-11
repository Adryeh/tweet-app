from datetime import datetime
from flask import render_template, url_for, request, redirect, flash, jsonify
from app import db, bcrypt
from app.users import users
from app.users.utils import save_picture
from app.models import User, Post, Message
from app.users.forms import RegistrationForm, LoginForm, UpdateAccountForm, MessageForm
from flask_login import login_user, current_user, logout_user, login_required


@users.route('/register', methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        flash('Logout first', 'info')
        return redirect(url_for('main.home_page'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        try:
            db.session.add(user)
            db.session.commit()
            flash('Your account has been created', 'success')
            return redirect(url_for('users.login'))
        except:
            return 'DB ERROR'
    return render_template('register.html', form=form)


@users.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home_page'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('Logged in', 'success')
            return redirect(next_page) if next_page else redirect(url_for('main.home_page'))
        else:
            flash('Login unsuccessful, Please check username and password', 'danger')
    return render_template('login.html', form=form)


@users.route('/logout')
@login_required
def logout():
    logout_user()
    flash('See you later', 'warning')
    return redirect(url_for('users.login'))


@users.route('/profile/<string:username>/edit', methods=['POST', 'GET'])
@login_required
def profile(username):
    user = User.query.filter_by(username=username).first()
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.name = form.name.data
        current_user.second_name = form.second_name.data
        db.session.commit()
        flash('Your account has been updated', 'success')
        return redirect(url_for('users.profile' , username=username))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.name.data = current_user.name
        form.second_name.data = current_user.second_name
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', image_file=image_file, form=form, user=user)


@users.route('/user/<int:id>')
def user_profile(id):
    user = User.query.get_or_404(id)
    return render_template('user_profile.html', user=user, title=user.username)


@users.route('/follow/<int:id>')
@login_required
def follow(id):
    user = User.query.filter_by(id=id).first()
    username = User.query.get_or_404(id).username
    if user is None:
        flash(f'User {username} not found', 'danger')
        return redirect(url_for('main.home_page'))
    if user == current_user:
        flash('You can not follow yourself', 'danger')
        return redirect(url_for('users.user_profile', id=id))
    current_user.follow(user)
    db.session.commit()
    flash(f'You are following {username}!', 'success')
    return redirect(url_for('users.user_profile', id=id))


@users.route('/unfollow/<int:id>')
@login_required
def unfollow(id):
    user = User.query.filter_by(id=id).first()
    username = User.query.get_or_404(id).username
    if user is None:
        flash(f'User {username} not found', 'danger')
        return redirect(url_for('main.home_page'))
    if user == current_user:
        flash('You can not unfollow yourself', 'danger')
        return redirect(url_for('users.user_profile', id=id))
    current_user.unfollow(user)
    db.session.commit()
    flash(f'You are not following {username}', 'info')
    return redirect(url_for('users.user_profile', id=id))


@users.route('/users')
@login_required
def users_list():
    users = User.query.all()
    return render_template('users.html', users=users)


@users.route('/dialog/<int:id>', methods=['GET', 'POST'])
@login_required
def chat(id):
    form = MessageForm()
    current_user.last_message_read_time = datetime.utcnow()
    db.session.commit()
    users = User.query.all()
    companion = User.query.get_or_404(id)
    own_msg = Message.query.filter_by(recipient_id=id).filter_by(sender_id=current_user.id)
    companion_msg = Message.query.filter_by(sender_id=id).filter_by(recipient_id=current_user.id)
    dialog = own_msg.union(companion_msg).order_by(Message.timestamp).all()
    if form.validate_on_submit():
        msg = Message(author=current_user, recipient=companion,
                      body=form.message.data)
        db.session.add(msg)
        db.session.commit()
        flash('Your message has been sent!', 'success')
        return redirect(url_for('users.chat', id=companion.id))
    return render_template('chat.html', companion=companion, dialog=dialog, users=users, form=form)
