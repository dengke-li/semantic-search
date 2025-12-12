import httpx
from fastapi import HTTPException

from app.config import settings
from app.retry import retry_policy


class EmbeddingClient:
    def __init__(self):
        self.url = settings.EMBEDDING_SERVICE_URL

    @retry_policy
    async def embed(self, text: str):
        async with httpx.AsyncClient(timeout=20) as client:
            try:
                print('embedding post')
                response = await client.post(self.url, json={"text": text})
                response.raise_for_status()
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
                        f"Embedding service error (status {status}): "
                        f"{exc.response.text}"
                    )
                ) from exc
            data = response.json()
            return data["embedding"]

embedding_client = EmbeddingClient()
