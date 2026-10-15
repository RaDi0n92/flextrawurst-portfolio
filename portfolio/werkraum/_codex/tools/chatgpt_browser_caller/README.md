# Eigenständiger ChatGPT-Browser-Caller

Dieser kleine Codex-Baustein nutzt ausschließlich die bereits laufende,
eingeloggte Chromium-Instanz über `http://127.0.0.1:9222`. Er ist absichtlich
getrennt von der Augen-&-Hände-Bridge und vom Browser-Recorder.

## Aktueller Umfang

```text
discover  → ChatGPT-Ziele read-only auflisten
inspect   → sichtbaren Live-DOM read-only prüfen
spawn     → neuen sichtbaren Tab öffnen, ersten Turn senden und als Slot pinnen
bind      → genau ein ausgewähltes Ziel explizit als Slot speichern
review    → Build-Checkpoint mit ausgewählten Dateien an einen Slot senden
collect   → späte Antwort desselben Slots abholen, ohne erneut zu senden
slots     → gespeicherte Slots anzeigen
send      → genau einem explizit gebundenen Slot eine Nachricht senden
            und eine neue Assistentenantwort aus dem sichtbaren DOM lesen
```

Es gibt kein automatisches Binden, keinen impliziten Fan-out, keine Cookie-
oder API-Nutzung und keinen versteckten Netzwerk-Call in ChatGPT. Der Caller
fasst keine anderen offenen Webseiten an.

## Verwendung

```bash
python3 /root/werkraum/_codex/tools/chatgpt_browser_caller/caller.py discover
python3 /root/werkraum/_codex/tools/chatgpt_browser_caller/caller.py bind \
  chatgpt-1 '<exakte target_id, URL oder Titel aus discover>'
python3 /root/werkraum/_codex/tools/chatgpt_browser_caller/caller.py slots
python3 /root/werkraum/_codex/tools/chatgpt_browser_caller/caller.py spawn \
  chatgpt-1 'Du bist mein unabhängiger ChatGPT-Arbeitskanal. Bestätige nur den Empfang.'
python3 /root/werkraum/_codex/tools/chatgpt_browser_caller/caller.py send \
  chatgpt-1 'Kurze Testfrage'
python3 /root/werkraum/_codex/tools/chatgpt_browser_caller/caller.py review \
  chatgpt-1 'Prüfe diesen Checkpoint auf Risiken.' \
  --context-file /root/werkraum/_codex/tools/chatgpt_browser_caller/caller.py
python3 /root/werkraum/_codex/tools/chatgpt_browser_caller/caller.py collect \
  chatgpt-1 --timeout 60
```

`spawn` öffnet den neuen Tab und den ersten Chat selbst. Danach bleibt der
Tab als sichtbarer Slot geöffnet. Bestehende Arbeitschats werden weder geraten
noch automatisch als Slot verwendet. `send` arbeitet später ausschließlich
über die gespeicherte Chromium-Target-ID plus Konversations-ID. Nach einem
Chromium-Neustart oder einem ersetzten Tab wird ein Slot bewusst als stale
behandelt und nicht automatisch neu geraten oder wiedergebunden. Ein neuer
Send wird außerdem abgelehnt, solange im gebundenen Tab noch eine vorherige
Antwort generiert wird.

## Proof-Marker

`send` berichtet nur beobachtete Zustände: `attached`, `target_selected`,
`composer_found`, `message_submitted` und
`assistant_response_observed`. Eine Antwort gilt erst als beobachtet, wenn ein
neuer sichtbarer Assistant-DOM-Block gelesen wurde.
