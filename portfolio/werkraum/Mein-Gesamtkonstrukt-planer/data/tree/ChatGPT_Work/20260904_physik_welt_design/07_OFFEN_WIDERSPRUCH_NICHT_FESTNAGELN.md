# Offen / widersprüchlich / bewusst nicht festnageln

Diese Datei enthält **nur Fragen, die aktuell falsche Architektur erzeugen könnten**.

Gelöste technische Geschichten gehören in Git oder `01_REALITAETSBEFUND.md`, nicht hierher.

## 1. Stromidentität ist noch nicht sauber genug

Bestätigte Trennungen:
- Gemgem ≠ Gravityy
- Claude Code ≠ Anthropic_Claude ≠ Haiku

Bekannter Atlasfehler:
- der aktuelle `gemini`-Stromkörper verbindet Gemgems Zuhause mit Gravityys Antigravity-Sessionquelle
- Haiku und Anthropic_Claude fehlen dort als eigene Stromkörper

Offen bleibt allgemein:
- dauerhafte Zuordnung
- aktuelle Benutzung
- aktuelle Anwesenheit
- letzte belegte Handlung

Diese Beziehungen nicht voreilig zu einer universellen Identity-Ontologie aufblasen.

## 2. Planer-ID und Atlas-/Pfadidentität passen noch nicht vollständig zusammen

Planer kann ein Arbeitsobjekt bei Verschiebung als **dasselbe Objekt mit neuem Pfad** behandeln.

Atlas/File-Identität ist stärker pfadbasiert.

Offen:
- Was bleibt bei einem Move identisch?
- Was ist nur dieselbe Arbeitsauflage / dieselbe Herkunft?

Nicht still `plannerObjectId = atlasNodeId` setzen und keinen dritten Master-ID-Raum erfinden, bevor eine echte Szene das Problem braucht.

## 3. Register sind Beobachter, keine Päpste

Atlas, Planer, Dateisystem, Service-Registry, Briefkästen und native Sessions können verschiedene Ausschnitte kennen.

Beispiele:
- Schema existiert, aber Tabelle/Queue ist leer
- Zuhause existiert auf Platte, aber Atlas kennt es nicht
- Capability steht im Toolvertrag, antwortet live aber nicht
- ein Scan sieht Änderung, aber keine konkrete Handlung

Darstellung muss solche Unterschiede aushalten, ohne automatisch eine Quelle zur Masterwahrheit zu ernennen.

## 4. Systemsignal und Ambient müssen unterscheidbar bleiben

Nicht jedes sichtbare Ding braucht Bedeutung.

Offen ist nur die **konsistente Signalgrammatik**, nicht eine Liste aller Metaphern.

Erlaubt:
- Pfütze ist Pfütze
- kaputtes Radio ist kaputtes Radio
- freie Fläche bleibt frei
- Deko kann semantiklos sein

Operative Darstellung dagegen braucht einen nachvollziehbaren Weltgrund.

## 5. Wer sieht was?

Noch nicht festgelegt:
- Daniel allein?
- AI-Instanzen mit eigener Perspektive?
- dieselbe Welt mit unterschiedlichen `seit meinem letzten Blick`-Zuständen?

Wichtig: `neu für Instanz A` ist nicht automatisch `global neu`.

Das erst an einer echten Szene entscheiden.

## 6. Darstellung darf nicht automatisch Handlung werden

Ein sichtbarer Weg / Werkzeug / Anschluss bedeutet nicht automatisch:
- aktueller Akteur darf ihn benutzen
- Aktion ist direkt ausführbar
- Wirkung ist reversibel

Für V0 nur die real auftretenden Machtgrenzen darstellen. Kein vollständiges Rechtssystem auf Vorrat.

## 7. Fortbestehende Arbeit braucht Relevanzschwelle

Nicht jeder Shellprozess wird Weltobjekt.

Sichtbar eigenständig werden sollte Arbeit nur, wenn ihr Fortbestand für Daniel relevant ist, z. B.:
- Background-Session
- längerer Prozess/Test
- Approval/Handoff
- Queue/Review, wenn tatsächlich belegt

Wo die Schwelle liegt, aus echten Szenen lernen.

## 8. Räumliche Erinnerung und Wachstum ziehen gegeneinander

Der Platz soll wiedererkennbar bleiben, aber wachsen und umgedeutet werden können.

Noch nicht technisch lösen.

Gestaltungsziel für frühe Szenen:
- große Orte bleiben ungefähr stabil
- mobile Arbeitskörper dürfen sich bewegen
- falsche Beschriftungen dürfen korrigiert werden
- freie Fläche bleibt Reserve

## 9. Renderer ist noch keine Architekturentscheidung

PixiJS, melonJS oder etwas anderes erst entscheiden, wenn der erste sichtbare Ausschnitt zeigt, was wirklich gebraucht wird.

Vielleicht reicht anfangs Kamera/Fokus + wenige bewegliche Körper und es braucht noch gar kein komplexes Pathfinding.

## 10. Lernen / Selflearning nicht mystifizieren

Arbeitsannahme:

`wiederholter belegter Fund → Kandidat → Review → akzeptierte/abgelehnte dauerhafte Änderung`

Kein Modellgewichtslernen behaupten.

Erst konkrete Promotion-/Reviewfälle bauen, bevor daraus eine allgemeine Lernmaschine wird.

## 11. Bestehende technische Prototypen sind keine Baupflicht

World-State, Runs, Goals, Real-FS-Lifecycle und Lauf-/Goal-Linsen wurden in diesem Durchgang teilweise gebaut.

Sie dürfen benutzt, korrigiert oder später verworfen werden.

Nicht die Welt um diese frühen Datenformen herum designen.

## Aktueller Gegencheck

Bevor hier ein neuer Punkt entsteht, zuerst fragen:

> Verhindert diese offene Frage **jetzt** eine reale Szene oder kann sie warten?

Wenn sie warten kann: nicht hier eintragen.