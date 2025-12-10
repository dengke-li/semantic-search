import time
import os
from typing import List
import logging, sys

from sentence_transformers import SentenceTransformer

from embedder.article_repo import PostgresArticleRepository, Article
from embedder.vector_repo import QdrantArticleRepository


def get_logger():
    logger = logging.getLogger("embeeding-worker")
    handler = logging.StreamHandler(sys.stdout)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger
logger = get_logger()
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL_SEC", "10"))
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "50"))


class EmbeddingWorker:
    def __init__(self, model=None, qdrant_repo=None, article_repo_factory=None):
        # Load model ONCE at startup
        # allow injecting model and repos for testing; lazy default to real ones
        self.model = model
        self.qdrant_repo = qdrant_repo
        self.article_repo_factory = article_repo_factory

    def process_batch(self, batch: List[Article], article_repo):
        if not batch:
            return

        texts = [a.content for a in batch]
        vectors = self.model.encode(texts, convert_to_numpy=True).tolist()

        for article, vec in zip(batch, vectors):
            payload = {
                "title": article.title,
                "url": article.url,
                "author": article.author,
                "summary": article.summary,
                "content": article.content,
            }

            self.qdrant_repo.upsert_embedding(article.id, vec, payload)
            article_repo.mark_embbeded(article.id)

    def run_once(self):
        article_repo = self.article_repo_factory()
        try:
            articles = article_repo.fetch_unembedded(limit=BATCH_SIZE)
            if not articles:
                logger.info("No pending articles...")
                return
            self.process_batch(articles, article_repo)
        finally:
            article_repo.close()

        logger.info(f"Processed {len(articles)} articles.")

    def run_forever(self):
        while True:
            self.run_once()
            time.sleep(POLL_INTERVAL)


def run():
    worker = EmbeddingWorker(
        model=SentenceTransformer(
            "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
        ),
        qdrant_repo=QdrantArticleRepository(),
        article_repo_factory=(lambda: PostgresArticleRepository()),
    )
    worker.run_forever()


if __name__ == "__main__":
    run()
