CabareteVibesBot V6

YouTube-RSS zu Telegram. Nur Videos mit einer tatsächlichen Laufzeit von mehr als 120 Sekunden werden veröffentlicht. Die Laufzeit wird mit yt-dlp abgefragt (ohne YouTube-API-Key). Kann die Laufzeit nicht ermittelt werden, wird das Video aus Sicherheitsgründen übersprungen und beim nächsten normalen Lauf erneut versucht. Beim Replay werden bis zu 15 RSS-Einträge geprüft; es können weniger als 15 Telegram-Posts entstehen.

Zum Update bot.py und .github/workflows/rss-to-telegram.yml auf GitHub ersetzen. posted_videos.json beibehalten. Der Workflow installiert yt-dlp selbst. YouTube kann automatisierte Metadatenabfragen gelegentlich blockieren; dann zeigt das Actions-Log die übersprungenen Videos.
