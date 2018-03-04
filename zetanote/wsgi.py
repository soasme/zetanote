# -*- coding: utf-8 -*-

import bleach
from uuid import uuid4
from markdown import Markdown
from urllib.parse import urlencode
from flask import Flask, request, abort, render_template, url_for, redirect
from zetanote.note import Note
from zetanote.app import (get_notes, parse_zql, select, upsert)

app = Flask(__name__, static_url_path='/static')
markdown = Markdown(extensions=['markdown.extensions.extra'])

def template_url(preserve_current=False, **kwargs):
    params = dict(request.params) if preserve_current else {}
    params.update(kwargs)
    return '?%s' % urlencode(params)

jinja_env = {
    'url': template_url
}
jinja_filters = {
    'markdown': markdown.convert,
    'sanitizer': bleach.clean,
}
app.jinja_env.globals.update(jinja_env)
app.jinja_env.filters.update(jinja_filters)

@app.route('/', methods=['GET', 'POST'])
def index():
    return route(request.args)

def route(args):
    action = args.get('a', 'ls')
    if action == 'cat':
        return show_note(args)
    elif action == 'ls':
        return list_notes(args)
    elif action == 'ed':
        return edit_note(args)
    elif action == 'ad':
        return add_note(args)
    else:
        return show_404(args)

@app.errorhandler(404)
def show_404(args=None):
    return render_template("404.html"), 404

def _ensure_note(args):
    key = args.get('key')
    if not key: abort(404)
    note = select(Note.key == key)
    if not note: abort(404)
    return note

def show_note(args):
    note = _ensure_note(args)
    note.setdefault('mime', 'text/markdown')
    ctx = {'note': note}
    return render_template('note.html', **ctx)


def list_notes(args):
    query = args.get('q', '')
    args = parse_zql(query) if query else {}
    hits = get_notes(args.get('field'), args.get('conditions'))
    context = dict(hits=hits, q=query)
    return render_template('home.html', **context)

def edit_note(args):
    note = _ensure_note(args)

    if request.method == 'POST':
        form = request.form.to_dict()
        form['key'] = note['key']
        form = {k.strip(): v.strip() for k, v in form.items()}
        upsert(form, Note.key == note['key'])
        return redirect(url_for('index', a='cat', key=note['key']))

    ctx = {'note': note}
    return render_template('edit.html', **ctx)


def add_note(args):
    ctx = {'note': {'key': '', 'text': ''}}

    if request.method == 'POST':
        form = request.form.to_dict()
        form['key'] = str(uuid4())
        form = {k.strip(): v.strip() for k, v in form.items()}
        doc_id = upsert(form, Note.key == form['key'])
        return redirect(url_for('index', a='cat', key=form['key']))

    return render_template('edit.html', **ctx)
