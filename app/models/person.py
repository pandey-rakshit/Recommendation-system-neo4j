from neomodel import StructuredNode, StringProperty, IntegerProperty, RelationshipTo

class Person(StructuredNode):
    name = StringProperty(unique_index=True, required=True)
    tmdb_id = IntegerProperty(required=False)

    acted_in = RelationshipTo('app.models.movie.Movie', 'ACTED_IN')
    directed = RelationshipTo('app.models.movie.Movie', 'DIRECTED')
