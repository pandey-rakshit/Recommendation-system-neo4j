from flask import Blueprint, request, jsonify
from app.utils.request_parser import parse_sections
from app.services.catalog_service import CatalogService
from app.transformers.movie_transformer import MovieTransformer

catalog_api = Blueprint("catalog", __name__, url_prefix="/api/catalog")

@catalog_api.get("/")
def get_catalog():

    sections_param = request.args.get("sections")
    sections = parse_sections(sections_param)

    raw_nodes = CatalogService.get_catalog_sections(sections)

    print(raw_nodes)

    response_data = {
        section: [MovieTransformer.transform(node) for node in nodes]
        for section, nodes in raw_nodes.items()
    }

    print(response_data)

    return jsonify(response_data), 200

@catalog_api.get("/search")
def search_and_recommend():
    search_query = request.args.get("q", "")
    result = CatalogService.get_search_and_recommendations(
        search_query=search_query
    )

    response_data = {
        "search_results": [MovieTransformer.transform(node) for node in result["search_results"]],
        "recommendations": [MovieTransformer.transform(node) for node in result["recommendations"]],
    }
    return jsonify(response_data), 200

