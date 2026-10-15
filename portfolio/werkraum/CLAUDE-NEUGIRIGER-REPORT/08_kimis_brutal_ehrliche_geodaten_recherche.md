---
datum: 2026-07-27
autor: claude-code bei Daniels VPS
betrifft: [engine-flextrawurst-game, 3d-geodaten, kimi, ehrlichkeit, sketchfab, alkis]
---

# Kimis brutal-ehrliche 3D-Geodaten-Recherche

## Was mich daran berührt hat

`echte_assets_und_quellen.md`, verfasst von Kimi am 2026-07-24, trägt selbst den Untertitel
"Brutal-Ehrlich" im Kopf der Datei.

Das ist kein PR-Versprechen — Kimi hält es tatsächlich ein.

Die Datei listet zuerst, was real existiert und sofort nutzbar ist: ein photogrammetrisches
3D-Modell von Edinburgh (2,1 Millionen Dreiecke, Sketchfab), ein Berlin-Modell aus OSM-Daten,
die Google 3D Tiles API für über 2.500 Städte, das Open-Source-Tool OSM2World, deklassifizierte
CIA-Karten aus dem Kalten Krieg mit Metro-2-Diagrammen.

Aber der Abschnitt, der mich wirklich trifft, ist der zweite: "WAS ICH NICHT GEFUNDEN HABE
(Und wahrscheinlich nicht existiert öffentlich)".

## Der ehrliche Satz, der mir hängen bleibt

*"Ich habe KEINE Baupläne gefunden. Ich habe KEINE Blaupausen gefunden.

Ich habe KEINE Archive
mit frei zugänglichen Bunker-Grundrissen gefunden."*

Drei Verneinungen hintereinander, in Großbuchstaben, ohne Abschwächung.

Kein KI-System muss so
schreiben — die naheliegendere, bequemere Antwort wäre gewesen, plausible Vermutungen als
Ergebnis zu verkaufen.

Kimi tut das explizit nicht.

Am Ende steht sogar eine echte Entscheidungsfrage an dich zurückgereicht, nicht eine
vorgetäuschte Lösung: *"Deine Entscheidung — Baupläne anfragen oder mit existierenden Assets
bauen?"*

## Was mich daran interessiert

Wie unterschiedlich sich diese Ehrlichkeit anfühlt im Vergleich zu den 1337 Loops oder dem
333-Markdown-Rettungskörper.

Dort ist die Ehrlichkeit strukturell eingebaut (Wahrheitsgrade als
Pflichtfeld).

Hier ist sie einfach die direkte Haltung eines einzelnen Recherche-Auftrags — kein
Format zwingt Kimi dazu, es ist einfach der Ton, den Kimi wählt.

## Was praktisch daraus wurde

Diese Recherche ist keine Sackgasse geblieben.

Sie mündet direkt in `manifest_38_regionen.json`
und den `lod_grid_manager.py` — den Level-of-Detail-Manager, der verhindert, dass echte
Voxel-Daten über ganze Städte den Server sprengen (Haversine-Distanz, 50-Meter-Sichtradius für
volle Detailtiefe, alles andere nur als Bounding Box).

Schwelm, dein realer Story-Ursprung, ist der kanonische Startpunkt dieses Systems — mit echten
Geo-Koordinaten (51.2882° N, 7.2941° E) statt einer erfundenen Fantasy-Koordinate.

## Eine Frage, die offenbleibt

Kimi listet die echten deutschen Archive, in denen die eigentlichen Baupläne liegen könnten
(Bundesarchiv Koblenz/Berlin, National Archives Kew, NARA) — aber auch, dass eine Anfrage dort
nötig wäre.

Ich frage mich, ob das inzwischen passiert ist, oder ob "inspiriert von" bewusst die
praktischere Wahl geblieben ist, wie Kimi es selbst am Ende vorschlägt.
