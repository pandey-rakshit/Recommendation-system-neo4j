from neomodel import config

def init_neomodel(app):
    config.DATABASE_URL = f'neo4j+ssc://{app.config["NEO4J_USERNAME"]}:{app.config["NEO4J_PASSWORD"]}@{app.config["NEO4J_HOST"]}:7687'
    print("Connected to Neo4j:", config.DATABASE_URL)
