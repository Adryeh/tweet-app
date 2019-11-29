from flask import render_template, url_for, request, redirect, flash
from app import db, bcrypt
from app.users import users
from app.users.utils import save_picture
from app.models import User, Post
from app.users.forms import RegistrationForm, LoginForm, UpdateAccountForm
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
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created', 'success')
        return redirect(url_for('users.login'))
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


@users.route('/profile/<string:username>', methods=['POST', 'GET'])
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

    return render_template('user_profile.html', user=user)


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