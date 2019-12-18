from flask import render_template, session, redirect, url_for, request, flash
from flask_login import current_user, login_required
from app.chat import chat
from app.chat.forms import RoomForm


@chat.route('/room')
def room():
    return render_template('room.html')


@chat.route('/enter', methods=['GET', 'POST'])
@login_required
def enter():
    """Login form to enter a room."""
    form = RoomForm()
    if form.validate_on_submit():
        session['name'] = form.name.data
        session['room'] = form.room.data
        return redirect(url_for('.msg'))
    elif request.method == 'GET':
        form.name.data = session.get('name', '')
        form.room.data = session.get('room', '')
    return render_template('enter.html', form=form)


@chat.route('/chat')
@login_required
def msg():
    """Chat room. The user's name and room must be stored in
    the session."""
    name = session.get('name', '')
    room = session.get('room', '')
    if name == '' or room == '':
        return redirect(url_for('.enter'))
    return render_template('msg.html', name=name, room=room)