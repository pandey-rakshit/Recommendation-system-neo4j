from neomodel import (
    StructuredNode, StringProperty, IntegerProperty, FloatProperty,
    RelationshipTo, RelationshipFrom
)

class Movie(StructuredNode):
    movie_id = IntegerProperty(unique_index=True, required=True)
    title = StringProperty()
    overview = StringProperty()
    popularity = FloatProperty()
    vote_average = FloatProperty()
    vote_count = IntegerProperty()
    release_year = IntegerProperty()
    runtime = IntegerProperty()
    poster_url = StringProperty()

    genres = RelationshipTo('app.models.genre.Genre', 'HAS_GENRE')
    keywords = RelationshipTo('app.models.keyword.Keyword', 'HAS_KEYWORD')
    cast = RelationshipFrom('app.models.person.Person', 'ACTED_IN')
    directors = RelationshipFrom('app.models.person.Person', 'DIRECTED')
    similar = RelationshipTo('app.models.movie.Movie', 'SIMILAR_TO')
