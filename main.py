# app/main.py

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from elasticsearch import Elasticsearch
import tensorflow as tf
import tensorflow_hub as hub
from elasticsearch.helpers import bulk
from utils.elasticsearch_operations import initialize_index, add_documents

app = FastAPI()

# Initialize Elasticsearch client
es = Elasticsearch(['http://localhost:9200'])
# Define your index
index_name = "fastchat"

# Initialize index and add documents
initialize_index(es, index_name)

# Define the documents you want to add
documents = [
    {"content": "I love FastAPI! It's a fantastic web framework."},
    {"content": "FastAPI makes it easy to build modern web APIs with Python."},
    {"content": "Elasticsearch is a powerful search engine for full-text search."},
]

# Add documents to the index
add_documents(es, index_name, documents)


# Load TensorFlow Universal Sentence Encoder from TensorFlow Hub
model_url = "https://tfhub.dev/google/universal-sentence-encoder/4"
embed = hub.load(model_url)
tf.saved_model.save(embed, "universal_sentence_encoder")

embed = tf.saved_model.load("universal_sentence_encoder")

# Initialize Jinja2 templates
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/search")
async def search(query: str):
    # Perform Elasticsearch search
    es_response = es.search(index=index_name, body={
                            "query": {"match": {"content": query}}})

    # Extract relevant information from Elasticsearch response
    hits = es_response["hits"]["hits"]
    if not hits:
        raise HTTPException(status_code=404, detail="No results found")

    # Extract text content from search results
    documents = [hit["_source"]["content"] for hit in hits]

    # Encode query and documents using Universal Sentence Encoder
    query_embedding = embed([query])
    document_embeddings = embed(documents)
    # Calculate cosine similarity
    similarities = tf.keras.losses.cosine_similarity(
        query_embedding, document_embeddings)

    # Get the index of the most similar document
    most_similar_index = tf.argmax(similarities).numpy()

    result = documents[most_similar_index]
    print(result)

    return {"message": "Search results", "query": query, "result": result}
