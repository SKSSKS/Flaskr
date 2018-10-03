from fpdf import FPDF
from flask import send_file
from tasks import html_to_pdf
from flask import (Blueprint, flash, g, redirect,
                   render_template, request, url_for)
from werkzeug.exceptions import abort
from flaskr.auth import login_required
from flaskr.db import get_db

from elasticsearch import Elasticsearch
es = Elasticsearch('http://localhost:9200')

bp = Blueprint('blog', __name__)


@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()

    submit = request.args.get('btn')
        # html_to_pdf()
        # return send_file('/home/dev/.venv/try flask/flaskapp/blogpost.pdf', attachment_filename='blogpost.pdf')
    q = request.args.get('input')


    if submit == 'search' and q:
        result = es.search(index='post', doc_type='post', body={'query': {'match': {'content': q}}})
        id_list = []
        if result:
            for results in result['hits']['hits']:
                id_list.append(results['_id'])
        id_list = ','.join(id_list)
        posts = db.execute(
            'SELECT p.id, title, body, created, author_id, username'
            ' FROM post p JOIN user u ON p.author_id = u.id where p.id in ({})'
            ' ORDER BY created DESC'.format(id_list)
        ).fetchall()
        if len(posts) == 0:
            flash("Search Returned Nothing", "info")
    return render_template('blog/index.html', posts=posts)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
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
                'INSERT INTO post (title, body, author_id)'
                ' VALUES (?, ?, ?)',
                (title, body, g.user['id'])
            )
            db.commit()
            posts = db.execute(
                'SELECT p.id, title, body, created, author_id, username'
                ' FROM post p JOIN user u ON p.author_id = u.id'
                ' ORDER BY created DESC'
            ).fetchall()
            for post in posts:
                es.index(index='post', doc_type='post',id=post['id'], body={'content': post['body']})
                # my_posts.append([ post['id'], post['author_id'], post['title'], post['username'], post['created'], post['body']])
            
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')


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
        abort(403)

    return post


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


@bp.route('/<int:id>/post', methods=('GET', 'POST'))
def download(id):
    post = get_post(id)
    title = post['title']
    body = post['body']
    print('>>>>>>>>>>', title)
    print('>>>>>>>>>>', body)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_xy(0, 0)
    pdf.set_font('arial', 'B', 20.0)
    pdf.cell(0, 10, txt=title, ln=1, align="C")
    pdf.set_font('arial', 'B', 13.0)
    line = ''
    for text in body:
        if text == '\n':
            pdf.cell(0, 10, txt=line, ln=1, align="L")
            line = ''
        else:
            line += text
    if len(line) != 0:
        pdf.cell(0, 10, txt=line, ln=1, align="L")
    pdf.output('{}.pdf'.format(title), 'F')
    return send_file('/home/dev/.venv/try flask/flaskapp/{}.pdf'.format(title), attachment_filename='{}.pdf'.format(title))
    #return redirect(url_for('blog.index'))


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))
