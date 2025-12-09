import time
import os

from sentence_transformers import SentenceTransformer

from embedder.article_repo import PostgresArticleRepository
from embedder.vector_repo import QdrantArticleRepository


POLL_INTERVAL = int(os.getenv("POLL_INTERVAL_SEC", "10"))
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "50"))


class EmbeddingWorker:
    def __init__(self):
        # Load model ONCE at startup
        print("Loading paraphrase-multilingual-mpnet-base-v2 model")
        self.model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-mpnet-base-v2")

        self.qdrant_repo = QdrantArticleRepository()

    def process_batch(self, batch: list, article_repo):
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
        article_repo = PostgresArticleRepository()
        articles = article_repo.fetch_unembedded(limit=BATCH_SIZE)
        if not articles:
            print("No pending articles...")
            return

        self.process_batch(articles, article_repo)
        article_repo.close()

        print(f"Processed {len(articles)} articles.")

    def run_forever(self):
        while True:
            self.run_once()
            time.sleep(POLL_INTERVAL)


def run():
    worker = EmbeddingWorker()
    worker.run_forever()


if __name__ == "__main__":
    run()


