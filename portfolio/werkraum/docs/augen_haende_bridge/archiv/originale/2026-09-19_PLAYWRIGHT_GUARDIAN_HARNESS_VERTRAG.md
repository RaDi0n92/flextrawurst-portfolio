---
datum: 2026-09-19
autor: codex bei Daniels VPS
status: umgesetzt als Browser-/Core-Gate; native Windows-Abnahme offen
betrifft: [augen-und-haende, playwright, creative-harness, fensterscanner, evidence]
---

# Playwright Guardian für die Creative-Harness

## Die Idee

Die Harness darf nicht mehr aus ihrem eigenen Zustand heraus behaupten, dass ein Schritt funktioniert hat. Playwright wird ein äußerer Zeuge für jeden browserbedienbaren Prüfpfad: Es benutzt die sichtbare Bedienung, liest danach die sichtbare Oberfläche und den laufenden Core zurück und vergleicht beides mit der Auditspur.

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

## Was der Guardian erzwingt

Jeder geprüfte Schritt erhält eine stabile `step_id`, die erwartete Aktion, erwartete DOM-Projektion, erwartete Core-Werte, eine direkt anschließende Audit-Sequenz und — sofern es um ein Ziel geht — einen aktuellen `target_id`- und Scanner-/Frame-Zeugen.

Die drei Verdikte sind absichtlich nicht austauschbar:

- `pass`: DOM, Core, Audit und erforderlicher frischer Zeuge passen zusammen.
- `blocked`: Eine Behauptung widerspricht einer anderen Schicht, zum Beispiel sichtbares `accepted` ohne passende Audit-Sequenz.
- `unknown`: Ein erforderlicher Zeuge fehlt, etwa der native Windows-Nachweis. `unknown` wird niemals still zu `pass` hochgestuft.

Der Vertrag liegt in `/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/guardian.py`. Der reale Playwright-Witness liegt in `/root/werkraum/augen_haende_bridge/tests/playwright_guardian.py`. Der Guardian benutzt die sichtbaren Rollen-/Button-Controls und sendet im Witness keine direkten `POST`-Mutationen.

## Was damit konkret besser wird

- Eine `observed`-Anzeige ohne Core-Rücklese ist kein Pass.
- Eine Policy-Akzeptanz ohne Target-/Frame-Zeugen ist kein vollständiger Ziel-Pass.
- Ein vorhandener Screenshot ohne passende strukturierte Auditspur ist kein Handlungsbeweis.
- Ein synthetischer Proof-Surface-Zustand bleibt als `synthetic.proof-surface` sichtbar.
- Der aktuelle Stand kann korrekt `unavailable` melden, statt einen nicht gebauten KDE-Adapter als beobachtet auszugeben.
- Der Guardian hebt einen Browser-Pass nicht zu einem nativen Windows-Pass an.

Die Proof-Surface liefert dafür jetzt einen gekoppelten synthetischen `TargetScanSnapshot` mit Inventar, `scan_id` und `frame_hash`. Das ist ein Vertragstest für die spätere native Scannerquelle, kein behaupteter Windows-Capture.

## Playwright-Werkzeuge und ihre Rolle

Der Witness nutzt Playwrights wiederholende Assertions für sichtbare Zustände, einen isolierten Browser-Kontext und Tracing mit Screenshots/Snapshots. Dadurch bleibt bei einem Fehlschlag nicht nur eine Exception, sondern eine rekonstruierbare Beweisspur.

Die offiziellen Bezugspunkte sind:

- Fixtures und isolierte Testumgebungen: https://playwright.dev/docs/test-fixtures
- Web-first Assertions und Screenshot-/ARIA-Beweise: https://playwright.dev/docs/test-assertions
- Tracing mit Screenshots und Snapshots: https://playwright.dev/docs/api/class-tracing
- stabile Screenshot-Vergleiche: https://playwright.dev/docs/api/class-pageassertions

## Die harte Grenze

Playwright kann DOM, lokale Proof-API und Browser-Netzwerk sehen. Es kann aus einer Browseranzeige nicht ableiten, dass ein natives Win32-/Tk-/EXE-Fenster sichtbar, fokussiert, klickdurchlässig oder wirklich bedient wurde. Für diese Schritte bleibt die Beweisform:

```text
Playwright-Protokollpass
+ native Plattformaufnahme
+ native Zustandsrücklese
```

Fehlt der zweite Teil, lautet das Ergebnis `UNKNOWN`. Genau diese Grenze ist der Schutz gegen eine wieder zu großzügige Harness.

## Nächste Anwendung

Der Guardian wird vor jeder weiteren browserbedienbaren Etappe als Pflichtschicht verwendet: Fensterscanner-Auswahl, Binding-Rücklese, Raute-/Regie-Aktionen, Terminal-Probe, Zeit-Scrubber und spätere Kapsel-Ansicht. Für echte Windows-Aktionen kommt jeweils ein separater nativer Zeuge hinzu; Playwright darf diese Lücke nicht kaschieren.

