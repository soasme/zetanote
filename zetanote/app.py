# -*- coding: utf-8 -*-


import os
from os import environ

from zetanote.note import DB

class Conf:

    DATA = environ.get('ZETANOTE_DATA') or '~/.zetanote'

def db():
    return DB(Conf.DATA)

def select(cond):
    return db().select(cond)

def upsert(note, cond):
    return db().upsert(note, cond)

def select_all():
    return db().select_all()

def delete(cond):
    return db().remove(cond)

def truncate(text, n=20):
    return text[:20] + '...' if len(text) > n else text

def ensure_data():
    if not os.path.exists(Conf.DATA):
        os.mkdir(Conf.DATA)

def make_key(default):
    return str(uuid4()) if default == '' else default

def textify_note(note, field):
    if not field:
        desc = note.get('title') or truncate(note['text'])
    elif ',' in field:
        desc = '\t'.join([note.get(f, '') for f in field.split(',')])
    else:
        desc = note.get(field, '')
    return desc

def get_notes(field):
    return [{'key': note['key'], 'desc': textify_note(note, field)}
            for note in select_all()]
