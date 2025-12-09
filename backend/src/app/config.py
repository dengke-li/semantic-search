import os

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    QDRANT_URL: str = "http://qdrant:6333"
    QDRANT_COLLECTION: str = "articles"
    EMBEDDING_MODEL: str = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
    EMBEDDING_SERVICE_URL: str = os.getenv("EMBEDDING_SERVICE_URL", "http://127.0.0.1:8080/embed")

settings = Settings()