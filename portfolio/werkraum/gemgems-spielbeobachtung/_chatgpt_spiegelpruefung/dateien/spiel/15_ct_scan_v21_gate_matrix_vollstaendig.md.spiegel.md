# Spiegelprüfung — `spiel/15_ct_scan_v21_gate_matrix_vollstaendig.md`

## Quellenidentität

- Original: `/root/werkraum/gemgems-spielbeobachtung/spiel/15_ct_scan_v21_gate_matrix_vollstaendig.md`
- Snapshot-SHA256: `bbf6bda7497db5e0453cc376db2d0f062ac69a667899a8095f860b4b4f5aacda`
- Bytes: 12533
- Zeilen: 150
- Snapshot-mtime: `2026-08-13T07:21:10.153779+00:00`

## Prüfstatus

- ORIGINAL UNVERÄNDERT: JA
- SEMANTISCHE PRÜFUNG DURCH CHATGPT: ABGESCHLOSSEN
- BIS EOF SEMANTISCH GEPRÜFT: JA
- AUSSAGENREGISTER: AUSGEFÜLLT
- PROVENIENZPRÜFUNG: AUSGEFÜLLT
- WIDERSPRÜCHE/UNSICHERHEITEN: AUSGEFÜLLT

## Leseabdeckung / Chunk-Fingerprints

- Zeilen 1–150: `f2f7b217d5935791fc64894168c6e63dacbf337a8595b37d06c4560e39cd1976` | semantisch: GEPRÜFT

## Was die Datei tatsächlich aussagt

- Inventarisiert 20 historische v21-Gate-Resultate: Gates 01–12 plus 13A–13H.
- Summiert 285 Passed und 0 Failed aus den historischen Result-JSONs vom 25.07.2026 und sagt ausdrücklich, dass diese Tests im CT-Lauf nicht neu ausgeführt wurden.
- Trennt für jedes Gate drei Ebenen: UI-Bedienroute im Code, tatsächlich per UI/Rendering im Auto-Test geprüft, und nur über interne `FW_TEST`-/`FW_GAME`-Schnittstellen geprüft.
- Deckt Start, Traversal, Magie, Untergrund, Fahrzeuge, Wesen/Consent, Zeitatlas, Creator, Kampf/Loot/Pause, Welt/Story, Werkstatt, Forschung sowie acht Skill-Erweiterungsgates ab.
- Rechnet Gates 01–12 = 173 Checks und 13A–13H = 112 Checks, zusammen 285.

## Wichtige Rohformulierungen / Zahlen / Pfade / Daten

- Gate-Ergebnisse: 10,11,11,14,16,18,14,16,17,15,13,19, dann 15,12,11,13,17,15,13,15.
- Gate09 Pause laut Datei über `Tab`.

## Provenienzklasse

Gemini-Audit-/Sekundärbericht vom 13.08.2026 über historische v21-Testresultate und Testcode-Bedienwege.

## Widersprüche / Unsicherheiten / Nicht bewiesene Sprünge

- `285/285 PASS` belegt die historischen Resultdateien, nicht eine aktuelle Re-Execution oder menschliche Spielabnahme.
- Viele tiefe Assertions laufen laut Datei über interne Testhooks; daher darf `UI-Bedienroute vorhanden` nicht mit `komplett über echte Benutzerbedienung getestet` gleichgesetzt werden.
- Einzelne Aussagen zur konkreten UI-Prüfung sind Interpretationen des Testcodes und müssten für absolute Sicherheit jeweils am Originaltest gegengeprüft werden.

## Abschlussmarker

`SPIEGEL_SEMANTISCH_ABGESCHLOSSEN = JA`
