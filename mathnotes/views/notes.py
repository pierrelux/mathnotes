from flask import Flask, redirect, url_for, render_template, jsonify, Response, current_app, Blueprint, request
from flask.ext.login import login_required, current_user
from mathnotes.refproviders import zoteroapi
from mathnotes.models import Note, User, db

notes = Blueprint('notes', __name__, url_prefix='/notes')

@notes.route('', methods=['GET', 'POST'])
@notes.route('/<int:note_id>', methods=['GET', 'PUT', 'POST'])
def get_note(note_id=None):
    if request.method == 'POST':
        current_app.logger.debug('New post')

        note = Note(current_user.id, request.form['title'], request.form['text'])
        db.session.add(note)
        db.session.commit()

        response = {'title':note.title, 'text':note.text}

        return jsonify(response), 201
    elif request.method == 'PUT':
        return jsonify({'id':123, 'title':request.form['title'], 'text':request.form['text']})
    else:
        return jsonify({'items':[{'id':note.id, 'title':note.title, 'text':note.text} for note in Note.query.order_by(db.desc(Note.dtime)).all()]})
