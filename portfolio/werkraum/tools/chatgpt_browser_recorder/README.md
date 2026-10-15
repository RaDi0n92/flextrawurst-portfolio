# ChatGPT Browser Recorder

Der Recorder liest ausschließlich den sichtbaren Browserinhalt und hält ihn
lokal beziehungsweise — nach sichtbarer Freigabe und mit Zugangsschlüssel —
auf dem VPS fest. Die Chromium-Erweiterung beobachtet sichtbare Nachrichten,
Scrollbewegungen, Links, Medien und Zustandswechsel. Sie liest keine Provider-
APIs, umgeht keinen Login und behauptet aus einem erreichten Seitenende keinen
vollständigen Chat.

Die aktuell geladene Referenz-Erweiterung liegt unter
`werkraum/refferenzen/AI-UI-RECORDER-v1.6.5-DIREKT-LADEN/`. Der ältere
Quell-/Paketstand liegt unter `werkraum/tools/chatgpt_browser_recorder/extension/`.
Beide Orte sind bewusst getrennt; ein Laufzeitfix in der Referenz ist erst dann
Quellparität, wenn er auch im Paketstand nachvollzogen wurde.

## Ablage

Jeder Chat erhält genau einen Ordner im Format
`YYYY-MM-DD__CHAT-TITEL__KURZE-CONVERSATION-ID` mit `MANIFEST.json`,
`messages.jsonl`, `visible_stream.jsonl`, `turns/` und `capture_gaps.jsonl`.
Die append-only Ablage liegt unter
`/root/werkraum/_gpt/ui_visible_conversations`.

## Sichtbares Webseitenabbild

Bei einer normalen Webseite und bei AI-Oberflächen entsteht zusätzlich ein
bereinigtes `page_capture`:

- Ausgangspunkt ist der sichtbare semantische Hauptbereich (`main`,
  `[role="main"]`, `article`, sonst `body`).
- Überschriften, Absätze, Listen, Tabellen, Code, Links und sichtbare Medien
  bleiben als HTML-Struktur erhalten.
- Skripte, Styles, Frames, Templates, Formulare und Eingabewerte,
  Event-Handler, versteckte DOM-Knoten und unsichere URL-Protokolle werden
  entfernt. Externe Links erhalten `target="_blank"` und
  `rel="noopener noreferrer"`.
- Das Snapshot-HTML ist auf 4 MiB begrenzt. Wird gekürzt, steht das explizit
  in JSON und Exportkopf; es ist dann ein sichtbarer Teilabdruck, kein
  Vollseitenbeweis.

Der Offline-HTML-Export rendert dieses Abbild. Der Markdown-Export ergänzt
Quell-URL, Snapshot-Größe und ein Linkverzeichnis; der JSON-Export bewahrt die
vollständigen Snapshot-Metadaten. Scroll-Aufnahmen ergänzen den Abbildstand um
die sichtbaren, einzeln erkannten Bereiche und ihre Belegkette.

## Aufnahme und Versand

Eine Aufnahme ist zunächst lokal. Fehlt der Zugangsschlüssel, werden Ereignisse
sofort im IndexedDB-Puffer abgelegt; Stoppen und Export bleiben dadurch
bedienbar. Der VPS-Versand wird ausschließlich über den sichtbaren Versandknopf
oder nach gesetztem Schlüssel ausgelöst. Ein lokaler Puffer ist kein VPS-ACK.

Die UI trennt deshalb:

- `Adapter erkannt`: die sichtbare Provider-/Webstruktur ist lesbar;
- `gesichert`: sichtbare Bereiche liegen lokal oder im Puffer;
- `VPS bestätigt`: der Empfänger hat einzelne Ereignisse bestätigt;
- `possibly_incomplete` oder `scroll_recording_stopped`: die Aufnahme ist
  bewusst nicht als vollständige Historie bewiesen.

## Grenzen

Der Recorder darf HTML so vollständig wie technisch möglich aus dem aktuellen
Browser-DOM abbilden, aber nicht aus unsichtbaren Daten, fremden APIs,
Session-Tokens oder Login-Geheimnissen. Virtualisierung, Nachladen,
eingeklappte Bereiche und fehlende Überlappung bleiben als Unsicherheit im
Export sichtbar.
