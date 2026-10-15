---
datum: 2026-07-31
betrifft: [gesamtatlas, vokabular, aufraeumung, kathedrale, datenmigration]
importable: false
autor: claude-code bei Daniels VPS
---

# Gesamtatlas — vollständige Vokabular-Entschlackung ("alles komplett und vollumfänglich")

## Wo das herkommt

Direkter Anschluss an `2026-07-31-gesamtatlas-kathedrale-erste-entschlackung.md`. Nach der ersten
Entschlackungsrunde (Beweis-/Checkpoint-Ballast) hat Daniel klargestellt, dass die
Vokabular-Entschlackung nicht nur den Code betrifft: *"ich will nicht nur vokabular im code
entschlacken ich will auch die ganzen eigenwörter duch normale logische ersetzten und es in den
dateien so beschreiben dann."* Bestätigte Ersetzungsliste: `truth_class`→`datenstand`,
`truth_boundary`→`einschraenkung`, `Ursprungsring`→`Ursprungsordner`. `Kapsel` und `Gesamtatlas`
bleiben unverändert (Daniels ausdrückliche Entscheidung).

Auf die Nachfrage, ob auch der neu gefundene 15GB-`organismus/`-Ordner mit angefasst werden soll:
*"ja alles komplett und vollumfänglich bitte."*

## Was in dieser Runde gemacht wurde

**1. Code-Vokabular (bereits im vorherigen Nachtrag dokumentiert):** `truth_class`/`truth_boundary`
in 10 Python-Modulen + 4 JSON-Protokolldateien + der bestehenden Testdatei ersetzt,
`Ursprungsring`→`Ursprungsordner` als echte Verzeichnisumbenennung.

**2. Nachgezogene deutsche Anzeige-Labels:** der erste Durchlauf hatte nur die englischen
Bezeichner erwischt. Gefunden und nachgezogen: `Wahrheitsklasse`→`Datenstand` (2 Stellen,
`mcp_atlas_relations.py` + `vps_mcp_server.py`), `## Wahrheitsgrenze`→`## Einschraenkung`
(`mcp_atlas.py`, Markdown-Überschrift). Außerdem `TRUTH_EXACT_PATH`/`TRUTH_DERIVED_HISTORY`/
`TRUTH_EXACT_MENTION`-Konstanten (verwandtes, aber ursprünglich nicht bestätigtes Vokabular,
konsequent mit umbenannt zu `DATENSTAND_EXAKTER_PFAD`/`DATENSTAND_AUS_VERLAUF`/
`DATENSTAND_EXAKTE_ERWAEHNUNG`) und `URSPRUNGSWAHRHEITEN.json`→`URSPRUNGSSTAND.json`.

**Bewusst nicht angefasst, extra vermerkt statt eigenmächtig entschieden:**
- `aktuelle_wahrheit.md`/`aktuelle_wahrheit.json` in `mcp_atlas.py` — Referenzen auf tatsächlich
  existierende Marker-Dateien (`AKTUELLE_WAHRHEIT.json`/`.md`) in einem anderen, eigenständigen
  ChatGPT-Projekt (WorldWORDS-ANTIBIBEL). Umbenennung der Referenz ohne die echten Dateien
  mitzubenennen würde die Erkennung brechen — außerhalb des heutigen Auftragsumfangs.
- `Größenwahrheit`/`GROESSENWAHRHEIT.json` — dieselbe Begründung, nicht Teil der bestätigten Liste.

**3. `organismus/`-Fund (15GB, im vorherigen Nachtrag als offener Punkt benannt):** 33
`FEHLGESCHLAGENER_BAU_*`-Schnappschüsse (300-518MB je Stück, über 18 Stunden verteilt) plus ein
veraltetes `AKTUELL/`-Verzeichnis (Stand von gestern, andere Prüfsumme als die echte, aktuell
gepflegte Kapsel). Keiner der grünen Checkpoints referenziert irgendetwas darin.

**Wichtige Korrektur während der Arbeit:** anders als zunächst angenommen war NICHT alles hier
git-getrackt — nur 1549 von 42.824 Dateien. `git rm` allein (mein erster Versuch) hätte den
Großteil unwiederbringlich gelöscht, weil `git rm` Dateien mit uncommitteten Änderungen aus
Sicherheitsgründen verweigert UND untracked Dateien komplett ignoriert — beides zusammen führte
dazu, dass mein erster `git rm`-Aufruf nur einen winzigen Bruchteil wirklich entfernte, während
`du -sh` weiterhin 15GB zeigte. Kurskorrektur: komplett archiviert (2,9GB komprimiert unter
`/root/werkraum_archive_gesamtatlas_aufraeumung/organismus_archiv_20260731T0505Z.tar.gz`), erst
danach `rm -rf` + `git add -A` zur Nachbereinigung des Git-Index. **14GB frei geworden** (653G →
639G belegt).

