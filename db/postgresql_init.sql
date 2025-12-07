CREATE TABLE IF NOT EXISTS articles (
    id TEXT PRIMARY KEY,
    title TEXT,
    url TEXT,
    author TEXT,
    published TIMESTAMP,
    tags TEXT[],
    summary TEXT,
    content TEXT,
    feed_id TEXT
);