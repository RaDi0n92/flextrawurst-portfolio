# Red-Team-Audit — AI UI Recorder v1.8.0

Datum: 2026-08-02  
Scope: Beweiskette, gesamte Recorder-Seitenleiste und reiner Code.  
Änderung am Recorder: **keine**. Dieser Bericht ist ein Befund, kein Fix.

## Methode und Grenze

Es wurden genau 99 unterschiedliche Szenarien ausgeführt: 33 gegen die
Beweiskette (`E`), 33 gegen die UI (`U`) und 33 gegen den Code (`C`).

Die kritischen UI-Zustandswechsel wurden nach Daniels Vorgabe im sichtbaren
virtuellen Desktop per Maus durchgeführt und jeweils nach 0,2 Sekunden per
Screenshot geprüft: Start, Pause, Fortsetzen, Stop, lokaler Reset sowie die
reinen Navigationen. Kein VPS-Schlüssel war hinterlegt; der Testscan wurde am
Ende sichtbar zurückgesetzt. Der Sendeknopf wurde nie angeklickt.

Statische Befunde sind ausdrücklich keine behaupteten Live-Fehler auf einer
fremden Provider-Oberfläche. Sie bezeichnen eine im Code vorhandene
Angriffsfläche, die noch gegen die jeweilige echte Oberfläche abgenommen
werden muss.

Ergebnis: **66 bestanden, 33 Befunde**.

## Tatsächlich bewiesene Ausgangslage

Im offenen Gordslider-Chat lagen am Ende acht Rollen-Nodes im DOM; genau eine
Turn-Fläche schnitt das echte Chatfenster. Die übrigen Nodes waren nicht nur
knapp außerhalb, sondern teils bis zu 673.000 CSS-Pixel versetzt. Damit ist
der alte DOM-Überlappungsbeweis für diesen Langchat widerlegt. Der neue
Viewport-Filter trennt diesen konkreten Angriff korrekt ab.

## Sofort relevante Befunde

1. **Beweisvollständigkeit darf nicht bei einem einzelnen Checkpoint entstehen**
   (`E24`, `C21`). Ein vollständiger Kettenclaim braucht mindestens einen
   dokumentierten Übergang, besser eine explizite Mindestzahl.
2. **`turn-N` wird als Primäranker weggeworfen** (`E15`, `C17`). Dadurch kann
   der Fallback zwei verschiedene, gleichlautende virtualisierte Beiträge
   zusammenführen (`E16`, `C18`).
3. **Ein leeres ACK kann einen Turn als vollständig markieren** (`C33`). Die
   Vollständigkeitsbestätigung muss eine erwartete ACK-Struktur und den
   korrekten Turnstatus verlangen.
4. **Nach Stop wird der VPS-Sendeknopf ohne Zugangsschlüssel aktiv** (`U12`).
   Der spätere Request scheitert vor `fetch`, aber die UI fordert zu einer
   unmöglichen und sensiblen Aktion auf.
5. **Kopfmetrik `Nachrichten` bleibt Roh-DOM** (`U03`, `C23`). Im selben
   Screen konnten „7 Nachrichten“ neben einer Sichtprüfung mit einem einzigen
   sichtbaren Output stehen.
6. **Lücken- und Klappbereichsknopf sind ohne Ziel aktiv** (`U14`, `U16`).
   Sie liefern nur einen kontrollierten Fehler; aktiviert sein dürfen sie
   trotzdem nicht.
7. **Drei DOM-XSS-Sinks im Sidepanel** (`U29`–`U31`): ausgeschlossene
   Chattitel, Klappbereichslabels und Providerdaten werden per `innerHTML`
   interpoliert.

## Szenarien — Beweiskette (33)

