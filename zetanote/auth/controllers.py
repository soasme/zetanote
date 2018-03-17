# -*- coding: utf-8 -*-

from flask import current_app, Blueprint, render_template, url_for, request, redirect
from sqlalchemy.exc import IntegrityError
from zetanote.core import db
from zetanote.auth.core import oauth, authorization_server
from zetanote.auth.app import (login as _login,
                               logout as _logout,
                               current_user,
                               oauth,
                               authorization_server,
                               )
from zetanote.auth.models import User

auth = Blueprint('auth', __name__, url_prefix='/auth')

@auth.route('/login')
def login():
    scheme = 'http' if current_app.config.get('DEBUG') else 'https'
    redirect_uri = url_for('auth.github_callback', _external=True, _scheme=scheme)
    return oauth.github.authorize_redirect(redirect_uri)

@auth.route('/github/callback')
def github_callback():
    token = oauth.github.authorize_access_token()
    res = oauth.github.get('/user')
    if res.status_code == 200:
        user_data = res.json()
        user = User.query.get(user_data['id'])
        if not user:
            try:
                user = User(id=user_data['id'],
                            username=user_data['login'])
                db.session.add(user)
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                user = User.query.get(user_data['id'])
        _login(user, permanent=True)
        return redirect(request.args.get('next') or url_for('index'))
    else:
        abort(401)

@auth.route('/logout')
def logout():
    _logout()
    return redirect(request.args.get('next') or url_for('index'))

@auth.route('/token', methods=['POST', 'GET'])
def issue_token():
    return authorization_server.create_token_response()
