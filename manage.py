#!/usr/bin/env python
import os

from flask.ext.script import Manager, Server
from mathnotes import create_app
from mathnotes.models import db, User, ZoteroAuthorization

app = create_app('config')
manager = Manager(app)

@manager.shell
def make_shell_context():
    """ Creates a python REPL with several default imports
        in the context of the app
    """

    return dict(app=app, db=db)

@manager.command
def createdb():
    """ Creates a database with all of the tables defined in
        your Alchemy models
    """
    db.create_all()
    user = User(username='pierrelux', email='pierrelucbacon@gmail.com', password='test')
    user.name='Pierre-Luc'
    user.website='http://pierrelucbacon.com'
    db.session.add(user)
    db.session.commit()

    auth = ZoteroAuthorization(userID='1735197', username='pierrelux', oauth_token='OaUoTtjALtyT6htGmeBZdwFi', oauth_secret='OaUoTtjALtyT6htGmeBZdwFi', user_id=user.id)
    db.session.add(auth)
    db.session.commit()

    print User.query.filter_by(username='pierrelux').first()

if __name__ == "__main__":
    manager.run()
