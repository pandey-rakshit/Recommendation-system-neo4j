from neomodel import db
from app.models.movie import Movie


class CatalogRepository:

    @staticmethod
    def popular(limit=20):
        """Returns movies ordered by simple popularity score."""
        return list(Movie.nodes.order_by("-popularity")[:limit])

    @staticmethod
    def trending(limit=20):
        """Returns recently released movies ordered by popularity."""
        return list(
            Movie.nodes.filter(release_date__gte="2020-01-01")
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
        """
        Movies related to a Genre node. Uses Cypher to ensure robustness.
        """
        query = """
        MATCH (g:Genre {name: $genre_name})
        MATCH (m:Movie)-[:IN_GENRE]->(g)
        RETURN m 
        ORDER BY m.popularity DESC
        LIMIT $limit
        """
        
        results, _ = db.cypher_query(query, {'genre_name': genre_name, 'limit': limit})
        
        # Manually inflate the Movie nodes
        return [Movie.inflate(row[0]) for row in results]

    @staticmethod
    def search_movies(query: str, limit: int = 5):
        """
        Performs a comprehensive, multi-field search using Full-Text Search (FTS).
        
        NOTE: This requires a pre-existing FTS index named 'movieSearch'.
        """
        if not query:
            return []

        # Prepare the search term with a wildcard for prefix matching
        search_term = query.strip() + "*"

        query = """
        CALL db.index.fulltext.queryNodes('movieSearch', $search_term) YIELD node AS m, score AS ft_score
        WITH m, ft_score
        WITH m, (ft_score * 0.7) + (m.vote_average * 0.03) AS final_score

        RETURN m
        ORDER BY final_score DESC
        LIMIT $limit
        """

        results, _ = db.cypher_query(query, {'search_term': search_term, 'limit': limit})
        return [Movie.inflate(row[0]) for row in results]


    @staticmethod
    def recommend_movies(seed_movie_ids: list, limit: int = 10):
        """
        Recommends movies based on high similarity to the seed movies.
        
        Args:
            seed_movie_ids: The movie_ids of the movies returned by the user's search query, 
                            used to determine the user's current interests.
        """
        if not seed_movie_ids:
            return []

        query = """
        WITH $seed_movie_ids AS seed_ids
        MATCH (m:Movie) WHERE m.movie_id IN seed_ids
        MATCH (m)-[:IN_GENRE|HAS_KEYWORD]->(trait)
        MATCH (rec:Movie)-[:IN_GENRE|HAS_KEYWORD]->(trait)
        OPTIONAL MATCH (m)-[s:SIMILAR_TO]->(rec)
        WHERE NOT rec.movie_id IN seed_ids
        WITH rec, 
             SUM(s.score) AS total_sim_score, 
             COUNT(DISTINCT trait) AS total_trait_count
        WITH rec, 
             COALESCE(total_sim_score * 10, total_trait_count) AS content_score
        WHERE content_score > 0
        WITH rec, (content_score + (rec.vote_average / 10.0)) AS final_score
        RETURN rec
        ORDER BY final_score DESC
        LIMIT $limit
        """
        
        results, _ = db.cypher_query(query, {
            'seed_movie_ids': seed_movie_ids, 
            'limit': limit
        })

        return [Movie.inflate(row[0]) for row in results]


    @staticmethod
    def search_and_recommend_unified(query: str, search_limit: int = 5, recommendation_limit: int = 10):
        
        if not query:
            return [], []

        search_term = query.strip() + "*"

        query = """
        CALL db.index.fulltext.queryNodes('movieSearch', $search_term) YIELD node AS search_movie, score AS ft_score
        WITH search_movie, (ft_score * 0.7) + (search_movie.vote_average * 0.03) AS final_search_score
        ORDER BY final_search_score DESC
        LIMIT $search_limit

        WITH COLLECT(search_movie) AS search_results, COLLECT(search_movie.movie_id) AS seed_ids

        UNWIND seed_ids AS seed_id
        MATCH (m:Movie {movie_id: seed_id})
        MATCH (m)-[:IN_GENRE|HAS_KEYWORD]->(trait)
        MATCH (rec:Movie)-[:IN_GENRE|HAS_KEYWORD]->(trait)
        OPTIONAL MATCH (m)-[s:SIMILAR_TO]->(rec)
        WHERE NOT rec.movie_id IN seed_ids
        WITH search_results, rec, 
             SUM(s.score) AS total_sim_score, 
             COUNT(DISTINCT trait) AS total_trait_count
        WITH search_results, rec, 
             COALESCE(total_sim_score * 10, total_trait_count) AS content_score
        WHERE content_score > 0
        WITH search_results, rec, (content_score + (rec.vote_average / 10.0)) AS final_score
        ORDER BY final_score DESC
        LIMIT $recommendation_limit
        RETURN search_results, COLLECT(rec) AS recommendations
        """
        
        results, _ = db.cypher_query(query, {
            'search_term': search_term, 
            'search_limit': search_limit,
            'recommendation_limit': recommendation_limit
        })
        
        if not results:
            return [], []
            
        search_nodes = results[0][0]
        recommendation_nodes = results[0][1]
        
        search_results = [Movie.inflate(node) for node in search_nodes]
        recommendations = [Movie.inflate(node) for node in recommendation_nodes]
        
        return search_results, recommendations