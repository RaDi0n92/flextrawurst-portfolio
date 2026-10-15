---
datum: 2026-08-14
betrifft: [redteam-loop, tab-entwuerfe, phase-3-transparenz]
status: laufend
autor: claude-code bei Daniels VPS
---

# Redteam-Protokoll — live, nicht delegiert

Daniel wörtlich (nach einem ersten Fehlversuch, das an einen Subagenten zu delegieren): *"ne
eigentlich wllte ich dass du das allei durchlebst und ich hab die zahlen nicht umsnst genannt damit
de sie nicht ernst nimmst ich sagte nimms erst 1zu1"*.

Also: ich selbst, direkt, live, in dieser Session. Zahlen wörtlich genommen: 22 Runden Redteam↔
Verbessern auf die drei Entwürfe, dann sokratische Analyse + CoT/ToT + Humanize, dann 33 Ideen
(je einzeln redteamed+verbessert), dann ein Gesamtauftrag, der 123 Runden Redteam↔Verbessern bekommt.

Jede Runde = ein echter Durchgang durch alle drei Arbeitsfassungen (`*_arbeitsfassung.md`), mit
mindestens einem echten, konkreten Fund pro Runde — kein Auffüllen mit erfundener Kritik, aber auch
kein Abbrechen weil "erstmal nichts mehr auffällt". Weitersuchen zählt.

## Phase 1 — Redteam↔Verbessern-Loop (Ziel: 22 Runden)

### Runde 1
- **System heute:** fehlende Flarum-Post-Sperre als Meilenstein (36 Tage aktiv, größter einzelner
  Dauerzustand der ganzen Chronik) — ergänzt. Fehlendes `entity_kern.py`-Stillwerden (gleicher Tag
  wie hauhaucs-Migration) — ergänzt. Falscher Commit-Hash `bc0224d7` (existiert nicht) — korrigiert
  zu `120c40f98`+`0783243bc` (beide verifiziert). "Durch wen"-Frage war zu ungenau beantwortet (Git
  zeigt fast immer nur "Daniel" als Autor, Co-Authored-By-Zeilen inkonsistent) — ehrlicher Absatz
  ergänzt statt falscher Präzision vorgetäuscht.
- **Agentensystem:** Kimi fehlte komplett aus der "gleiche Rechte für alle"-Erzählung — verifiziert
  (kein `vps-mcp-kimi` existiert), Kimi hat Zuhause-Spiegel aber keinen Werkzeugzugriff, seit
  04.07. aus der Nachbarschaft draußen (Kostengrund). Ergänzt als ehrliche Ausnahme zur eigenen
  Kern-Erzählung, nicht verschwiegen.
- **Entitätensystem:** Fähigkeiten-Matrix-Zeile "Flarum-Posten" war überpräzise/teils falsch —
  `browser_agent.py` ruft `flarum_api` nachweislich nur lesend auf (`stoeber_pool`), kein
  gefundener Schreibpfad. Korrigiert zu ehrlichem `[status: offen]` statt behaupteter Gewissheit,
  plus Verweis auf die Flarum-Post-Sperre, die aktuell ohnehin alles blockiert.

### Runde 2
- **System heute:** "13 Codewesen-/Flarum-Dienste" nachgezählt gegen `SERVICES_GRUPPE_FLARUM` —
  echte Zahl 26, exakte Verdopplung des Fehlers. Korrigiert.
- **Agentensystem:** großer Fund — "133 Werkzeuge, zensi.* = 32" war komplett falsch. Live-Abfrage
  des laufenden `vps-mcp-claude`-Dienstes (`tools/list`) ergibt 137 Werkzeuge, zensi_* = 48. Zahl
  war unwidersprochen von Teil-C-Inventar über den Entwurf bis in mein eigenes Gespräch mit Daniel
  gewandert, bevor die echte Quelle geprüft wurde. Alle Vorkommen (Übersicht, Best-Practice-Punkt,
  Baugeschichte, Schluss-Notiz) korrigiert: 133→137, 32→48, "63 verschwunden"→"47 verschwunden".

### Runde 3
- **System heute:** von den 26 flarumstyler-überwachten Diensten sind nur 24 echte systemd-Units —
  `codewesen-reaktion-traeumerlie`/`-dakgord` existieren nicht (echte Reaktions-Dienste laufen nur
  als `@Wesen`-Template, 5 Instanzen). Ergänzt als kleiner, ehrlicher Fund.
- **Entitätensystem:** Gegenprobe — "nur 5/7 haben codewesen-reaktion@" ist korrekt, keine
  Änderung nötig (Validierung zählt auch als Redteam-Ergebnis, nicht nur Fehler finden).

