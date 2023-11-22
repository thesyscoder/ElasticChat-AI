#  create flask app

from flask import Flask
from .routes.route import chatbot_bp


def create_app():
    app = Flask(__name__)
    app.register_blueprint(chatbot_bp)
    return app
