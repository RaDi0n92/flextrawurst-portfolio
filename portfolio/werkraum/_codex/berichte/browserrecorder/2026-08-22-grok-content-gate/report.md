# Grok-Content-Gate · sichtbarer Input ohne Output

EVIDENCE_VERSION: 1
DATE: 2026-08-22
SURFACE: Desktop 1, headful Chromium über CDP 9235

## Aktion

Auf der sichtbaren anonymen Grok-Startseite wurde der deterministische Testinput über die sichtbare Textarea eingegeben und per sichtbarer Enter-Aktion abgesendet:

`Antworte exakt mit zwei nummerierten Punkten: Erstens ALPHA, zweitens OMEGA. Keine weiteren Sätze.`

Vorher-, ausgefüllter- und Nachher-Screenshot sowie DOM-Rücklese liegen in diesem Ordner.

## Sichtbar

Nach dem Absenden erschien der Nutzerinput als sichtbare `user-message`. Ein Assistant-Output, Thinking-Block oder Tool-Schritt erschien nicht. Stattdessen zeigte Grok sichtbar: `Melde dich an, um nahtlos Groks volle Leistung zu nutzen`.

## Rücklese

DOM-Reihenfolge nach der Aktion: Nutzerinput → Login-Aufforderung. Es gibt keinen Output, der exportiert oder gegen eine Replica verglichen werden könnte. Dieser Lauf wird deshalb nicht als vollständiger Grok-Chat gezählt.

- REC-GATE-001: PASS — Recorder-Verträge geprüft.
- REC-EYE-001: PASS — Eingabe, Absenden und Nachher-Zustand sichtbar fotografiert.
- REC-FETCH-001: PASS — Nutzerinput, sichtbare Login-Aufforderung und fehlender Assistant-Output aus DOM rückgelesen.
- REC-SEC-001: PASS — keine Zugangsdaten automatisiert oder gespeichert.
- REC-DOC-001: PASS — Input-ohne-Output-Gate und Abnahmegrenze dokumentiert.

PROVIDER_CONTENT_ABNAHME: BLOCKED — Grok verlangt für den Assistant-Output eine sichtbare Anmeldung.
OUTCOME: PASS
