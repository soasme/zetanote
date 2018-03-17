# -*- coding: utf-8 -*-

from authlib.client import OAuth2Session
from requests.auth import HTTPBasicAuth

#
# insert into client (user_id, client_id, client_secret, is_confidential, redirect_uris, default_redirect_uri, allowed_scopes) value (369081, '1001', '1234567890', 1, '', '', '');
client_id = '1001'
client_secret = '1234567890'
scope = 'note'
session = OAuth2Session(client_id, client_secret, scope=scope)
token_url = 'http://127.0.0.1:8964/auth/token'
token = session.fetch_access_token(token_url, grant_type='client_credentials')
print(token)

