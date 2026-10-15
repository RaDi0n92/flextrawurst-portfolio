# Spiegelprüfung — `scratch/read_flarum_to_eof.py`

## Quellenidentität

- Original: `/root/werkraum/gemgems-spielbeobachtung/scratch/read_flarum_to_eof.py`
- Snapshot-SHA256: `a1e679bcb1d3518366a69284ec885a033ef6042f117e8880eb80dc543fcce97e`
- Bytes: 2471
- Zeilen: 63
- Snapshot-mtime: `2026-08-13T00:49:34.724846+00:00`

## Prüfstatus

- ORIGINAL UNVERÄNDERT: JA
- SEMANTISCHE PRÜFUNG DURCH CHATGPT: ABGESCHLOSSEN
- BIS EOF SEMANTISCH GEPRÜFT: JA
- AUSSAGENREGISTER: AUSGEFÜLLT
- PROVENIENZPRÜFUNG: AUSGEFÜLLT
- WIDERSPRÜCHE/UNSICHERHEITEN: AUSGEFÜLLT

## Leseabdeckung / Chunk-Fingerprints

- Zeilen 1–63: `34be94298b2fbf41900a0e8d122fc85e29e7e5c2ad8d04baf582913abdcc7485` | semantisch: GEPRÜFT

## Was die Datei tatsächlich aussagt

- Liest `flarum_vollexport.html` vollständig mit `f.read()` und parst es mit BeautifulSoup.
- Findet alle `section.diskussion`, extrahiert Diskussions-ID, Titel, Tags und alle `div.post`.
- Pro Post speichert es ID, Autor, Zeitstempel, Nummer, `is_wesen` und nur die ersten 100 Zeichen des bereinigten Bodytexts als `snippet`.
- Schreibt die resultierende Liste nach `scratch/flarum_index.json`.

## Wichtige Rohformulierungen / Zahlen / Pfade / Daten

- Der Kommentar sagt ausdrücklich: `Extrahiere die ersten 50 Zeichen`, der Code nimmt tatsächlich `[:100]`.
- `is_wesen` wird über `'wesen' in p_class` bestimmt.

## Provenienzklasse

Technisches Indexierungs-/Extraktionsskript der Flarum-Ausgrabung.

## Widersprüche / Unsicherheiten / Nicht bewiesene Sprünge

- Das erzeugte Index-JSON ist kein Volltextspiegel der Posts, sondern enthält nur 100-Zeichen-Snippets.
- Kommentar und Code widersprechen sich bei 50 vs. 100 Zeichen.
- `p.get('class')` könnte theoretisch `None` sein; dann wäre `'wesen' in p_class` fehleranfällig. Ob dies im konkreten Export vorkommt, sagt die Datei nicht.

## Abschlussmarker

`SPIEGEL_SEMANTISCH_ABGESCHLOSSEN = JA`
