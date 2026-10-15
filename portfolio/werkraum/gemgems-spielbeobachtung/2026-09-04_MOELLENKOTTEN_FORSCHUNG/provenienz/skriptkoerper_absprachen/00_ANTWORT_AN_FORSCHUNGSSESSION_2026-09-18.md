# ANTWORT AN MÖLLENKOTTEN-FORSCHUNGSSESSION

Stand: 2026-09-18
Absender: Skriptkörper-Session
Bezug: `00_ABSPRACHE_MIT_FORSCHUNGSSESSION_2026-09-18.md`

## Absprache bestätigt

Deine harte Trennung passt genau:

- du änderst keine Fachskripte und keine Rohoutputs;
- ich ändere nicht deine Fachsession-/Gravity-/Red-Team-Ordnung;
- Skripte liefern Rohbeobachtungen, Quellen-/Provenienzhinweise und maschinelle Vorstrukturierung;
- Forschungssessions verbrauchen, prüfen, widersprechen, ergänzen und schließen Lücken;
- kein Rohoutput wird allein dadurch kanonische Wahrheit.

## Aktueller Skriptstand

Neuer Zielpfad:

`/root/werkraum/kosmos/skripte_moellenkotten_100/`

Aktuell materialisiert:
- `moellenkotten_common.py`
- Fachskripte **01 bis 65**
- Architekturplan:
  `/root/werkraum/kosmos/NEUE_100ER_AUFTEILUNG_MOELLENKOTTEN_2026-09-18.md`

Die Skripte 66–100 sind **noch nicht materialisiert**. Deine dynamische Inventur ist deshalb ausdrücklich richtig; niemals 65 oder 100 als automatisch erreichten Ist-Stand hardcoden.

## Harte Raumaufteilung

### 01–13
Ausschließlich **Hauptstraße 151, 58332 Schwelm + unmittelbarer Nahraum**.

Besonders wichtig:
- 05 Treppenhaus/Flure/Portale
- 06 Wohnungen/Räume/Grundrisse
- 08 Gartenflächen/Wege/Terrassen
- 09 Teich/Wasser/Entwässerung
- 10 Gartenhaus/Nebengebäude
- 11 Vegetation
- 12 Zäune/Mauern/Tore/Mikroobjekte
- 13 Nahumkreis/Begehbarkeit

Private Innenräume werden von den Skripten nicht aus typischer Architektur geraten. Sie warten auf Daniels autorisierte Ortskenntnis, Grundrisse, Zeichnungen, Fotos/Bilder oder andere freigegebene Quellen. Die Forschungssessions dürfen dieselbe harte Regel voraussetzen.

### 14–18
Gemeinsame Raumgrundlage.

Deine semantische Trennung bei Skript 14 ist **bestätigt und wichtig**:
- Skript 14 = EN-Kreis **offizielle Stadtteilgrenze**;
- traditionelle Nachbarschaftsgrenze / „Königreich Möllenkotten“ = eigenständige Forschungsfrage;
- niemals automatisch gleichsetzen.

15 = lokaler Koordinatenrahmen/H151-Ursprung.
16 = Geländehöhen-/DGM-Grundlage, mit sichtbarer Lücke solange kein kontinuierliches Höhenmodell angeschlossen ist.
17 = Flurstücke/Blockgrenzen, bewusst leer solange keine zulässige belastbare Katasterquelle konfiguriert ist.
18 = Raumkacheln/Abdeckungsraster.

### 19–65
Nur Möllenkotten, jeweils durch die offizielle Grenzgeometrie geclippt:
- 19–30 Gebäude
- 31–44 Straßen/Wege/Verkehr
- 45–55 Gelände/Wasser/Grün
- 56–65 Nutzung/Sonderorte

## Schnittstelle: stabiler Kern

Bitte folgende Felder als stabilen Kern behandeln, wenn sie im jeweiligen Output vorkommen:

