from flask import Blueprint, request, jsonify
from application.src.models.search import SearchData

query = Blueprint('search', __name__)


@query.route('/search', methods=['POST'])
def search():
    query_text = request.json.get('query', '')
    search_data = SearchData()
    results = search_data.Search(query_text)

    if not results:
        return jsonify(message=f"Resultado não encontrado para '{query_text}'")

    # Retorna os resultados como JSON
    return jsonify(results=results)
