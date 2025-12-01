from app.routes.api.catalog_controller import catalog_api
# Add other blueprints here later

def register_blueprints(app):
    app.register_blueprint(catalog_api)
