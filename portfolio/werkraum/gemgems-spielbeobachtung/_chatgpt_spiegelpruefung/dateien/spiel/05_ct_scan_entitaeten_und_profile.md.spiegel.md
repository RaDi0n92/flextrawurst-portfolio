# Spiegelprüfung — `spiel/05_ct_scan_entitaeten_und_profile.md`

## Quellenidentität

- Original: `/root/werkraum/gemgems-spielbeobachtung/spiel/05_ct_scan_entitaeten_und_profile.md`
- Snapshot-SHA256: `8a487542c3a1f84c9080e7973382e2ae46c001634e57324e7ba0d6a8aba2f244`
- Bytes: 4179
- Zeilen: 46
- Snapshot-mtime: `2026-08-13T01:48:33.977693+00:00`

## Prüfstatus

- ORIGINAL UNVERÄNDERT: JA
- SEMANTISCHE PRÜFUNG DURCH CHATGPT: ABGESCHLOSSEN
- BIS EOF SEMANTISCH GEPRÜFT: JA
- AUSSAGENREGISTER: AUSGEFÜLLT
- PROVENIENZPRÜFUNG: AUSGEFÜLLT
- WIDERSPRÜCHE/UNSICHERHEITEN: AUSGEFÜLLT

## Leseabdeckung / Chunk-Fingerprints

- Zeilen 1–46: `b47162b1d6ed613a1e5c22d5d44140baf9b7476cad632866968474ae1e53a1c8` | semantisch: GEPRÜFT

## Was die Datei tatsächlich aussagt

- Prüft zwei Provenienzfragen: Entitäten-Schicht sowie historische Codewesen-Profilbezeichnungen.
- Beschreibt SQL-Tabellen `entity_profiles`, `entity_activity`, `entity_thinking_log`; unterscheidet den API-Endpunkt `/wesen` (`entity_slots`/`entity_states`) von anderen Surface-Routen.
- Bewertet die Abstammung Flarum → konkrete Entitätenarchitektur nur als `Indizien vorhanden`, weil ein direkter Link fehlt.
- Zu Rollen wie `Spannungswesen`/`Reduktionswächter`: dokumentiert Flarum #321 und spätere Spiegel/RAG-Übernahme, aber keine harten Attribute in heutigen `wesen.md`; daher ebenfalls nur Indizien.
- Berichtet einen curl-Test gegen Port 8030: `/wesen` liefert leere öffentliche Liste, `/health` `ok`; erklärt die Leere mit interner Sichtbarkeit der Slots und nennt 8 Slots, 7 Profile und >96.000 Logs.

## Wichtige Rohformulierungen / Zahlen / Pfade / Daten

- Methodik: `Flarum-Fossil -> MD Konzepte/Notizen -> Code/DB/Backend-Skripte -> Laufendes System`.
- Explizite Korrektur: leeres `/wesen` bedeutet laut Datei nicht, dass keine Wesen existieren.

## Provenienzklasse

Gemini-CT-/Sekundärbericht vom 13.08.2026, der Flarum, Dateien und behauptete Runtime-Abfragen zusammenführt.

## Widersprüche / Unsicherheiten / Nicht bewiesene Sprünge

- Die Datei enthält die Ergebnisse eines Runtime-Tests als Bericht, aber nicht die vollständigen Roh-HTTP-/DB-Protokolle.
- Zahlen wie 8 Slots, 7 Profile und >96.000 Logs werden hier behauptet; ihre unabhängige DB-Verifikation ist nicht Teil dieser einzelnen Datei.
- RAG-Fähigkeit bzw. Vorhandensein historischer Dokumente beweist nicht, dass ein Wesen bei einer konkreten Antwort tatsächlich genau dieses Dokument abgerufen hat.

## Abschlussmarker

`SPIEGEL_SEMANTISCH_ABGESCHLOSSEN = JA`
