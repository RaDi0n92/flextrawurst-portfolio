# Exporter-Parity-Inventar — sichtbare Desktop-1-Prüfung

EVIDENCE_VERSION: 1
DATE: 2026-08-22
SURFACE: headful Chromium auf Desktop 1, Playwright über `127.0.0.1:9235`
SCOPE: ChatGPT Exporter 6.10.0, Grok Exporter 2.4.1, Claude Exporter 3.8.1, Gemini Exporter 4.3.0

## Aktion

Die vier tatsächlich geladenen Extension-Origin-Oberflächen wurden einzeln als `popup.html` und `options.html` geöffnet. Pro Oberfläche wurden sichtbarer Text, Buttons, Schalter, Eingaben, Comboboxen und Links aus dem DOM gelesen und ein Screenshot gespeichert. Die vier Anbieter-Popups zeigen dieselbe Grundstruktur; die Unterschiede sind in den sichtbaren Beschriftungen und provider-spezifischen Schaltern festgehalten.

## Sichtbar

Gemeinsame Grundstruktur aller vier Exporter:

| Bereich | Sichtbare Funktion |
|---|---|
| Kopf | Exportieren, Feedback |
| Häufige/allgemeine Einstellungen | Export-Buttons anzeigen/verstecken; Auswahl nach Export automatisch schließen |
| Dateiname | Dateinamensformat; benutzerdefinierter Teil; Muster `{Benutzerdefinierter Teil}-{Gesprächstitel}-{Zeitstempel}` |
| Ablage | Download-Standort/Speicherort; Einstellungen öffnen |
| Quellen/Metadaten | Gesprächslink; Nachrichten-Zeitstempel; Denkprozess; Websuchquellen; Inhaltstitel; Benutzerinfo; Datum & Uhrzeit |
| Ausgabe | In Zwischenablage kopieren |

Gesprächsformate, die in allen vier Content-Skripten als sichtbare Auswahl definiert sind:

`CSV` · `JSON` · `TEXT` · `MARKDOWN` · `PDF`

Provider-Deltas:

- ChatGPT: Deep-Research-Referenzen zusätzlich zu Websuchquellen.
- Grok: gleiche gemeinsame sichtbare Format-/Metadatenstruktur wie ChatGPT; Deep-Research-Referenzen sichtbar.
- Claude: Artefakte-Inhalt, Tool-Schritte, Websuche-Quellen und `Bilder einbetten (nur Markdown)`; Projektmodus bietet zusätzlich `ZIP`.
- Gemini: Deep-Research-Referenzen und `Bilder einbetten (nur Markdown)`; Unterhaltungslink statt Gesprächslink.

Screenshots und DOM-Rücklese:

- `chatgpt-popup.png`, `chatgpt-options.png`
- `grok-popup.png`, `grok-options.png`
- `claude-popup.png`, `claude-options.png`
- `gemini-popup.png`, `gemini-options.png`
- `dom-inventory.json`

## Rücklese

Die sichtbaren Export-Format-Arrays wurden zusätzlich aus den geladenen Content-Skripten geprüft:

```text
ChatGPT: csv, json, txt, md, pdf
Grok:    csv, json, txt, md, pdf
Claude:  csv, json, txt, md, pdf
Claude-Projekt: zip
Gemini:  csv, json, txt, md, pdf
```

DOCX ist kein Format der vier Fremd-Exporter. Unsere vorhandenen Office-Pfade bleiben deshalb eine eigene Recorder-Projektion und werden nicht fälschlich als Fremd-Exporter-Parität ausgegeben.

## Offen/Unbekannt

- Ein angemeldeter Provider-Chat war für diese Inventur nicht notwendig und wurde nicht heimlich geöffnet.
- Die sichtbare Formatliste ist belegt; die pixelgenaue interne Dateierzeugung der Fremd-Exporter ist nicht Teil der Replica.
- PDF kann bei den Fremd-Exportern über einen externen PDF-Dienst laufen; diese Netzwerk-/Analytics-/Berechtigungsmechanik bleibt außerhalb der Parity-Schicht.

## Marker

- REC-GATE-001: PASS — Contract-Gate meldete `ok: true`, 10 Marker/10 Skills.
- REC-EYE-001: PASS — Acht sichtbare Popup-/Options-Screenshots und `dom-inventory.json` liegen in diesem Ordner.
- REC-FETCH-001: PASS — Für die Inventur wurden keine Provider-Seiten heimlich gecrawlt und keine Exporter-Netzwerkpfade übernommen.
- REC-SEC-001: PASS — Keine Zugangsdaten, Cookies oder Token wurden gelesen oder gespeichert.
- REC-DOC-001: PASS — Aktion, Sichtbar, Rücklese und Offen/Unbekannt sind getrennt dokumentiert.

OUTCOME: PASS
