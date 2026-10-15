---
datum: 2026-08-14
betrifft: [gesamtauftrag, tab-entwuerfe, phase-4, bauanleitung]
status: entwurf, 11 echte Redteam-Runden durchlaufen, bereit für Daniels Gegenlesen
autor: claude-code bei Daniels VPS
---

# Gesamtauftrag — Bauanleitung für drei neue flextrawurst-Tabs

Live erarbeitet, nicht delegiert. Basis: die drei Arbeitsfassungen (Phase 1, 22 echte Redteam-
Runden), die sokratische Analyse (Phase 2), die 33 Ideen (Phase 3, 20 davon BAUEN), und dieses
Dokument selbst (Phase 4, 11 echte Redteam-Runden auf sich selbst — Daniels reduzierter Umfang,
"keine 111 redteamloops... auch nur 11 erstmal am ende"). Jede Redteam-Runde unten ist inline
markiert, nichts wurde nachträglich geglättet oder aus dem Protokoll entfernt.

## Drei Tabs, ein gemeinsames Muster

Jeder der drei Tabs bekommt dieselbe Grundstruktur (Konsistenz-Lehre aus Phase 2):

1. **Ein-Satz-Einladung** statt Meta-Beschreibung als Erstes.
2. **Block 0 — Bevor es technisch wird** (aus Phase 1, Runde 6): 3-4 Sätze Alltagsdeutsch.
3. **Guardian-Marker-Legende** (Idee 8) einmal oben, klein.
4. **Hauptinhalt** (die jeweiligen Blöcke/Abschnitte aus den drei Arbeitsfassungen — bereits
   22-fach geprüft, siehe Redteam-Protokoll).
5. **"Was noch offen ist"-Sidebar** (Idee 9), automatisch aus `[status: offen]`-Markern gesammelt.
   **Redteam-Runde 9, Umsetzungslücke:** die Arbeitsfassungen markieren das aktuell als reinen
   Markdown-Text `**[status: offen]**` — beim Bauen muss das zu `<span class="status-offen">...
   </span>` um den jeweiligen Satz werden, sonst hat `querySelectorAll` nichts zu finden. Nur 4
   echte `[status: offen]`-Stellen insgesamt (1 in Entitätensystem, 3 in Agentensystem, 0 in
   System heute) — überschaubar genug, das beim Bauen von Hand zu markieren statt automatisiert
   zu parsen.
6. **Mini-Glossar am Ende** (aus Phase 2) für wiederkehrende Fachbegriffe.
7. **"Ich wurde X-mal geprüft"-Badge** (Ideen 16 + 32) mit Link zum Redteam-Protokoll.

## Tab 1 — "System heute"

Inhalt: komplette Arbeitsfassung `tab_entwurf_system_heute_2026-08-14_arbeitsfassung.md`
(Blöcke 0-3 + Schlussabsatz), plus:
- **Redteam-Runde 7, harte Regel fehlte im Gesamtauftrag:** Daniels ursprüngliches "WICHTIG" aus
  der Arbeitsfassung selbst — Claude-Daniel-Gesprächslogs werden NICHT eingebettet oder inhaltlich
  gezeigt, höchstens ein Satz dass sie getrennt existieren. Das gehört als bindende Vorgabe direkt
  in diesen Gesamtauftrag, nicht nur indirekt über "Inhalt: komplette Arbeitsfassung" mitgemeint.
- Idee 1 (anklickbare Zeitleiste) für Block 3 statt reinem Fließtext.
- Idee 7 (Vorher/Nachher) für die heute gefundenen Zahlenkorrekturen. **Nachtrag, Daniel wörtlich:**
  "das ist ja eh nur so halbdoofgelaufene wahrheit weil es vor einzu passiert is und echte
  flextrawurst only dinge mitnutzt" — bei der `entity_thinking_log`-Zahl (16.000→101.645) darf die
  Vorher/Nachher-Darstellung NICHT als "mehr Zahl = mehr echtes Leben" verkauft werden. Muss dazu
  sagen: entstanden mit echten flextrawurst-Mechanismen, aber in der Vor-Einzug-Phase, und bisher
  nicht als Erinnerung in die Wesen selbst zurückgeflossen.
