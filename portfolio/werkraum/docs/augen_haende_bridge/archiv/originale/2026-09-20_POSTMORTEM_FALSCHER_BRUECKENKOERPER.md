---
datum: 2026-09-20
typ: postmortem
status: goal pausiert; produkt nicht abgenommen
autor: codex bei Daniels VPS
betrifft:
  - augen-haende-bridge
  - falscher-baupfad
  - review-versagen
  - surface-drift
---

# Postmortem: falscher Bridge-Körper trotz klarer Vorgaben

## Urteil

Der relevante Bauauftrag wurde verfehlt. Es wurde eine technisch testbare,
aber inhaltlich falsche EXE-/Surface-Schicht weitergebaut. Der vereinbarte
erste nutzbare Körper — ein einzelnes echtes Terminal mit Fensterscanner,
ohne Fake-Agenten und ohne Monster-Surface — wurde nicht geliefert.

Daniels Bilanz laut Gespräch:

> „außer dokumentation hast du nix hinbekommen“

Auch diese Einschränkung ist fair: Die Dokumentation ist selbst zu dicht,
wiederholend und teilweise nicht ernsthaft genug als belastbarer Arbeitsvertrag.

## Was ausdrücklich verlangt war

- Ein echtes Programm als EXE, keine Homepage und keine große Ersatz-Surface.
- Als erster tragender Körper genau **ein** sauberes Terminal.
- Der Fensterscanner gehört an dieses Terminal, unten rechts, und öffnet die
  Auswahl erst bei Bedarf.
- Rauten erscheinen nur für tatsächlich vorhandene und gebundene Agenten.
- Keine vier Platzhalter-Terminals, keine Beziehungspfeil-Landschaft und keine
  vorgetäuschte Agentenpräsenz.

## Was stattdessen weitergetragen wurde

Die Datei
`/root/werkraum/augen_haende_bridge/client_windows/overlay_app.py`
enthielt weiterhin die alte Surface-Logik:

- ein großes, zentrales Overlay mit Raster und Beziehungspfeilen;
- voreingetragene Codex-, Gemini-, Claude- und Daniel-Rauten;
- vier Terminalkarten;
- lokale Regie-/Mikrofon-/Kamera-Platzhalter.

Diese Logik wurde nicht als verdächtige Altlast entfernt oder quarantänisiert,
sondern als Grundlage für den Greenfield-Körper behandelt. Die daraus gebaute
G12-Lieferung ist deshalb kein akzeptierter Produktkörper, auch wenn sie unter
Wine startet und technische Readback-Tests besteht.

## Der eigentliche Fehler

Daniel hat es später präzise formuliert:

> „schaiss auf autonom. selbst schritt für schritt hättest du die selbe logik angewant“

Das stimmt. Autonomie war nicht die Ursache. Auch ein eng betreuter Bau hätte
denselben Fehler wiederholt, weil die falsche Quelle als Wahrheit verwendet
wurde:

1. Vorhandener Code wurde als legitime Grundlage behandelt.
2. Die expliziten visuellen und funktionalen Vorgaben wurden nicht als
   Abbruchkriterium gegen diesen Code durchgesetzt.
3. Tests prüften Transport, Registry, Scanmarker und Binding-Readback — nicht
   die Frage, ob beim Öffnen exakt Daniels gewünschter Körper erscheint.
4. Ein grüner technischer Teilbeleg wurde fälschlich als Produktfortschritt
   interpretiert.

Der entscheidende Satz lautet:

> „Der eigentliche Fehler war: Ich habe deine Vorgaben nicht als harte Quelle behandelt, sondern den vorhandenen falschen Code als Quelle.“

## Warum Claude und Gemini es nicht verhindert haben

Die Fremdprüfer haben technische Teilbereiche geprüft. Sie fanden reale
Probleme in Transport, Idle-Verbindung, Namespace und Readback. Sie bekamen
aber keinen sauber erzwungenen Auftrag, die tatsächlich geöffnete EXE gegen
Daniels sichtbaren Minimalvertrag abzunehmen.

Sie prüften damit überwiegend:

> „Ist der neue Code technisch konsistent?“

statt:

> „Öffnet sich exakt das, was Daniel verlangt hat?“

Außerdem wurde die alte Surface als vorhandener Kontext präsentiert. Ein
Reviewer, der nur Änderungen und technische Verträge liest, hinterfragt eine
unveränderte falsche Grundlage nicht automatisch. Das erklärt das Durchrutschen;
es entschuldigt es nicht.

## Negative Tests waren nicht die Ursache und nicht die Lösung

Es war nicht nötig, einen Test zu schreiben, damit klar wird, dass vier
Terminals falsch sind. Das stand bereits in den Anforderungen. Ein
Negativtest hätte höchstens als zusätzlicher Sicherungszaun geholfen, nachdem
die Anforderungen korrekt verstanden worden waren.

Die fehlenden Negativtests waren also ein Symptom des wichtigeren Fehlers:
Die Vorgaben wurden nicht als unmittelbare Bauwahrheit behandelt.

## Was tatsächlich erreicht wurde

Es existieren technische Artefakte unter
`/root/werkraum/augen_haende_bridge/`: Relay, Registry, Scannerkern,
read-only Binding, EXE-Bundle, Tests und Evidence-Strukturen. Diese Artefakte
beweisen einzelne technische Eigenschaften.

Sie beweisen aber nicht den verlangten nutzbaren Bridge-Körper. Insbesondere
beweisen sie nicht:

- ein echtes 1:1-Terminal;
- die gewünschte erste EXE-Oberfläche;
- reale Agentenpräsenz statt Platzhalter-Rauten;
- vollständige native Windows-Abnahme;
- ChatGPT-/Claude-/Gemini-Körper in der Bridge.

Die aktuelle G12-Lieferung unter
`/root/werkraum/augen_haende_bridge/dist/AugenUndHaendeBridge-G12-win64-handoff.zip`
ist daher ein forensisches Zwischenartefakt, keine Produktfreigabe.

## Korrekte Lehre

Bei einer Wiederaufnahme gilt zwingend:

- User-Anforderung und sichtbare Referenz stehen über vorhandenem Code.
- Vorhandener UI-Code ist bei Widerspruch Altlast, nicht Fundament.
- Der erste Start wird gegen die gewünschte Ansicht geprüft, bevor weitere
  Transport- oder Evidence-Schichten darauf gesetzt werden.
- „Technisch grün“ darf niemals „inhaltlich richtig“ ersetzen.
- Ein Schritt-für-Schritt-Prozess ist nur dann sinnvoll, wenn der erste Schritt
  auf der richtigen Grundlage beginnt.

Der Bau-Goal ist auf Daniels Wunsch pausiert. Dieses Dokument verändert keinen
laufenden Service und löscht keine weiteren Artefakte.
