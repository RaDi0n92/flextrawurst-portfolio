EVIDENCE_VERSION: 1

# UI-Security-Abnahme: untrusted Texte bleiben Text

Datum: 2026-08-15 15:18 +0200
Ort: sichtbares isoliertes Chromium unter `xvfb-run`
Test: `_codex/tools/test_recorder_ui_security_live.js`

## Aktion

Providerlabel, Providerstatus, Importlabel, Selbsttestname und Exclusion-nahe UI-Werte wurden absichtlich mit `<img src=x onerror=alert(1)>` befüllt. Die Sidepanel- und Popup-Renderer wurden danach im sichtbaren Extension-Tab ausgeführt.

## Sichtbar

Screenshot der geladenen Sidepanel-Oberfläche: `/tmp/dak-recorder-ui-security.png`. Die Oberfläche wurde mit `view_image` angesehen. Der Angriffstext erscheint nicht als Bild oder Script; die technische Ausgabe bleibt separat als DOM-Rücklese erhalten.

## Rücklese

- Sidepanel Provider: `activeNodes: 0`; der Text enthält den vollständigen Angriffstext, HTML zeigt escaped `&lt;img`.
- Sidepanel Selbsttest: `activeNodes: 0`; der Angriffstext bleibt `textContent`.
- Sidepanel Importbereich: `activeNodes: 0`; auch Ordinal und Label bleiben Text.
- Popup Provider: `activeNodes: 0`; der gleiche Angriffstext wurde nicht als DOM-Element interpretiert.
- Overlay-Regression: `content.js` enthält keinen `box.innerHTML`-Sink mehr.
- Syntaxchecks für Sidepanel, Popup, Content-Script und Sicherheitstest sowie Crawler-/Download-Regression blieben grün.

## Offen / unbekannt

Die absichtlich statischen `innerHTML`-Blöcke für Shadow-DOM-CSS und leere Workspace-Zustände sind keine untrusted Datenpfade. Die erzeugten Offline-HTML-/Markdown-/PDF-Projektionen bleiben eigene Artefaktpfade und brauchen separat Format-/Escaping-Abnahmen.

Die Manifest-Berechtigung `debugger` bleibt als bereits vorhandene breite Berechtigung bestehen; in diesem Schnitt wurde sie nicht weiter erweitert und nicht als minimal bewiesen. Eine eigene Berechtigungs-/Production-Policy-Abnahme bleibt offen.

- REC-GATE-001: PASS — Vertragsgate vor dem UI-Schnitt und Evidenzgate nach dem Live-Test.
- REC-SEC-001: PASS — absichtliche HTML-Injektionen erzeugten in Sidepanel und Popup null aktive HTML-/Script-Knoten; Werte wurden als Text rückgelesen.
- REC-DOC-001: PASS — Aktion, sichtbarer Screenshot, DOM-Rücklese und offene Permission-/Artefaktgrenzen sind getrennt dokumentiert.

OUTCOME: PASS
