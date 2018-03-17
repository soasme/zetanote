from flask import jsonify

from zetanote.api.core import api
from zetanote.auth.app import current_token, require_oauth


@api.route('/user')
@require_oauth()
def get_user():
    user = current_token.user
    return jsonify(user.as_dict())
