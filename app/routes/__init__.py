from app.routes.api.catalog_controller import catalog_api
from app.routes.ui import ui
from app.middleware.error_handler import register_error_handlers

def register_blueprints(app):
    register_error_handlers(app)
    app.register_blueprint(catalog_api)
    app.register_blueprint(ui)
