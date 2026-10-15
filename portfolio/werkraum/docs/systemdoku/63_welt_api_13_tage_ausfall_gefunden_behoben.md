# welt-api.service: 13 Tage stiller Ausfall gefunden und behoben (2026-09-03)

## Fund

Beim Redteam-Test einer ganz anderen, heute gebauten Funktion (echter VPS-
Dateisystemzugriff im Gesamtkonstrukt-Planer, Stufe 5) fiel `_redteam_test`-Prüfung
auf `/root/werkraum/../../root/.ssh/authorized_keys` auf. Beim Nachverfolgen einer
ganz unabhängigen alten Notiz (`/root/SECRET_FINDINGS_REDACTED.md`, ein Sicherheits-
audit vom 30.05.2026) wurde geprüft, ob dessen zehn Funde inzwischen behoben sind.
Dabei zeigte `welt-api.service` beim Statuscheck: `Active: activating (auto-restart)
(Result: exit-code)`.

## Root Cause

Commit `1bd94d400` (21.08.2026, Titel "backup: vor Nemotron-3-Nano-PRISM-Q8_0-Download
(Chat-Instanz-Test)", Autor "AI-Strom") hat neben zwei absichtlichen, kleinen
Kommentar-Kürzungen (Guardianstyle-Erzählpassagen entfernt, passt zur später
dokumentierten "Fehler-Schweige-Regel" - diese zwei Stellen wurden NICHT
zurückgerollt) **versehentlich 618 Netto-Zeilen echten, ausführbaren Codes am
Dateiende von `welt/api.py` gelöscht** - darunter:

- mehrere komplette Guardianstyle-Hilfsfunktionen (`_gs_marker_koerper_ende`,
  `_gs_marker_saubern`)
- den "systemweite Archäologie"-Watcher-Thread (`_sa_watcher_loop`,
  `_sa_watcher_starten`)
- **den kompletten Server-Start-Block:**
  ```python
  if __name__ == "__main__":
      import uvicorn
      uvicorn.run(app, host="127.0.0.1", port=8030)
  ```

Übrig blieb eine einzelne verwaiste Zeile (`return text[:33333]`, Rest von
`_gs_marker_saubern`, außerhalb jeder Funktion), die die Datei syntaktisch ungültig
machte (`IndentationError`).

Da `welt-api.service` `Restart=always` + `RestartSec=5` gesetzt hat, ist der Dienst
seit diesem Commit **13 Tage lang alle 5 Sekunden neu gestartet und sofort wieder
abgestürzt** - Port 8030 war die ganze Zeit unerreichbar. Log-Beleg:
`/root/werkraum/logs/welt_api.log` wuchs dabei auf **4,3 Millionen Zeilen** (nur
Wiederholungen desselben `IndentationError`). Niemandem ist der Ausfall aufgefallen,
vermutlich weil kein aktiver Traffic/Monitoring auf den betroffenen `/api/*`-Routen
lag oder Fehler dort bislang niemand direkt zugeordnet hat.

## Fix

Datei aus dem Elterncommit (`1bd94d400~1`) rekonstruiert: die zwei absichtlichen
Kommentar-Kürzungen blieben erhalten (nicht zurückgerollt), nur der dritte,
zusammenhängende 618-Zeilen-Verlust wurde aus der Elternversion wiederhergestellt.
Erster Fix-Versuch (nur die eine verwaiste Zeile entfernen, um `ast.parse` zu
bestehen) war unzureichend - die Datei wurde dadurch syntaktisch gültig, aber der
Dienst beendete sich trotzdem sofort sauber (exit 0), weil der komplette
Server-Start-Aufruf weiterhin fehlte. Erst die vollständige Wiederherstellung der
618 Zeilen brachte den Dienst wirklich zum Laufen.

**Live verifiziert:** `systemctl status` zeigt `Active: active (running)`, stabil
über mehrere Prüfungen (30+ Sekunden ohne erneuten Absturz, PID unverändert,
Speicherverbrauch normal wachsend). `curl` gegen Port 8030 liefert `404` (korrektes
Verhalten für den nicht geroutet Wurzelpfad, beweist dass der Server echt antwortet,
nicht mehr `connection refused`).

## Nebenfund beim Debuggen

Beim ersten Debug-Versuch (`python3 api.py` direkt über SSH statt via `systemctl`)
täuschte ein `psycopg2.OperationalError: password authentication failed` einen
zweiten, unabhängigen Bug vor - tatsächlich lud die manuelle Shell die
`EnvironmentFile`-Variablen von systemd nicht, wodurch der Code auf einen im Code
hart codierten Dummy-Fallback (`postgresql://dak:[GESCHWAERZT]@...`) zurückfiel. Kein
echter zweiter Bug, nur eine irreführende Nebenwirkung der Debug-Methode - beim
erneuten Testen mit korrekt geladenen Environment-Variablen (`source
.agent/flarum.env; source .agent/flextrawurst-db.env`) verschwand der Fehler.

## Zusammenhang mit dem ungelösten FUND-006

Das über drei Monate alte Sicherheitsaudit (`SECRET_FINDINGS_REDACTED.md`) hatte
schon damals bemängelt, dass `welt/api.py` (und ~15 weitere `welt/*.py`-Dateien) ein
Datenbank-Passwort hart codiert im Code tragen (`DB_URI = _os.environ.get(...,
"postgresql://dak:[GESCHWAERZT]@localhost:5432/flextrawurst")`, Zeile 47). Genau dieser
alte, nie behobene Fallback-Wert war es, der beim ersten Debug-Versuch die
irreführende Fehlermeldung erzeugte - ein konkretes, praktisches Beispiel dafür,
warum der alte Fund nach wie vor sinnvoll wäre zu beheben.
