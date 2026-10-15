# Übergabekörper · ChatGPT Work / Codex

Stand: 2026-08-23  
Geltung: Dieser Text ist eine belegte Übergabe, kein Abschluss und kein Behauptungsersatz.

## Wofür dieser Körper da ist

Lies diese Datei zuerst, wenn du die bisherige Codex-Work-Session übernehmen willst.

Der Planer soll kein einzelnes Dokument mit sechs globalen Ansichten sein. Zielrichtung ist ein Betriebssystem für viele echte Arbeitskörper, Dateien, Quellen, Kanten, Ereignisse und unterschiedliche Werkstätten. Der Browser ist Oberfläche; VPS-Dateien und der Serverzustand sind die gemeinsame Wahrheit.

## Reale Orte

- Projekt: `/root/werkraum/Mein-Gesamtkonstrukt-planer/`
- Öffentliche Seite: `https://flextrawurst.de/Mein-Gesamtkonstrukt-planer/`
- Service: `worldwords-antibibel.service`
- Serverlogik: `server/planner_api.py`
- Hauptoberfläche: `app/index.html`
- Nachgeladene Schichten: `server/sync.js`, `server/workspace.js`, `server/streams.js`, `server/universal_notes.js`, `server/dom_contract.js`, `server/replica_registry.js`, `server/operating_shell.js`
- Gemeinsamer Zustand: `data/current.json`
- Arbeitsbaum: `data/tree/`
- Agenten-/Menschenprotokoll: `data/ai_spuren.json`
- Container-Vertrag: `data/replica_containers.json`

## Was Codex tatsächlich gebaut oder geändert hat

### Arbeitsraum und Herkunft

- Dateibaum kann Dateien/Ordner anlegen, bearbeiten, umbenennen, verschieben, einklappen und in den Papierkorb legen.
- Eine übernommene Datei wird als reales Arbeitsobjekt mit `werkraum://...`-Herkunft angelegt.
- Umbenennen/Verschieben schreibt die Herkunft der betroffenen Arbeitsobjekte um.
- Universelle Notiz erzeugt Datei, Arbeitsobjekt und Kante.
- `Arbeitsobjekt aktualisieren` liest die reale Quelldatei erneut in das übernommene Objekt ein.
- `dom_contract.js` markiert Quellen, Werkzeuge und eindeutige Objektbezüge im DOM.

### Betriebssystem-Hülle

`server/operating_shell.js` fügt den sichtbaren Knopf **Betriebssystem** ein. Die Hülle hat:
- Arbeitsraum-Baum links;
- gewählten Arbeitskörper/Werkstatt in der Mitte;
- Werkstattwahl rechts;
- mobile Umschaltung Ort / Körper / Werkzeuge;
- bewusste Graph-Ebenen als Darstellungskonzept.

Wichtig: Das ist ein begonnener Ersatzkörper, keine abgeschlossene UI-Neugestaltung. Die Legacy-Oberfläche existiert weiter.

### Replica-Vertrag und Ablagen

`server/replica_registry.js` enthält 17 Werkstatt-IDs:
`sketch, reference, cluster, knowledge, paint, vector, automation, blueprint, geometry, procedure, live, signal, analysis, organize, code, version, interface`.

Für jede dieser Werkstätten existiert ein eigener realer Container unter:
`01_Material/Replica-Container/<id>-eigen/`

Zusätzlich existiert ein realer Mehrfachcontainer:
`01_Material/Replica-Container/visual-thinking/`

Zugriff dort: `cluster, knowledge, reference, sketch`.

Die Verankerung steht in `data/replica_containers.json`. Der Server prüft bei einer Werkstattoperation, ob die gewählte Werkstatt in `replicaIds` steht. Ein nicht erlaubter Container wird abgewiesen.

### Browser- und Plattenbeleg

Im sichtbaren VPS-Desktop-Browser wurde die Skizzen-Werkstatt geöffnet, der Container `visual-thinking` gewählt und echte Daten gespeichert.

Belegte Dateien:
- `01_Material/Replica-Container/visual-thinking/Operationen/sketch/20260823T044103Z_Pfeil.md`
- `01_Material/Replica-Container/visual-thinking/Inhalte/sketch/20260823T044243Z_arrow.json`
- `01_Material/Replica-Container/visual-thinking/Inhalte/sketch/20260823T045128Z_shape.json`

Für die letzte Datei zeigte der sichtbare Browser:
`Skizzenelement gespeichert: ...shape.json · Container visual-thinking · Objekt + Kante`

