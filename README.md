# CabareteVibesBot

Automatische Veröffentlichung neuer YouTube-Videos von **Don Miguel de Cabarete** im öffentlichen Telegram-Kanal **[@CabareteVibes](https://t.me/CabareteVibes)**.

## Funktionsumfang (V7)

- Liest den offiziellen YouTube-RSS-Feed des Kanals `UCCujh8Bdc8hhaMI9CjhF-6w`.
- Veröffentlicht **Videos einschließlich Shorts**; es gibt **keine Laufzeitprüfung** und keine Abhängigkeit von `yt-dlp` oder der YouTube Data API.
- Sendet das YouTube-Thumbnail als Telegram-Foto, dazu Videotitel, eine auf maximal **250 Zeichen** gekürzte RSS-Beschreibung und den YouTube-Link.
- Entfernt reine Hashtag-Zeilen aus der Beschreibung. Ist das Thumbnail nicht abrufbar, erfolgt ein Textbeitrag als Fallback.
- Merkt sich veröffentlichte Video-IDs in `posted_videos.json`, damit reguläre Durchläufe keine Duplikate erzeugen.
- Läuft über GitHub Actions **einmal täglich um 10:00 UTC**; außerdem manuell startbar.
- Optionaler manueller Probelauf mit `replay_recent`, der **bis zu 15 letzte RSS-Videos erneut veröffentlicht** (auch wenn sie bereits gepostet wurden).

## Einrichtung

1. Einen öffentlichen Telegram-Kanal erstellen und einen Bot über [@BotFather](https://t.me/BotFather) anlegen.
2. Den Bot als Administrator von `@CabareteVibes` hinzufügen, mit der Berechtigung, Nachrichten zu veröffentlichen.
3. Im GitHub-Repository unter **Settings → Secrets and variables → Actions** das Repository-Secret `TELEGRAM_BOT_TOKEN` mit dem Bot-Token anlegen. Den Token niemals im Code veröffentlichen.
4. Die Dateien `bot.py` und `.github/workflows/rss-to-telegram.yml` im Repository hinterlegen.
5. Unter **Actions → YouTube RSS to Telegram → Run workflow** manuell starten.

## Normalbetrieb und Test

- **Normaler Start:** `replay_recent` deaktiviert lassen. Bereits in `posted_videos.json` verzeichnete Videos werden übersprungen.
- **Wiederholungstest:** `replay_recent` aktivieren. Die letzten bis zu 15 RSS-Einträge werden absichtlich erneut gepostet; vorhandene Telegram-Beiträge werden nicht gelöscht.
- `posted_videos.json` nicht manuell löschen oder überschreiben. Der Workflow aktualisiert und committet die Datei nach dem Lauf, wenn sich etwas geändert hat. Dafür benötigt der Workflow `contents: write`.

## Hinweise

- Der RSS-Feed enthält nur eine begrenzte Anzahl aktueller Einträge; ein Replay ist kein vollständiges Kanalarchiv.
- Die Beschreibung kann nur so vollständig sein wie das von YouTube gelieferte RSS-Feld `media:description`.
- Geplante GitHub-Actions-Ausführungen können verzögert stattfinden.
- Änderungen am Skript wirken sich nur auf zukünftige Beiträge aus; alte Telegram-Posts werden nicht automatisch angepasst.