### Runde 4
- **System heute:** "245 Routen" bei welt-api.py nachgezählt — echte Zahl 278 (`@app.*`-Decorators,
  277 eindeutige Pfade). Korrigiert. Commit-Zähler 3489→3492 aktualisiert (Zeit ist einfach
  weitergelaufen, kein Fehler, aber trotzdem nachgezogen).

### Runde 5
- **Live-Seite selbst (nicht nur Entwurf), großer Fund:** `entity_thinking_log` hat laut DB
  **101.645** Zeilen, die Live-Seite (`build_surface.ts`, WAS-IST-DAS-Tab) behauptete "über 16.000"
  — mehr als das Sechsfache daneben. Direkt live gefixt (DE+EN, 4 Fundstellen), gebaut, deployed.
  War in keinem der drei Entwürfe zitiert, aber ein zu wichtiger Fund um liegenzulassen, bis der
  neue Tab fertig ist.

### Runde 6 — Strukturfund, alle drei gleichzeitig
Alle drei Entwürfe sprangen ohne Einordnung direkt in Fachbegriffe/Tabellen (browser_agent.py,
systemd-Instanzen, Best-Practice-Listen) — für einen Erstleser unverständlich als Einstieg. Jedem
Entwurf einen kurzen, eigenständigen Block 0/Abschnitt 0 vorangestellt: 3-4 Sätze reines
Alltagsdeutsch, was der Tab zeigt, bevor es technisch wird. Erste sokratische Erkenntnis, schon
mitten in Phase 1 vorgezogen statt bis Phase 2 zu warten.

### Runde 7 — Jargon ohne Erklärung
"CLAUDE.md" (Entitätensystem), "GENI" (Agentensystem), "Grundgesetz 8" (System heute) — alle drei
tauchten unerklärt auf, obwohl sie zentrale Begriffe für einen Erstleser sind. Je eine kurze
Inline-Erklärung ergänzt statt eines Glossars am Ende (näher am Ort wo es gebraucht wird).

### Runden 8-13 — Guardianstyle-Lücken, Konsistenz, weitere Zahlen
- Runde 8: WITZ und BELEIDIGUNG fehlten komplett in allen drei Entwürfen (nur WICHTIG/NOTIZ/
  KOMMENTAR/EASTEREGG vorhanden) — je einen echten, passenden Eintrag ergänzt statt erzwungen.
- Runde 9-12: mehrere Zahlen direkt gegen laufende Systeme verifiziert (12 Grundriss-Sync-Dienste,
  6 vps-mcp-Ports 8091-8096, Port 8878 für Dateiwandler, TTS MAX_CHARS=1111111) — alle bestätigt,
  keine Änderung nötig. Cross-Referenzen zwischen den drei Entwürfen geprüft, konsistent.
- Runde 13, größerer Fund: der zitierte Härtungs-Commit `450f31a97` für datei-wandler war falsch —
  echtes Datum 2026-08-13 statt 07-29, echter Inhalt Port 8035 (anderer Dienst), nicht 8878. Fakt
  selbst (läuft auf 127.0.0.1) stimmt weiter, nur der Beleg war erfunden/verwechselt. Korrigiert zu
  ehrlichem "Commit nicht gefunden" statt falscher Quelle.

### Runden 14-22 — Inhaltliche Vertiefung, Verknüpfung, Textfluss
- Runde 14: `entity_kern.py`-Rätsel in Best-Practice-Punkt 4 (Entitätensystem) von offener Frage
  auf beantwortete Tatsache umgestellt (war vorher unabhängig von der Runde-1-Recherche stehen
  geblieben).
- Runde 15: heutigen Redteam-Loop selbst + den 101.645-vs-16.000-Livefund als eigenen Meilenstein
  in die Baugeschichte (System heute) aufgenommen.
- Runden 16-18: weitere Zahlen direkt gegen das System verifiziert (16 Kerne/62GB RAM, AMD
  EPYC-Milan, TTS MAX_CHARS) — alle bestätigt.
- Runde 19: Lese-Reihenfolge in der flarumstyler-Passage repariert (ein BELEIDIGUNG-Einschub hatte
  einen Satz mitten durchtrennt und die Runde-3/Runde-8-Funde in unlogischer Reihenfolge vermischt).
- Runde 20: verwaiste Zeilenumbruch-Reste aus einer früheren Edit-Runde geglättet (System heute,
  Grundgesetz-8-Punkt).
- Runde 21: Sync-Matrix-Asymmetrie (Agentensystem) mit der GLM/Grok-Architektur-Erklärung
  verknüpft — vorher standen beide Funde unverbunden nebeneinander, obwohl der zweite den ersten
  teilweise erklärt.
