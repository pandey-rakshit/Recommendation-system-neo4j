from neomodel import db
from app.models.movie import Movie


class CatalogRepository:

    SECTION_MAPPINGS = {
        "popular": lambda: CatalogRepository.popular(),
        "trending": lambda: CatalogRepository.trending(),
        "topRated": lambda: CatalogRepository.top_rated(),

        # Genre-based
        "action": lambda: CatalogRepository.by_genre("Action"),
        "comedy": lambda: CatalogRepository.by_genre("Comedy"),
        "drama": lambda: CatalogRepository.by_genre("Drama"),
    }

    @staticmethod
    def popular(limit=20):
        """Returns movies ordered by simple popularity score."""
        return list(Movie.nodes.order_by("-popularity")[:limit])

    @staticmethod
    def trending(limit=20):
        """Returns recently released movies ordered by popularity."""
        return list(
            Movie.nodes.filter(release_year__gte=2020)
            .order_by("-popularity")[:limit]
        )

    @staticmethod
    def top_rated(limit=20):
        """Returns highly-rated movies with a minimum vote count."""
        return list(
            Movie.nodes.filter(vote_count__gt=500)
            .order_by("-vote_average")[:limit]
        )

    @staticmethod
    def by_genre(genre_name, limit=20):
        query = """
        MATCH (g:Genre {name: $genre})
        MATCH (m:Movie)-[:HAS_GENRE]->(g)
        RETURN m ORDER BY m.popularity DESC LIMIT $limit
        """
        results, _ = db.cypher_query(query, {
            "genre": genre_name, "limit": limit
        })
        return [Movie.inflate(row[0]) for row in results]
    

    @staticmethod
    def get_sections(section_list: list[str]):
        """
        Returns sections as dict: { section_name: movie_list }
        Only loads the sections requested.
        """
        result = {}
        for name in section_list:
            key = name.strip()
            if key in CatalogRepository.SECTION_MAPPINGS:
                result[key] = CatalogRepository.SECTION_MAPPINGS[key]()

        return result

    @staticmethod
    def search_movies(query: str, limit=5):
        if not query:
            return []

        search_term = query.strip() + "*"

        cypher = """
        CALL db.index.fulltext.queryNodes('movieSearch', $term)
        YIELD node AS m, score AS ft_score
        WITH m, ft_score + (m.vote_average * 0.03) AS score
        RETURN m ORDER BY score DESC LIMIT $limit
        """

        results, _ = db.cypher_query(cypher, {
            "term": search_term,
            "limit": limit
        })
        return [Movie.inflate(row[0]) for row in results]

    @staticmethod
    def similar_movies(movie_id: int, limit=10):
        """
        USES THE PYTHON-COMPUTED SIMILAR_TO edges.
        Fast, accurate, no Cypher scoring needed.
        """
        query = """
        MATCH (m:Movie {movie_id: $id})-[s:SIMILAR_TO]->(rec:Movie)
        RETURN rec ORDER BY s.score DESC LIMIT $limit
        """

        results, _ = db.cypher_query(query, {
            "id": movie_id,
            "limit": limit
        })

        return [Movie.inflate(row[0]) for row in results]

    @staticmethod
    def search_and_recommend(query: str, search_limit=5, rec_limit=10):
        """
        1. Full-text search movies
        2. For each search result, fetch similar movies via SIMILAR_TO
        3. Merge + dedupe results
        """
        search_results = CatalogRepository.search_movies(query, limit=search_limit)

        if not search_results:
            return [], []

        seed_ids = [m.movie_id for m in search_results]

        all_recs = []
        for sid in seed_ids:
            all_recs.extend(CatalogRepository.similar_movies(sid, limit=rec_limit))

        seen = set(seed_ids)
        unique_recs = []
        for m in all_recs:
            if m.movie_id not in seen:
                unique_recs.append(m)
                seen.add(m.movie_id)

        return search_results, unique_recs[:rec_limit]
