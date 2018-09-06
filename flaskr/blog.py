from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.auth import load_logged_in_user
from flaskr.db import get_db

bp = Blueprint('blog', __name__)

#SHOW posts.
@bp.route('/')
@login_required
def index():
    db = get_db()
    #posts = db.execute(
    #    'SELECT p.id, title, body, created, author_id, username, complete
    #    ' FROM post p JOIN user u ON p.author_id = u.id'
    #    ' ORDER BY created DESC'
    #    ).fetchall()

    posts = db.execute(
        ' SELECT p.id, p.title, p.body, p.created, p.author_id, u.username, p.complete, u.id '
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
        ).fetchall()

    return render_template('blog/index.html', posts=posts)

#CREATE Posts
@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        complete = False
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id, complete)'
                ' VALUES (?, ?, ?, ?)',
                (title, body, g.user['id'], complete)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')

#DISPLAY posts
def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    if check_author and post['author_id'] != g.user['id']:
        abort(403) #Error 403: Forbidden.

    return post

#SHOW blogs without checking the authorself.
@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)

#DELETE a blog post.
@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))

#COMPLETE an item.
@bp.route('/complete/<int:id>')
@login_required
def complete(id):
    get_post(id)
    db = get_db()
    db.execute('UPDATE post SET complete = 1  WHERE id = ?',(id,))
    db.commit()
    return redirect(url_for('blog.index'))
    #return '<h1>{}</h1>'.format(id)
