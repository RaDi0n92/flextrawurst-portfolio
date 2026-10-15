# Code-Archäologie-Tab: Dropdown, Suchbox, Live-Update, dynamische Datei-Erkennung

Entstanden am 17.08.2026, direkt im Anschluss an den Reibungsgewebe-Bau
(`57_reibungsgewebe.md`), in derselben Session. Reine Faktenchronik.

---

## Ursprung

Daniel bemerkte beim Draufschauen auf den bestehenden CODE-ARCHÄOLOGIE-Tab, dass die
Zahlen veraltet wirkten ("das erste wo bisher nur 5 einträge sind — wohl nicht
aktualisiert"). Geprüft: der Tab ist server-seitig zum Build-Zeitpunkt vorgebacken (SSR,
`generateCodeArchaeologieFeedSSR()`), ohne Live-Update-Mechanismus — ein offener Tab zeigt
den Stand vom letzten Build, bis die Seite neu geladen wird. Kein Bug, aber eine echte
Lücke gegenüber Grundgesetz 8 ("Live statt F5").

Daniel direkt danach: "wir müssen eine ui schaffen die sobald ne neue md da ist dese
filterbar macht per dropdown sie indexiert un verlinkt und auch ne suchbox haben und jede
md muss zu öffnen sein und lesbar komplett (aber es werden ja sobald wir dakgord verlassen
ja viel mehr mds)".

## Vorgefunden, schon fertig

Beim genaueren Hinsehen war ein Teil davon bereits gebaut, nur nicht sichtbar gemacht:
- Backend-Endpunkt `/code-archaeologie/eintraege` unterstützt schon `datei`- und
  `search`-Query-Parameter, liest alle Dateien live von der Platte (kein Cache).
- Ein `roh=true`-Modus liefert den kompletten Originaltext einer Datei unverarbeitet, für
  ein Popup (`caRohdateiOeffnen`) — "jede MD muss zu öffnen sein und lesbar komplett" war
  also schon erfüllt, nur ohne UI-Zugang außer den fest verlinkten Datei-Buttons unten.

Was fehlte: kein Dropdown, keine Suchbox im Frontend, keine Live-Registrierung, und die
Dateiliste selbst (`CODE_ARCHAEOLOGIE_DATEIEN`) war eine fest codierte 4-Einträge-Liste —
"sobald ne neue MD da ist" hätte bedeutet, dass jemand diese Liste von Hand pflegt.

## Gebaut

### 1. Dynamische Datei-Erkennung (`welt/api.py`)

`_code_archaeologie_dateien_dynamisch()`: die vier bekannten Dateien behalten ihre feste
Reihenfolge/Titel/Beschreibung (Daniels explizite output-wortlaut-zuerst-Entscheidung
bleibt unangetastet), zusätzlich wird `docs/code_archaeologie*.md` per Glob durchsucht —
jede neue, nicht gelistete Datei wird automatisch mit Titel aus dem Dateinamen angehängt.

**Sofort real bestätigt, nicht nur behauptet:** beim ersten Testlauf tauchte tatsächlich
eine bisher unbekannte fünfte Datei auf — `code_archaeologie_datei_1_bis_6_uebersicht.md`
— die nie in der alten Handliste stand.

Offen gelassen, bewusst nicht entschieden: sobald ein Systemwechsel weg von
`dak_gord_system` passiert, ist unklar ob künftige Archäologie-Dateien denselben
`code_archaeologie`-Präfix behalten. Das Glob-Muster müsste dann nachgezogen werden.

### 2. Live-Watcher (`welt/api.py`)

`_codearchaeologie_watcher_loop()`, 1:1 nach dem Muster des bestehenden
Guardianstyle-Watchers: mtime-Polling alle 5s über alle erkannten Dateien, bei Änderung
ein `INSERT INTO events (event_type='system.codearchaeologie_update')` — läuft über den
bestehenden `events_stream`-Kanal, kein neuer Dienst.

### 3. Dropdown + Suchbox (`scripts/build_surface.ts`)

`<select id="ca-dateifilter">` (baut sich bei jedem Laden aus der Server-Antwort neu auf,
nicht aus einer festen Liste — genau deshalb tauchen neue Dateien automatisch auf) und
`<input id="ca-search">` (debounced, 350ms). Beide hängen an `codeArchLaden()`, das jetzt
`datei`/`search` als Query-Parameter mitschickt. `ftwLiveRegistrieren('system.codearchaeologie', ...)`
lädt automatisch neu, wenn der Tab offen ist und sich eine Datei ändert.

## Getestet — mit Belegen, nicht nur behauptet

Nach Daniels berechtigter Nachfrage von vorhin ("echt getestet oder mit playwright in den
stein gemeisselt") diesmal von Anfang an beides: 4 neue dauerhafte Tests in
`tests/surface_ring_23.test.ts` (Dropdown/Suchbox im DOM, dynamischer Dropdown-Aufbau,
Debounce-Verdrahtung, i18n-Symmetrie) — 103/103 Tests grün. Zusätzlich Playwright-Lauf mit
echten Daten: Dropdown zeigt alle 5 (jetzt real erkannten) Dateien, Suche nach "Vision 4"
liefert den echten Treffer aus der Code-Archäologie-Historiendoku, keine Konsolenfehler.

## Was noch fehlt

- Keine automatische Migration falls künftige Systeme einen anderen Datei-Präfix als
  `code_archaeologie_` verwenden (siehe Leerstelle oben) — müsste beim nächsten
  Systemwechsel neu entschieden werden, nicht vorab geraten.
- "Indexiert und verlinkt" ist bisher nur als Dropdown + Rohdatei-Links umgesetzt, kein
  eigenes Inhaltsverzeichnis pro Datei (z.B. Sprung zu einer einzelnen "Datei N" ohne erst
  zu scrollen) — nicht verlangt, aber eine mögliche nächste Ausbaustufe.
