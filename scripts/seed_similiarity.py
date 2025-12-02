import pandas as pd
import numpy as np
from sklearn.preprocessing import MultiLabelBinarizer, StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
from neo4j import GraphDatabase
from tqdm import tqdm
import os
from dotenv import load_dotenv

load_dotenv()


# ----------------------------------------------------------
# LOAD YOUR PROCESSED DATA
# ----------------------------------------------------------
movies_df = pd.read_csv("data/movies.csv")
genres_df = pd.read_csv("data/genres.csv")
keywords_df = pd.read_csv("data/keywords.csv")
cast_df = pd.read_csv("data/cast.csv")
directors_df = pd.read_csv("data/directors.csv")

print("Loaded datasets.")


# ----------------------------------------------------------
# PREP FEATURE TABLES
# ----------------------------------------------------------
print("Preparing feature lists...")

movie_ids = movies_df["movie_id"].tolist()

movie_to_genres = genres_df.groupby("movie_id")["genre"].apply(list)
movie_to_keywords = keywords_df.groupby("movie_id")["keyword"].apply(list)
movie_to_actors = cast_df.groupby("movie_id")["name"].apply(list)
movie_to_directors = directors_df.groupby("movie_id")["director"].apply(list)


# Ensure lists (avoid missing entries)
def safe_get(mapping, movie_id):
    return mapping[movie_id] if movie_id in mapping.index else []


# ----------------------------------------------------------
# BUILD STRUCTURED FEATURE TABLE
# ----------------------------------------------------------
data = []

for _, row in movies_df.iterrows():
    mid = row["movie_id"]

    data.append({
        "movie_id": mid,
        "genres": safe_get(movie_to_genres, mid),
        "keywords": safe_get(movie_to_keywords, mid),
        "actors": safe_get(movie_to_actors, mid),
        "directors": safe_get(movie_to_directors, mid),
        "year": row["release_year"],
        "rating": row["vote_average"],
        "popularity": row["popularity"]
    })

features_df = pd.DataFrame(data)


# ----------------------------------------------------------
# LIMIT ACTORS TO TOP 2000 (avoid huge vectors)
# ----------------------------------------------------------
TOP_ACTORS = 2000

actor_counts = cast_df["name"].value_counts().head(TOP_ACTORS).index
features_df["actors"] = features_df["actors"].apply(
    lambda lst: [a for a in lst if a in actor_counts]
)


# ----------------------------------------------------------
# VECTORIZE MULTI-LABEL COLUMNS
# ----------------------------------------------------------
def binarize_column(column_values):
    mlb = MultiLabelBinarizer()
    return mlb.fit_transform(column_values), mlb


genre_matrix, genre_mlb = binarize_column(features_df["genres"])
keyword_matrix, keyword_mlb = binarize_column(features_df["keywords"])
actor_matrix, actor_mlb = binarize_column(features_df["actors"])
director_matrix, director_mlb = binarize_column(features_df["directors"])

print("Vectorized multi-label features.")


# ----------------------------------------------------------
# NORMALIZE NUMERIC FEATURES
# ----------------------------------------------------------
numeric = features_df[["year", "rating", "popularity"]].fillna(0)
scaler = StandardScaler()
numeric_matrix = scaler.fit_transform(numeric)

print("Normalized numeric features.")


# ----------------------------------------------------------
# CONCATENATE ALL FEATURES INTO FINAL VECTORS
# ----------------------------------------------------------
X = np.hstack([
    genre_matrix * 5,         # weighted genres
    keyword_matrix * 3,       # weighted keywords
    actor_matrix * 8,         # weighted actors
    director_matrix * 4,      # weighted directors
    numeric_matrix            # year, rating, popularity
])

print("Final feature matrix shape:", X.shape)


# ----------------------------------------------------------
# COMPUTE COSINE SIMILARITY
# ----------------------------------------------------------
print("Computing cosine similarity...")

cos_sim = cosine_similarity(X)

print("Similarity matrix computed.")


# ----------------------------------------------------------
# SELECT TOP-K SIMILAR MOVIES
# ----------------------------------------------------------
TOP_K = 20
similarity_results = []

print("Selecting top-K similar movies...")

for i, mid in enumerate(tqdm(movie_ids)):
    sim_scores = cos_sim[i]
    top_indices = sim_scores.argsort()[::-1][1:TOP_K + 1]

    for idx in top_indices:
        similarity_results.append({
            "m1": mid,
            "m2": movie_ids[idx],
            "score": float(sim_scores[idx])
        })

print(f"Generated {len(similarity_results)} similarity pairs.")


# ----------------------------------------------------------
# WRITE SIMILARITY EDGES TO NEO4J
# ----------------------------------------------------------
print("Connecting to Neo4j...")

driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD"))
)

driver.verify_connectivity()
print("Connected.")


def write_similarity_batch(tx, batch):
    tx.run("""
        UNWIND $rows AS row
        MATCH (m1:Movie {movie_id: row.m1})
        MATCH (m2:Movie {movie_id: row.m2})
        MERGE (m1)-[s:SIMILAR_TO]->(m2)
        SET s.score = row.score
    """, rows=batch)


BATCH = 500

print("Writing SIMILAR_TO edges...")

for i in range(0, len(similarity_results), BATCH):
    batch = similarity_results[i:i + BATCH]
    with driver.session() as session:
        session.execute_write(write_similarity_batch, batch)

print("DONE. Vector-based SIMILAR_TO edges created!")
