#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
Note = An object contains "key" + "text" with customized fields.
Store = A file formatted Notes as JSON array.
"""


import os
from os import environ
from copy import deepcopy
import re
import sys
import json
from glob import glob
import logging
import os.path
from uuid import uuid4
import tempfile
import traceback
import webbrowser

import click
from zetanote.note import DB, Meta, EditorText, Note
from zetanote.daemon import Daemon
from zetanote.app import (Conf, db, select, upsert, select_all,
                          delete, truncate, ensure_data, make_key,
                          textify_note, get_notes)


@click.group()
def zetanote():
    """Zetanote - Organizing notes in less pain."""
    ensure_data()


@zetanote.command(name='open')
@click.argument('key', default='')
def open_note(key):
    """ """
    # Load note content into temp file if exists
    key = make_key(key)
    prefix = 'zetanote-%s-' % key
    with tempfile.NamedTemporaryFile(prefix=prefix, delete=False) as f:
        note = select(Note.key == key) or {'text': ''}
        note['key'] = key
        f.write(Meta.to_editor_text(note).encode('utf-8'))

    # Edit file and save it.
    try:
        click.edit(filename=f.name)
        with open(f.name) as f:
            content = f.read()
            if content:
                note = EditorText.to_meta(content)
                note['key'] = key
                upsert(note, Note.key == key)
    except Exception as e:
        click.echo('saving work to /tmp.')
        os.system('cp %s /tmp/' % f.name)
        traceback.print_exc()
    finally:
        os.remove(f.name)

    # Need key if it's newly generated
    click.echo(key)


@zetanote.command('cat')
@click.argument('key')
def show_note(key):
    """Show a note

    Example::

        $ zeta cat 02ee4ba7-71ce-4e02-b2cb-fd1582b5a103
    """
    note = select(Note.key == key)
    if note:
        click.echo(Meta.to_editor_text(note))
    else:
        click.echo('zeta cat: note not found.', err=True)
        sys.exit(1)



@zetanote.command('ls')
@click.argument('filter', default='')
@click.option('--field', '-f', default='')
def list_notes(filter, field):
    """List all notes

    Example::

        $ zeta ls -f date,url | grep 2018-02-25
        $ zeta ls
        $ zeta ls -f date | grep 2018-02-26 | awk '{print $1}' | xargs -I {} zeta show {}
    """
    for obj in get_notes(field):
        click.echo('%(key)s\t%(desc)s' % obj)


@zetanote.command('rm')
@click.argument('key', default='')
def remove_note(key):
    try:
        delete(Note.key == key)
    except KeyError:
        click.echo('zeta rm: cannot remove \'%s\': No such note' % key)


@zetanote.group()
@click.option('--port', default=8964, type=int)
@click.option('--pidfile', default='')
@click.option('--logfile', default='')
@click.pass_context
def instaweb(ctx, port, pidfile, logfile):
    pidfile = pidfile or '/tmp/zetanote.%s.pid' % port
    logfile = logfile or '/tmp/zetanote.%s.log' % port
    ctx.obj = ctx.obj or {}
    ctx.obj['daemon'] = Daemon(pidfile, logfile, port)

@instaweb.command('start')
@click.pass_context
def start_instaweb(ctx):
    ctx.obj['daemon'].start()

@instaweb.command('open')
@click.pass_context
def open_instaweb(ctx):
    webbrowser.open('http://localhost:%s' % ctx.obj['daemon'].port)

@instaweb.command('stop')
@click.pass_context
def stop_instaweb(ctx):
    ctx.obj['daemon'].stop()

@instaweb.command('restart')
@click.pass_context
def restart_instaweb(ctx):
    ctx.obj['daemon'].restart()


if __name__ == '__main__':
    zetanote(obj={})
