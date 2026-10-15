# Provider-Session-Probe · Voraussetzung für Inhaltsabnahme

EVIDENCE_VERSION: 1
DATE: 2026-08-22
SURFACE: Desktop 1, headful Chromium über CDP 9235

## Aktion

Playwright öffnete die vier Original-Providerseiten sichtbar und las pro Seite URL, Titel, sichtbaren Text, sichtbare Buttons und sichtbare Eingabeflächen. Pro Provider wurde ein Screenshot vor jeder weiteren Aktion gespeichert. Es wurde kein Login automatisiert und kein Zugangstoken gelesen.

## Sichtbar

| Provider | sichtbarer Zustand | Eingabe sichtbar | Thinking-/Chat-Abnahme möglich |
|---|---|---:|---:|
| ChatGPT | Login-/Willkommensseite, „Anmelden“ sichtbar | Ja, Chat-Eingabe-DIV | Nein, kein Chat geladen |
| Grok | Öffentliche Startseite mit „Frag Grok …“ | Ja, Textarea | Teilweise, aber kein authentifizierter Bestandchat |
| Claude | `/login`, Google/E-Mail/SSO-Anmeldung | Nein, nur E-Mail-Login | Nein |
| Gemini | Startseite mit Google-„Anmelden“ und Cookie-Dialog | Ja, Prompt-DIV | Nein, kein Chat geladen |

DOM-Rücklese und Screenshots: `provider-session-probe.json`, `provider-*-session-probe.png`.

## Rücklese

Die vier Original-Exporter sind geladen; die fehlende Voraussetzung ist nicht die Extension, sondern ein sichtbarer Provider-Chat. Ohne Anmeldung kann ich keine Eingaben/Outputs, Reihenfolge, eingeklappte Thinking-Blöcke oder vollständige Original-Exportdateien behaupten.

- REC-GATE-001: PASS — Recorder-Verträge geprüft.
- REC-EYE-001: PASS — jede Providerseite sichtbar geöffnet und fotografiert.
- REC-FETCH-001: PASS — DOM-Status und Eingabeflächen rückgelesen.
- REC-SEC-001: PASS — keine Zugangsdaten automatisiert oder gespeichert.
- REC-DOC-001: PASS — Voraussetzung und Grenze explizit dokumentiert.

PROVIDER_CONTENT_ABNAHME: BLOCKED — sichtbare Anmeldung in ChatGPT, Claude und Gemini erforderlich; danach wird die Inhalts-/Thinking-/Export-Abnahme fortgesetzt.

OUTCOME: PASS
