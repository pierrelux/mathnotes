from flask_oauthlib.client import OAuth
from mathnotes.models import db, ZoteroAuthorization

from flask import Flask, redirect, url_for, render_template, jsonify, Response, current_app, Blueprint, request
from flask.ext.login import login_required, current_user

oauth = OAuth()
auth = Blueprint('auth', __name__, url_prefix='/auth')

zotero = oauth.remote_app(
    'zotero',
    base_url='https://api.zotero.org',
    request_token_url='https://www.zotero.org/oauth/request',
    access_token_url='https://www.zotero.org/oauth/access',
    authorize_url='https://www.zotero.org/oauth/authorize',
    app_key='ZOTERO'
)

@zotero.tokengetter
def get_zotero_token():
    auth=current_user.authorizations.first()
    if auth is not None:
        return auth.oauth_token, auth.oauth_secret

    return None

@auth.route('/oauth/zotero')
@login_required
def zotero_auth():
    callback_url = url_for('auth.zotero_authorized', next=request.args.get('next'))
    return zotero.authorize(callback=callback_url or request.referrer or None)

@auth.route('/oauth/zotero/authorized')
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

    return redirect(request.args.get("next") or url_for("frontend.index"))

@auth.route('/oauth/zotero/disconnect')
@login_required
def zotero_disconnect():
    auth=current_user.authorizations.first()
    db.session.delete(auth)
    db.session.commit()

    return redirect(request.args.get("next") or url_for("frontend.index"))
