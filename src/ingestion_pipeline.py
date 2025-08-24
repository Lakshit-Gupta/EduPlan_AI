import json
from src.embedding.nv_embed import NVEmbed
from src.database.qdrant_connector import QdrantConnector
from src.config import QDRANT_COLLECTION_NAME, QDRANT_VECTOR_SIZE, QDRANT_HOST, QDRANT_PORT

def ingest_documents(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    texts = [item["text"] if isinstance(item, dict) and "text" in item else str(item) for item in data]
    embedder = NVEmbed()
    embeddings = embedder.embed(texts)
    points = [
        {
            "id": idx,
            "vector": emb.tolist(),
            "payload": {"text": text}
        }
        for idx, (emb, text) in enumerate(zip(embeddings, texts))
    ]
    connector = QdrantConnector(QDRANT_HOST, QDRANT_PORT, QDRANT_COLLECTION_NAME, QDRANT_VECTOR_SIZE)
    connector.upsert(points)
