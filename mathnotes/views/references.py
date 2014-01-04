from flask import Flask, redirect, url_for, render_template, jsonify, Response, current_app, Blueprint, request
from flask.ext.login import login_required, current_user
from mathnotes.refproviders import zoteroapi

references = Blueprint('references', __name__, url_prefix='/references')

@references.route('/hints')
def hints():
    return jsonify(zoteroapi.hints())

def to_typeahead(entry):
    entry['value'] = entry['title']
    entry['tokens'] = [name for author in entry['authors'] for name in author.split(' ')]
    entry['tokens'].extend(entry['title'].split())
    return entry

@references.route('/hints/typeahead')
def typeahead_hints():
    hints = zoteroapi.hints()
    hints['items'] = map(to_typeahead, hints['items'])
    return jsonify(hints)

@references.route('/<search_query>')
def search(search_query):
    return jsonify(zoteroapi.search(search_query))

@references.route('/typeahead/<search_query>')
def typeahead_search(search_query):
    results = zoteroapi.search(search_query)
    results['items'] = map(to_typeahead, results['items'])
    return jsonify(results)
