#coding=utf-8
from flask import (
            Blueprint, flash, g, redirect, render_template, request, url_for
            )
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename

from auth import login_required
from db import get_db
import math
import os

blog = Blueprint('blog', __name__)

@blog.route('/')
def index():
    if request.method == 'GET':
        if request.args.get('id') is not None:
            page = int(request.args.get('id'))
        else:
            page = 1 #当前页码，默认为1
    per_page = 5 #每页展示数量
    db = get_db()
    cursor = db.cursor()
    sql = "select id from post"
    cursor.execute(sql)
    total = len(cursor.fetchall())
    pages = math.ceil(total/per_page)
    if page < pages:
        next_num = page + 1
    else:
        next_num = None

    if page <= 1:
        prev_num = None
    else:
        prev_num = page - 1

    sql = u"""
            SELECT p.id, title, body, created, author_id, username, image_path
                FROM post p JOIN user u ON 
                p.author_id = u.id 
                ORDER BY created DESC
                limit {},{}
          """.format((page-1)*per_page, per_page)
    cursor.execute(sql)
    posts = cursor.fetchall()
    return render_template('blog/index.html', posts=posts, pages=pages, next_num=next_num, prev_num=prev_num)

@blog.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        file_obj = request.files.get("upfile")
        save_image_path = os.path.join('static/images', file_obj.filename)
        file_obj.save(save_image_path)
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            cursor = db.cursor()
            sql = "insert into post (title, body, author_id, image_path) values ('%s', '%s', %d, '%s')" % (title, body, g.user['id'], file_obj.filename)
            cursor.execute(sql)
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')

@blog.route('/details', methods=('GET', 'POST'))
def details():
    db = get_db()
    cursor =db.cursor()
    if request.method == 'GET':
        post_id = int(request.args.get('id'))
        sql = "select * from post where id=%d" % (post_id)
        cursor.execute(sql)
        posts = cursor.fetchall()
        sql = "select * from comments where post_id=%d" % (post_id)
        cursor.execute(sql)
        comments = cursor.fetchall()
        return render_template('blog/details.html', posts=posts, comments=comments)
    elif request.method == 'POST':
        post_id = int(request.args.get('id'))
        print (g)
        if g.user is None:
            return redirect(url_for('blog.details', id=post_id))
        comments = request.form['comments']
        sql = "insert into comments (post_id, comments_text, user_id, user_name) values (%d, '%s', %d, '%s')" % (post_id, comments, g.user['id'], g.user['username'])
        cursor.execute(sql)
        db.commit()
        return redirect(url_for('blog.details', id=post_id))


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

@blog.route('/<int:id>/update', methods=('GET', 'POST'))
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

@blog.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))

@blog.route('/page', methods=('GET', 'POST'))
@login_required
def page_list():
    if request.method == 'GET':
        if request.args.get('id') is not None:
            page = int(request.args.get('id'))
        else:
            page = 1 #当前页码，默认为1
    per_page = 5 #每页展示数量
    db = get_db()
    cursor = db.cursor()
    sql = "select id from post"
    cursor.execute(sql)
    total = len(cursor.fetchall())
    pages = math.ceil(total/per_page)
    if page < pages:
        next_num = page + 1
    else:
        next_num = None

    if page <= 1:
        prev_num = None
    else:
        prev_num = page - 1

    return render_template('blog/page.html', pages=pages, next_num=next_num, prev_num=prev_num)

@blog.route('/upload', methods=('GET', 'POST'))
def upload():
    if request.method == 'POST':
        file_obj = request.files.get("upfile")
        print (file_obj.filename)
        save_image_path = os.path.join('./static/images/',  file_obj.filename)
        print (save_image_path)
        if file_obj is None:
            return "未上传文件"

        file_obj.save(save_image_path)
        return "上传成功"

    return render_template('/blog/upload.html')
