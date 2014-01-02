from app import db, bcrypt
from flask.ext.login import make_secure_token

class Tag(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)

    def __repr__(self):
        return self.name

class Note(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable = False)
    text = db.Column(db.String, nullable = False)
    dtime = db.Column(db.DateTime(), nullable = False, server_default=db.func.now())

    tags = db.relationship("Tag", secondary="note_tag", backref="notes")
    citations = db.relationship("Citation", secondary="note_citation", backref="notes")
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, text, tagnames):
        self.title = title
        self.text = text
        self.tags = []

        for tagname in tagnames:
            tag = Tag.query.filter(Tag.name == tagname).first()
            if tag == None:
                tag = Tag(name = tagname)
            self.tags.append(tag)

    def __repr__(self):
        return self.title + '\n' +self.text

note_tag = db.Table('note_tag', db.Model.metadata,
    db.Column('note_id', db.Integer, db.ForeignKey('note.id', onupdate="CASCADE", ondelete="CASCADE"),
                    primary_key = True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id', onupdate="CASCADE", ondelete="CASCADE"),
                    primary_key = True)
)

class Citation(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    bibtex = db.Column(db.String, nullable = False)

    def __repr__(self):
        return self.bibtex

Note_Citation = db.Table('note_citation', db.Model.metadata,
    db.Column("note_id", db.Integer, db.ForeignKey('note.id', onupdate="CASCADE", ondelete="CASCADE"),
                    primary_key = True, nullable = False),
    db.Column("citation_id", db.Integer, db.ForeignKey('citation.id', onupdate="CASCADE", ondelete="CASCADE"),
                    primary_key = True, nullable = False))

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(64), nullable = False)
    password = db.Column(db.String(60), nullable = False)
    email = db.Column(db.String(120))
    name = db.Column(db.String(64))
    website = db.Column(db.String(120))

    notes = db.relationship('Note', backref = 'user', lazy = 'dynamic')
    authorizations = db.relationship('ServiceAuthorization', backref = 'user', lazy = 'dynamic')

    def __init__(self, username, password, email):
        self.username = username
        self.password = bcrypt.generate_password_hash(password)
        self.email = email

    def check_password(self, passwd):
        return bcrypt.check_password_hash(self.password, passwd)

    def get_auth_token(self):
        return make_secure_token(self.username, self.password)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def __repr__(self):
        return '<User %r>' % (self.username)

class ServiceAuthorization(db.Model):
    """ Authorization to a remote OAuth service

    A user can have multiple authorization.
    An authorization is unique to a given user.

    """
    id = db.Column(db.Integer, primary_key = True)
    oauth_token = db.Column(db.String(200))
    oauth_secret = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    type = db.Column(db.String(50))

    __mapper_args__ = {
        'polymorphic_identity':'service_authorization',
        'polymorphic_on':type
    }

class ZoteroAuthorization(ServiceAuthorization):
    """ An authorization to Zotero

    """
    id = db.Column(db.Integer, db.ForeignKey('service_authorization.id'), primary_key=True)
    userID = db.Column(db.String(60))
    username = db.Column(db.String(60))

    __mapper_args__ = {
        'polymorphic_identity':'zotero_authorization',
    }
