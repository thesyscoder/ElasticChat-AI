# chatbot blueprint
from flask import Blueprint, jsonify, abort, request, render_template
from utils.elasticsearch_utils import index_vector, search_vectors
from models.universal_sentence_encoder import get_embedding


chatbot_bp = Blueprint('chatbot', __name__,
                       template_folder='template', static_folder='static')


@chatbot_bp.route('/embed', methods=['POST'])
def embed():
    data = request.json
    text = data.get('text')

    if text:
        # Embed the text using Universal Sentence Encoder
        embedded_text = embed([text]).numpy().tolist()[0]

        # Index the embedded vector in Elasticsearch
        index_name = 'vector_index'
        doc = {'vector': embedded_text}
        es.index(index=index_name, body=doc)

        return jsonify({'message': 'Text embedded and indexed successfully'}), 201
    else:
        return jsonify({'error': 'Text not provided'}), 400


@chatbot_bp.route('/search', methods=['POST'])
def search():
    data = request.json
    query_text = data.get('query_text')

    if query_text:
        # Embed the query text using Universal Sentence Encoder
        query_vector = embed([query_text]).numpy().tolist()[0]

        index_name = 'vector_index'
        script_query = {
            "script_score": {
                "query": {"match_all": {}},
                "script": {
                    "source": "cosineSimilarity(params.query_vector, 'vector') + 1.0",
                    "params": {"query_vector": query_vector}
                }
            }
        }

        results = es.search(index=index_name, body={"query": script_query})
        return jsonify(results), 200
    else:
        return jsonify({'error': 'Query text not provided'}), 400


@chatbot_bp.route('/', methods=['POST'])
def chatbot():
    data = request.json
    user_input = data.get('user_input')

    if user_input:
        # Use the /search endpoint to find similar texts
        search_data = {'query_text': user_input}
        search_response = search_data(search_data)

        # Extract the most relevant result
        if 'hits' in search_response and 'hits' in search_response['hits']:
            top_hit = search_response['hits']['hits'][0]['_source']
            similar_text = top_hit['text']

            # Implement your chatbot logic here based on the similar_text
            # For simplicity, just echoing the similar_text in this example
            return jsonify({'chatbot_response': similar_text}), 200
        else:
            return jsonify({'chatbot_response': 'No matching response found'}), 200
    else:
        return jsonify({'error': 'User input not provided'}), 400