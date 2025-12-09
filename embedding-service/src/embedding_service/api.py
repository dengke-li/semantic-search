import logging

from fastapi import FastAPI
from pydantic import BaseModel

from embedding_service.model import embedding_model


logger = logging.getLogger("embedding-service")
app = FastAPI(title="Embedding service", version="1.0")


class EmbeddingRequest(BaseModel):
    text: str


@app.post("/embed")
async def embed_text(req: EmbeddingRequest):
    try:
        vec = await embedding_model.embed(req.text)
        return {"embedding": vec}
    except Exception as e:
        logger.error(f"Embedding error: {e}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8081)
