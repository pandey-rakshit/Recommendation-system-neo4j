from neo4j import GraphDatabase
import pandas as pd
import json
import os

from dotenv import load_dotenv

load_dotenv()

df = pd.read_csv("data/movies.csv")

driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))
)

driver.verify_connectivity()
print("Connected to Neo4j database.")


def parse_list(value):
    if pd.isna(value) or value == "[]":
        return []
    try:
        data = json.loads(value.replace("'", '"'))
        return [item.get("name") for item in data]
    except:
        return []

def create_fulltext_index(tx):

    tx.run("""
        CREATE FULLTEXT INDEX movieSearch IF NOT EXISTS 
        FOR (m:Movie) ON EACH [m.title, m.overview]
    """)

    tx.run("CREATE CONSTRAINT movie_id_unique IF NOT EXISTS FOR (m:Movie) REQUIRE m.movie_id IS UNIQUE")
    tx.run("CREATE CONSTRAINT genre_name_unique IF NOT EXISTS FOR (g:Genre) REQUIRE g.name IS UNIQUE")


def seed_movies(tx, rows):
    tx.run("""
        UNWIND $rows AS row
        MERGE (m:Movie {movie_id: row.movie_id})
        SET m += row.properties
    """, rows=rows)


def seed_genres(tx, rows):
    tx.run("""
        UNWIND $rows AS row
        MATCH (m:Movie {movie_id: row.movie_id})
        UNWIND row.genres AS g
        MERGE (genre:Genre {name: g})
        MERGE (m)-[:IN_GENRE]->(genre)
    """, rows=rows)


def seed_keywords(tx, rows):
    tx.run("""
        UNWIND $rows AS row
        MATCH (m:Movie {movie_id: row.movie_id})
        UNWIND row.keywords AS kw
        MERGE (k:Keyword {name: kw})
        MERGE (m)-[:HAS_KEYWORD]->(k)
    """, rows=rows)


def seed_languages(tx, rows):
    tx.run("""
        UNWIND $rows AS row
        MATCH (m:Movie {movie_id: row.movie_id})
        UNWIND row.languages AS lang
        MERGE (l:Language {name: lang})
        MERGE (m)-[:HAS_LANGUAGE]->(l)
    """, rows=rows)

def seed_movie_similarity(tx):
    print("Executing Movie Similarity Calculation...")
    tx.run("""
        MATCH (m1:Movie)-[:IN_GENRE|HAS_KEYWORD]->(trait)
        <-[:IN_GENRE|HAS_KEYWORD]-(m2:Movie)
        WHERE m1 <> m2 
        WITH m1, m2, COUNT(DISTINCT trait) AS shared_traits
        // Filter for movies that share a significant number of features
        WHERE shared_traits > 3 
        // MERGE the SIMILAR_TO relationship with the score (number of shared traits)
        MERGE (m1)-[s:SIMILAR_TO]->(m2)
        SET s.score = shared_traits
    """)

print("Preparing rows...")
rows = []
all_movie_ids = []

for _, row in df.iterrows():
    movie_id = int(row["id"])
    all_movie_ids.append(movie_id)
    
    rows.append({
        "movie_id": movie_id,
        "properties": {
            "title": row["title"],
            "overview": row["overview"],
            "popularity": float(row["popularity"]),
            "vote_average": float(row["vote_average"]),
            "vote_count": int(row["vote_count"]),
            "release_date": row["release_date"],
            "runtime": row["runtime"]
        },
        "genres": parse_list(row["genres"]),
        "keywords": parse_list(row["keywords"]),
        "languages": parse_list(row["spoken_languages"]),
    })

CHUNK = 300

def chunkify(x):
    return [x[i:i+CHUNK] for i in range(0, len(x), CHUNK)]

with driver.session() as session:
    print("Creating indexes and constraints...")
    session.execute_write(create_fulltext_index)
    
    print("Seeding movies...")
    for part in chunkify(rows):
        session.execute_write(seed_movies, part)

    print("Seeding genres...")
    for part in chunkify(rows):
        session.execute_write(seed_genres, part)

    print("Seeding keywords...")
    for part in chunkify(rows):
        session.execute_write(seed_keywords, part)

    print("Seeding languages...")
    for part in chunkify(rows):
        session.execute_write(seed_languages, part)

    print("Calculating and Seeding Movie Similarity (SIMILAR_TO)...")
    session.execute_write(seed_movie_similarity)

print("Done! Full content graph seeded, including direct movie similarity links.")