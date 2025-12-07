import os
import time

#import psycopg

from ingest_etl.crawler import Crawler
from ingest_etl.sink import DBSink, InMemorySink
from ingest_etl.config import public_feeds, vsd_feeds


DATABASE_URL = os.getenv("DATABASE_URL")
PUBLIC_FEEDS = os.getenv("public_FEEDS", public_feeds).split(",")
VSD_FEEDS = os.getenv("VSD_FEEDS", vsd_feeds).split(",")

POLL_INTERVAL = int(os.getenv("POLL_INTERVAL_SEC", "300"))

def run_once(crawlers):
    for c in crawlers:
        try:
            c.poll_once()
        except Exception as e:
            print("poll error for", c.url, e)


def main_loop():
    db_sink = InMemorySink()
    site_feeds = {'vsd': VSD_FEEDS, 'public': PUBLIC_FEEDS}
    crawlers = []
    for site in site_feeds:
        feeds = site_feeds[site]
        for category_url in feeds:
            print(category_url.split(' : '))
            category, url = tuple(category_url.split(' : '))
            path = f"data/{site}_{category}.xml"
            crawlers.append(
                Crawler(url=url, path=path, sink=db_sink),
            )
    while True:
        run_once(crawlers)
        time.sleep(POLL_INTERVAL)

if __name__ == '__main__':
    main_loop()