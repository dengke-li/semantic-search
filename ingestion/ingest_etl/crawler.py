import hashlib
import os
import uuid
import logging

import requests
import feedparser
from dateutil import parser as dateparser

logger = logging.getLogger("ingestion-service")

# Deterministic id from url (or GUID)
def make_article_id(entry):
    guid = entry.get('id') or entry.get('guid') or entry.get('link')
    return uuid.uuid3(uuid.NAMESPACE_URL, guid)

def make_feed_id(path):
    return hashlib.sha256(path.encode('utf-8')).hexdigest()

class Crawler:
    def __init__(self, url, path, sink):
        self.path = path
        self.url = url
        self.sink = sink
        self.feed_id = make_feed_id(path)

    def download_feed(self):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        logger.info("Download article for ", self.url)
        r = requests.get(self.url, headers=headers)
        r.raise_for_status()
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "wb") as f:
            f.write(r.content)

    def _normalize_entry(self, entry):
        published = dateparser.parse(entry.published)
        title = entry.get('title')
        url = entry.get('link')
        author = entry.get('author', '')

        #tags = [tag.get('term', '') for tag in entry.get('tags')]
        summary = entry.get('summary')
        content = entry.get('content')[0].get('value') if entry.get('content') else ''
        id = make_article_id(entry)

        art = {
            'title': title,
            'url': url,
            'author': author,
            'published': published,
            'summary': summary,
            'content': content,
            'id': id,
            'feed_id': self.feed_id,
        }
        return art

    def extract(self, sink_watermark=None):
        logger.info("Extract article from ", self.path)
        d = feedparser.parse(self.path)
        for entry in d.entries:
            try:
                published = dateparser.parse(entry.published)
                if published and sink_watermark and published < sink_watermark:
                    continue
                norm = self._normalize_entry(entry)
                yield norm
            except Exception as ee:
                logger.error('entry error', ee)

    def ingest(self, arts):
        for art in arts:
            ok = self.sink.upsert_article(art)

    # Poll feeds incrementally
    def poll_once(self):
        self.download_feed()
        last_published_time = self.sink.get_feed_last_published_time(self.feed_id)
        logger.info(f'last_published_time: {last_published_time}')
        arts = self.extract(last_published_time)
        self.ingest(arts)