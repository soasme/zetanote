# -*- coding: utf-8 -*-

from urllib.parse import urlencode
from flask import Flask, request, abort, render_template, send_from_directory
from zetanote.app import (get_notes, parse_zql)

app = Flask(__name__, static_url_path='/static')

def template_url(preserve_current=False, **kwargs):
    params = dict(request.params) if preserve_current else {}
    params.update(kwargs)
    return '?%s' % urlencode(params)

jinja_env = {
    'url': template_url
}
app.jinja_env.globals.update(jinja_env)

@app.route('/')
def index():
    return route(request.args)

def route(args):
    action = args.get('a', 'ls')
    if action == 'cat':
        return show_note(args)
    elif action == 'ls':
        return list_notes(args)
    else:
        return show_404(args)

@app.errorhandler(404)
def show_404(args=None):
    return render_template("404.html"), 404

def show_note(args):
    key = args.get('key')
    if not key: abort(404)
    return 'show single note'


def list_notes(args):
    query = args.get('q', '')
    args = parse_zql(query) if query else {}
    hits = get_notes(args.get('field'), args.get('conditions'))
    context = dict(hits=hits, q=query)
    return render_template('home.html', **context)
