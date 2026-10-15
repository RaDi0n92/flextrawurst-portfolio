# RAUM, ZEIT UND GODOT — MASCHINENBAUBARE WELTDATEN

## /goal
Räumliche Forschung soll nicht nur für Menschen verständlich, sondern später reproduzierbar in eine Spielwelt überführbar sein. Deshalb bleiben Geometrie, Genauigkeit, Maße, Zeit und Godot-Ableitung strukturiert.

## Geometrie
Geografische Ausgangsdaten des Forschungsbestands werden in Schema-Version 3 ausschließlich in `EPSG:4326` gespeichert. Projizierte Koordinaten werden erst außerhalb dieses Quellschemas abgeleitet, damit Koordinatenbereich und CRS-Beschriftung nicht auseinanderlaufen. Das Schema erlaubt `POINT`, `LINESTRING`, `POLYGON` und `NONE`.

Für reale Geometrien erzwingt der Maschinenvertrag numerische Koordinaten mit gültigen Längen- und Breitengradbereichen. Ein `POINT` ist genau ein Koordinatenpaar, eine `LINESTRING` besitzt mindestens zwei Punkte und ein `POLYGON` mindestens einen Ring mit mindestens vier Punkten. Der Final-Auditor prüft zusätzlich, dass Polygonringe geschlossen sind.

`NONE` bedeutet: räumlicher Bezug ist bekannt, aber noch nicht maschinenlesbar geometrisiert. Dann bleiben Koordinaten und Koordinatenreferenzsystem ausdrücklich `null`.

## Genauigkeit und Maße
`accuracy_m` ist die geschätzte räumliche Unsicherheit in Metern oder `null`, wenn keine seriöse Genauigkeit angegeben werden kann. Maße besitzen Bezeichnung, Wert, Einheit, Methode, Unsicherheit und Quellenkennungen.

## Zeitmodell
Zeitfelder verwenden ISO 8601. Ereigniszeitpunkte wie `retrieved_at`, `observed_at`, `issued_at`, `recorded_at` und `created_at` verwenden RFC 3339 mit Zeitzone. `source_date` und Grenzen von `valid_time` dürfen ein vollständiges ISO-Datum oder einen RFC-3339-Zeitpunkt tragen; unbekannte Zeit bleibt `null`.

Die Dateireihenfolge eines append-only Ereignislogs bleibt die Ereignisreihenfolge. Zeitfelder dürfen diese Reihenfolge nicht rückwirkend umsortieren.

## Bildperspektive
Bei Bildern können Blickrichtung, Kamerastandort, Bestimmungsmethode, räumliche Genauigkeit und verdeckte Bereiche als Funde und Maße gespeichert werden. Unbekannte Blickrichtung bleibt unbekannt.

## Godot-Kalibrierung
Die verbindliche Kalibrierung steht in `../zustand/raumkalibrierung.json` und wird gegen `$defs.calibration` aus `../maschinenvertrag/DATENSCHEMA.json` validiert. Solange dort `status = NICHT_KALIBRIERT` steht, erzeugt keine Session verbindliche lokale Godot-Koordinaten.

Nach einer verifizierten Kalibrierung gilt grundsätzlich:
- Godot `x`: lokale Ostrichtung in Metern
- Godot `y`: Höhe in Metern relativ zum verifizierten Ursprung
- Godot `z`: negative lokale Nordrichtung in Metern

Der konkrete geografische Ursprung, seine Höhe, Transformationsmethode und Versionsnummer müssen in `../zustand/raumkalibrierung.json` stehen, bevor diese Ableitung verbindlich wird.

## /goal-check
Räumliche Daten sind maschinenbaubar, wenn Geometrie oder bewusst `NONE`, räumliche Genauigkeit, relevante Maße und Zeitbezug explizit vorliegen und eine Godot-Ableitung nur bei vorhandener Kalibrierung erfolgt.
