# 🎬 Neo4j Movie Recommender  
*A graph-based movie recommendation system built with Flask, Neo4j, and Neomodel.*

This project is a complete movie discovery and recommendation platform powered by Neo4j Graph Database.  
It supports fast movie lookup, intelligent recommendations based on search queries, dynamic movie sections, and a clean interactive frontend.

---

## 🚀 Overview

The **Neo4j Movie Recommender** is a full-stack movie exploration system built around a graph database model.  
Instead of using a traditional relational database, movie entities and their relationships are stored in **Neo4j**, allowing fast traversal, similarity search, and flexible querying.

The project contains:

- A **Flask backend** exposing clean REST APIs  
- A **Neo4j graph database** accessed via *Neomodel*  
- A **lightweight frontend (HTML/CSS/JS)**  
- Intelligent recommendations based on **user search query**  
- Dynamic sections with **infinite scroll**  
- A local caching layer on the browser for speed  
- A pipeline (CSV → DataFrame → Neo4j) currently being converted into a reusable **SQL → Neo4j ingestion pipeline**

---

## 🛠 Tech Stack

### **Backend**
- Python 3
- Flask (REST API)
- Neo4j Graph Database
- Neomodel (ORM for Neo4j)

### **Frontend**
- HTML5
- CSS3 (custom Netflix-like UI)
- Vanilla JavaScript (no frameworks)
- Browser caching using `sessionStorage`

### **Data Processing**
- Pandas  
- CSV ingestion → Neo4j using Neomodel  
- *(In progress)* SQL → Neo4j ingestion pipeline

---

## ⭐ Key Features

### 🎞 Homepage Sections
- Popular  
- Trending  
- Top Rated  
- Infinite scroll dynamic sections (Action, Comedy, Drama, Sci-Fi, Adventure…)

Sections load progressively as the user scrolls, and each section is cached for performance.

---

### 🔍 Search + Recommendation Engine
- Search for movies using keywords  
- Instant results  
- Recommendations **based on the search query**  
- Cached responses to avoid repeated API calls  
- Clean UI with hover expansion showing details  
- Fallback when poster images fail (404-proof)

**Recommendation Logic:**  
The system uses the search query to:
- Find the closest matching movies  
- Retrieve related movies via graph relationships (genre → movie; movie → similar movies)  
- Return a curated list of suggestions

---

### 🖼 Movie Card UI (Netflix-style)
- Real poster shown when valid  
- Fallback “No Image” card when poster URL fails  
- Hover-expand animation that shows:
  - Title  
  - Overview snippet  
  - Rating  
  - Release year  
  - Vote count  
- Smooth transitions  
- No duplicate images  
- No dark overlays on the poster

---

### ⚡ Browser-Side Caching (sessionStorage)
To reduce API calls:
- Homepage sections cached  
- Search results cached per query  
- Dynamic sections cached  
- State preserved while browsing

---

## 🗂 Data Pipeline (Implemented + Planned)

### ✔ **Current: CSV → DataFrame → Neo4j Import**
The current workflow uses:
- CSV files  
- Pandas DataFrames  
- Neomodel ORM  
To load movies, genres, and relationships into Neo4j.

### 🚧 **Upcoming (WIP): SQL → Neo4j Pipeline**
A generic ingestion pipeline is being developed:
- Connect to SQL database  
- Extract movie data  
- Transform + clean  
- Populate Neo4j nodes and relationships automatically  

This will replace manual CSV imports and make the system production-ready.

---

## 🔌 API Endpoints

### **1. Get sections**
`GET /api/catalog?sections=`
Returns default sections: popular, trending, topRated.

### **2. Get specific sections**
`GET /api/catalog?sections=action,comedy`


### **3. Search movies**
`GET /api/catalog/search?q=<query>`
Response:
- search_results  
- recommendations (based on search query)

### **4. Get dynamic scrolling sections**
Same as above:
`GET /api/catalog?sections=drama`


---

## 🖥 Frontend UX

The UI was designed to resemble Netflix-style browsing:
- Clean rows of content  
- Hover-expand cards  
- Infinite section loading  
- No frameworks required  
- Reliable caching layer  

The frontend calls only 3 API endpoints and builds everything dynamically using vanilla JS.

---
