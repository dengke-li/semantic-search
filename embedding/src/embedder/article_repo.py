import psycopg
import os

from pydantic import BaseModel


class Article(BaseModel):
    id: str
    title: str
    url: str
    author: str
    summary: str
    content: str


class PostgresArticleRepository:
    def __init__(self):
        dsn = os.getenv("DATABASE_URL")
        self.conn = psycopg.connect(dsn)

    def fetch_unembedded(self, limit=50):
        sql = """
            SELECT id, title, url, author, summary, content
            FROM articles
            WHERE embedded_at IS NULL
            ORDER BY published DESC
            LIMIT %s
        """
        with self.conn.cursor() as cur:
            cur.execute(sql, (limit,))
            rows = cur.fetchall()
        return [
            Article(
                **dict(zip(["id", "title", "url", "author", "summary", "content"], r))
            )
            for r in rows
        ]

    def mark_embbeded(self, article_id: str):
        sql = """
            UPDATE articles
            SET embedded_at = now()
            WHERE id = %s
        """
        try:
            with self.conn.cursor() as cur:
                cur.execute(sql, (article_id,))
            self.conn.commit()
            return True
        except Exception as e:
            try:
                self.conn.rollback()
            except Exception:
                pass
            print("DB upsert error", e)
            return False

    def close(self):
        self.conn.close()
