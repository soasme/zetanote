# -*- coding: utf-8 -*-

import io
import bleach
import json
from uuid import uuid4
from markdown import Markdown
from urllib.parse import urlencode
from flask import Flask, request, abort, render_template, url_for, redirect, session, g, send_file
from flask_sslify import SSLify
from authlib.flask.client import OAuth
from authlib.client.apps import github
from authlib.client.errors import OAuthException
from zetanote.note import Note, RC, DB
from zetanote.app import (Conf, get_notes, parse_zql, ensure_user_dir,
                          get_user_dir, validate_bucket_name, validate_bucket_num,
                          validate_bucket_size,
                          get_notes_artifact, AppError)

app = Flask(__name__, static_url_path='/static')
app.config.from_object(Conf)
oauth = OAuth(app)
github.register_to(oauth)
sslify = Conf.DEBUG and SSLify(app)
markdown = Markdown(extensions=['markdown.extensions.extra'])

def urlgen(**kwargs):
    scheme = 'http' if Conf.DEBUG else 'https'
    kwargs['b'] = request.args.get('b', 'default')
    return url_for('index', _external=True, _scheme=scheme, **kwargs)

jinja_env = {
    'url': urlgen
}
jinja_filters = {
    'markdown': markdown.convert,
    'sanitizer': bleach.clean,
}
app.jinja_env.globals.update(jinja_env)
app.jinja_env.filters.update(jinja_filters)

@app.context_processor
def inject_db():
    return dict(
        db=hasattr(g, 'db') and g.db,
        conf=hasattr(g, 'conf') and g.conf,
        user=hasattr(g, 'user') and g.user,
        bucket=hasattr(g, 'bucket') and g.bucket,
    )

@app.before_request
def start_a_request():
    if request.path.startswith('/static'):
        return
    g.user = session.get('u') and json.loads(session['u'])
    g.root = g.user and get_user_dir(g.user, type='gh')
    g.conf = g.user and RC(g.root).read() or RC.DEFAULT
    g.bucket = request.args.get('b', 'default')
    if g.user and g.bucket:
        validate_bucket_name(g.bucket)
        validate_bucket_num(g.root, g.bucket, g.conf)
    try:
        g.db = g.user and DB(g.root, g.bucket)
    except FileNotFoundError:
        ensure_user_dir(g.user, type='gh')
        g.db = g.user and DB(g.root, g.bucket)

@app.route('/', methods=['GET', 'POST'])
def index():
    return route(request.args)

def get_user():
    return session.get('u') and json.loads(session.get('u'))

def route(args):
    action = args.get('a', 'ls')

    if action == 'login':
        return login(args)
    elif action == 'authorize':
        return authorize(args)

    u = get_user()
    if not u:
        return show_proj(args)

    if action == 'cat':
        return show_note(args)
    elif action == 'ls':
        return list_notes(args)
    elif action == 'ed':
        return edit_note(args)
    elif action == 'ad':
        return add_note(args)
    elif action == 'dump':
        return dump_note(args)
    elif action == 'logout':
        return logout(args)
    else:
        return show_404(None, args)


@app.errorhandler(404)
def show_404(e, args=None):
    return render_template("404.html"), 404

@app.errorhandler(401)
def show_404(e, args=None):
    return render_template("401.html"), 401

@app.errorhandler(OAuthException)
def show_oautherror(e, args=None):
    return render_template('4xx.html', e=e), 400

@app.errorhandler(AppError)
def show_oautherror(e, args=None):
    return render_template('4xx.html', e=e), 400

def show_proj(args):
    return render_template('proj.html')

def _ensure_note(args):
    key = args.get('key')
    if not key: abort(404)
    note = g.db.select(Note.key == key)
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
    hits = get_notes(g.db, args.get('field'), args.get('conditions'))
    context = dict(u=get_user(), hits=hits, q=query)
    return render_template('home.html', **context)

def edit_note(args):
    validate_bucket_size(g.db, g.conf)

    note = _ensure_note(args)

    if request.method == 'POST':
        form = request.form.to_dict()
        form['key'] = note['key']
        form = {k.strip(): v.strip() for k, v in form.items()}
        g.db.upsert(form, Note.key == note['key'])
        return redirect(urlgen(a='cat', key=note['key']))

    ctx = {'note': note}
    return render_template('edit.html', **ctx)


def add_note(args):
    validate_bucket_size(g.db, g.conf)

    ctx = {'note': {'key': '', 'text': ''}}

    if request.method == 'POST':
        form = request.form.to_dict()
        form['key'] = str(uuid4())
        form = {k.strip(): v.strip() for k, v in form.items()}
        doc_id = g.db.upsert(form, Note.key == form['key'])
        return redirect(urlgen(a='cat', key=form['key']))

    return render_template('edit.html', **ctx)

def dump_note(args):
    data = get_notes_artifact(g.db)
    memory_file = io.BytesIO(data.encode('utf8'))
    return send_file(memory_file,
                     attachment_filename='data.json',
                     as_attachment=True)


def login(args):
    redirect_uri = urlgen(a='authorize')
    return oauth.github.authorize_redirect(redirect_uri)

def authorize(args):
    token = oauth.github.authorize_access_token()
    res = oauth.github.get('/user')
    if res.status_code == 200:
        user = res.json()
        ensure_user_dir(user, type='gh')
        session['u'] = json.dumps(user)
        return redirect(urlgen())
    else:
        abort(401)

def logout(args):
    session.pop('u', None)
    return redirect(urlgen())