| ID | Szenario | Ergebnis |
|---|---|---|
| E01 | Erster Sichtstand erzeugt keinen Übergang | bestanden |
| E02 | Gleiche native ID beweist Übergang | bestanden |
| E03 | Disjunkte native IDs werden als Lücke markiert | bestanden |
| E04 | Exakt 8 Pixel zählen als Bewegung | bestanden |
| E05 | 7 Pixel zählen nicht als Bewegung | bestanden |
| E06 | Voller Sichtwechsel unter 8 Pixeln | **Befund:** unbeobachtete Blindstelle |
| E07 | Leerer Sichtstand nach Bewegung | bestanden, fail-closed |
| E08 | Zwei leere Sichtstände nach Bewegung | bestanden, fail-closed |
| E09 | ID-Überlappung trotz Umordnung | bestanden |
| E10 | Doppelte sichtbare ID bläht Overlap nicht auf | bestanden |
| E11 | Ereignis-ID ist importgebunden | bestanden |
| E12 | Textrevision erzeugt nachvollziehbares Ereignis | bestanden |
| E13 | Provider-ID hält Revision bei einem Primärbeitrag | bestanden |
| E14 | Stabiler DOM-Anker hält Primäridentität | bestanden |
| E15 | `turn-N` als dauerhafter Anker | **Befund:** wird verworfen |
| E16 | Gleicher Fallback-Text/Rolle/Ordinal | **Befund:** Kollisionsrisiko |
| E17 | Fallback trennt unterschiedlichen Text | bestanden |
| E18 | Fallback trennt unterschiedliche Rollen | bestanden |
| E19 | Manueller Scan kann nicht vollständig heißen | bestanden |
| E20 | Automatik ohne Anfang | bestanden, unvollständig |
| E21 | Automatik ohne Ende | bestanden, unvollständig |
| E22 | Automatik mit Lücke | bestanden, unvollständig |
| E23 | Automatik mit nur Baseline | Code akzeptiert sie formal |
| E24 | Ein Checkpoint als Kettenbeweis | **Befund:** zu schwache Bedingung |
| E25 | Fehlende Geometrie wird ausgewiesen | bestanden |
| E26 | `historyProof` erzwingt Geometry selbst | **Befund:** nur Normalpfad schützt |
| E27 | Adapter ohne Geometry-Capability | bestanden, kein Ersatzbeweis |
| E28 | Lückenclaim enthält keine Vollständigkeitsbehauptung | bestanden |
| E29 | Lückenprotokoll bewahrt von/bis-Position | bestanden |
| E30 | Sichtbare Adjazenz wird gesichert | bestanden |
| E31 | Checkpoint bekommt strict Viewportblocks, nicht Raw-DOM | bestanden |
| E32 | Snapshot erklärt `currently_loaded_dom_only` | bestanden |
| E33 | Normalexport bei retained Offscreen-DOM | **Befund:** Beschriftung irreführend |

## Szenarien — Bedienoberfläche (33)

| ID | Szenario | Ergebnis / Methode |
|---|---|---|
| U01 | Hauptschalter erklärt „Aus“ | bestanden, live sichtbar |
| U02 | Fehlender Schlüssel erklärt lokalen Puffer | bestanden, live sichtbar |
| U03 | Kopfmetrik `Nachrichten` | **Befund:** unmarkiertes Raw-DOM, live |
| U04 | Sichtprüfung trennt Sichtfenster/Raw-DOM | bestanden, live |
| U05 | Frischer Scan behauptet keine Kette | bestanden, live |
| U06 | Frischer Scan: Start aktiv, Pause/Stopp gesperrt | bestanden, live |
| U07 | Start einer lokalen Aufnahme | bestanden, Maus + 0,2 s Screenshot |
| U08 | Pause | bestanden, Maus + 0,2 s Screenshot |
| U09 | Fortsetzen | bestanden, Maus + 0,2 s Screenshot |
| U10 | Stop | bestanden, Maus + 0,2 s Screenshot |
| U11 | Lokaler Reset | bestanden, Maus + 0,2 s Screenshot |
| U12 | VPS-Senden nach Stop ohne Schlüssel | **Befund:** aktiv, nicht geklickt |
| U13 | Reset sperrt den Sendeknopf wieder | bestanden, live |
| U14 | Lückenknopf bei 0 Lücken | **Befund:** trotzdem aktiv |
| U15 | Leerer Lückenknopf verändert Chat nicht | bestanden, Maus + 0,2 s Screenshot |
| U16 | Klappbereichsknopf bei 0 Bereichen | **Befund:** trotzdem aktiv |
| U17 | Leerer Klappbereichsknopf öffnet keinen Text | bestanden, Maus + 0,2 s Screenshot |
| U18 | Vier Aufnahme-Exports ohne Aufnahme | **Befund:** aktiv, live sichtbar |
| U19 | Segmentexport weist leeren Abschnitt ab | bestanden, statisch |
| U20 | Normalexport deklariert Raw-DOM-Grenze | **Befund:** fehlt |
| U21 | Globaler Puffer-Sendeknopf ohne Schlüssel | **Befund:** nicht gesperrt |
| U22 | Automatik-Pause/Abbruch im Leerlauf | bestanden, gesperrt |
| U23 | Navigation während laufendem Import | bestanden, statisch gesperrt |
| U24 | „Nicht aufnehmen“ bei Freigabe | **Befund:** Zustandsumkehr möglich |
| U25 | Ausschluss ist klar als Gefahr markiert | bestanden, live sichtbar |
| U26 | Tab-Pause ist korrekt gegatet | bestanden, statisch |
| U27 | Manuelle Aufnahme ist korrekt gegatet | bestanden, statisch |
| U28 | Reset während Navigation wird gegatet | bestanden, statisch |
| U29 | Exclusion-Liste | **Befund:** `innerHTML`-XSS-Sink |
| U30 | Klappbereichslabels | **Befund:** `innerHTML`-XSS-Sink |
| U31 | Providerkatalog | **Befund:** `innerHTML`-XSS-Sink |
| U32 | Not-Aus-Aufhebung | **Befund:** schaltet global immer ein |
| U33 | Fehler nach Not-Aus | **Befund:** kein Rollback des globalen Schalters |

