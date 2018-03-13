# -*- coding: utf-8 -*-

from contextlib import contextmanager

import os
import os.path
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
from tinydb import TinyDB, Query
from tinydb.operations import delete

Note = Query()

class Meta:

    @classmethod
    def to_editor_text(cls, note):
        note = deepcopy(note)
        text = note.pop('text')
        meta = []
        for key in sorted(note):
            meta.append('%s: %s' % (key, note[key]))
        return '%s\n\n%s' % ('\n'.join(meta), text)

class EditorText:

    @classmethod
    def to_meta(cls, content):
        lines = content.splitlines()
        start_processing_body = False
        body_lines = []
        meta = {}
        for line in lines:
            if not start_processing_body and not line:
                start_processing_body = True
            elif start_processing_body:
                body_lines.append(line)
            else:
                key = line[:line.index(':')]
                value = line[line.index(':')+1:]
                meta[key] = value.strip()
        meta['text'] = '\n'.join(body_lines)
        return meta

class RC:

    FILENAME = '.zetanoterc'
    DEFAULT = {
        "maximum_bucket_num": 1,
    }

    def __init__(self, root):
        self.root = root
        self.path = f'{root}/{self.FILENAME}'

    def read(self):
        if not os.path.exists(self.path):
            return self.DEFAULT
        with open(self.path) as f:
            return json.load(f)


class DB:

    def __init__(self, dir, bucket):
        self.path = '%s/%s.json' % (dir, bucket)
        self.db = TinyDB(self.path)

    def select(self, cond):
        return self.db.table('notes').get(cond)

    def upsert(self, note, cond):
        orig = self.select(cond)
        if orig:
            #for key in (set(note.keys()) - set(orig.keys())):
            #    self.db.table('notes').update(delete(key), cond)
            for key in (set(orig.keys()) - set(note.keys())):
                self.db.table('notes').update(delete(key), doc_ids=[orig.doc_id])
        return self.db.table('notes').upsert(note, cond)

    def select_all(self):
        return self.db.table('notes').all()

    def remove(self, cond):
        doc_ids = [n.doc_id for n in self.db.table('notes').search(cond)]
        return self.db.table('notes').remove(doc_ids=doc_ids)
