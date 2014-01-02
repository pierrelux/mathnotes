# -*- coding: utf-8 -*-
"""
    Mathnotes
    ~~~~~~

    A microblog for organizing scientific notes and thinking outloud.

    :copyright: (c) 2010 by Pierre-Luc Bacon and Gayane Petrosyan
    :license: BSD, see LICENSE for more details.
"""

from app import app, db, zotero, login_manager
from forms import LoginForm, RegistrationForm, SettingsForm
from dbmodels import Note, Tag, Citation, User, ZoteroAuthorization

from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, Markup, jsonify, Response

from flask.ext.login import login_required, login_user, logout_user, current_user


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

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        login_user(user, remember=form.remember_me.data)
        return redirect(request.args.get("next") or url_for("index"))
    else:
        flash_errors(form)
    return render_template('registration.html', form=form)

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    form = SettingsForm(obj=current_user)
    if form.validate_on_submit():
        form.populate_obj(current_user)
        db.session.commit()

    return render_template('settings.html', form=form, auth=current_user.authorizations.first())

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        login_user(form.user, remember=form.remember_me.data)
        flash("Logged in successfully.")
        return redirect(request.args.get("next") or url_for("index"))
    else:
        flash_errors(form)

    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@zotero.tokengetter
def get_zotero_token():
    auth=current_user.authorizations.first()
    if auth is not None:
        return auth.oauth_token, auth.oauth_secret

    return None

@app.route('/auth/oauth/zotero')
@login_required
def zotero_auth():
    callback_url = url_for('zotero_authorized', next=request.args.get('next'))
    return zotero.authorize(callback=callback_url or request.referrer or None)

@app.route('/auth/oauth/zotero/authorized')
@login_required
@zotero.authorized_handler
def zotero_authorized(resp):
    if resp is not None:
        auth = ZoteroAuthorization(oauth_token=resp['oauth_token'],
                                oauth_secret=resp['oauth_token_secret'],
                                userID=resp['userID'],
                                username=resp['username'],
                                user_id=current_user.id)
        db.session.add(auth)
        db.session.commit()
    else:
        flash("Remote authentication to Zotero failed")

    return redirect(request.args.get("next") or url_for("index"))

@app.route('/auth/oauth/zotero/disconnect')
@login_required
def zotero_disconnect():
    auth=current_user.authorizations.first()
    db.session.delete(auth)
    db.session.commit()

    return redirect(request.args.get("next") or url_for("index"))