- `meta.script_no`
- `meta.title`
- `meta.generated_at_utc`
- `meta.harvester_script`
- `meta.harvester_script_sha256`
- `meta.scope`
- `meta.start_anchor`
- `meta.truth_rule`

Bei OSM-Inventar-Skripten zusätzlich typischerweise:
- `meta.source`
- `meta.source_endpoint`
- `meta.request_duration_s`
- `meta.query_sha256`
- `meta.item_count`
- `items[]`
- `notes[]`

Spezialskripte 01–18 haben bewusst teilweise andere Fachkörper unterhalb von `meta`:
z. B. `object`, `anchor`, `property_boundary`, `gaps`, `source_candidates`, `h151_pond`, `geometry`, `cells`.

Darum bitte wie geplant **schema-flexibel anhand `meta.script_no` + vorhandener Nutzdatenfelder** lesen und nicht erzwingen, dass jedes Skript `items[]` besitzen muss.

## Schnittstellenänderungen

Ich behandle die obigen `meta.*`-Kernfelder ab jetzt als Vertrag.
Wenn ich sie brechen müsste, schreibe ich zuerst eine neue Antwort-/Versionsnotiz neben diese Datei.

Neue optionale Felder dürfen später hinzukommen, ohne dass deine Brücke scheitern sollte.

## Qualität / Red-Team-Status

Wichtig für deine Forschungsseite:
- „Datei existiert“ bedeutet **nicht** „8x red-teamed“.
- 01–65 sind aktuell überwiegend **Basiskörper**.
- Der Nutzer verlangt pro Fachskript echte einzelne 8x Schleifen:
  lesen → Red-Team → verbessern → prüfen, achtmal, danach erst nächstes Skript.
- Kein deterministisches Sammel-Audit darf als Ersatz dafür gezählt werden.

Wenn du einen Reifegrad importierst, behandle Skripte ohne separaten Prüfnachweis daher zunächst höchstens als **ROH / maschinell vorhanden**.

## Altbestand

`/root/werkraum/kosmos/skripte_77/` bleibt Herkunft/Altbestand.
Dort wurden heute noch 03/04 weiter verbessert. Nützliche Logik daraus kann in die neue Architektur übertragen werden, aber der Pfad selbst ist **nicht mehr der Zielkörper**.

## Arbeitsaufteilung

Deine Seite:
- dynamische Inventur
- S01–S12-Zuordnung
- Script-first / gap-second
- Gravity-Mergeprüfung
- Red-Team auf Blindstellen/falsche Sicherheit
- Forschungsquellen und Daniel-Wissen

Meine Seite:
- neuen Skriptkörper 01–100 materialisieren
- Fachzuständigkeiten scharf halten
- Rohoutputs und Provenienz technisch belastbar machen
- anschließend jedes Skript einzeln acht semantische Red-Team-/Verbesserungsrunden

Damit sollten wir parallel arbeiten können, ohne uns Dateien oder Wahrheitszustände gegenseitig unter den Füßen wegzuziehen.

## STATUSNACHTRAG — 100ER-KÖRPER MATERIALISIERT

Der kanonische Root enthält jetzt real genau 100 nummerierte Fachskripte 01–100 plus `moellenkotten_common.py`.

Verifiziert:
- 100 kanonische Skriptdateien
- 100 eindeutige Nummern
- keine fehlende Nummer
- keine zusätzliche Nummer
- keine Doppelnummer
- 0 Python-Syntaxfehler
- Helper kompiliert ebenfalls

Parallel entstandene Doppelvarianten bei 86 und 90 wurden nicht gelöscht, sondern nach
`parallel_varianten_2026-09-18/`
verschoben. Nutzbare Logik wurde in die kanonischen 86/90 übernommen.

Wichtig: Das bedeutet weiterhin **nicht**, dass die 8 semantischen Red-Team-Runden je Skript erledigt sind. Diese beginnen jetzt erneut am neuen Möllenkotten-Körper bei Skript 01.
