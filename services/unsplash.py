import os
import requests
from typing import List


def search_images(query: str, count: int = 5) -> List[str]:
    """Search images on Unsplash and return local URLs (downloaded paths).

    Requires `UNSPLASH_ACCESS_KEY` in env. If not present, returns empty list.
    """
    key = os.getenv('UNSPLASH_ACCESS_KEY')
    if not key:
        return []
    url = 'https://api.unsplash.com/search/photos'
    params = {'query': query, 'per_page': count}
    headers = {'Authorization': f'Client-ID {key}'}
    r = requests.get(url, params=params, headers=headers, timeout=10)
    r.raise_for_status()
    data = r.json()
    results = []
    os.makedirs('media/images', exist_ok=True)
    for i, item in enumerate(data.get('results', [])[:count]):
        img_url = item['urls']['regular']
        ext = 'jpg'
        path = f"media/images/{query.replace(' ','_')}_{i}.{ext}"
        try:
            resp = requests.get(img_url, timeout=15)
            with open(path, 'wb') as f:
                f.write(resp.content)
            results.append(path)
        except Exception:
            continue
    return results
