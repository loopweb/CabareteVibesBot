# CabareteVibesBot

Automatische Veröffentlichung von YouTube-RSS-Videos auf Telegram.

- Jeden Tag um 10:00 UTC prüft GitHub Actions neue Videos.
- Neue Videos erscheinen mit Thumbnail, Titel, gekürzter Beschreibung und Link.
- Die Datei `posted_videos.json` verhindert Duplikate im normalen Betrieb.
- Für einen **einmaligen Test**: Actions → YouTube RSS to Telegram → Run workflow → Häkchen bei `replay_recent` setzen → Run workflow. Dadurch werden die letzten 10 RSS-Videos erneut gepostet, auch wenn sie bereits veröffentlicht wurden.
- Bei normalen manuellen und zeitgesteuerten Starts `replay_recent` **nicht** aktivieren.
- Die Telegram-Bot-Berechtigung „Nachrichten veröffentlichen“ muss aktiviert sein.
- Das GitHub-Secret `TELEGRAM_BOT_TOKEN` bleibt unverändert.
- Telegram erlaubt maximal 1024 Zeichen als Bildunterschrift; Beschreibungen werden daher gekürzt.
- Bereits bestehende Telegram-Beiträge werden nicht automatisch gelöscht.

V3: Beschreibung pro Telegram-Beitrag maximal 300 Zeichen (ohne reine Hashtag-Zeilen). Zum erneuten Test unter Actions `replay_recent` aktivieren.
