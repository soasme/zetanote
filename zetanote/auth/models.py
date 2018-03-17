# -*- coding: utf-8 -*-

from authlib.flask.oauth2.sqla import OAuth2ClientMixin
from authlib.flask.oauth2.sqla import OAuth2TokenMixin
from authlib.specs.rfc6749.grants import ClientCredentialsGrant as _ClientCredentialsGrant

from zetanote.core import db


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)

    def __repr__(self):
        return '@%r' % self.username

    def get_user_id(self):
        """Get user id.

        Authlib SPEC: A resource owner SHOULD implement get_user_id() method
        """
        return self.id


class Client(db.Model, OAuth2ClientMixin):
    """A client is an application making protected resource requests on
    behalf of the resource owner and with its authorization
    """

    id = db.Column(db.Integer, primary_key=True)

    # A client is registered by a user (developer) on your website.
    # Check https://docs.authlib.org/en/latest/spec/rfc6749.html#authlib.specs.rfc6749.ClientMixin
    user_id = db.Column(
        db.Integer, db.ForeignKey('user.id', ondelete='CASCADE')
    )
    user = db.relationship('User')


class Token(db.Model, OAuth2TokenMixin):
    """Tokens are used to access the users’ resources. A token is issued
    with a valid duration, limited scopes and etc.
    """

    id = db.Column(db.Integer, primary_key=True)

    # A token is associated with a resource owner.
    user_id = db.Column(
        db.Integer, db.ForeignKey('user.id', ondelete='CASCADE')
    )
    user = db.relationship('User')


class ClientCredentialsGrant(_ClientCredentialsGrant):
    """Customize client credentials grant class to save token.

    Please use `save_token` parameter in AuthorizationServer when upgrade to authlib >= 0.6.0.
    """
    def create_access_token(self, token, client):
        item = Token(
            client_id=client.client_id,
            user_id=client.user_id,
            **token
        )
        db.session.add(item)
        db.session.commit()