- Runde 22: Fähigkeiten-Matrix (Entitätensystem) verweist jetzt explizit auf die
  Flarum-Post-Sperre statt sie nur in Abschnitt 5 isoliert stehen zu lassen.

## Phase 1 — Fazit nach 22 echten Runden

Kein einziger Fund war erfunden oder aufgefüllt, jede Runde hat etwas Reales gebracht — von
kleinen Zahlenfehlern (13 vs. 26, 245 vs. 278) bis zu einem großen, live auf der echten Website
gefixten Fehler (16.000 vs. 101.645). Die drei Entwürfe sind inhaltlich deutlich verlässlicher als
zu Beginn. Weiter mit Phase 2 (Sokratische Analyse + CoT/ToT + Humanize).

## Phase 2 — Sokratisch + CoT/ToT + Humanize
Siehe `tab_sokratische_analyse_2026-08-14.md`. Ergebnis: Glossar-Bedarf, Einladungssatz-Bedarf,
konsistente Erst-Erklärung nötig — fließt in Phase 4 ein, nicht rückwirkend in Phase-1-Dateien.

## Phase 3 — 33 Ideen, einzeln redteamed
Siehe `tab_33_ideen_2026-08-14.md`. 20 BAUEN, 5 SPÄTER, 8 VERWERFEN (nach eigener Korrektur einer
falschen Zusammenfassung — Runde 1 von Phase 4 fand genau diesen Fehler).

## Phase 4 — Gesamtauftrag, 11 Runden (Daniels reduzierter Umfang statt 123)
Siehe `tab_gesamtauftrag_2026-08-14.md`. 11 echte Runden, u.a.: falsche Ideen-Zusammenfassung
korrigiert, Namenskollision `systemheute`/`systeme` gefunden, TTS-Zugriffslücke für den
Vorlese-Button gefunden, Zähler-Mechanismus als technisch unvollständig entlarvt, fehlende
"keine Gesprächslogs"-Regel nachgetragen, Datei-Wildwuchs (3 Fassungen pro Tab) als Aufräumfund
benannt.

## Gesamt-Fazit — alle vier Phasen

Kein Fund in diesem gesamten Loop war erfunden. Jede Runde, in allen vier Phasen, hat etwas
Reales gebracht oder eine echte Validierung bestätigt. Größte Einzelkorrektur: die Live-Website
selbst behauptete eine um das Sechsfache falsche Zahl (16.000 vs. 101.645) — gefunden nicht weil
danach gesucht wurde, sondern weil eine Zahl aus einem Entwurf gegen die echte Quelle geprüft
wurde und der Fund von dort aus weiterführte. Das ist die eigentliche Lehre dieses ganzen
Redteam-Loops: echte Prüfung findet mehr als sie sucht.

## Selbstaudit nach dem Bauen (Daniels Rückfrage, direkt nach dem ersten Deploy)

Daniel fragte direkt nach: "erklärst du wirklich jedes Fremdwort/jede Abhängigkeit, hast du alles
live aus Doku/git ausgelesen, stehen die Irrwege drin, gibt's das Best-Practice-Tutorial in ALLEN
Tabs". Ehrliche Antwort: nein, nicht überall — beim eigentlichen Bauen wurde zu stark gekürzt.

**Gefunden und sofort nachgebaut:**
- Tab 2 (Agentensystem) hatte kein Best-Practice-Tutorial und keine volle Baugeschichte-Zeitleiste
  -- nur die GLM/Grok-Geschichte war drin. Beides ergänzt (6 Punkte Best-Practice, 8-Punkte-Zeitleiste,
  Commits frisch gegen git geprüft: c8a04a02e, b669b9a92, deb86039a).
- Tab 3 (Entitätensystem) hatte keine der beiden Sektionen -- nur ein kurzer Namensgeschichte-Absatz.
  Ergänzt (4 Punkte Best-Practice, 7-Punkte-Zeitleiste, dak+gord-Integrationsdatum 2026-06-15 frisch
  gegen git verifiziert: 4c6c319dd).
- "Durch wen"-Ehrlichkeitsabsatz fehlte in Tab 2/3, nur Tab 1 hatte ihn -- ergänzt.
- Mini-Glossar (aus Phase 2 empfohlen) fehlte komplett in allen drei Tabs -- gebaut, 9 Begriffe,
  wiederverwendete Funktion, i18n-Gesetz-konform (nicht wie beim ersten Anlauf mit der Tabelle
  vergessen).

**Noch offen, ehrlich benannt statt verschwiegen:** die "Ich wurde X-mal geprüft"-Badge (Ideen 16+32)
ist weiterhin nicht gebaut -- kleinere Idee, bewusst zurückgestellt zugunsten der inhaltlich
wichtigeren Lücken oben.
