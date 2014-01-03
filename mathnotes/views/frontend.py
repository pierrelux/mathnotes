# -*- coding: utf-8 -*-
"""
    Mathnotes
    ~~~~~~

    A microblog for organizing scientific notes and thinking outloud.

    :copyright: (c) 2010 by Pierre-Luc Bacon and Gayane Petrosyan
    :license: BSD, see LICENSE for more details.
"""
from mathnotes.forms import LoginForm, RegistrationForm, SettingsForm
from mathnotes.models import Note, Tag, Citation, User, ZoteroAuthorization, db

from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, Markup, jsonify, Response, current_app, Blueprint
from flask.ext.login import login_required, login_user, logout_user, current_user

frontend = Blueprint('frontend', __name__)

@frontend.route('/')
def index():
    if not current_user.is_authenticated():
        return render_template('index.html')
    else:
        return render_template('write.html')

@frontend.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        login_user(user, remember=form.remember_me.data)
        return redirect(request.args.get("next") or url_for(".index"))
    else:
        current_app.logger.error('Signup')

    return render_template('registration.html', form=form)

@frontend.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    form = SettingsForm(obj=current_user)
    if form.validate_on_submit():
        form.populate_obj(current_user)
        db.session.commit()

    return render_template('settings.html', form=form, auth=current_user.authorizations.first())

@frontend.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        login_user(form.user, remember=form.remember_me.data)
        flash("Logged in successfully.")
        return redirect(request.args.get("next") or url_for(".index"))
    else:
        current_app.logger.error('Logging failed')

    return render_template('login.html', form=form)

@frontend.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('.index'))
