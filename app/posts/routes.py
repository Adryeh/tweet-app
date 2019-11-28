from flask import redirect, render_template, request, url_for
from flask_login import current_user
from app import db
from app.posts import posts
from app.models import Post, PostLike


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