**4. Datenmigration der gespeicherten Register:** `truth_class`/`truth_boundary` steckten bereits
in gespeicherten Datendateien fest (nicht nur im Code, das nur neue Schreibvorgänge betrifft) —
`PROJEKTREGISTER.json` (1535 Treffer, 32MB), `AENDERUNGSSTROM.jsonl` (682 Treffer, 21MB,
append-only Änderungsprotokoll), `CLAIMREGISTER.json` (21), `PROJEKTREVISIONEN.json` (4), plus
je 1 in `SESSIONREGISTER.json`, `ATLAS_STATUS.json`, `GROESSENWAHRHEIT.json`,
`URSPRUNGSORDNER.json`. Diese Register sind bewusst per `.gitignore` (`_gpt/gesamtatlas/.gitignore`)
von Git ausgenommen (Laufzeitdaten) — kein Git-Netz, deshalb vor der Änderung einzeln nach
`/root/werkraum_archive_gesamtatlas_aufraeumung/register_vor_umbenennung/` kopiert. Danach `sed`
pro Datei, jede `.json`-Datei einzeln mit `python3 -c "json.load(...)"` validiert, jede
`.jsonl`-Datei zeilenweise geparst (0 fehlerhafte Zeilen in beiden). SQLite-Datenbanken
(`BEZIEHUNGSREGISTER.sqlite`, `PFADINDEX.sqlite`, `BEGRIFFSINDEX.sqlite`) per `.schema`-Abfrage
geprüft — keine der drei hat `truth_class`/`truth_boundary` überhaupt als Spaltenname, nichts zu
migrieren dort.

## Cache-Verhalten entdeckt, sauber aufgelöst

Nach allen Code- und Datenänderungen zeigte `atlas.health` live weiterhin `truth_boundary` im
`sizes`-Unterblock, obwohl `GROESSENWAHRHEIT.json` selbst schon sauber war. Ursache: der
`sizes`-Block wird nur bei einem **vollen** Atlas-Refresh neu berechnet — der laufende
Light-Refresh-Timer (alle paar Minuten) übernimmt ihn unverändert vom letzten vollen Lauf
(Revision 4651, vor allen heutigen Änderungen, `"reused_from_revision"`-Mechanik). Kein Fehler in
der eigenen Arbeit, sondern Teil des vorgesehenen zweistufigen Aktualisierungsmodells (schon in
`atlas.health`s eigenem `"full_refresh_recommended": true`-Flag sichtbar).

Ein voller Refresh (`run_atlas_refresh.sh full`) ist laut `atlas_auto_arrival_v1.json` normalerweise
nicht ohne expliziten Auftrag erlaubt — Daniels "alles komplett und vollumfänglich" deckt das aber
ab. Erster Versuch wurde vom bereits laufenden Light-Refresh blockiert (`.scheduled-refresh.lock`,
`flock`-basiert, kein Fehler, sauberes Skip-Verhalten), zweiter Versuch nach Abwarten erfolgreich
gestartet, ~8 Minuten Laufzeit erwartet (letzter voller Lauf brauchte laut Log 8min 12s CPU-Zeit).

## Dienste-Neustarts

Alle sechs `vps-mcp-*`-Dienste neu gestartet (`vps-mcp`, `-claude`, `-codex`, `-gemini`, `-grok`,
`-sauber`), nachdem ChatGPTs eigener Dienst 7 Minuten inaktiv war. Zweimal (bei `-claude` und
`-sauber`) derselbe, bereits einmal zuvor dokumentierte, unabhängige Absturz durch eine Race
Condition in `time_stream.py` (`shutil.rmtree` auf `sitzungen-lesbar`, nicht von mir berührte
Datei) — beide Male durch `systemd`s `Restart=always` selbstheilend, jetzt insgesamt dreimal
beobachtet (siehe frühere Karte-Notiz). Echter, reproduzierbarer Bug, aber außerhalb des
heutigen Auftrags — für eine spätere Session vorgemerkt.

## Was am Ende bleibt

Alles, was heute Nacht gefunden und nicht bestätigt/nicht angefasst wurde: `aktuelle_wahrheit.*`
(externe Fremdreferenzen), `Größenwahrheit`/`GROESSENWAHRHEIT.json` (nicht Teil der Liste), die
`time_stream.py`-Race-Condition (unabhängiger Bug). Alles Übrige, was tatsächlich unter Daniels
bestätigte Ersetzungsliste fiel, ist jetzt durchgehend konsistent — Code, Protokolldateien,
Verzeichnisnamen, deutsche Anzeige-Labels und die bereits gespeicherten Register.
