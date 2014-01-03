from flask import Flask, redirect, url_for, render_template, jsonify, Response, current_app, Blueprint, request
from flask.ext.login import login_required, current_user

references = Blueprint('references', __name__, url_prefix='/references')

@references.route('/<search_query>')
def search(search_query):
    return {}
