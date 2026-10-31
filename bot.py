import json
import os
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

FEED = 'https://www.youtube.com/feeds/videos.xml?channel_id=UCCujh8Bdc8hhaMI9CjhF-6w'
STATE = Path('posted_videos.json')
TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
CHAT = os.environ.get('TELEGRAM_CHAT_ID', '@CabareteVibes')
NS = {'atom': 'http://www.w3.org/2005/Atom', 'yt': 'http://www.youtube.com/xml/schemas/2015'}

def get_feed():
    with urllib.request.urlopen(urllib.request.Request(FEED, headers={'User-Agent':'CabareteVibesBot/1.0'}), timeout=30) as r:
        root = ET.fromstring(r.read())
    videos = []
    for entry in root.findall('atom:entry', NS):
        vid = entry.findtext('yt:videoId', namespaces=NS)
        title = entry.findtext('atom:title', default='Neues Video', namespaces=NS)
        published = entry.findtext('atom:published', default='', namespaces=NS)
        if vid:
            videos.append((published, vid, title))
    return sorted(videos)

def send(vid, title):
    message = f'🎶 {title}\n\nhttps://www.youtube.com/watch?v={vid}'
    body = urllib.parse.urlencode({'chat_id': CHAT, 'text': message, 'disable_web_page_preview': 'false'}).encode()
    request = urllib.request.Request(f'https://api.telegram.org/bot{TOKEN}/sendMessage', data=body)
    with urllib.request.urlopen(request, timeout=30) as r:
        response = json.load(r)
    if not response.get('ok'):
        raise RuntimeError('Telegram did not confirm publication')

def main():
    posted = set(json.loads(STATE.read_text(encoding='utf-8'))) if STATE.exists() else set()
    videos = get_feed()
    if not videos:
        raise RuntimeError('No videos returned by RSS feed')
    # First run: seed the channel with the 10 newest feed videos, oldest first.
    candidates = videos[-10:] if not STATE.exists() else videos
    changed = False
    for _, vid, title in candidates:
        if vid in posted:
            continue
        send(vid, title)
        posted.add(vid)
        STATE.write_text(json.dumps(sorted(posted), indent=2) + '\n', encoding='utf-8')
        changed = True
        print(f'Published {vid}: {title}')
        time.sleep(30)
    print('Done; published:', changed)

if __name__ == '__main__':
    main()
