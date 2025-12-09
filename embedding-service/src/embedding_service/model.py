from sentence_transformers import SentenceTransformer
import asyncio
from concurrent.futures import ProcessPoolExecutor

# Separate worker function (must be top-level for multiprocessing)
_model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-mpnet-base-v2")

def _embed_worker(text: str):
    """Runs inside a separate process."""
    return _model.encode(text).tolist()

class EmbeddingModel:
    def __init__(self):
        self.executor = ProcessPoolExecutor(max_workers=1)

    async def embed(self, text: str):
        loop = asyncio.get_event_loop()
        # Offload heavy computation to executor so FastAPI event loop stays async
        vector = await loop.run_in_executor(self.executor, _embed_worker, text)
        return vector

embedding_model = EmbeddingModel()