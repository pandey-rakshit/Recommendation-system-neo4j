import os
from dotenv import load_dotenv

load_dotenv()
class Config:
    FLASK_ENV = os.environ.get("FLASK_ENV", "production")
    SECRET_KEY = os.environ.get("SECRET_KEY", "your-secret-key")

    # Neo4j Aura connection settings
    NEO4J_URI = os.environ.get("NEO4J_URI")
    NEO4J_USERNAME = os.environ.get("NEO4J_USERNAME")
    NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD")
    NEO4J_DATABASE = os.environ.get("NEO4J_DATABASE")
    AURA_INSTANCEID = os.environ.get("AURA_INSTANCEID")
    AURA_INSTANCENAME = os.environ.get("AURA_INSTANCENAME", "Free instance")
    NEO4J_HOST = os.environ.get("NEO4J_HOST")

    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI", "sqlite:///movies.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = os.environ.get("SQLALCHEMY_TRACK_MODIFICATIONS", "False") == "True"