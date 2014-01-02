# -*- coding: utf-8 -*-
"""
    Mathnotes
    ~~~~~~

    A microblog for organizing scientific notes and thinking outloud.

    :copyright: (c) 2010 by Pierre-Luc Bacon and Gayane Petrosyan
    :license: BSD, see LICENSE for more details.
"""

from app import app, db, zotero, login_manager
from forms import LoginForm
from dbmodels import Note, Tag, Citation, User

from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, Markup, jsonify, Response

from flask.ext.login import login_required, login_user, logout_user, current_user

@zotero.tokengetter
def get_zotero_token():
    if 'zotero_oauth' in session:
        resp = session['zotero_oauth']
        return resp['oauth_token'], resp['oauth_token_secret']

@app.before_request
def before_request():
    g.user = None
    if 'zotero_oauth' in session:
        g.user = session['zotero_oauth']

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

@app.template_filter("markdown")
def render_markdown(markdown_text):
    return Markup(markdown.markdown(markdown_text))

@app.route('/')
def index():
    if not current_user.is_authenticated():
        return render_template('index.html')
    else:
        return render_template('write.html')

@app.route('/add', methods=['POST'])
@login_required
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    note = Note(title = request.form['title'], text = request.form['text'], tagnames = request.form.getlist('tags'))
    db.session.add(note)
    db.session.commit()

    flash('New entry was successfully posted')
    return redirect(url_for('index'))

@login_manager.user_loader
def load_user(userid):
    return User.query.get(userid)

def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ))

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        login_user(form.user, remember=form.remember_me.data)
        flash("Logged in successfully.")
        return redirect(request.args.get("next") or url_for("index"))
    else:
        flash_errors(form)

    return render_template("login.html", form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/auth/oauth/zotero')
def auth():
    callback_url = url_for('oauthorized', next=request.args.get('next'))
    return zotero.authorize(callback=callback_url or request.referrer or None)

@app.route('/auth/oauth/zotero/authorized')
@zotero.authorized_handler
def oauthorized(resp):
    if resp is None:
        flash('You denied the request to sign in.')
        return redirect(url_for('index'))

    user = User.query.filter_by(username = resp['username']).first()
    if user is None:
       print 'Adding user'
       user = User(resp['username'])
       db.session.add(user)

    #user.oauth_token = resp['oauth_token']
    #user.oauth_secret = resp['oauth_token_secret']
    db.session.commit()
    print 'User already there'

    return redirect(url_for('index'))

