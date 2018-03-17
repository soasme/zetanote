from flask import Blueprint,

api = Blueprint('api', __name__, url_prefix='/api/1')

def init_app(app):
    import zetanote.api.controllers
    app.register_blueprint(api)
