from neomodel import StructuredNode, StringProperty, IntegerProperty, FloatProperty, RelationshipTo

class Movie(StructuredNode):
    movie_id = IntegerProperty(unique_index=True, required=True)
    title = StringProperty()
    overview = StringProperty()
    popularity = FloatProperty()
    vote_average = FloatProperty()
    vote_count = IntegerProperty()
    release_date = StringProperty()
    runtime = IntegerProperty()

    genres = RelationshipTo('app.models.genre.Genre', "IN_GENRE")
    keywords = RelationshipTo('app.models.keyword.Keyword', "HAS_KEYWORD")