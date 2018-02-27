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

import click
from zetanote.note import DB, Meta, EditorText, Note


def db():
    return DB(environ['ZETANOTE_DATA'], environ['ZETANOTE_USER'])

def select(cond):
    return db().select(cond)

def upsert(note, cond):
    return db().upsert(note, cond)

@click.group()
def zetanote():
    """Zetanote - Organizing notes in less pain."""

@zetanote.command(name='open')
@click.argument('key', default='*')
def open_note(key):
    """ """
    # Load note content into temp file if exists
    key = str(uuid4()) if key == '*' else key
    user = environ.get('ZETANOTE_USER') or environ['USER']
    prefix = 'zetanote-%s-%s-' % (user, key)
    with tempfile.NamedTemporaryFile(prefix=prefix, delete=False) as f:
        note = select(Note.key == key)
        if note:
            f.write(Meta.to_editor_text(note).encode('utf-8'))

    # Edit file and save it.
    try:
        click.edit(filename=f.name)
        with open(f.name) as f:
            content = f.read()
            if content:
                note = EditorText.to_meta(content)
                upsert(note, Note.key == key)
    except Exception as e:
        click.echo('saving work to /tmp.')
        os.system('cp %s /tmp/' % f.name)
        traceback.print_exc()
    finally:
        os.remove(f.name)

    # Need key if it's newly generated
    click.echo(key)


@zetanote.command('show')
@click.argument('key')
def show_note(key):
    note = select(Note.key == key)
    if note:
        click.echo(Meta.to_editor_text(note))
    else:
        print('Note not found.', stderr=True)
        sys.exit(1)


if __name__ == '__main__':
    zetanote()
