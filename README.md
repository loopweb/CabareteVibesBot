# CabareteVibesBot

Automatische Veröffentlichung neuer YouTube-Videos von Don Miguel de Cabarete in Telegram `@CabareteVibes`.

## Einrichtung
1. Öffentliches GitHub-Repository erstellen und diese Dateien mit ihrer Ordnerstruktur hochladen.
2. Unter **Settings → Secrets and variables → Actions → New repository secret** das Secret `TELEGRAM_BOT_TOKEN` mit dem Token von BotFather anlegen. Niemals den Token in eine Datei schreiben.
3. Bot als Administrator von `@CabareteVibes` mit der Berechtigung **Nachrichten veröffentlichen** hinzufügen.
4. Unter **Actions → YouTube RSS to Telegram → Run workflow** den ersten Lauf manuell starten.
5. Beim ersten Lauf werden bis zu 10 Videos aus dem Feed in chronologischer Reihenfolge veröffentlicht (30 Sekunden Abstand). Danach werden nur neue Videos gepostet.

Der Workflow prüft alle 30 Minuten, soweit GitHub Actions ihn planmäßig ausführt. Der Zustand wird in `posted_videos.json` im Repository gespeichert. Die Datei nicht löschen, sonst können die letzten 10 Videos erneut gepostet werden.

**Hinweis:** Der erste Lauf dauert bei 10 Videos rund fünf Minuten. Für öffentliche Repositories kann GitHub zeitgesteuerte Workflows nach längerer Inaktivität deaktivieren. GitHub-Actions-Zeitpläne können sich verzögern.
