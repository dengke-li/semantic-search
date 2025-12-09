from fastapi import FastAPI
from pydantic import BaseModel

from embedding_service.model import embedding_model

app = FastAPI(title="Embedding service", version="1.0")

class EmbeddingRequest(BaseModel):
    text: str

@app.post("/embed")
async def embed_text(req: EmbeddingRequest):
    vec = await embedding_model.embed(req.text)
    return {"embedding": vec}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)