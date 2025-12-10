import os

from dateutil import parser as dateparser


class Sink:
    """Abstract sink interface for articles."""

    def get_feed_last_published_time(self, id):
        raise NotImplementedError

    def upsert_article(self, article: dict) -> bool:
        raise NotImplementedError


class DBSink(Sink):
    """Database sink. Lazy-imports psycopg so tests can avoid DB dependency."""

    def __init__(self, conn=None):
        self.dsn = os.getenv("DATABASE_URL")
        if conn is not None:
            self.conn = conn
        else:
            import psycopg  # lazy import

            self.conn = psycopg.connect(self.dsn)

    def get_feed_last_published_time(self, feed_id):
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT MAX(published) FROM articles where feed_id=%s;", (feed_id,)
            )
            row = cur.fetchone()
            if row and row[0]:
                return row[0]
            else:
                return dateparser.parse("1970-01-01T00:00:00")

    def upsert_article(self, article: dict) -> bool:
        sql = (
            "INSERT INTO articles (id, title, url, author, published, summary, content, feed_id) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s) "
            "ON CONFLICT (id) DO UPDATE SET "
            "title = EXCLUDED.title, url = EXCLUDED.url, author = EXCLUDED.author, "
            "published = EXCLUDED.published, summary = EXCLUDED.summary, "
            "content = EXCLUDED.content, "
            "feed_id = EXCLUDED.feed_id;"
        )
        params = (
            article["id"],
            article.get("title"),
            article.get("url"),
            article.get("author"),
            article.get("published"),
            article.get("summary"),
            article.get("content"),
            article.get("feed_id"),
        )
        try:
            with self.conn.cursor() as cur:
                cur.execute(sql, params)
            self.conn.commit()
            return True
        except Exception as e:
            try:
                self.conn.rollback()
            except Exception:
                pass
            print("DB upsert error", e)
            return False


class InMemorySink(Sink):
    """In-memory sink used for unit tests."""

    def __init__(self):
        self.articles = {}  # id -> article dict

    def get_feed_last_published_time(self, feed_id):
        if not self.articles:
            return dateparser.parse("1970-01-01T00:00:00")
        max_published = max(
            (
                a["published"]
                for a in self.articles.values()
                if a.get("feed_id") == feed_id and a.get("published")
            ),
            default=dateparser.parse("1970-01-01T00:00:00"),
        )
        return max_published

    def upsert_article(self, article: dict) -> bool:
        self.articles[article["id"]] = article
        return True
