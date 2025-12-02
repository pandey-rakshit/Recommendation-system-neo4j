from neomodel import StructuredNode, StringProperty, RelationshipFrom

class Genre(StructuredNode):
    name = StringProperty(unique_index=True, required=True)
    movies = RelationshipFrom('app.models.movie.Movie', "HAS_GENRE")
