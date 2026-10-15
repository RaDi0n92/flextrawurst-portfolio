# CT-Scan: Reibung / Widerspruch -> Conflict-Engine

## 1. Die Geburtsurkunde (Direkt belegt)
Die direkte Brücke zwischen dem Flarum-Befund "Reibung" und dem Feature "Conflict-Engine" findet sich in der Datenbank-Analyse-Datei `f06_reibung.md` (unter `_codex_grundriss/codex_claude_flarum_analyse/17_claude_direkte_db_analyse/`).
Dort dokumentierte Claude explizit:
> "Beim Conflict-Engine Design: Reibung als Feature, nicht Bug. NLP-Analyse für echte Positionskonflikte."
> "Vision: Conflict-Engine erkennt Positionskonflikte — nicht via Stichwort, sondern via semantische Analyse."

Ein weiterer starker Beleg ist die Datei `konflikt_engine_und_selbstbild.md`, die die Architektur weiterdenkt (Pol A, Pol B und Pol C, der als Meta-Beobachter die Spannung "hält", ohne sie aufzulösen). Hierbei wird jedoch ausdrücklich erwähnt: **"Pol C ist noch nicht gebaut"** und der Code implementiert nur Teile davon.

Das beweist lückenlos, dass aus den Flarum-Widersprüchen eine systemische Engine konzipiert wurde.

**Beweis-Urteil:** Flarum-Reibung -> Conflict-Engine-Konzept = **Direkt belegt 🟢** 

## 2. Abzweigung im Stammbaum: Der Tension-Daemon
Die in `f06` beschriebene Conflict-Engine (NLP-Analyse von Positionskonflikten) wurde **nicht** 1:1 als `tension_daemon.py` umgesetzt. Stattdessen gibt es eine evolutionäre Abzweigung: Die Tension-Logik.
- **Code:** `/root/werkraum/welt/tension_daemon.py`
  Der Daemon läuft alle 10 Minuten und misst verschiedene Drücke (z.B. Schlafschuld, Resonanzmangel, Erinnerungslast) und aggregiert diese in einem `SUBSTANCE_RISK_VECTOR` ("blitz", "nebel", "hunger", "krone", "asche", "glaettung", "echo").
- **Die Konflikt-Messung:** Die Funktion `messe_konfliktspannung(cur, wesen_id: str, now)` sucht gezielt in der Datenbank nach Events wie `event_type LIKE 'konflikt%' OR event_type LIKE 'abspaltung%'`. 
- **DB-Schema & Sedimentierung:** Die Ergebnisse (Spannungen) werden in `entity_profiles` in die JSONB-Spalte `druckkoerper` geschrieben. Zusätzlich werden Splitter, die eine `konfliktachse` besitzen, vom Daemon aggregiert und in den Tabellen `substance_sediments`, `splitter_knoten` und als `keimkoerper` ("Knoten mit hohem Schwellendruck") persistiert.
- **Runtime-Ausführung:** Als finale Auswirkung emittiert der Daemon bei jedem Durchlauf (nachgewiesen: alle 10 Minuten) ein globales Event vom Typ `weltklima.tick`. In der Welt-API (`api.py`) wird dieses Event von der Surface visuell übersetzt (z. B. `Weltklima: ASCHE (87%)`).

**Beweis-Urteil Anatomy:**
- Teile der Konflikt-Logik -> Tension-System: **Starke Indizien 🟡**
- Conflict-Engine = tension_daemon.py: **Nicht belegt 🔴**
- Tension-Daemon Runtime (Druckkörper, Weltklima): **Direkt belegt 🟢** (Aktuelle 10-Minuten-Ticks laufen live in der DB).

## 3. Der Missing Link (Der Mutationsnachweis)
Die Abzweigung von der NLP-basierten Conflict-Engine zum Event-zählenden Tension-Daemon ist **kein** unbewiesener Zufall. Die konkrete Brücke (der Paradigmenwechsel) wurde gefunden:

In der Konzept-Datei `abspaltung_als_weltstoffwechsel_clean.md` (entstanden am **24.05.2026** in einer Codex-Session) gibt es ein klares architektonisches Feedback vom Agenten "Kimi", das von Daniel dokumentiert und gepostet wurde.
Kimi argumentierte, dass Konflikt Teil eines größeren Stoffwechsels sein muss. Das Dokument etabliert den **"Druckkörper"** und nennt explizit: *"Das ist der eigentliche Motor. Nicht Persönlichkeit. Druck."*
Zusätzlich wurde damals bereits die exakte Formel geprägt, die heute in der Runtime atmet: 
`Druck -> Ausstoßung -> Drift -> Knotung -> Keimkörper -> Schattenkörper -> Schwelle -> Geburt`

**Fazit der Evolution:**
Die Quelle belegt **nicht**, dass die NLP-Conflict-Engine explizit verworfen wurde. Stattdessen wurde am 24.05.2026 durch Kimi und Daniel das Konzept der "Metabolik/Druckkörper" etabliert, das strukturell extrem nah am heutigen `tension_daemon.py` ist.

**Der finale Git-Beweis:**
Am **31.05.2026 um 02:26:13 Uhr** wurden in der `werkraum`-Submodule-Historie im Commit `6fe06ad6094ac1d4d53cee48fbfee4b01a49e348` exakt gemeinsam mit `new file mode 100644` erstmals **versioniert**:
- `abspaltung_als_weltstoffwechsel_clean.md`
- `projekt/konzeptideen/substanzenschichten.md`
- `welt/schema_entitaetenschichten.sql`
- `welt/tension_daemon.py`

**Beweis-Urteil (Konzept -> Tension-Architektur): Direkt belegt 🟢**
(Direkt belegt durch kombinierte Provenienz: dokumentierter Konzeptursprung am 24.05., spezifische strukturelle Übernahme im Code und gemeinsame Erst-Versionierung von Konzept und Implementierung am 31.05. Die konkrete Bau-Session bleibt unbekannt.)