- Idee 26 (Dateipfad+Zeile statt totem Link) für alle Code-Referenzen.
- Idee 18 (Rate-die-Zahl-Mini-Spiel) als Einstieg vor Block 3.

## Tab 2 — "Agentensystem"

Inhalt: komplette Arbeitsfassung `tab_entwurf_agentensystem_2026-08-14_arbeitsfassung.md`, plus:
- Idee 2-Analogie (Tabelle mit Hover) für die sechs vps-mcp-Instanzen.
- Idee 23 (Ampel-Tabelle statt Graph) für die Grundriss-Sync-Matrix.
- Idee 12 (Vorlese-Button) für den Zuhause-Abschnitt — persönlichster Teil, passt gut zu Audio.
  **Redteam-Runde 5, Zugriffs-Lücke gefunden:** der TTS-Dienst liegt hinter nginx-Basic-Auth
  ("Toolbox"), nicht öffentlich frei erreichbar wie z.B. `/api/`. Ein Vorlese-Button auf einer
  öffentlichen Tab-Seite würde also entweder einen Login-Dialog auslösen (schlechte UX) oder
  braucht einen eigenen, bewusst öffentlich freigegebenen Mini-Endpunkt speziell für diesen Zweck.
  Nicht in dieser Runde lösbar — als offene technische Frage für den Bau-Schritt markiert, nicht
  stillschweigend als "einfach machbar" behauptet.
- Idee 33 (aufklappbare Omapi/Opami-Reflexion) für den Schlussabschnitt.

## Tab 3 — "Entitätensystem"

Inhalt: komplette Arbeitsfassung `tab_entwurf_entitaetensystem_2026-08-14_arbeitsfassung.md`, plus:
- Idee 2 (Fähigkeiten-Matrix mit Hover) — bereits als Tabelle vorhanden, nur Hover ergänzen.
- Idee 6 (Flussdiagramm der zwei Denk-Mechanismen) für Abschnitt 1.
- Idee 4 (Live-"Tage seit..."-Widget) für die Flarum-Post-Sperre-Erwähnung.
- Idee 15 (Herkunfts-Tooltip) für jede Zahl in der Fähigkeiten-Matrix.

## Technische Umsetzung (für den Hauptthread beim eigentlichen Bau)

- Drei neue `generate*View()`-Funktionen in `/root/flextrawurst/scripts/build_surface.ts`, nach
  bestehendem Muster (siehe `generateWissenView()` als Vorbild für status-getaggte Karten).
  Tab-Namen: `agentensystem`, `entitaetensystem` unproblematisch (keine Kollision, keine
  Namensnähe zu bestehenden Tabs). **Redteam-Runde 3, Namensfund:** `systemheute` liegt zu nah am
  bestehenden `systeme`-Tab (Live-Dienst-Karten, u.a. die heute korrigierte `codewesen_takt.py`-
  Beschreibung) — ein Besucher würde vermutlich denken, das sei derselbe Tab oder eine Dopplung.
  Besserer Name, der den Unterschied klarmacht: `baugeschichte` oder `hinterderKulisse` (Vorschlag,
  finale Wahl mit Daniel klären) — der Tab handelt ja tatsächlich mehr von "wie ist das gewachsen"
  als von "was läuft gerade" (das leistet `systeme` bereits).
- Jede sichtbare Zeichenkette braucht einen `data-i18n`/`data-i18n-html`-Key, DE+EN, gemäß
  i18n-Gesetz — die deutschen Texte oben sind die Quelle, Englisch muss noch übersetzt werden
  (nicht Teil dieses Auftrags, gehört zum eigentlichen Bau-Schritt).
