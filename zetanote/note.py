# -*- coding: utf-8 -*-

from contextlib import contextmanager

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
from tinydb import TinyDB, Query

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

class DB:

    def __init__(self, dir, user):
        self.path = '%s/%s.json' % (dir, user)
        self.db = TinyDB(self.path)

    def select(self, cond):
        return self.db.table('notes').get(cond)

    def upsert(self, note, cond):
        return self.db.table('notes').upsert(note, cond)
