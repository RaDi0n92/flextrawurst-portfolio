---
autor: claude bei Daniels VPS
datum: 2026-09-20
herkunft: Playwright-Guardian-Vertrag von codex bei Daniels VPS (2026-09-19) und Beweisstrategie aus der Baustartprüfung von codex bei Daniels VPS (2026-09-19). Neu geschrieben von Claude aus den Originalen in archiv/originale/
status: Guardian umgesetzt als Browser- und Core-Gate; native Windows-Abnahme offen
betrifft: [augen-und-haende, playwright, creative-harness, fensterscanner, evidence]
---

# Augen & Hände — Nachweise

Dieses Dokument legt fest, was in der Bridge als Beweis gilt und was nicht. Es hat zwei Teile: die allgemeine Beweisstrategie und den Playwright-Guardian, der sie für alles Browserbedienbare erzwingt.

## Beweisstrategie ohne Selbsttäuschung

Für jede Funktion wird festgehalten: die Anforderung, die echte Quelle, die ausgeführte Aktion, die erwartete Beobachtung, die tatsächliche Beobachtung und die verbleibende Grenze.

- Core-Tests prüfen Logik, Transporttests prüfen Nachrichten und Ausfälle.
- Playwright bleibt für browserbedienbare Entwicklungs- und Prüfwege erforderlich. Es beweist deren Verhalten und nicht automatisch Win32-Eingaben oder Tk-Fenster.
- Native UI braucht zusätzlich echte Windows-Aufnahmen und eine Rücklese von Betriebssystem und App. Eine Webseite, die »F12 funktioniert« anzeigt, ist kein Not-Aus-Test.
- Gezielte Fehlerfälle werden geprüft: falscher Empfänger, unbekanntes Ziel, abgelaufene Lease, veralteter Frame, Replay nach Reconnect, geschlossene Session, fehlende Kamera, geänderte DPI und UI-Hänger.
- Timing und Ressourcen werden auf dem tatsächlichen Gerät gemessen. Vorher sind sie Ziele. Messrate, Lücken und Unsicherheit gehören in den Bericht.

## Der Playwright-Guardian

Status: umgesetzt als Browser- und Core-Gate. Die native Windows-Abnahme ist offen.

### Die Idee

Die Harness darf nicht mehr aus ihrem eigenen Zustand heraus behaupten, dass ein Schritt funktioniert hat. Playwright wird ein äußerer Zeuge für jeden browserbedienbaren Prüfpfad. Es benutzt die sichtbare Bedienung, liest danach die sichtbare Oberfläche und den laufenden Core zurück und vergleicht beides mit der Auditspur.

Playwright ist dabei nicht die Autorität und kein Ersatz für den nativen Windows-Adapter. Es ist ein strenger Wächter gegen die typische Abkürzung:

```text
Button behauptet Erfolg → Harness glaubt Erfolg → Test wird grün
```

Die neue Kette lautet:

```text
sichtbarer Control-Klick
→ DOM-Rücklese
→ Core-State-Rücklese
→ Audit-Suffix-Rücklese
→ frischer Scanner-/Frame-Zeuge
→ Guardian-Verdikt
```

Nur wenn alle browserseitig erwartbaren Schichten zusammenpassen, darf der Schritt `PASS` heißen.

### Was der Guardian erzwingt

Jeder geprüfte Schritt erhält eine stabile `step_id`, die erwartete Aktion, die erwartete DOM-Projektion, die erwarteten Core-Werte und eine direkt anschließende Audit-Sequenz. Geht es um ein Ziel, kommen ein aktueller `target_id` und ein Scanner- oder Frame-Zeuge dazu.

Die drei Verdikte sind absichtlich nicht austauschbar:

- `pass`: DOM, Core, Audit und der erforderliche frische Zeuge passen zusammen.
- `blocked`: Eine Behauptung widerspricht einer anderen Schicht, zum Beispiel ein sichtbares `accepted` ohne passende Audit-Sequenz.
- `unknown`: Ein erforderlicher Zeuge fehlt, etwa der native Windows-Nachweis. `unknown` wird niemals still zu `pass` hochgestuft.

Der Vertrag liegt in `/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/guardian.py`. Der reale Playwright-Witness liegt in `/root/werkraum/augen_haende_bridge/tests/playwright_guardian.py`. Der Guardian benutzt die sichtbaren Rollen- und Button-Controls und sendet im Witness keine direkten `POST`-Mutationen.

### Was damit besser wird

- Eine `observed`-Anzeige ohne Core-Rücklese ist kein Pass.
- Eine Policy-Akzeptanz ohne Target- und Frame-Zeugen ist kein vollständiger Ziel-Pass.
- Ein vorhandener Screenshot ohne passende strukturierte Auditspur ist kein Handlungsbeweis.
- Ein synthetischer Proof-Surface-Zustand bleibt als `synthetic.proof-surface` sichtbar.
- Der aktuelle Stand kann korrekt `unavailable` melden, statt einen nicht gebauten KDE-Adapter als beobachtet auszugeben.
- Der Guardian hebt einen Browser-Pass nicht zu einem nativen Windows-Pass an.

Die Proof-Surface liefert dafür jetzt einen gekoppelten synthetischen `TargetScanSnapshot` mit Inventar, `scan_id` und `frame_hash`. Das ist ein Vertragstest für die spätere native Scannerquelle und kein behaupteter Windows-Capture.

### Playwright-Werkzeuge und ihre Rolle

Der Witness nutzt die wiederholenden Assertions von Playwright für sichtbare Zustände, einen isolierten Browser-Kontext und Tracing mit Screenshots und Snapshots. Bei einem Fehlschlag bleibt dadurch nicht nur eine Exception, sondern eine rekonstruierbare Beweisspur.

Die offiziellen Bezugspunkte sind:

- Fixtures und isolierte Testumgebungen: https://playwright.dev/docs/test-fixtures
- Web-first Assertions und Screenshot- und ARIA-Beweise: https://playwright.dev/docs/test-assertions
- Tracing mit Screenshots und Snapshots: https://playwright.dev/docs/api/class-tracing
- stabile Screenshot-Vergleiche: https://playwright.dev/docs/api/class-pageassertions

### Die harte Grenze

Playwright sieht DOM, lokale Proof-API und Browser-Netzwerk. Aus einer Browseranzeige kann es nicht ableiten, dass ein natives Win32-, Tk- oder EXE-Fenster sichtbar, fokussiert, klickdurchlässig oder wirklich bedient wurde. Für diese Schritte bleibt die Beweisform:

```text
Playwright-Protokollpass
+ native Plattformaufnahme
+ native Zustandsrücklese
```

Fehlt der zweite Teil, lautet das Ergebnis `UNKNOWN`. Genau diese Grenze schützt vor einer wieder zu großzügigen Harness.

### Nächste Anwendung

Der Guardian wird vor jeder weiteren browserbedienbaren Etappe als Pflichtschicht verwendet: bei der Auswahl im Fensterscanner, der Rücklese des Bindings, den Aktionen von Raute und Regie, der Terminal-Probe, dem Zeit-Scrubber und der späteren Kapsel-Ansicht. Für echte Windows-Aktionen kommt jeweils ein eigener nativer Zeuge hinzu. Playwright darf diese Lücke nicht kaschieren.
