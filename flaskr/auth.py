#coding=utf-8

import functools
from flask import (
            Blueprint, flash, g, redirect, render_template, request, session, url_for
            )
from werkzeug.security import check_password_hash, generate_password_hash
from db import get_db

auth = Blueprint('auth',__name__)
blog = Blueprint('blog',__name__)

@auth.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        cursor = db.cursor()
        error = None
        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif error is None:
            sql = "select id from user where username='%s'" % (username)
            cursor.execute(sql)
            result = cursor.fetchone()
            print (result)
            if result is not None:
                error = 'User {} is already registered.'.format(username)

        if error is None:
            sql = "INSERT INTO user (username, password) VALUES ('%s', '%s')" % (username, generate_password_hash(password))
            cursor.execute(sql)
            db.commit()
            return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/register.html')


@auth.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        cursor = db.cursor()
        error = None
        sql = "SELECT * FROM user WHERE username = '%s'" % username
        cursor.execute(sql)
        user = cursor.fetchone()
        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('blog.index'))

        flash(error)

    return render_template('auth/login.html')

@auth.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view

@auth.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    print (user_id)

    if user_id is None:
        g.user = None
    else:
        db = get_db()
        cursor = db.cursor()
        sql = "select * from user where id=%d" % (user_id)
        cursor.execute(sql)
        g.user = cursor.fetchone()
        print (g.user)
