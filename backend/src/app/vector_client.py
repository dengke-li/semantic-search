from qdrant_client import AsyncQdrantClient
import httpx
from fastapi import HTTPException

from app.config import settings
from app.retry import retry_policy


qdrant = AsyncQdrantClient(url=settings.QDRANT_URL)


@retry_policy
async def vector_search(query_vector, limit=5):
    try:
        response = await qdrant.query_points(
            collection_name=settings.QDRANT_COLLECTION, query=query_vector, limit=limit
        )
    except httpx.HTTPStatusError as exc:
        status = exc.response.status_code
        # - 429 Too Many Requests
        # - 503 Service Unavailable
        if status in (429, 503):
            raise
        #    Should NOT be retried.
        raise HTTPException(
            status_code=502,
            detail=(
                f"qdrant database service error (status {status}): "
                f"{exc.response.text}"
            )
        ) from exc
    return response
