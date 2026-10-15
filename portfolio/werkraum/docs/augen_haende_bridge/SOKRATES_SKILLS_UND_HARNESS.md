# Sokrates mit dem Skill: Stand, offene Punkte, Verbesserungen (Stand 2026-10-02)

Lupe: die Skills `skill-schreiben` und `bridge-praxistest` samt Harness.

Jede Aussage nennt ihren Beleg. Aussagen ohne Beleg stehen als „offen“.

## Frage 1: Welche Doku und Anleitungen sind erfüllt, welche offen?

### Erfüllt (belegt)

Beschreibung mit Auslösern und Gegenfällen, kurzer Körper, flache Verweise, Warum statt Drohung,
Ausreden-Tabelle, Standing orders.

Beleg: `skill_pruefen.py` meldet 0 Fehler und 0 Hinweise; der Validator des Skill-Creators
(`quick_validate.py`) meldet bei beiden Skills „valid“.

Regel 0 (nichts im Verborgenen) und die Ansage vor jedem Schritt sind in Skill, Drehbuch und
Harness verankert (Tests: `test_praxis_lauf`, `test_praxis_dienst`).

Ledger mit Gegenprobe. Gesamtregression: siehe `REDTEAM_PREMORTEM_SKILLS.md` für den aktuellen Lauf.

### Offen

1. Erprobungslauf je Skill mit und ohne Skill (Skill-Creator: zwei bis drei Anfragen) und
   Beschreibungs-Optimierer (`run_loop.py`, `improve_description.py` sind vorhanden, nicht gelaufen).
2. Lesbarkeitsregel für .md (Absatzumbruch nach etwa 100 Zeichen): in den beiden SKILL.md stehen
   17 und 24 Zeilen über 100 Zeichen (ohne Tabellen und Code). Der Prüfer kennt die Regel noch nicht.
3. Bauprotokoll (BUILD_LOG) und Abnahme für G15, Seeds, Loops, Set-of-Mark, Praxistest, Skills.
4. Windows-Paket: sechs Körper- und Transportdateien sind seit dem Bau geändert; neues Paket nötig.
5. Karte und Notiz am Sessionende: erst ansagen, dann Daniels „go“.

## Frage 2: Was fehlt?

- **P0: Bestätigung, dass die Ansage in der Raute wirklich erscheint.** Der Körper tippt nur, wenn
  Hände an sind, kein Not-Aus gilt, nichts anderes läuft und der Agent nicht „nur Terminal“ ist; sonst
  bleibt es stumm oder erscheint nur als Ticker. Die Harness weiß das heute nicht.
- Vorflug-Check vor Schritt 1 (Körper verbunden, Raute tippt, Ziel gebunden, Lease, Bilder).
- Käfig-Freigabe für Bridge-Menüs, mit Liste erlaubter Einträge (nicht „Bridge beenden“).
- Wiederaufnahme eines Laufs nach Neustart des Starters.
- Wie Gemgem (agy) Skills findet: unbekannt.
- Windows: nichts davon belegt.
- Aus dem Test auf vd1: Chat nimmt kein Einfügen an; keine Transparenz (kein Compositor).

## Frage 3: Womit können wir es pimpen?

Erst nach P0 und P1 (siehe Reihenfolge). Alles hier ist Idee mit Prüfpunkt.

1. Klick-Ringe in Agentenfarbe an jeder Aktion der Hände. Prüfpunkt: kleiner Machbarkeitstest auf
   vd1 ohne Compositor.
2. Praxistest-Tafel: Karte, Knoten, Fortschritt, Lesezeit-Countdown, Knopf „nicht verstanden“.
3. Jeder Schritt wird eine Kapsel. Der Scrubber zeigt dann einen Zeitraffer aus Ereignissen und
   Standbildern (je Agent höchstens zehn Bilder pro Kapsel), keinen Film.
4. Befunde (anders, fehler, Entdeckung) werden automatisch Seed-Vorschläge mit Kapsel als Herkunft.
5. Mitdenkende Harness: wiederholt sich ein Grund, Planänderung vorschlagen, Schritt als
   „verdächtig“ markieren.
6. Szenario-Bibliothek (Browser, Editor, Spiel, Blender) mit WorldDOM-Profilen je Programm.
7. Probelauf in der Pipeline mit zwei Skript-Agenten im Xvfb.
8. Skill-Evals und Beschreibungs-Optimierer.
9. Prüfer lernt die Lesbarkeitsregel.
