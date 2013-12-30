# -*- coding: utf-8 -*-
"""
    Flaskr
    ~~~~~~

    A microblog example application written as Flask tutorial with
    Flask and sqlite3.

    :copyright: (c) 2010 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""

import requests
import markdown
import json
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash, Markup, jsonify, Response

from settings import flaskconfig as config
import dbmodels
from dbmodels import Session, Note, Tag, Citation

# create our little application :)
app = Flask(__name__)
app.config.update(config)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

@app.template_filter("markdown")
def render_markdown(markdown_text):
    return Markup(markdown.markdown(markdown_text))

@app.route('/')
def show_entries():
    entries = dbmodels.getAll();
    return render_template('show_entries.html', entries=entries)

@app.route('/search/citation/<paper_title>')
def get_citation(paper_title):
  payload = {'q':paper_title,  'format':'json'}
  r = requests.get("http://www.dblp.org/search/api/", params=payload)
  result = r.json()

  if int(result['result']['hits']['@sent']) == 0:
    abort(404)

  hits = result['result']['hits']['hit']
  if isinstance(hits, list):
    abort(404)
  elif isinstance(hits, dict):
    return jsonify(author=hits['info']['authors']['author'],
		   title=hits['info']['title']['text'],
		   year=hits['info']['year'],
		   url=hits['url'])

@app.route('/add', methods=['POST'])
def add_entry():
	if not session.get('logged_in'):
		abort(401)
	note = Note(title = request.form['title'], text = request.form['text'], tagnames = request.form.getlist('tags'))
	dbmodels.save_db(note)
	
	flash('New entry was successfully posted')
	return redirect(url_for('show_entries'))


@app.route('/login', methods=['GET', 'POST'])
def login():
	print 'bla'
	error = None
	if request.method == 'POST':
		if request.form['username'] != config['USERNAME']:
			error = 'Invalid username'
		elif request.form['password'] != config['PASSWORD']:
			error = 'Invalid password'
		else:
			session['logged_in'] = True
			flash('You were logged in')
			return redirect(url_for('show_entries'))
	return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))

@app.route('/references/')
@app.route('/references/search/<search>')
def get_mostrecent_references(search=None):
    data = [dict({ 'value':'Time delay embedding', 'tokens':['time', 'Doina', 'Precup'], 'authors':'Doina Precup', 'year':'2013'}),
            dict({ 'value':'Options Discovery', 'tokens':['option', 'Doina', 'Precup'], 'authors':'Doina Precup, Pierre-Luc Bacon', 'year':'2013'})]

    if search:
      print search
      data = [{ 'value':'Manifold Learning', 'tokens':['manifold'], 'authors':'Doina Precup', 'year':'2013'},
              { 'value':'Support Vector Machine', 'tokens':['Support', 'Vector'], 'authors':'Doina Precup, Pierre-Luc Bacon', 'year':'2013'}]

    return Response(json.dumps(data),  mimetype='application/json')

if __name__ == '__main__':
	dbmodels.init_db()
	app.run()
