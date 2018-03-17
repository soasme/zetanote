# -*- coding: utf-8 -*-


import re
import os
from os import environ
import glob
import argparse
import json

from zetanote.note import DB, RC

class Conf:

    DEBUG = bool(environ.get('FLASK_DEBUG') or environ.get('DEBUG'))
    DATA = environ.get('ZETANOTE_DATA') or '~/.zetanote'
    SECRET_KEY = environ.get('SECRET_KEY') or 'ofINfQJarBfljciupHQRqsGlRJXECLFC'
    SQLALCHEMY_DATABASE_URI = environ.get('SQLALCHEMY_DATABASE_URI' )
    GITHUB_CLIENT_ID = environ.get('GITHUB_CLIENT_ID')
    GITHUB_CLIENT_SECRET = environ.get('GITHUB_CLIENT_SECRET')
    OAUTH2_ACCESS_TOKEN_GENERATOR = environ.get('OAUTH2_ACCESS_TOKEN_GENERATOR')
    OAUTH2_REFRESH_TOKEN_GENERATOR = environ.get('OAUTH2_REFRESH_TOKEN_GENERATOR')

class AppError(Exception):
    def __init__(self, message):
        self.message = message

class InvalidBucketName(AppError):
    pass

class BucketNumLimited(AppError):
    pass

class BucketSizeLimited(AppError):
    pass

def get_user_dir(user, type='gh'):
    return f'{Conf.DATA}/{type}/{user.id}'

def ensure_user_dir(user, type='gh'):
    path = get_user_dir(user, type=type)
    if os.path.exists(path):
        return
    os.makedirs(path)

def select_all(db):
    return db.select_all()

def truncate(text, n=20):
    return text[:20] + '...' if len(text) > n else text

def ensure_data():
    if not os.path.exists(Conf.DATA):
        os.mkdir(Conf.DATA)

def make_key(default):
    return str(uuid4()) if default == '' else default

def validate_bucket_name(bucket):
    if not bucket or bucket.startswith('.'):
        raise InvalidBucketName(f'`{bucket}` is an invalid bucket name.')

def validate_bucket_num(root, bucket, conf):
    buckets = glob.glob(f'{root}/*.json')
    if f'{root}/{bucket}.json' not in buckets \
            and len(buckets) >= conf.get('maximum_bucket_num',
                                         RC.DEFAULT['maximum_bucket_num']):
        raise BucketNumLimited('You cannot create more buckets. Please upgrade account.')

def validate_bucket_size(db, conf):
    if db.stat.st_size > conf.get('maximum_bucket_size', RC.DEFAULT['maximum_bucket_size']):
        raise BucketSizeLimited('You have reached size limitation of a bucket.')

def textify_note(note, field):
    if not field:
        desc = note.get('title') or truncate(note['text'])
    elif ',' in field:
        desc = '\t'.join([note.get(f) or '' for f in field.split(',')])
    else:
        desc = note.get(field, '')
    return desc

def filter_note(note, condition):
    key = condition['key']
    value = condition['value']
    note_value = note.get(key) or ''
    if condition['op'] == '=':
        return note_value == value
    elif condition['op'] == '!=':
        return note_value != value
    elif condition['op'] == '~':
        return bool(re.search(value, note_value))
    elif condition['op'] == '!~':
        return not bool(re.search(value, note_value))
    else:
        return False

def get_notes_artifact(db):
    notes = [note for note in select_all(db)]
    return json.dumps(notes, indent=4)


def get_notes(db, field, conditions=None):
    hits = []
    conditions = conditions or []
    for note in select_all(db):
        # fixme: please customize a more sophisticated algorithm
        if not all(filter_note(note, c) for c in conditions):
            continue
        elem = {'key': note['key'], 'desc': textify_note(note, field), 'note': note}
        hits.append(elem)
    return hits

def parse_zql(q):
    # fixme: please customize a more sophisticated algorithm
    field_match = re.search(r'\s*(-f|--field)\s+([^ ]+)', q)
    field = field_match.group(2) if field_match else None
    condition_match = re.findall(r'\s*(-c|--condition)\s+([^!=~ ]+)(=|~|!=|!~)(\S+)', q)
    conditions = [
        {'key': match[1], 'op': match[2], 'value': match[3]}
        for match in condition_match
    ]
    return {'field': field, 'conditions': conditions}
