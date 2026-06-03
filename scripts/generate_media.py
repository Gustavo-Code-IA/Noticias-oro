import os
import sqlite3
from hashlib import sha256
from agents.media_generator import generate_media_for_text
from agents.tts_agent import synthesize_text
from services.unsplash import search_images


def _latest_article(db_path='data/articles.db'):
    if not os.path.exists(db_path):
        return None
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute('SELECT id, title, summary FROM articles ORDER BY created_at DESC LIMIT 1')
    row = cur.fetchone()
    con.close()
    if not row:
        return None
    return {'id': row[0], 'title': row[1], 'summary': row[2]}


def _slug(text: str) -> str:
    return sha256(text.encode('utf-8')).hexdigest()[:12]


def main():
    art = _latest_article()
    if not art:
        print('No article found in DB (data/articles.db)')
        return
    title = art['title'] or 'Noticias Oro'
    text = art['summary'] or ''
    print('Generating media for:', title)
    images = []
    # try Unsplash
    try:
        images = search_images(title, count=5)
    except Exception as e:
        print('Image search failed:', e)

    # if no images, use placeholder (create simple color image)
    if not images:
        from PIL import Image, ImageDraw, ImageFont
        os.makedirs('media/images', exist_ok=True)
        p = f"media/images/placeholder_{_slug(title)}.jpg"
        img = Image.new('RGB', (1280, 720), color=(30, 30, 30))
        d = ImageDraw.Draw(img)
        d.text((50, 350), title[:80], fill=(255, 255, 255))
        img.save(p, 'JPEG')
        images = [p]

    out_dir = 'media/videos'
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"{_slug(title)}.mp4")
    video = generate_media_for_text(title, text, images, out_path, synthesize_text)
    print('Video generated:', video)


if __name__ == '__main__':
    main()
