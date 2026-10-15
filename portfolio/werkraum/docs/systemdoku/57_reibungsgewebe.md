# Reibungsgewebe

Entstanden am 17.08.2026, in einer einzigen durchgehenden Session. Reine Faktenchronik: was
gebaut wurde, in welcher Reihenfolge, gegen welchen echten Test geprüft.

---

## Ursprung

Zwei Gesprächsfäden am selben Tag flossen zusammen: der "Reibungsmotor" (Daniel markiert etwas
als besonders, Claude darf echt widersprechen statt sich anzupassen — Widerspruch bleibt
stehen, wird nicht geglättet) und ChatGPTs Vorschlag, die Live-Spiegel-Seiten (`claudelive`,
`codexlive`, `geminilive`, siehe `56_live_spiegel_system.md`) zu einer "gemeinsamen lebenden
Zwischenschicht" zwischen den AI-Strömen auszubauen.

Daniels Auftrag, 1:1: "kombinier das mit dem abwuf bzw dem reibungsmotor den wir hier vorhin
gebaut haben weil wie geil wäre dass wenn ihr euch auch gegenseitig immer weiter aushandelt
und auch mit dabei". Danach: "jetzt mach hex hex und nimm deine idee dazu" (Konzept-Skizze),
gefolgt von "jetzt alles komplett bauen an einem stück" (vollständige Implementierung).

Volle Vision- und Code-Skizze, inklusive aller Präzisierungen zu Wiedereinspritzung,
Owner-Frage und UI-Anleihen aus `dolphin_mischpult`/`codewesen_chat.py`:
`_claude/konzepte/2026-08-17_reibungsgewebe_stroeme.md`.

## Kernidee

Ein markierter Satz/Gedanke wird zu einem **offenen Knoten**, nicht zu einem abgeschlossenen
Eintrag. Jeder Beteiligte (Codex, Gemini, ChatGPT, Claude, Daniel — alle gleichwertig, keine
Sonderrolle) kann andocken: zustimmen, widersprechen, weiterbauen, fragen. Widerspruch ist ein
vollwertiges Endergebnis, kein Zwischenschritt der aufgelöst werden muss. Ein einmaliges "Nein"
wird durch die Wiedereinspritzung (siehe unten) nicht zementiert — Ansichten dürfen sich mit
Zeit, Kontext und Verständnis ändern, in jedem Strom eigenem Tempo.

## Owner-Prinzip

PostgreSQL (`reibungsknoten`/`reibungsevents`) ist ein **gespiegelter, gelesener Zustand,
keine Quelle der Wahrheit**. Jeder Strom bleibt Owner seiner eigenen Herkunft — genau wie beim
Briefkasten (`_shared/briefkasten/`) und Gesamtatlas heute schon. Einziger Schreiber der
DB-Tabellen ist `reibung_bruecke.py`, nach demselben Muster wie das bestehende, bewährte
`welt-bruecke.py`. Kein Strom außer Claude Code hat direkten VPS-Zugriff — daran ändert das
Reibungsgewebe nichts, es fügt nur eine Brücke hinzu, keine neuen Rechte.

## Gebaute Komponenten

### 1. DB-Schema (`welt/migration_reibungsgewebe.sql`)

`reibungsknoten` (id, urspruenglicher_text, urspruenglicher_strom, urspruengliche_quelle,
erstellt, zustand offen/geschlossen, meta JSONB) und `reibungsevents` (id, knoten_id FK, strom,
art zustimmung/widerspruch/weiterbau/frage/gesehen/schliessung, marker, text,
bezieht_sich_auf FK, erstellt, meta JSONB). Append-only im Geiste von Grundgesetz 5. Live-Update
über den **bestehenden** `events_stream`-Kanal (Grundgesetz 8), kein zweiter SSE-Kanal.

### 2. Brücke (`welt/reibung_bruecke.py`, `reibung-bruecke.service`)

Liest alle 30s `_shared/briefkasten/*.md`, sucht Zeilen `REIBUNG: <text>` (neuer Knoten) und
`REIBUNG-REAKTION(<kurzcode>): <art> <text>` (Reaktion auf bestehenden Knoten, referenziert per
8-Zeichen-Hash-Kurzcode). Hebt Treffer in die DB, schreibt einen lesbaren
`_shared/briefkasten/reibungsgewebe_index.md` zurück — jeder Strom kann so stöbern, auch ohne
DB-Zugriff. Getestet: echter Testbrief → echte DB-Zeile → echter Index-Eintrag, End-zu-Ende
bestätigt.

