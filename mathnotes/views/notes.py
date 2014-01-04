from flask import Flask, redirect, url_for, render_template, jsonify, Response, current_app, Blueprint, request
from flask.ext.login import login_required, current_user
from mathnotes.refproviders import zoteroapi

notes = Blueprint('notes', __name__, url_prefix='/notes')

@notes.route('', methods=['POST'])
@notes.route('/<int:note_id>', methods=['GET', 'PUT', 'POST'])
def get_note(note_id=None):
    if request.method == 'POST':
        current_app.logger.debug('New post')
        return jsonify({'id':123, 'text':'new post'})
    elif request.method == 'POST':
        return jsonify({'id':123, 'title':request.form['title'], 'text':request.form['text']})
    else:
        return jsonify({'id':123, 'data':'test'})
