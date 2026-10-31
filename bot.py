import html
import json
import os
import re
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

FEED = 'https://www.youtube.com/feeds/videos.xml?channel_id=UCCujh8Bdc8hhaMI9CjhF-6w'
STATE = Path('posted_videos.json')
TOKEN = os.environ['TELEGRAM_BOT_TOKEN'].strip()
CHAT = os.environ.get('TELEGRAM_CHAT_ID', '@CabareteVibes')
NS = {
    'atom': 'http://www.w3.org/2005/Atom',
    'yt': 'http://www.youtube.com/xml/schemas/2015',
    'media': 'http://search.yahoo.com/mrss/',
}


def get_feed():
    request = urllib.request.Request(FEED, headers={'User-Agent': 'CabareteVibesBot/1.1'})
    with urllib.request.urlopen(request, timeout=30) as response:
        root = ET.fromstring(response.read())
    videos = []
    for entry in root.findall('atom:entry', NS):
        vid = entry.findtext('yt:videoId', namespaces=NS)
        title = entry.findtext('atom:title', default='Neues Video', namespaces=NS)
        published = entry.findtext('atom:published', default='', namespaces=NS)
        # YouTube usually supplies a description under media:group/media:description.
        description = entry.findtext('media:group/media:description', default='', namespaces=NS)
        description = html.unescape(description or '')
        description = re.sub(r'\r\n?', '\n', description).strip()
        if vid:
            videos.append((published, vid, title, description))
    return sorted(videos)


def send(vid, title, description):
    link = f'https://www.youtube.com/watch?v={vid}'
    header = f'🎶 {title.strip()}\n\n'
    footer = f'\n\n{link}'
    # Telegram sendMessage accepts at most 4096 characters.
    available = 4096 - len(header) - len(footer)
    if description and available > 0:
        if len(description) > available:
            description = description[:max(0, available - 1)].rstrip() + '…'
        message = header + description + footer
    else:
        message = header.rstrip() + footer
    body = urllib.parse.urlencode({
        'chat_id': CHAT,
        'text': message,
        'disable_web_page_preview': 'false',
    }).encode('utf-8')
    request = urllib.request.Request(f'https://api.telegram.org/bot{TOKEN}/sendMessage', data=body)
    with urllib.request.urlopen(request, timeout=30) as response:
        result = json.load(response)
    if not result.get('ok'):
        raise RuntimeError('Telegram did not confirm publication')


def main():
    posted = set(json.loads(STATE.read_text(encoding='utf-8'))) if STATE.exists() else set()
    videos = get_feed()
    if not videos:
        raise RuntimeError('No videos returned by RSS feed')
    candidates = videos[-10:] if not STATE.exists() else videos
    count = 0
    for _, vid, title, description in candidates:
        if vid in posted:
            continue
        send(vid, title, description)
        posted.add(vid)
        STATE.write_text(json.dumps(sorted(posted), indent=2) + '\n', encoding='utf-8')
        count += 1
        print(f'Published {vid}: {title} (description: {len(description)} chars)')
        time.sleep(30)
    print(f'Done; published: {count}')


if __name__ == '__main__':
    main()
