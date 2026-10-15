# Systemdokumentation 40: KompOase — Echtdaten-Feed wiederhergestellt + Weltrückfluss implementiert

---
autor: claude-code bei Daniels VPS
datum: 2026-07-29
status: Beide Fixes live verifiziert
---

## 1. Anlass

Direkt im Anschluss an die Port-Härtung (Systemdoku 39): Daniel erinnerte sich, dass KompOase
im "Theater"/Realmodus früher wirklich gemischte, echte Inhalte aus mehreren Quellen zeigte —
ihn selbst, Codex, die Codewesen, dak+gord, GENI — und dass das irgendwann verschwunden war,
sowohl auf der Surface (Port 8787) als auch auf dem eigenständigen KompOase-Server (Port 8900).

## 2. Fund 1 — GENIs `/api/splitter`-Endpunkt lieferte `[]`

`kompoase/server.py` proxy't `/api/splitter` direkt zu `GENI_URL =
"https://localhost:8020/api/splitter"`. Dieser Endpunkt (`geni/dialog.py:
splitter_endpoint()`) las echte GENI-Gedächtnisknoten und wandelte sie in
Splitter-Objekte um — genau der Mechanismus, den Daniel erlebt hatte, weil GENI alles unter
`/root/werkraum` beobachtet und mit einer `quelle`-Markierung versieht (`flarum`→Codewesen,
`daniel`→Daniel, `geni_*`→Resonanz).

**Live gemessen:** von den letzten 5000 GENI-Knoten waren 4999 reines `vps_dateisystem`-Rauschen
(Dateisystem-Beobachter-Events, werden explizit gefiltert). Über die letzten 100.000 Knoten
(Stichprobe alle 50): **100% Rauschen, keine einzige echte Quelle mehr.** Der alte Endpunkt
scannte sequenziell durch genau diese jüngsten ID-Fenster (2000/5000/500 IDs) — bei der
aktuellen Schreibgeschwindigkeit (mehrere AI-Ströme parallel aktiv) sind diese Fenster
inzwischen zu 100% mit Rauschen vollgelaufen, obwohl echte Inhalte weiterhin existieren
(15.788 `flarum`-, 352 `daniel`-, 575 `geni_muster`/`geni_selbst`-Knoten insgesamt), nur zeitlich
viel weiter zurückliegend als die gescannten Fenster reichen.

**Fix:** `splitter_endpoint()` fragt jetzt direkt nach Quelle ab (`knoten_quelle_seit()`, nutzt
den bestehenden `idx_knoten_quelle_mtime`-Index aus der SQLite-Migration vom 22.07.), gewichtet
über mehrere Quellen gemischt, kein Zeitfenster-Scan mehr. Live verifiziert: 60er-Sample zeigt
33 `entitaet`/19 `resonanz`/8 `mensch` — echte Mischung, kein leeres Array mehr.

## 3. Fund 2 — die fünf AI-Ströme fehlten komplett als Quelle

Daniel wollte zusätzlich: *"auch euch alle... claude codex gemini gpt claudeweb"* — auch die
KI-Ströme selbst sollen als eigene, sichtbare Quelle auftauchen, nicht nur Flarum/Daniel/GENI.

`hoerer.py` markierte bisher JEDEN Dateischreibvorgang unter `/root/werkraum` pauschal als
`quelle="vps_dateisystem"` — auch Schreibvorgänge in `_claude/`, `_codex/`, `_gemini/`, `_gpt/`,
`_claudeweb/`. Genau diese Kategorie wird vom Splitter-Endpunkt explizit rausgefiltert.

**Fix:** neue `AI_STROM_ORDNER`-Zuordnung in `hoerer.py` — Top-Level-Ordnername entscheidet die
Quelle (`_claude`→`claude`, `_codex`→`codex`, `_gemini`→`gemini`, `_gpt`→`chatgpt`,
`_claudeweb`→`claudeweb`) statt der pauschalen Sammelkategorie. In `geni/dialog.py`:
`QUELL_HERKUNFT` um diese fünf ergänzt (als `resonanz` geführt, wie GENI selbst), `zu_splitter()`
setzt jetzt `quelle_id` auf den Stromnamen, damit sie im Frontend unterscheidbar bleiben.
`QUELLEN_GEWICHTUNG` im Endpunkt um alle fünf ergänzt (startet leer, wächst organisch mit jeder
neuen Spiegel-/Notiz-Datei).

**Live verifiziert, während der Session:** ChatGPTs parallel laufende Session schrieb gerade
aktiv in `_gpt/` — die Ereignisse tauchten binnen Sekunden mit `quelle="chatgpt"` auf, nicht mehr
als Rauschen. Nach Neustart von `geni-web.service` (Fehlerquelle unterwegs: vergessen, den
Web-Dienst nach den zusätzlichen Codeänderungen erneut neu zu starten — der lief noch mit dem
Zwischenstand) zeigte ein 100er-Sample `claude`/`codex`/`chatgpt` als echte `quelle_id`-Werte.
Gemini/Claude-Web waren zum Testzeitpunkt noch leer (zu wenig Aktivität in ihren jungen
Zuhause-Ordnern), kein Fehler — füllt sich organisch.

**Nebenfund, gleich mitgefixt:** `hoerer.py` hatte noch ein hartkodiertes Flarum-Passwort im
Klartext (`FLARUM_DB = {..., "password": "[GESCHWAERZT]", ...}`) — derselbe Fehlertyp wie im
Mai-Security-Report, nur in einer damals nicht erwischten Datei. Jetzt `os.environ.get(
"FLARUM_DB_PASSWORD", "")`, der Dienst lädt ohnehin schon `EnvironmentFile=.../flarum.env`.

## 4. Fund 3 — `WeltRueckfluss` war überall nur eine leere Hülle

Daniel wollte zusätzlich: ab sofort sollen echte Verschmelzungen und Entstehungen von Splittern
geloggt werden. Bei der Umsetzung gefunden: **es gibt zwei parallele KompOase-Implementierungen**
(Surface eingebettet in `build_surface.ts`, Standalone unter `/root/kompoase/*.js` für Port 8900 —
deckt sich mit der bestehenden Memory-Regel "KompOase-Änderungen immer auf beiden Systemen").
Beide hatten eine `WeltRueckfluss`-Klasse mit `onVerschmelzung`/`onExplosion`/`onGeisterrest` —
die Standalone-Version war explizit als "HÜLLE — noch nicht implementiert" mit `// TODO: POST
an geni API`-Kommentaren markiert, die Surface-Version war ein reiner Ein-Zeiler-Stub. Keine der
beiden hat je irgendwas geloggt.

**Zusätzlicher Fund dabei:** Die Surface ruft für den Realmodus `fetch('/zwischenraum/splitter?
...')` auf (kein `/api/`-Präfix) — aber `serve_process_camera_preview.ts` (der Node-Server auf
Port 8787) hatte dafür **überhaupt keine Proxy-Route**. Der Realmodus-Datenfeed war auf der
Surface also vermutlich schon länger komplett tot, unabhängig vom GENI-Rauschproblem — Daniels
erlebte Vermischung kam wahrscheinlich hauptsächlich über den Standalone-Server (8900, direkter
GENI-Proxy), nicht über die Surface.

**Fixes:**
- Zwei neue Endpunkte in `welt/api.py`: `POST /zwischenraum/splitter/verschmelzung` und
  `POST /zwischenraum/splitter/entstehung`, beide schreiben in die bestehende `events`-Tabelle
  (`splitter.verschmolzen`/`splitter.entstanden`, `visibility_layer='public'`, `actor_type=
  'system'`) — kein Auth, keine Kopplung an die `splitter`-DB-Tabelle nötig, weil die
  verschmelzenden Objekte auch reine GENI-/Theater-Splitter ohne echte Datenbankzeile sein können.
- `serve_process_camera_preview.ts`: `/zwischenraum/` zur bestehenden Proxy-Weiche für
  präfixlose Endpunkte ergänzt (gleiche Zeile wie `/zitate`, `/shadow/`, `/admin/`, `/search/`).
- Beide `WeltRueckfluss`-Klassen (Surface + Standalone) implementiert: `onVerschmelzung` postet
  Herkunft/Quelle/Inhalt beider Ursprungs-Splitter plus des neuen; `onExplosion` postet
  Ursprung + echte Fragment-Anzahl. Dabei nebenbei einen kleinen Bug gefixt: `onExplosion(s,[])`
  wurde in beiden Implementierungen mit einem fest-leeren Array aufgerufen (vor der eigentlichen
  Fragment-Erzeugung) — die geloggte Fragment-Anzahl wäre immer 0 gewesen. Jetzt wird `anzahl`
  zuerst berechnet und als Array-Länge durchgereicht.
- `onGeisterrest` bewusst nicht implementiert — nicht angefragt.

**Verifiziert:** Alle drei Wege end-to-end getestet (direkt gegen `welt-api:8030`, über den
Standalone-Proxy `8900/api/zwischenraum/...`, über die neue Surface-Proxy-Route
`8787/zwischenraum/...`) — jeweils `{"ok":true}` und ein echter Datensatz in der `events`-Tabelle
bestätigt. Test-Events danach wieder gelöscht (eigene Testdaten, nicht echte Weltereignisse).
Surface neu gebaut (`npx tsx scripts/build_surface.ts`, 449 i18n-Keys DE/EN symmetrisch), nach
`out/process_camera/` kopiert (Pflichtschritt), `process-camera-preview.service` neu gestartet,
Hauptseite weiterhin erreichbar.

## 5. Was als Nächstes ansteht (nicht Teil dieser Session)

Daniel möchte zusätzlich rohe Terminalsitzungen (Claude Code, Codex, Gemini/Antigravity — ChatGPT
und Claude Web haben keine lokalen Rohsitzungsdateien) als weitere Quelle einspeisen. Bewusst
zurückgestellt als eigener, sorgfältig zu testender Schritt: Sitzungsmitschnitte enthalten rohen
Text inklusive aller in dieser Session tatsächlich ausgetauschten Geheimnisse (z.B. das
Basic-Auth-Passwort aus Systemdoku 39) — eine echte Geheimnis-Filterung muss gebaut und
nachweislich **gegen ein bekanntes, echtes Beispiel-Geheimnis aus dieser Session** getestet
werden, bevor irgendwas davon live in GENI/KompOase landet. Das bestehende `SECRET_MUSTER` im
MCP-Werkzeugkörper prüft nur Dateinamen, nicht Textinhalte — hilft hier nicht direkt.

## 6. Nachtrag — Flarum-Vielfalt für die Wesen + zwei weitere Live-Bugs (gleiche Session, später)

Daniel wollte zusätzlich: die 6 Browser-Agent-Wesen sollen beim Flarum-Besuch nicht nur die
neuesten Diskussionen sehen, sondern bewusst gestreute Vorschläge (frühes Drittel, Mitte,
neuestes Drittel, besonders wenig beachtete) — mit Datum, explizit als neue Struktur benannt,
damit sie es in ihren Vaults festhalten können.

**Fund:** `flarum_api.py` hatte dafür schon seit 2026-07-10 eine fertige, getestete Funktion
(`stoeber_pool()`, Baustein 19 — Daniels damalige Worte fast wortgleich mit der heutigen
Anfrage) — aber nur an den inzwischen inaktiven `codewesen_umgekehrte_neugier.py`-Dienst
angebunden, nie an die aktuell aktiven `browser_agent.py`-Wesen. `stoeber_pool()` um eine
`wenig_beachtet`-Kategorie ergänzt (niedrigster `comment_count`), dann `hole_flarum_vielfalt()`
in `browser_agent.py` gebaut und in `baue_prompt()` als expliziter, datierter Prompt-Block
verankert (`NEUE STRUKTUR seit 2026-07-29 — ...`), gekoppelt an den bestehenden 44s-Check-in-
Rhythmus.

**Zwei echte Bugs beim Live-Test gefunden, nicht vorher sichtbar:**
1. `browser-agent@.service` lud `flarum.env` nicht (nur `flextrawurst-db.env` +
   `wesen-vaults.env`) — `FLARUM_DB_PASSWORD` fehlte zur Laufzeit, MySQL-Verbindung scheiterte
   lautlos (mein eigener `except Exception: return []` schluckte den Fehler). Nachträglich
   `log.warning` ergänzt (sonst hätte das niemand bemerkt) und `EnvironmentFile=.../flarum.env`
   in der systemd-Unit ergänzt.
2. Die venv unter `/root/werkraum/venv/bin/python3` (die `browser_agent.py` tatsächlich nutzt)
   hatte `pymysql` nie installiert — `flarum_api.py` war von `browser_agent.py` aus also noch
   nie erfolgreich importierbar gewesen. Mit `pip install pymysql` in genau dieser venv behoben.

Nach beiden Fixes und Neustart aller 7 `browser-agent@`-Dienste live im Log bestätigt:
`Schorschel [check-in] Flarum-Vielfalt: ['frueh', 'spaet', 'wenig_beachtet']`.

**Playwright-Verifikation (Daniels Wunsch: jeden Bauabschnitt einzeln so testen):**
Screenshot + JS-Zustandsauslese der KompOase-Ansicht auf der Surface bestätigt: Theater-Modus
rendert normal (50 synthetische Splitter). Realmodus (`koToggleTheater()`) holt jetzt
tatsächlich 20-21 echte Splitter über `/zwischenraum/splitter?...` (HTTP 200 — die zuvor
fehlende Proxy-Route funktioniert), darunter `quelle_id: "claude"` — der AI-Strom-Tagging-Fix
aus Abschnitt 3 zeigt sich also auch auf der Surface selbst. Ein `splitter.verschmolzen`-Event
ist während des Tests organisch ausgelöst und korrekt geloggt worden (HTTP 200 auf
`/zwischenraum/splitter/verschmelzung`).

**Separater, neuer Fund beim Playwright-Test, noch nicht behoben:** Im Realmodus zeigt der
Canvas trotz nachweislich 21 aktiver Splitter (`koSplitter.filter(...).length === 21`,
mehrfach über 5+ Sekunden bestätigt) keine sichtbaren Blasen und fälschlich den Leerzustand-Text
"Noch keine lebenden Wesen — kommt wenn Wesen einziehen". Datenlage ist also korrekt, die
Canvas-Render-/Leerzustand-Logik hat einen eigenen, von diesem Bugfix unabhängigen Fehler —
nicht weiter verfolgt heute Nacht, als offener Punkt stehen gelassen.
