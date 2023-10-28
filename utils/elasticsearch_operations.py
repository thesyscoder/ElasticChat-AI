# elasticsearch_operations.py

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk


def initialize_index(es, index_name):
    if not es.indices.exists(index=index_name):
        print(f"Index {index_name} does not exist, creating now...")
        es.indices.create(index=index_name)
        print(f"Index {index_name} created successfully.")
    else:
        print(f"Index {index_name} exists.")


def add_documents(es, index_name, documents):
    actions = [
        {"_op_type": "index", "_index": index_name, "_source": doc} for doc in documents
    ]
    success, failed = bulk(es, actions)
    print(f"Successfully indexed {success} documents.")
    print(f"Failed to index {failed} documents.")
