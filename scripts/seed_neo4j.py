from neo4j import GraphDatabase
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

# -------------------------------------------------------------------
# LOAD CLEANED CSV FILES (from your data/)
# -------------------------------------------------------------------
movies_df = pd.read_csv("data/movies.csv")
genres_df = pd.read_csv("data/genres.csv")
keywords_df = pd.read_csv("data/keywords.csv")
cast_df = pd.read_csv("data/cast.csv")
directors_df = pd.read_csv("data/directors.csv")

# -------------------------------------------------------------------
# CONNECT TO NEO4J
# -------------------------------------------------------------------
driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))
)

driver.verify_connectivity()
print("Connected to Neo4j database.")


# -------------------------------------------------------------------
# CREATE INDEXES (USE YOUR WORKING FULLTEXT SYNTAX)
# -------------------------------------------------------------------
def create_indexes(tx):

    # YOUR WORKING FULLTEXT SYNTAX (unchanged)
    tx.run("""
        CREATE FULLTEXT INDEX movieSearch IF NOT EXISTS
        FOR (m:Movie) ON EACH [m.title, m.overview]
    """)

    tx.run("""
        CREATE CONSTRAINT movie_id_unique IF NOT EXISTS
        FOR (m:Movie) REQUIRE m.movie_id IS UNIQUE
    """)

    tx.run("""
        CREATE CONSTRAINT genre_unique IF NOT EXISTS
        FOR (g:Genre) REQUIRE g.name IS UNIQUE
    """)

    tx.run("""
        CREATE CONSTRAINT keyword_unique IF NOT EXISTS
        FOR (k:Keyword) REQUIRE k.name IS UNIQUE
    """)

    tx.run("""
        CREATE CONSTRAINT person_unique IF NOT EXISTS
        FOR (p:Person) REQUIRE p.name IS UNIQUE
    """)


# -------------------------------------------------------------------
# SEED MOVIES
# -------------------------------------------------------------------
def seed_movies(tx, rows):
    tx.run("""
        UNWIND $rows AS row
        MERGE (m:Movie {movie_id: row.movie_id})
        SET m.title = row.title,
            m.overview = row.overview,
            m.release_year = row.release_year,
            m.runtime = row.runtime,
            m.vote_average = row.vote_average,
            m.vote_count = row.vote_count,
            m.popularity = row.popularity,
            m.poster_url = row.poster_url
    """, rows=rows)


# -------------------------------------------------------------------
# SEED GENRES
# -------------------------------------------------------------------
def seed_genres(tx, rows):
    tx.run("""
        UNWIND $rows AS row
        MATCH (m:Movie {movie_id: row.movie_id})
        MERGE (g:Genre {name: row.genre})
        MERGE (m)-[:HAS_GENRE]->(g)
    """, rows=rows)


# -------------------------------------------------------------------
# SEED KEYWORDS
# -------------------------------------------------------------------
def seed_keywords(tx, rows):
    tx.run("""
        UNWIND $rows AS row
        MATCH (m:Movie {movie_id: row.movie_id})
        MERGE (k:Keyword {name: row.keyword})
        MERGE (m)-[:HAS_KEYWORD]->(k)
    """, rows=rows)


# -------------------------------------------------------------------
# SEED CAST
# -------------------------------------------------------------------
def seed_cast(tx, rows):
    tx.run("""
        UNWIND $rows AS row
        MATCH (m:Movie {movie_id: row.movie_id})
        MERGE (p:Person {name: row.name})
            SET p.tmdb_id = row.person_id
        MERGE (p)-[:ACTED_IN]->(m)
    """, rows=rows)



# -------------------------------------------------------------------
# SEED DIRECTORS
# -------------------------------------------------------------------
def seed_directors(tx, rows):
    tx.run("""
        UNWIND $rows AS row
        MATCH (m:Movie {movie_id: row.movie_id})
        MERGE (p:Person {name: row.director})
        MERGE (p)-[:DIRECTED]->(m)
    """, rows=rows)


# -------------------------------------------------------------------
# CHUNKING UTILITY
# -------------------------------------------------------------------
CHUNK = 400
SIM_CHUNK = 50

def chunkify(df):
    for i in range(0, len(df), CHUNK):
        yield df.iloc[i:i+CHUNK].to_dict("records")

def chunkify_list(lst, size):
    for i in range(0, len(lst), size):
        yield lst[i:i + size]



# -------------------------------------------------------------------
# RUN IMPORT PROCESS
# -------------------------------------------------------------------
with driver.session() as session:

    print("Creating indexes and constraints...")
    session.execute_write(create_indexes)

    print("Seeding movies...")
    for chunk in chunkify(movies_df):
        session.execute_write(seed_movies, chunk)

    print("Seeding genres...")
    for chunk in chunkify(genres_df):
        session.execute_write(seed_genres, chunk)

    print("Seeding keywords...")
    for chunk in chunkify(keywords_df):
        session.execute_write(seed_keywords, chunk)

    print("Seeding cast...")
    for chunk in chunkify(cast_df):
        session.execute_write(seed_cast, chunk)

    print("Seeding directors...")
    for chunk in chunkify(directors_df):
        session.execute_write(seed_directors, chunk)


print("Done! Graph imported successfully with advanced similarity.")
