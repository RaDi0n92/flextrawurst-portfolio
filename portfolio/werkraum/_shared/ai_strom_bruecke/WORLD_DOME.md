# WorldDome-Zielbild und Minimalumfang dieser Bridge

Stand: 2026-10-03

## Was WorldDome hier bedeutet

WorldDome ist **kein Browser-DOM** und nicht auf HTML, Webseiten oder vorhandene Accessibility-Strukturen begrenzt.

Er ist die universelle Bedeutungsschicht des Agenten über jeder sichtbaren und bedienbaren Oberfläche.

- Wo eine echte Struktur existiert (Browser-DOM, Accessibility-Baum, Fenster-/Control-Struktur), wird sie benutzt.
- Wo nur Bild/Pixelsicht existiert, darf der Agent daraus eigene semantische Bereiche, Objekte, Anker und Beziehungen erzeugen.
- Jeder Pixel ist grundsätzlich adressierbar und kann zu einem semantischen Objekt aufgelöst werden, ohne jeden Pixel als eigenen Knoten zu speichern.
- Ein semantisches Objekt kann lesbar, klickbar, drückbar, ziehbar, beschreibbar, merkbar, organisierbar oder nur beobachtbar sein.
- Eigene Bedeutungen müssen von gemessenen Fakten unterscheidbar bleiben. Erzeugte Bedeutung darf nie als native Wahrheit ausgegeben werden.
- Der Agent darf seine eigene Struktur selbst erweitern, umordnen, benennen, gruppieren, erinnern und wieder verwerfen.
- Daniel kann Hinweise geben oder Fragen stellen. Der WorldDome ist aber primär Arbeits- und Orientierungsraum des Agenten, keine Bedienoberfläche für Daniel.

Denkmodell:

    sichtbare Welt
      -> echte Struktur, wenn vorhanden
      -> Bild/Pixel/Geometrie
      -> semantische Objekte und Affordanzen
      -> eigene Anker/Beziehungen/Erinnerungen
      -> Handlung
      -> neue Beobachtung
      -> Korrektur/Erweiterung der eigenen Weltstruktur

Die spätere große Form kann Scene Graph, Semantic Map, Affordance Map, Inventar, Erinnerung und eigene räumliche Ordnung verbinden.

## Herkunft / epistemische Trennung

Mindestens diese Kategorien bleiben getrennt:

- real: direkt aus echter Struktur gelesen
- inferred: aus Bild, Geometrie, Text oder Verhalten erschlossen
- authored: bewusst vom Agenten oder Daniel angelegt
- projected: möglicher zukünftiger Zustand, nie als gegenwärtige Realität behandeln

## Minimalumfang in dieser alten AI-Strom-Brücke

Diese Bridge soll **nicht** den kompletten großen WorldDome der neueren Augen-und-Hände-Bridge duplizieren.

Für den LibreOffice-Pilot reicht hier zunächst:

1. aktuelles Ziel/Fenster eindeutig erfassen,
2. Fokus und relevante Geometrie erfassen,
3. einen relevanten Schreib-/Interaktionsbereich semantisch binden,
4. Plan an frischen Zielzustand binden,
5. unmittelbar vor Eingabe erneut prüfen,
6. fremde Eingriffe/Fokuswechsel als stale behandeln,
7. erst dann klicken/tippen,
8. danach neu beobachten und Wirkung verifizieren.

Minimaler Arbeitsfluss:

    SEE
      -> TARGET
      -> SEMANTIC BINDING
      -> PRE-ACTION RESCAN
      -> CAN_DISPATCH
      -> ACT
      -> SEE AGAIN
      -> VERIFY

Ein neuer Bildframe allein ist **keine** neue Weltrevision. Eine Revision entsteht nur bei handlungsrelevanter semantischer Änderung, z. B. Fokuswechsel, Ziel verschwunden/ersetzt, relevante Geometrie geändert oder fremder Eingriff.

## Wichtige Grenze

Der große WorldDome gehört langfristig in die neuere Augen-und-Hände-Bridge, wo bereits echte WorldDOM-Knoten, authored-Anker, Profile und mehrere Strukturquellen existieren.

Diese alte Bridge bekommt nur den kleinen tragenden Ausschnitt, der nötig ist, um auf Virtual Desktop 2 / LibreOffice zuverlässig zu sehen, zu binden, zu handeln und nach fremder Intervention sauber neu anzusetzen.
