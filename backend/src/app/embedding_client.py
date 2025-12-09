import httpx

from app.config import settings


class EmbeddingClient:
    def __init__(self):
        self.url = settings.EMBEDDING_SERVICE_URL

    async def embed(self, text: str):
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(self.url, json={"text": text})
            response.raise_for_status()
            data = response.json()
            return data["embedding"]


embedding_client = EmbeddingClient()
