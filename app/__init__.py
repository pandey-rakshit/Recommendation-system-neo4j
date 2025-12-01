from flask import Flask
from config import Config

from app.routes import register_blueprints
from db.neo4j.neomodel_config import init_neomodel

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    init_neomodel(app)
    register_blueprints(app)

    return app
