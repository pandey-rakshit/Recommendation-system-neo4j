from app.routes.api.catalog_controller import catalog_api

def register_blueprints(app):
    app.register_blueprint(catalog_api)