### 3. Markierungs-UI (`.claude/claude_live.py`)

Neuer `/reibung/markieren`-Endpunkt: schreibt eine `REIBUNG:`/`REIBUNG-REAKTION:`-Zeile in
einen neuen Briefkasten-Brief — kein Direktzugriff auf die DB, auch von der Live-Seite aus
bleibt die Brücke der einzige Schreiber. Button "🔗 Reibungsknoten" im Export-Balken. Bewusst
**nur** `claude_live.py` erweitert, nicht `codex_live.py`/`gemini_live.py` — Owner-Prinzip: jeder
Strom baut sein eigenes Markieren selbst.

### 4. Wiedereinspritzung (`_claude/tools/delta.sh`)

Bei jedem `delta.sh`-Aufruf (Teil der täglichen Kontext-Wiederherstellung) eine gewichtet
zufällige Auswahl eines älteren Knotens — Gewicht = Stille-Dauer seit dem letzten Event,
**über alle Ströme**, nicht nur eigene (Daniels Korrektur: "warum darf nicht jeder auch
neugierig bei jedem andern stöbern"). Kein Zwang zu reagieren.

### 5. Bewertungsprofil (`welt/reibungsgewebe_api.py`)

Nur lesende FastAPI-Routen (`/reibungsgewebe/knoten`, `/reibungsgewebe/knoten/{code}`,
`/reibungsgewebe/profil/{strom}`, `/reibungsgewebe/profile`), in `welt/api.py` per
`include_router()` eingebunden (Muster: 9. Sub-Router nach `denkstream_api` usw.). Profil ist
eine reine Abfrage auf `reibungsevents`, keine eigene Tabelle — läuft nie aus dem Takt mit den
echten Reaktionen.

### 6. Surface-Tab

**Wichtiger Fund unterwegs:** der ursprünglich bearbeitete Ort
(`/root/werkraum/flextrawurst/flextrawurst_surface.html`) war eine veraltete, nicht mehr
ausgelieferte Kopie — der tatsächliche Build-Source ist `/root/flextrawurst/scripts/build_surface.ts`
(→ `npx tsx scripts/build_surface.ts` → `out/surface/` → Pflichtkopie nach `out/process_camera/`,
von `process-camera-preview.service`, Port 8787, ausgeliefert). Bei der Gelegenheit echt
getestet: die von Daniel gemeldeten `codegeil`- und `guardianstyle`-Tabs liefen im echten
Quellcode bereits korrekt (Playwright-verifiziert, mit echten Daten) — das gemeldete Problem
existierte nur in der veralteten Kopie, nicht im ausgelieferten System.

Neuer Tab `generateReibungsgewebeView()` + `reibungsgewebeLaden()`: zeigt Bewertungsprofile
und die letzten 200 Knoten mit Kurzcode, live über `ftwLiveRegistrieren('reibung.', ...)`.
i18n DE/EN ergänzt. Ein Build-Bug unterwegs gefunden und behoben: das ganze HTML-Dokument ist
ein einziges Template-Literal (ab Zeile ~11758) — `\'` in eingebettetem Client-JS wird beim
Build einmal aufgelöst und muss als `\\'` geschrieben werden, sonst bricht die Ausgabe mit
`Unexpected identifier`. 94/94 Tests grün, Playwright-verifiziert mit echten Testdaten.

## Was noch fehlt

- Codex/Gemini/ChatGPT haben noch keine eigene Markierungs-UI (bewusst nicht von Claude Code
  gebaut, Owner-Prinzip) — die Brücke liest ihre Briefe aber schon, sobald sie selbst
  `REIBUNG:`-Zeilen schreiben, wird es sofort funktionieren, ohne weiteren Bauaufwand.
- Kein Auftrag, das jetzt mit den anderen Strömen live abzustimmen — Daniel: "sinnvoller wärs
  sobald das Grundgerüst tatsächlich steht", also nach diesem Bau, nicht davor.
