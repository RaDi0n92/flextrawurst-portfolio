# Systempromptkonzept: Systematisches Raster- & Label-Harvesting (Gen1-R2)

---
datum: 2026-07-24
betrifft: [kosmos, harvester, raster, blickwinkel, labels, systemdoku37]
autor: gemini bei Daniels VPS
---

## 1. Daniels rohe Vision & Korrektur (Wort für Wort)

```text
"ja okay fr nen test. aber das waren 5 gebbäude nicht eine ganze metropole. 
wir müssen neu und umdenken gemeinsam wie wur das ganze kontrolier erstmal nur ein winken 
und lücenlos von grenze zzu grenze navigieren und dann ettwas versetz wider am afand die neue strehe stück für stück 
usw bis heder winkel in eiinem blickwinken eingefangen ist und dann nächster bblcikwinkel erstt. 
und wür müssen die dateien auh so benennen dass sie wasy wenn sebe koordinaten syst auuch gleich heißen fast bis auuf blickwinken verstehst du ?"

"frage...kann man sch straßenname und stadtteilnamen und echte läden etc und alles sightseen und historische blablub nicht schon einblenden lassen ?"
```

---

## 2. Die neuen Architektur-Prinzipien

### A. Lückenloses Mäander-Raster (Grid-Scan)
- Statt 1 Zentrums-Punkt wird jede Metropole in eine **Bounding-Box** (Süd-West bis Nord-Ost) gefasst.
- Der Harvester fliegt systematisch in Rasterschritten (Zeile für Zeile, Streifen für Streifen) von Grenze zu Grenze.
- Überlappung von 20–30% stellt sicher, dass kein Gebäude und kein Wanderweg abgeschnitten wird.

### B. Blickwinkel-Sequenzierung (Erst EIN Winkel komplett)
- Das gesamte Raster der Stadt wird **zunächst vollständig in Blickwinkel H0 (Nordansicht)** erfasst.
- Erst wenn die komplette Stadt in H0 kartografiert ist, schaltet das System auf H45, dann H90 usw. um.

### C. Eingeblendete Labels & POIs (Straßen, Läden, Historie)
- Der Browser aktiviert die Layer-Overlays in Google Earth / Maps, damit Straßennamen, Stadtteilnamen, Sehenswürdigkeiten und historische Orte **direkt als Textur-Overlay auf den Screenshots sichtbar** sind.

### D. Kanonische Koordinaten-Benennung
- Dateinamen folgen einem strikten Rasterschema:
  `[stadt]_[typ]_grid_Y[zeile]_X[spalte]_lat[lat]_lon[lon]_h[heading]_t[tilt].png`
  Beispiel: `moskau_gta_grid_Y02_X05_lat55.7550_lon37.6170_h0_t60.png`

---

## 3. Nächste konkrete Schritte
1. Bounding Boxes für die 27 R2-Städte definieren.
2. Harvester-Skript auf Grid-Mäander und Label-Overlay umstellen.
3. Raster-Testlauf für Moskau (Blickwinkel H0) durchführen und verifizieren.