## Szenarien — Code und Robustheit (33)

| ID | Szenario | Ergebnis |
|---|---|---|
| C01 | Syntax aller aktiven JS-Dateien | bestanden (`node --check`) |
| C02 | Versionsnahe Tests in aktiver Quelle | **Befund:** fehlen |
| C03 | ChatGPT-Ladereihenfolge | bestanden |
| C04 | ChatGPT-Viewport-Capability | bestanden |
| C05 | Claude-Viewport-Capability | bestanden |
| C06 | Vollständig Offscreen liegende Turnfläche | bestanden, verworfen |
| C07 | Teilweise sichtbare Turnfläche | bestanden, gezählt |
| C08 | Nullbreiten-Fläche | bestanden, verworfen |
| C09 | Strict blocks für Checkpoint | bestanden |
| C10 | Rohsichtung bleibt Diagnose | bestanden |
| C11 | Scrollcontainer bei Claude | **Risiko:** ChatGPT-Selektor im Core |
| C12 | Feste UI verdeckt Chatfläche | **Risiko:** Geometrie zählt sie dennoch |
| C13 | Claude-Klappbereichsregex | **Risiko:** zu breit |
| C14 | ChatGPT schließt Bild/Datei/Dialog aus | bestanden |
| C15 | Rollen-Fallback ohne Marker | **Risiko:** alternierend erfunden |
| C16 | Stabile Ereignis-ID enthält alle Bindungen | bestanden |
| C17 | `turn-N` als Identität | **Befund:** verworfen |
| C18 | Fallback-Kollision | **Befund:** möglich |
| C19 | Keine Geometry-Capability | bestanden, fail-closed |
| C20 | Geometry als Kerninvariante | **Befund:** nicht in `historyProof` |
| C21 | Mindestzahl Checkpoints | **Befund:** nur >0 |
| C22 | Unbelegte Übergänge sind begrenzt | **Befund:** unbegrenzt |
| C23 | `pageStatus.message_count` | **Befund:** Raw-DOM |
| C24 | Synchroner Chrome-Runtime-Fehler | bestanden, abgefangen |
| C25 | Emit ohne Freigabe | bestanden, blockiert |
| C26 | Background prüft Eventfreigabe erneut | bestanden |
| C27 | provider_id gegen Sender-URL | **Risiko:** Gleichheitscheck fehlt |
| C28 | Fehlender Schlüssel vor Netzrequest | bestanden, nur lokal |
| C29 | Reset bewahrt Queue absichtlich | bestanden |
| C30 | Automatikgeschwindigkeit | bestanden, begrenzt |
| C31 | Sicherungsfehler bei Automatik | bestanden, pausiert |
| C32 | Unbekannte Live-Follow-Aktion | **Befund:** aktiviert Follow |
| C33 | Leeres ACK | **Befund:** kann `vollständig` ergeben |

## Was daraus nicht folgt

- Die 33 Befunde sind nicht gleich schwer. C11–C13, C15 und C27 sind
  statische Risiken, bis sie gegen eine echte Claude-/Provideroberfläche
  reproduziert sind.
- Der bestehende ChatGPT-Viewport-Fix ist durch diesen Audit nicht widerlegt.
  Im Gegenteil: Der ursprüngliche retained-DOM-Angriff wird im realen Langchat
  korrekt abgefangen.
- Es wurde keine Recorderquelle verändert und keine Aufzeichnung an den VPS
  gesendet.

## Empfohlene Fix-Reihenfolge — noch nicht ausgeführt

1. Ketteninvarianten: Geometry als Pflicht, mindestens zwei Checkpoints und
   mindestens ein belegter Übergang; `turn-N` als stabilen Anker behandeln.
2. ACK-Vertrag: nur erwartetes ACK mit passendem Turn-/Statusschema darf
   `vollständig` auslösen.
3. UI-Gating: leere Navigationsknöpfe, Exporte ohne Segment und Senden ohne
   Schlüssel deaktivieren; Kopfmetrik in „DOM angeheftet“ umbenennen.
4. Alle `innerHTML`-Sinks auf DOM-API oder Escaping umstellen.
5. Claude erst mit einer realen Claude-Fixture freigeben; Scrollroot und
   Klappbereichsdefinition an den jeweiligen Provideradapter binden.
