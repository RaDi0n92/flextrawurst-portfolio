# Augen & Hände — Greenfield-Neubau

## START HIER für jeden Bridge-Agenten

Der kanonische Einstieg für Codex, Claude, Gemini und Menschen ist
`/root/werkraum/augen_haende_bridge/START_HIER.md`.

Dieser Ordner ist der gemeinsame lebende Arbeitskörper. Hier liegen der
aktuelle Harness-/Runtime-Code, Tests, Buildstand und die direkten Skill-
Verweise unter `/root/werkraum/augen_haende_bridge/skills/`. Die laufenden
Bridge-Dokumente sind über
`/root/werkraum/augen_haende_bridge/bridge_docs/` erreichbar.

Die Übergabekapsel unter
`/root/werkraum/übergabekapseln/augen_haende_bridge/` ist nur die Lese- und
Weitergabeverpackung darum herum. Sie ist nicht der produktive Arbeitsort.

Dieser Ordner ist der neue Produktionspfad für die Augen-und-Hände-Bridge.

Der vorhandene Gemini-Prototyp unter `/root/werkraum/_gemini/windows_bridge/` wurde am 2026-09-20 auf ausdrücklichen Auftrag entfernt. Er bleibt nur in der Git-Historie nachvollziehbar und ist keine aktive Referenz, Laufzeit oder Testquelle.

Das gewünschte Programm-Overlay soll auf Windows oder KDE-Desktop 1/2 angezeigt werden können. Anzeigeort und Arbeitsziel sind unabhängig; ein Zielwechsel erzeugt keine neue Agentensession. Diese Plattformfunktionen sind noch nicht vollständig implementiert oder abgenommen.

**Statuskorrektur, Codex 2026-09-19:** Die nachfolgenden historischen Abschlüsse betreffen ihre jeweiligen Core-/Browserbeweise. Insbesondere B4.6 ist keine native Overlay-Abnahme. Es liegt hier kein nachgewiesen ausgeliefertes Windows-Paket mit vollständigem Rückkanal vor. Maßgeblich für den nächsten Einstieg: `/root/werkraum/docs/augen_haende_bridge/ANFORDERUNGEN.md`.

## Aktueller Stand

- B0/B1: Domänenvertrag und fail-closed Policy-Grundlage — abgeschlossen
- B2: deterministischer In-Memory-Loopback-Kern — abgeschlossen
- B3: VisionSession, Frame-Ring und Audience-Sichtbarkeit — abgeschlossen
- B0–B4: Kernlogik und Playwright-Proof-Gate — abgeschlossen
- H1: Creative Harness-Core und Playwright-Dogfood — abgeschlossen
- B4.5a: Terminal-Inspector und Live-Target-Switcher — Core + Playwright mit echten Konsole-Snapshots abgeschlossen
- B4.5b: gekäfigte Live-Eingabeprobe mit `accepted -> delivered -> echoed -> observed -> audited` — Core + Playwright abgeschlossen
- B4.6: referenzgetriebene Windows-Bridge-Surface — Core + sichtbarer Playwright-Beleg abgeschlossen — Name historisch; nicht gegen Daniels dokumentierte Vorgaben abgenommen (maßgeblich: `START_HIER.md`, Abschnitt „Zuerst: die Quelle“)
- G01: side-effect-free Plattform-Preflight ausgeführt; Linux/KDE-Transport ist hier prüfbar, Windows-EXE, native Overlay-Evidence und das ausgewählte Originalterminal bleiben ausdrücklich offen
- G01–G04: Greenfield-Transport, TargetRegistry, stabile Terminal-Identität und Bridge-Readback — Core-/Playwright-Belege abgeschlossen
- G05: vollständiges Windows-EXE-Bundle vorhanden; native Windows-Abnahme bleibt offen
- G06: gebündelter EXE-Erstkontakt mit sichtbarem Nachricht-Rücklesen im Wine-Smoke
- G07: read-only GDI-Frame plus Win32-Fensterscanner im Wine-Smoke; native Windows bleibt offen
- G08: aktueller VPS-Relay auf Loopback `19880` plus SSH-LocalForward-Launcher lokal bewiesen; echter Windows-/SSH-E2E bleibt offen
- G09: read-only Binding-Core mit Frame-/Generation-Rücklese — abgeschlossen als Core, native Auswahl offen
- G10: nativer Windows-Acceptance-Witness vorbereitet; echter Windows-Lauf offen
- G11: gebündelter EXE-Scan führt observe-only Binding im Wine-Smoke zurück; native Windows bleibt offen
- B5: MCP-Fassade — als Nächstes
- B6+: geplant im Bauplan

## Beweisvertrag

Ein grüner Unit-Test schließt keine Etappe allein. Jede Etappe braucht zusätzlich
einen Playwright-Beleg mit sichtbarem Zustand, Screenshot, DOM-/Status-Rücklese,
konkreter Aktion, Antwort und Auditspur. Die laufenden Belege liegen unter
`/root/werkraum/augen_haende_bridge/tests/evidence/`.

## Ausführen

```text
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

Für die sichtbare referenzgetriebene Bridge-Surface auf Windows:

```text
PYTHONPATH=src python3 -m augen_haende_bridge.reference_surface
```

Das ist die räumliche Surface aus der Referenz: Zielschiene, gebundene Desktopfläche,
Agenten-Rauten, beschriftete Beziehungspfeile, Terminalflächen, Regie unten links
und ein Fensterscanner je Terminal. Sie ist keine Homepage.

Für den ehrlichen Voraussetzungen-Nachweis von G01:

```text
PYTHONPATH=src python3 -m augen_haende_bridge.preflight
```

Der Preflight verändert keine Prozesse, Fenster oder Dateien. `AVAILABLE` bedeutet
nur, dass die lokale Voraussetzung sichtbar ist; `NOT_PROVEN` bleibt offen und ist
kein Ersatz für einen Windows-/KDE-Livebeleg.

Der Preflight ist ein Diagnosewerkzeug, nicht die Produkt-Surface. Die historische
Proof-Surface und der alte Gemini-Prototyp sind aus dem aktiven Pfad entfernt;
historische Reports werden nicht als aktuelle Produktbeweise gewertet.

Der erste Baukern verwendet bewusst nur Python-Standardbibliothek. Transport, Windows-Adapter, Linux-Adapter, MCP und UI kommen als getrennte Etappen hinzu.
