# Spiegelprüfung — `spiel/18_ct_scan_kosmos_geodaten_prospektion_vs_runtime.md`

## Quellenidentität

- Original: `/root/werkraum/gemgems-spielbeobachtung/spiel/18_ct_scan_kosmos_geodaten_prospektion_vs_runtime.md`
- Snapshot-SHA256: `6f247d0038e1ff63a563feeba55cf863c917b9037f4a7cc12346feb586554ab5`
- Bytes: 5301
- Zeilen: 56
- Snapshot-mtime: `2026-08-13T07:34:43.737962+00:00`

## Prüfstatus

- ORIGINAL UNVERÄNDERT: JA
- SEMANTISCHE PRÜFUNG DURCH CHATGPT: ABGESCHLOSSEN
- BIS EOF SEMANTISCH GEPRÜFT: JA
- AUSSAGENREGISTER: AUSGEFÜLLT
- PROVENIENZPRÜFUNG: AUSGEFÜLLT
- WIDERSPRÜCHE/UNSICHERHEITEN: AUSGEFÜLLT

## Leseabdeckung / Chunk-Fingerprints

- Zeilen 1–56: `6f37c73adb75dde0e68f5fa79c4a6b3254a7661808282b1f13f80ed8f16df2b2` | semantisch: GEPRÜFT

## Was die Datei tatsächlich aussagt

- Klassifiziert den Kosmos-Geodatenbestand (~68 MB) nach echter OSM-Herkunft, synthetischem Fallback und Mischkörpern.
- Nennt `gebaeude_2d_3d.geojson` (~14,86 MB) und Wuppertaler Straßendaten (~38 MB) als echte transformierte OSM-Vektoren.
- Nennt `04_schwelm_eingaenge_tueren_tore.json` mit 3.591 echten OSM-Nodes und einem Velbert-Leak unbekannter Ursache.
- Kennzeichnet Dateien mit `status: synthetisch_verifiziert` als synthetische Fallbacks nach Overpass-Problemen.
- Korrigiert frühere LoD2/DGM1-Erzählungen: keine physischen `.gml`, `.obj`, `.tif`, `.las`/vergleichbaren echten OpenData-NRW-3D-/Höhenkörper auf der Platte; die Verifikation war metadaten-/gitterbasiert bzw. interpoliert.
- Trennt Kosmos-Geodaten von v21-Runtime, v22-Generator und Godot-Slice; Godot nutzt aktuell nur Platzhalter und keine konvertierten GeoJSON-Szenen.

## Wichtige Rohformulierungen / Zahlen / Pfade / Daten

- Tür-Nodes: 3.591; Beispielkoordinate 51.333704 / 7.0510672 mit Velbert-Adresse.
- Google-Earth-Snapshots: ~28 MB Moskau.
- LoD2/DGM1 binäre Rohkörper laut Bericht: 0 Bytes.

## Provenienzklasse

Gemini-Geodaten-Audit vom 13.08.2026 über `/root/werkraum/kosmos/`.

## Widersprüche / Unsicherheiten / Nicht bewiesene Sprünge

- Die Ursache des Velbert-Leaks bleibt ausdrücklich offen.
- Der Abschnitt über 1m³-Voxel-Interior behauptet eine Ableitung bei <50 m und verweist auf `gen3_schwelm_housing_interior.json`; die konkrete Ausführung/Runtime dieses Systems wird in der Datei nicht separat bewiesen.
- `vollständige CT-Scan-Analyse` ist stärker als die gezeigte Auswahl einzelner Schlüsseldateien; als globaler Vollständigkeitsbeweis reicht der Bericht allein nicht.

## Abschlussmarker

`SPIEGEL_SEMANTISCH_ABGESCHLOSSEN = JA`
