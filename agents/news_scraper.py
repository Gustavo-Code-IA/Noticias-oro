import os
import feedparser
import sqlite3
from typing import List, Dict, Optional
from hashlib import sha256


def _hash(text: str) -> str:
    return sha256(text.encode('utf-8')).hexdigest()


def fetch_feeds(urls: List[str]) -> List[Dict]:
    """Descarga entradas desde listas de feeds RSS/Atom."""
    results: List[Dict] = []
    for u in urls:
        d = feedparser.parse(u)
        for e in d.entries:
            guid = e.get('id') or e.get('guid') or e.get('link') or e.get('title')
            title = e.get('title', '')
            summary = e.get('summary', '')
            link = e.get('link', '')
            published = e.get('published', '')
            results.append({
                'guid': guid,
                'guid_hash': _hash(str(guid)),
                'title': title,
                'link': link,
                'summary': summary,
                'published': published,
            })
    return results


class ArticleStore:
    def __init__(self, path: str = 'data/articles.db'):
        self.path = path
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        self._init_db()

    def _init_db(self):
        con = sqlite3.connect(self.path)
        cur = con.cursor()
        cur.execute(
            '''
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY,
                guid_hash TEXT UNIQUE,
                guid TEXT,
                title TEXT,
                link TEXT,
                summary TEXT,
                published TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            '''
        )
        con.commit()
        con.close()

    def exists(self, guid_hash: str) -> bool:
        con = sqlite3.connect(self.path)
        cur = con.cursor()
        cur.execute('SELECT 1 FROM articles WHERE guid_hash = ? LIMIT 1', (guid_hash,))
        res = cur.fetchone()
        con.close()
        return res is not None

    def save(self, article: Dict) -> bool:
        if self.exists(article['guid_hash']):
            return False
        con = sqlite3.connect(self.path)
        cur = con.cursor()
        cur.execute(
            'INSERT INTO articles (guid_hash, guid, title, link, summary, published) VALUES (?,?,?,?,?,?)',
            (article['guid_hash'], article.get('guid'), article.get('title'), article.get('link'), article.get('summary'), article.get('published'))
        )
        con.commit()
        con.close()
        return True


def process_and_store(urls: List[str], db_path: Optional[str] = None) -> List[Dict]:
    """Descarga feeds, guarda nuevos artículos y devuelve la lista de añadidos."""
    if db_path:
        store = ArticleStore(db_path)
    else:
        store = ArticleStore()

    items = fetch_feeds(urls)
    added = []
    for it in items:
        if store.save(it):
            added.append(it)
    return added


if __name__ == '__main__':
    urls = os.getenv('NEWS_RSS_URLS', '')
    urls_list = [u.strip() for u in urls.split(',') if u.strip()]
    added = process_and_store(urls_list)
    print(f'New articles saved: {len(added)}')
