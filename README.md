# 🎬 Movie Recommendation System (Neo4j + Flask)

A production-grade **content-based movie recommendation system** built using:

* **Neo4j AuraDB** (Graph Database)
* **Python + Flask API backend**
* **NeoModel (ORM for Neo4j)**
* **Pandas + Scikit-Learn** for similarity vectorization
* **Front-end: HTML + JS** movie browser UI

This system imports movie metadata from the Kaggle dataset, builds a full graph in Neo4j, computes vector-based similarities, and exposes an API to deliver fast movie recommendations.

---

## 📡 **Data Source**

Dataset used:
👉 [https://www.kaggle.com/datasets/rounakbanik/the-movies-dataset](https://www.kaggle.com/datasets/rounakbanik/the-movies-dataset)

It includes:

* movie metadata (overview, genres, keywords, cast, directors)
* ratings
* popularity stats
* rich TMDB metadata

We preprocess these CSVs, convert them into a graph structure, and then compute similarity scores for recommendations.

---

# 🚀 **How to Run the Project**

### **1️⃣ Create Neo4j AuraDB Free Instance**

* Visit [https://console.neo4j.io/](https://console.neo4j.io/)
* Create a **free AuraDB instance**
* Save the connection URI, username, and password

These go into `.env`.

---

### **2️⃣ Clone the Repository**

```bash
git clone https://github.com/<your-repo>
cd <repo>
```

---

### **3️⃣ Add Environment Variables**

Create a file `.env` using the structure from `.env.example`:

```
NEO4J_URI=neo4j+ssc://xxxxx.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your-password
```

---

### **4️⃣ Run Data Import Scripts**

#### **Step 1: Import CSV → Neo4j Graph**

```bash
python scripts/seed_neo4j.py
```

This script:

✔ Reads cleaned CSVs from `/data`

✔ Creates all Neo4j indexes + constraints

✔ Seeds:

* Movies
* Genres
* Keywords
* Cast (actors)
* Directors
  ✔ Builds graph relationships using:

  * `HAS_GENRE`
  * `HAS_KEYWORD`
  * `ACTED_IN`
  * `DIRECTED`

---

#### **Step 2: Compute Movie Similarity (Vectors + Cosine Similarity)**

```bash
python scripts/seed_similarity.py
```

This script:

✔ Builds movie feature vectors using:

* Genres
* Keywords
* Top 2000 actors
* Directors
* Year
* Rating
* Popularity

✔ Uses **scikit-learn** to compute cosine similarity
✔ Writes top 20 similar movies into Neo4j:

```
(m1:Movie)-[:SIMILAR_TO {score: 0.93}]->(m2:Movie)
```

These relationships power the recommendation engine.

---

### **5️⃣ Run the Flask Server**

```bash
python run.py
```

Backend starts at:
👉 [http://localhost:5000](http://localhost:5000)

Front-end UI at:
👉 [http://localhost:5000/](http://localhost:5000/)

---

# 🧩 **Project Structure**

```
project/
│── app/
│   ├── models/          # NeoModel ORM classes
│   ├── controllers/     # Flask API endpoints
│   ├── services/        # Business logic layer
│   ├── repositories/    # Neo4j DB read/write logic
│   ├── transformers/    # Convert Neo4j nodes → JSON
│   ├── utils/           # Helpers, config
│── scripts/
│   ├── seed_neo4j.py    # CSV → Neo4j import
│   ├── seed_similarity.py # vector similarity computation
│── data/                # processed CSV files
│── templates/           # HTML views
│── static/              # JS, CSS, images
│── run.py               # Flask entry point
│── README.md
└── .env
```

---

# 🧠 **Internal Architecture**

## **1. Models (NeoModel)**

Each graph node type has a corresponding model:

* `Movie`
* `Genre`
* `Keyword`
* `Person` (Actor/Director)

Example:

```python
class Movie(StructuredNode):
    movie_id = IntegerProperty(unique_index=True)
    title = StringProperty()
    popularity = FloatProperty()

    genres = RelationshipTo("Genre", "HAS_GENRE")
    keywords = RelationshipTo("Keyword", "HAS_KEYWORD")
    actors = RelationshipFrom("Person", "ACTED_IN")
```

---

## **2. Controllers → API Endpoints**

Flask controllers expose REST endpoints:

### GET `/api/catalog?sections=popular,trending`

Returns homepage sections.

### GET `/api/catalog/search?q=inception`

Returns:

* search results (full text search)
* recommendations (from SIMILAR_TO)

### GET `/api/movie/<id>`

Get movie details.

---

## **3. Service Layer**

Business logic goes here.

Example: search + recommend:

```python
search_results, recommendations = CatalogRepository.search_and_recommend(...)
```

---

## **4. Repository Layer (Neo4j calls)**

Handles raw Cypher queries or ORM queries.

Examples:

```python
MATCH (m:Movie)-[:HAS_GENRE]->(g:Genre {name: "Action"})
RETURN m
```

```python
MATCH (:Movie {movie_id: $id})-[s:SIMILAR_TO]->(rec)
RETURN rec ORDER BY s.score DESC
```

This keeps database logic in one place.

---

# 🔍 **How the Recommendation Engine Works**

There are two stages:

---

## **Stage 1: Graph Modeling in Neo4j**

Movies become interconnected via:

* `(:Movie)-[:HAS_GENRE]->(:Genre)`
* `(:Movie)-[:HAS_KEYWORD]->(:Keyword)`
* `(:Person)-[:ACTED_IN]->(:Movie)`
* `(:Person)-[:DIRECTED]->(:Movie)`

This allows:

* Genre filtering
* Actor/Director queries
* Rich contextual relationships

---

## **Stage 2: Vector Similarity + Cosine Similarity**

For each movie, a feature vector is created:

| Feature Type | Example                  | Weight     |
| ------------ | ------------------------ | ---------- |
| Genres       | Action, Comedy           | ×5         |
| Keywords     | hero, revenge            | ×3         |
| Actors       | Tom Cruise               | ×8         |
| Directors    | Nolan                    | ×4         |
| Metadata     | year, rating, popularity | normalized |

Then:

```
similarity = cosine(vectorA, vectorB)
```

Top 20 similar movies are written back as graph edges:

```
(m1)-[:SIMILAR_TO {score: 0.92}]->(m2)
```

These edges are used by:

* Search suggestions
* “Similar movies” UI section
* Recommendation API

---

# 🎥 **Front-End (Movie Browser UI)**

UI features:

* Homepage sections (Popular, Trending, Top Rated)
* Infinite scroll genre sections
* Search page with:

  * Live search results
  * Recommendations
* Poster fallback handling
* Dynamic loading states
* Cached API calls for performance

---

# 🎯 **Summary — What This Project Delivers**

✔ Full content-based recommendation system

✔ Neo4j-powered knowledge graph

✔ Vector similarity + cosine scoring

✔ Fully optimized relationships

✔ Search + Recommendations API

✔ Modern interactive movie browser

✔ Modular clean backend architecture

✔ Production-ready codebase