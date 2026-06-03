import os
from agents.news_scraper import process_and_store
from agents.impact_analyzer import classify_impact


def run_once():
    urls = os.getenv('NEWS_RSS_URLS', '')
    urls_list = [u.strip() for u in urls.split(',') if u.strip()]
    added = process_and_store(urls_list, db_path='data/articles.db')
    for it in added:
        impact = classify_impact(it.get('summary', it.get('title', '')))
        if impact in ('medium', 'high'):
            print('Relevant:', it.get('title'), 'impact=', impact)


if __name__ == '__main__':
    run_once()
