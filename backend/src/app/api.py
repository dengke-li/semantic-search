import logging

from fastapi import FastAPI
from pydantic import BaseModel

from app.embedding_client import embedding_client
from app.vector_client import vector_search


logger = logging.getLogger("backend-service")
app = FastAPI(title="Semantic search", version="1.0")

class SearchInput(BaseModel):
    query: str
    limit: int = 5

class SearchResultItem(BaseModel):
    results: list[dict]

@app.post("/search", response_model=SearchResultItem)
async def semantic_search(payload: SearchInput):
    logger.info(f"Received search request: {payload.query} with limit {payload.limit}")
    try:
        query_vec = await embedding_client.embed(payload.query)
    except Exception as e:
        logger.error(f"Embedding error: {e}")
    try:
        hits = await vector_search(query_vec, payload.limit)
    except Exception as e:
        logger.error(f"Vector search error: {e}")

    results = []
    for h in hits:
        points = h[1]
        for point in points:
            results.append({
                "score": point.score,
                "payload": point.payload
            })

    return SearchResultItem(results=results)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)