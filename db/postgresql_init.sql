CREATE TABLE IF NOT EXISTS articles (
    id TEXT PRIMARY KEY,
    title TEXT,
    url TEXT,
    author TEXT,
    published TIMESTAMP,
    summary TEXT,
    content TEXT,
    feed_id TEXT,
    embedded_at TIMESTAMP
);