Skizze hat damit als erste Werkstatt ein eigenes strukturiertes Dateiformat:
`gkos.sketch.element.v1`.
Stift/Form/Pfeil/Gruppe schreiben JSON-Elemente, nicht nur eine allgemeine Operationsnotiz.

## Protokollspuren, die dazu gehören

In `data/ai_spuren.json`:
- `spur-5a9cd321-b1a4-4832-9523-5e7a21bda13f` — Entscheidung: Mehrfachzugriff auf Werkstattcontainer
- `spur-29540502-4ab7-416b-85cc-191634fceed9` — Browser- und Plattenbeleg Container
- `spur-447a5446-c927-4f89-917a-e0dc2a34262c` — Folgepunkt: Skizze braucht räumliche Werte, Auswahl/Manipulation und Zeichenfläche

Weitere vorhandene Lesepfade:
- `00_Start/00_GESAMTKONSTRUKTBETRIEBSSYSTEMKOSMOS.md`
- `00_Start/01_AKTIVER_ARBEITSKOERPER.md`
- `00_Start/02_DOM_VERTRAG_FUER_WESEN.md`
- `00_Start/03_UI_NEUBAU_ARBEITSRAUM_KOERPER_WERKZEUG.md`
- `03_Abläufe/02_AUFBAUZUG_REPLICA_WERKSTAETTEN.md`
- `03_Gemeinsame_Arbeit/BAUGESCHICHTE_GESAMTBETRIEBSSYSTEM.md`
- `03_Gemeinsame_Arbeit/01_REPLICA_RECHERCHE_ERWEITERUNGEN_UND_NUTZERWUENSCHE.md`
- `03_Gemeinsame_Arbeit/02_CLOUDBROWSER_GEGENPROBE_REPLICAS_2026-08-22.md`

## Nicht als gebaut ausgeben

- Die globale Architektur Start / Canvas / Netz / Plan / Zeitspur / Replicas ist noch nicht ausreichend in Werkzeuge am gewählten Bestand überführt.
- Die neue Betriebssystem-Hülle ist keine fertige Desktop- oder Mobile-UI.
- Die meisten 17 Werkstätten haben noch keine eigene Kernhandlung mit eigenem strukturiertem Ergebnis. Der Registry-Eintrag und der eigene Container allein reichen nicht.
- Skizze speichert Elemente, hat aber noch keine echte freie Zeichenfläche, Geometrie, räumliche Werte, Auswahl, Verschiebung oder Gruppenbearbeitung.
- Reference, Cluster und Knowledge dürfen den Mehrfachcontainer benutzen, haben aber noch keine eigene strukturierte Fachdatei.
- Andere Werkstätten erzeugen derzeit überwiegend dokumentierte Operationen; das ist kein Ersatz für ihre eigentlichen Fachhandlungen.
- Die alten Ordner `07_AI-Spuren` sind noch vorhanden. Nicht blind löschen: Inhalte vergleichen, Umzug belegen, dann kontrolliert bereinigen.
- Mobile Bedienbarkeit ist nicht abgeschlossen.

## Sinnvolle nächste Reihenfolge

1. Skizze vollständig machen: sichtbare Zeichenfläche, Elementpositionen, Auswahl, Verschieben, gruppierbare Beziehungen, Reload-Test.
2. Reference / Cluster / Knowledge als zusammenhängendes erstes Mehrfachcontainer-System bauen:
   - Reference erzeugt Referenzkarten mit Quelle;
   - Cluster ordnet dieselben Karten in Frames/Cluster;
   - Knowledge erzeugt Rückverweise/Auszüge ohne neue Fakten oder Kanten zu erfinden.
3. Jede danach folgende Werkstatt einzeln anhand ihrer eigenen Kernhandlung bauen und testen; nicht 17 Oberflächen parallel faken.
4. Erst wenn Werkstätten echte Daten erzeugen, den globalen Wechsel von „Tabs“ zu „Werkzeuge am gewählten Bestand“ auch in Legacy, Mobil und Deep-Link-Struktur durchziehen.
5. Nach jedem Fix: echter Browser-Test, Reload, Sokrates-Frage, dreifaches Redteam, Folgepunkt als gemeinsame Spur.

## Arbeitsregel für Übernahme

Keine Abschlussbehauptungen ohne Browser- und Reload-Beleg.
Keine neue globale UI, bevor die nächste konkrete Kernhandlung einer Werkstatt feststeht.
Nicht einfach weitere MD-Manifeste erzeugen: Dateien nur dann, wenn sie einen echten Einstieg, Beleg, Arbeitskörper oder Übergabepunkt liefern.
