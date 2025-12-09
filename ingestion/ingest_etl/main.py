import os
import time

from ingest_etl.crawler import Crawler, logger
from ingest_etl.sink import DBSink, InMemorySink


DATABASE_URL = os.getenv("DATABASE_URL")
PUBLIC_FEEDS = os.getenv("PUBLIC_FEEDS").split(", ")
VSD_FEEDS = os.getenv("VSD_FEEDS").split(", ")

POLL_INTERVAL = int(os.getenv("POLL_INTERVAL_SEC", "30000"))


def main_loop():
    db_sink = DBSink()  # InMemorySink() #
    site_feeds = {"vsd": VSD_FEEDS, "public": PUBLIC_FEEDS}
    crawlers = []
    for site in site_feeds:
        feeds = site_feeds[site]
        for category_url in feeds:
            category, url = tuple(category_url.split(" : "))
            path = f"data/{site}_{category}.xml"
            crawlers.append(
                Crawler(url=url, path=path, sink=db_sink),
            )
    while True:
        for c in crawlers:
            try:
                c.poll_once()
            except Exception as e:
                logger.error("poll error for", c.url, e)
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main_loop()
