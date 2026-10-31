import html
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

FEED = 'https://www.youtube.com/feeds/videos.xml?channel_id=UCCujh8Bdc8hhaMI9CjhF-6w'
STATE = Path('posted_videos.json')
TOKEN = os.environ['TELEGRAM_BOT_TOKEN'].strip()
CHAT = os.environ.get('TELEGRAM_CHAT_ID', '@CabareteVibes').strip()
REPLAY = os.environ.get('REPLAY_RECENT', 'false').lower() == 'true'
NS = {'atom': 'http://www.w3.org/2005/Atom', 'yt': 'http://www.youtube.com/xml/schemas/2015', 'media': 'http://search.yahoo.com/mrss/'}


def get_feed():
    req = urllib.request.Request(FEED, headers={'User-Agent': 'CabareteVibesBot/2.0'})
    with urllib.request.urlopen(req, timeout=30) as response:
        root = ET.fromstring(response.read())
    videos = []
    for entry in root.findall('atom:entry', NS):
        vid = entry.findtext('yt:videoId', namespaces=NS)
        if not vid:
            continue
        title = entry.findtext('atom:title', default='Nuevo video', namespaces=NS)
        published = entry.findtext('atom:published', default='', namespaces=NS)
        description = entry.findtext('media:group/media:description', default='', namespaces=NS)
        description = re.sub(r'\r\n?', '\n', html.unescape(description or '')).strip()
        thumbnail = entry.find('media:group/media:thumbnail', NS)
        thumb_url = thumbnail.get('url', '') if thumbnail is not None else ''
        if not thumb_url:
            thumb_url = f'https://i.ytimg.com/vi/{vid}/hqdefault.jpg'
        videos.append((published, vid, title, description, thumb_url))
    return sorted(videos)


def telegram(method, params):
    data = urllib.parse.urlencode(params).encode('utf-8')
    req = urllib.request.Request(f'https://api.telegram.org/bot{TOKEN}/{method}', data=data)
    try:
        with urllib.request.urlopen(req, timeout=40) as response:
            result = json.load(response)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode('utf-8', errors='replace')
        raise RuntimeError(f'Telegram {method} failed (HTTP {exc.code}): {detail}') from exc
    if not result.get('ok'):
        raise RuntimeError(f'Telegram {method} failed: {result.get("description", "unknown error")}')


def send(vid, title, description, thumbnail):
    link = f'https://www.youtube.com/watch?v={vid}'
    header = f'🎶 {title.strip()}'
    footer = f'\n\n▶️ {link}'
    # Keep Telegram posts short and remove promotional hashtag lines.
    cleaned = []
    for line in description.splitlines():
        line = line.strip()
        if not line:
            if cleaned and cleaned[-1] != '':
                cleaned.append('')
            continue
        if line.startswith('#') or re.fullmatch(r'(?:#[\w-]+\s*)+', line):
            continue
        cleaned.append(line)
    short_description = ' '.join(cleaned).strip()
    # Avoid repeating the video's title at the beginning of its description.
    if short_description.casefold().startswith(title.strip().casefold()):
        short_description = short_description[len(title.strip()):].lstrip(' -–—:|').strip()
    limit = min(250, max(0, 1024 - len(header) - len(footer) - 2))
    excerpt = short_description[:limit].rstrip()
    if len(short_description) > limit and excerpt:
        excerpt = excerpt.rstrip(' .,;:') + '…'
    caption = header + ('\n\n' + excerpt if excerpt else '') + footer
    try:
        telegram('sendPhoto', {'chat_id': CHAT, 'photo': thumbnail, 'caption': caption})
    except RuntimeError as exc:
        # If a thumbnail is unavailable, do not lose the post.
        print(f'Photo failed for {vid}; falling back to text: {exc}')
        text = caption[:4096]
        telegram('sendMessage', {'chat_id': CHAT, 'text': text, 'link_preview_options': json.dumps({'is_disabled': True})})


def duration_seconds(video_id):
    """Read the actual video duration; skip on lookup failure rather than posting a Short."""
    import yt_dlp
    url = f'https://www.youtube.com/watch?v={video_id}'
    opts = {'quiet': True, 'no_warnings': True, 'skip_download': True,
            'extract_flat': False, 'noplaylist': True,
            'socket_timeout': 20, 'retries': 2}
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
        duration = info.get('duration') if info else None
        return float(duration) if duration is not None else None
    except Exception as exc:
        print(f'Could not determine duration for {video_id}: {exc}')
        return None


def main():
    posted = set(json.loads(STATE.read_text(encoding='utf-8'))) if STATE.exists() else set()
    videos = get_feed()
    if not videos:
        raise RuntimeError('No videos returned by RSS feed')
    selected = videos[-15:] if REPLAY or not STATE.exists() else videos
    count = 0
    for _, vid, title, description, thumbnail in selected:
        if not REPLAY and vid in posted:
            continue
        duration = duration_seconds(vid)
        if duration is None:
            print(f'Skipped {vid}: duration unavailable; will retry on next regular run')
            continue
        if duration <= 120:
            print(f'Skipped {vid}: only {duration:.0f} seconds (must be over 120)')
            posted.add(vid)
            STATE.write_text(json.dumps(sorted(posted), ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
            continue
        send(vid, title, description, thumbnail)
        posted.add(vid)
        STATE.write_text(json.dumps(sorted(posted), ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        count += 1
        print(f'Published {vid}: {title} ({len(description)} description chars)')
        time.sleep(30)
    print(f'Done; published: {count}; replay mode: {REPLAY}')


if __name__ == '__main__':
    main()
