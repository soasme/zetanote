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
from zetanote.api.app import create_app


def db():
    return DB(environ['ZETANOTE_DATA'], environ['ZETANOTE_USER'])

def select(cond):
    return db().select(cond)

def upsert(note, cond):
    return db().upsert(note, cond)

def select_all():
    return db().select_all()

def delete(cond):
    return db().remove(cond)

def format_note_in_shell(note, field):
    if not field:
        desc = note.get('title') or truncate(note['text'])
    elif ',' in field:
        desc = '\t'.join([note.get(f, '') for f in field.split(',')])
    else:
        desc = note.get(field, '')
    return desc

@click.group()
def zetanote():
    """Zetanote - Organizing notes in less pain."""

@zetanote.command(name='open')
@click.argument('key', default='')
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


def truncate(text, n=20):
    if len(text) > n:
        return text[:20] + '...'
    else:
        return text

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
    for note in select_all():
        click.echo('%s\t%s' % (note['key'],
                               format_note_in_shell(note, field)))


@zetanote.command('rm')
@click.argument('key', default='')
def remove_note(key):
    try:
        delete(Note.key == key)
    except KeyError:
        click.echo('zeta rm: cannot remove \'%s\': No such note' % key)


if __name__ == '__main__':
    zetanote()
