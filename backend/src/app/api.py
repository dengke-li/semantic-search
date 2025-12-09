from fastapi import FastAPI
from pydantic import BaseModel

from app.embedding_client import embedding_client
from app.vector_client import vector_search

app = FastAPI(title="Semantic search", version="1.0")

class SearchInput(BaseModel):
    query: str
    limit: int = 5

class SearchResultItem(BaseModel):
    results: list[dict]

@app.post("/search", response_model=SearchResultItem)
async def semantic_search(payload: SearchInput):
    query_vec = await embedding_client.embed(payload.query)
    print(query_vec)

    hits = await vector_search(query_vec, payload.limit)

    results = []
    for h in hits:
        print(h)
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