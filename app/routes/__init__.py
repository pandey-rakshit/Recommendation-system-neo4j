from app.routes.api.catalog_controller import catalog_api
from app.routes.ui import ui

def register_blueprints(app):
    app.register_blueprint(catalog_api)
    app.register_blueprint(ui)
