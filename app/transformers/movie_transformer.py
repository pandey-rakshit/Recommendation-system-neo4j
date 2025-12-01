class MovieTransformer:

    @staticmethod
    def transform(node):
        if node is None:
            return None
        data = dict(node.__properties__)
        return data
