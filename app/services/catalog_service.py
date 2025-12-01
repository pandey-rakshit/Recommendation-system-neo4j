from app.repositories.catalog_repository import CatalogRepository

class CatalogService:

    @staticmethod
    def get_catalog_sections(sections: list[str]):
        """
        sections: list like ["popular", "trending", "topRated"]
        Returns Neo4j nodes grouped by section.
        """
        # Assuming CatalogRepository.get_sections is implemented for this
        return CatalogRepository.get_sections(sections)

    @staticmethod
    def get_search_and_recommendations(search_query: str, search_limit: int = 5, rec_limit: int = 10):
        """
        Combines search results and content-based recommendations into a single, 
        efficient database call using CatalogRepository.search_and_recommend_unified.
        
        This saves on API cost and reduces network latency compared to two separate queries.
        
        Args:
            search_query (str): The text the user entered.
            search_limit (int): Max number of direct search results.
            rec_limit (int): Max number of recommendations.
            
        Returns:
            dict: Dictionary containing 'search_results' and 'recommendations'.
        """
        
        # We now use the unified method which executes both steps in a single Cypher transaction.
        search_results, recommendations = CatalogRepository.search_and_recommend_unified(
            query=search_query,
            search_limit=search_limit,
            recommendation_limit=rec_limit
        )

        if not search_results:
            return {
                "search_results": [],
                "recommendations": CatalogRepository.popular(limit=rec_limit)
            }

        return {
            "search_results": search_results,
            "recommendations": recommendations
        }