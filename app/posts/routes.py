from flask import redirect, render_template, request, url_for, abort, flash
from flask_login import current_user
from app import db
from app.posts import posts
from app.models import Post, PostLike
from app.posts.forms import CreatePost


@posts.route('/post/<int:id>', methods=["GET","POST"])
def post(id):
    likes = PostLike.query.filter_by(post_id=id).count()
    post = Post.query.get_or_404(id)
    if request.args.get("vote"):
        post.likes = post.likes + 1
        db.session.commit()
        return redirect(url_for('posts.post', id=post.id))
    return render_template('post.html', post=post, likes=likes)


@posts.route('/like/<int:post_id>/<action>')
def like_action(post_id, action):
    post = Post.query.filter_by(id=post_id).first_or_404()
    if action == 'like':
        current_user.like_post(post)
        db.session.commit()
    if action == 'unlike':
        current_user.unlike_post(post)
        db.session.commit()
    return redirect(request.referrer)


@posts.route('/post/<int:post_id>/update', methods=["GET","POST"])
def post_update(post_id):
    form = CreatePost()
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    if request.method == 'POST' and form.validate_on_submit():
        post.title = form.title.data
        post.text = form.text.data
        db.session.commit()
        flash('Post has been updated', 'success')
        return redirect(url_for('posts.post', id=post_id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.text.data = post.text
    return render_template('update_post.html', form=form)


@posts.route('/post/<int:post_id>/delete', methods=["GET","POST"])
def post_delete(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted', 'success')
    return redirect(url_for('main.home_page'))