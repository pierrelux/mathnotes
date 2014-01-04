from flask import Flask
from flask.ext.login import LoginManager

from mathnotes.models import db, bcrypt, User

login_manager = LoginManager()

@login_manager.user_loader
def load_user(userid):
    return User.query.get(userid)

def create_app(object_name):

    app = Flask(__name__)
    app.config.from_object(object_name)

    @app.template_filter("markdown")
    def render_markdown(markdown_text):
        return Markup(markdown.markdown(markdown_text))

    db.init_app(app)
    bcrypt.init_app(app)

    login_manager.init_app(app)

    from mathnotes.views.frontend import frontend
    app.register_blueprint(frontend)

    from mathnotes.views.auth import auth, oauth
    oauth.init_app(app)
    app.register_blueprint(auth)

    from mathnotes.views.references import references
    app.register_blueprint(references)

    from mathnotes.refproviders import cache
    cache.init_app(app)

    from mathnotes.views.notes import notes
    app.register_blueprint(notes)

    return app

if __name__ == '__main__':
    create_app('config')
    app.run(debug=True)
