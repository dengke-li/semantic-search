from qdrant_client import AsyncQdrantClient

from app.config import settings


qdrant = AsyncQdrantClient(url=settings.QDRANT_URL)

async def vector_search(query_vector, limit=5):
    return await qdrant.query_points(
        collection_name=settings.QDRANT_COLLECTION,
        query=query_vector,
        limit=limit
    )
