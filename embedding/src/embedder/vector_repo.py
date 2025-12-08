import os

from qdrant_client.models import PointStruct
from qdrant_client import QdrantClient


class QdrantArticleRepository:
    def __init__(self):
        self.client = QdrantClient(
            url=os.getenv("QDRANT_URL", "http://qdrant:6333"),
        )
        self.collection = os.getenv("QDRANT_COLLECTION", "articles")
        if not self.client.collection_exists(self.collection):
            self.client.create_collection(
                collection_name=self.collection,
                vectors_config={
                    "size": 768,
                    "distance": "Cosine",
                },
            )

    def upsert_embedding(self, article_id, vector, payload):
        point = PointStruct(
            id=article_id,
            vector=vector,
            payload=payload,
        )
        self.client.upsert(
            collection_name=self.collection,
            points=[point],
            wait=True,
        )
