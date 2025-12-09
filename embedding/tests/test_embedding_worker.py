# python
import pytest
from unittest.mock import MagicMock
import numpy as np

from embedder.worker import Article, EmbeddingWorker


def make_article(i):
    return Article(
        id=i,
        title=f"title-{i}",
        url=f"http://example/{i}",
        author="author",
        summary="summary",
        content=f"content {i}",
    )


def test_process_batch_calls_upsert_and_mark():
    model = MagicMock()
    # encode returns something convertible to a list of vectors
    model.encode.return_value = np.array([[0.1, 0.2], [0.3, 0.4]])

    qdrant = MagicMock()
    article_repo = MagicMock()
    # repo uses the original misspelled method name in code
    article_repo.mark_embbeded = MagicMock()

    worker = EmbeddingWorker(
        model=model, qdrant_repo=qdrant, article_repo_factory=lambda: article_repo
    )

    batch = [make_article("1"), make_article("2")]

    # Act
    worker.process_batch(batch, article_repo)

    # Assert
    assert qdrant.upsert_embedding.call_count == 2
    # check first call payload and vector
    first_call_args = qdrant.upsert_embedding.call_args_list[0][0]
    assert first_call_args[0] == "1"  # article id
    assert isinstance(first_call_args[1], list)  # vector
    assert isinstance(first_call_args[2], dict)  # payload

    assert article_repo.mark_embbeded.call_count == 2


def test_run_once_no_articles(monkeypatch):
    # Arrange
    model = MagicMock()
    qdrant = MagicMock()

    fake_repo = MagicMock()
    fake_repo.fetch_unembedded.return_value = []
    fake_repo.close = MagicMock()

    worker = EmbeddingWorker(
        model=model,
        qdrant_repo=qdrant,
        article_repo_factory=lambda: fake_repo,
    )

    # spy on process_batch to ensure it's not called
    worker.process_batch = MagicMock()

    # Act
    worker.run_once()

    # Assert
    worker.process_batch.assert_not_called()
    fake_repo.close.assert_called_once()


def test_run_once_processes_articles(monkeypatch):
    model = MagicMock()
    model.encode.return_value = np.array([[0.5, 0.6]])

    qdrant = MagicMock()
    processed_repo = MagicMock()
    article = make_article("10")
    processed_repo.fetch_unembedded.return_value = [article]
    processed_repo.mark_embbeded = MagicMock()
    processed_repo.close = MagicMock()

    worker = EmbeddingWorker(
        model=model,
        qdrant_repo=qdrant,
        article_repo_factory=lambda: processed_repo,
    )

    worker.run_once()

    # Assert
    qdrant.upsert_embedding.assert_called_once()
    processed_repo.mark_embbeded.assert_called_once_with(article.id)
    processed_repo.close.assert_called_once()
