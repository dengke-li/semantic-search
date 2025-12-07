from unittest.mock import patch
from dateutil import parser as dateparser

from ingestion.ingest_etl.crawler import Crawler
from ingestion.ingest_etl.sink import InMemorySink

SAMPLE_FEED = """<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
<channel>
  <title>Test Feed</title>
  <item>
    <title>First article</title>
    <link>http://example.com/1</link>
    <pubDate>Wed, 01 Jan 2020 12:00:00 GMT</pubDate>
    <description>Summary here</description>
    <guid>abc-1</guid>
  </item>
</channel>
</rss>
"""


def fake_get(url,headers=None):
    class R:
        def __init__(self, content):
            self.content = content
            self.status_code = 200

        def raise_for_status(self):
            if self.status_code >= 400:
                raise Exception("HTTP error")

    return R(content=SAMPLE_FEED.encode('utf-8'))


@patch('ingestion.ingest_etl.crawler.requests.get', side_effect=fake_get)
def test_poll_once_and_inmemory_sink(mock_get, tmp_path):
    sink = InMemorySink()
    # put path under tmp_path to avoid writing to repo
    path = str(tmp_path / "feed.xml")
    c = Crawler(url="http://example.com/feed", path=path, sink=sink)

    # before polling, sink empty
    assert sink.articles == {}

    c.poll_once()

    # after polling, one article stored
    assert len(sink.articles) == 1
    art = next(iter(sink.articles.values()))
    assert art['title'] == "First article"
    assert art['url'] == "http://example.com/1"
    assert isinstance(art['published'], type(dateparser.parse("2020-01-01T12:00:00Z")))