# -*- coding: utf-8 -*-

from flask import Flask, request, abort, render_template, send_from_directory
from zetanote.app import (get_notes, )

app = Flask(__name__, static_url_path='/static')

@app.route('/')
def index():
    return route(request.args)

def route(args):
    action = args.get('a', 'home')
    if action == 'home':
        return go_home(args)
    elif action == 'sn':
        return show_note(args)
    elif action == 'ls':
        return list_notes(args)
    else:
        return show_404(args)

@app.errorhandler(404)
def show_404(args=None):
    return render_template("404.html"), 404

def go_home(args):
    return render_template('home.html')

def show_note(args):
    key = args.get('key')
    if not key: abort(404)
    return 'show single note'

def list_notes(args):
    html = ''
    field = args.get('f', '')
    for note in get_notes(field):
        html += ('<p>%s | %s<p>' % (note['key'], note['desc']))
    return html
