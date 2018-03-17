from uuid import uuid4

from flask import g, session
from werkzeug.local import LocalProxy

from .models import User


SESSION_ID = 'sid'

def login(user, permanent=True):
    session[SESSION_ID] = user.id
    session.permanent = permanent
    g.current_user = user


def logout():
    if SESSION_ID in session:
        del session[SESSION_ID]

def generate_token():
    return uuid4().hex + uuid4().hex

def get_current_user():
    user = getattr(g, 'current_user', None)
    if user:
        return user

    sid = session.get(SESSION_ID)
    if not sid:
        return None

    user = User.query.get(sid)
    if not user:
        logout()
        return None

    g.current_user = user
    return user


current_user = LocalProxy(get_current_user)
