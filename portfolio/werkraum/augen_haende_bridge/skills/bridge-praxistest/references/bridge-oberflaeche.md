# Was es in der Bridge zu bedienen gibt

- **Raute** (Name und Farbe jedes Agenten): gehört genau einem Agenten, dort entsteht deine Ansage.
  Rechtsklick **bei gehaltener Bedientaste** öffnet das Menü.
  Dort: Name, Farbe, Deckkraft, Größe, Zeichnen, Anzeigeort, Not-Aus.
- **Bedientaste:** Strg+Alt.
  Die Fenster der Bridge nehmen Klicks nur an, solange sie gehalten wird.
  Ohne sie gehen Klicks an das Programm darunter, so steht die Bridge niemandem im Weg.
- **Terminal** (dein Fenster): Die Tastatur geht, nachdem man hineingeklickt hat.
  Unten rechts stehen „Ziel: …“ und der Scanner-Knopf (Fadenkreuz) zum Binden eines Fensters.
- **Regieleiste** (unten links): Mik, Cam, Regie, STOP und ein Prozent-Knopf für die Deckkraft.
  Zustände stehen auch als Wort da (aus, …, an, Fehler).
- **Chat:** zeigt alle Agenten, „An: …“ schaltet den Empfänger durch.
  ▲ ▼ springen zwischen Nachrichten, das Mausrad blättert.
- **Zeichnen:** Raute-Menü → „Zeichnen im Ziel …“.
  Werkzeuge: Pfeil, Text, Stift, Marker. Strg+Z und Strg+Y, dann „Fertig“.
- **Hände:** wirken nur im gebundenen Fenster und nur mit Lease (`lease`).
  Daniels Maus und F12 gehen immer vor.

## Was bewusst nicht geht

- Außerhalb des gebundenen Fensters klicken (Antwort `ausserhalb`).
  Das ist eine Schutzgrenze, kein Fehler.
- Menü-Fenster der Bridge bedienen, solange Daniel sie nicht für die Hände freigegeben hat (danach nur
  beim Namen: `bridge_cli.py menue "Name"`, nie mit Koordinaten).