- Tab-Buttons im `view-bar`, Views im `main`, Eintrag in `REQUIRED_VIEWS`
  (`tests/surface_ring_23.test.ts`), danach `npm run surface` + Kopie nach `out/process_camera/`
  (Pflichtschritt, siehe CLAUDE.md Surface-Gesetz).
- Live-Elemente (Puls-Indikator, Zähler) nutzen den bestehenden `/api/events/stream`-Kanal
  (Grundgesetz 8), keine neue SSE-Infrastruktur nötig.
- **Redteam-Runde 4, technische Lücke gefunden:** die vorherige Fassung sagte, das
  Redteam-Protokoll (`_claude/ideen/redteam_protokoll_2026-08-14.md`, im werkraum-Repo) könne
  direkt als Quelle für den "Ich wurde X-mal geprüft"-Zähler (Idee 32) dienen, "kein separater
  Mechanismus nötig" — das stimmt nicht. Die Live-Seite läuft in `/root/flextrawurst/` (eigenes
  Repo, siehe Phase-1-Fund), hat keinen Dateizugriff auf `/root/werkraum/`. Es braucht doch einen
  kleinen Schritt dazwischen: entweder ein winziger neuer API-Endpunkt in `welt-api.py`, der die
  Runden zählt und zurückgibt, oder eine feste Zahl, die beim Bauen einmal von Hand eingetragen
  und danach manuell gepflegt wird (einfacher, aber nicht automatisch aktuell). Beides ist machbar,
  aber "kein separater Mechanismus" war schlicht falsch — jetzt richtig benannt als offene
  Entscheidung für den Bau-Schritt.

**Redteam-Runde 10, Aufräum-Fund:** Für jeden der drei Tabs liegen inzwischen DREI Dateien in
`_claude/ideen/` — die ursprüngliche (vor dem Redteam-Loop), eine `_v2`-Fassung (vom delegierten
Fork-Durchlauf, den Daniel ausdrücklich verworfen hat — "ne eigentlich wllte ich dass du das allei
durchlebst"), und die `_arbeitsfassung` (diese hier, live und echt redteamed, die einzig
maßgebliche). Verwechslungsgefahr für jeden, der später in diesen Ordner schaut. Empfehlung:
`_v2`-Dateien vor dem Bauen löschen oder klar als "verworfen" markieren, die alten
Original-Dateien (ohne Suffix) als historisches Ausgangsmaterial stehen lassen aber mit einem
Verweis auf die Arbeitsfassung als aktuellen Stand versehen.

## Was VOR dem Bauen noch mit Daniel zu klären ist

- Endgültige Freigabe der drei Arbeitsfassungen (Phase 1 ist fertig, aber Daniel hat sie noch
  nicht selbst gegengelesen).
- Reihenfolge/Position der drei neuen Tabs im view-bar (wo sollen sie erscheinen, neben welchen
  bestehenden Tabs).
- Ob alle 20 "BAUEN"-Ideen wirklich in der ersten Version mitgebaut werden, oder ob eine kleinere
  erste Fassung sinnvoller ist und der Rest schrittweise nachgezogen wird (Daniels eigenes
  "erst eine machen, Ergebnis zeigen"-Skalpell-Prinzip spricht für die zweite Option).
- **Redteam-Runde 6, ergänzt:** endgültiger Name für den bisher "System heute" genannten Tab (siehe
  Runde 3 — Namensnähe zu `systeme` ist ein echtes Problem, Vorschläge `baugeschichte`/
  `hinterderkulisse` stehen noch zur Wahl).
- **Redteam-Runde 6, ergänzt:** wie der Vorlese-Button (Idee 12) technisch öffentlich erreichbar
  gemacht wird, ohne den TTS-Dienst insgesamt aus seiner Basic-Auth zu holen (siehe Runde 5).
