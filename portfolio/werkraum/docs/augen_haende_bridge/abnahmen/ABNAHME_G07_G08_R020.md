---
autor: claude bei Daniels VPS
datum: 2026-10-02
status: Entwurf zur Abnahme durch Daniel; nur auf dem VPS und unter Wine geprüft
herkunft: `PLAN.md` (G07, G08), `ANFORDERUNGEN.md` (R020, R036–R051, R113), Tests und Proben der Version 0.9.0-g02
---

# Abnahmeprotokoll G07 (Rest), R020 und G08 (Windows) — Version 0.9.0-g02

Ergänzt `ABNAHME_G05_G055_G07.md`. Zeichen: **belegt** (Test oder Wine-Probe), **nativ offen** (steht in `PRUEFLISTE_0.9.0.md`), **Lücke**, **Entscheidung**.

## G07 — jetzt vollständig bis auf Mikrofon und Replay

| Forderung | Stand | Beleg |
|---|---|---|
| Bildsequenz als Quelle (R038) | belegt (Test), nativ offen | Raute-Menü „Bildfolge (Ordner) an den Agenten …“: ab dem gewählten Bild alle Bilder des Ordners in Namensreihenfolge (höchstens 500), alle 2 s, mit Pausieren, Fortsetzen und Stoppen (`bildfolge.py`, 20 Tests). Not-Aus, „nur Terminal“, Agent entfernen und Beenden stoppen sie; nichts startet von selbst neu. |
| Frische, Überlast sichtbar (R042) | belegt (Test) | Das Bilder-Menü zeigt „Überlast: N verworfen“, wenn die Sendewarteschlange Bilder verwerfen musste; Frames tragen Quelle (`capture`, `file`), Zeit und Größe. |
| Replay (R037) | Lücke | Hängt an G13 (Zeitleiste), nicht gebaut. |
| Mikrofon nativ | offen | Von Daniel bis zum Schluss zurückgestellt. |

## R020 — Terminalansichten umbelegen

| Forderung | Stand | Beleg |
|---|---|---|
| Zwei Ansichten umbelegen; Quelle eindeutig, Sitzung bleibt erhalten | belegt (Test), nativ offen | Raute-Menü „Terminal-Platz tauschen …“: zwei Terminals tauschen Ort und Größe, jede Sitzung behält Terminal, Namen und Farbe; zweimal tauschen stellt den Ursprung wieder her; bleibt nach dem Neustart (normale Fenstereinstellungen). |

## G08 — Bilder, Texte und Zeichnen als gemeinsame Arbeitsfläche (Windows)

Entwurf (nach Daniels Entscheidung vom 2026-10-02: „nur da, wo der oder die Agenten sitzen, malen; ist es der ganze Desktop, dann dort“):
Ein Objekt gehört zu einem **Gate** (dem gebundenen Fenster, sonst dem Desktop). Es hat zwei unabhängige Einstellungen: **auf dem Bildschirm** (physisch sichtbar, damit im Basisbild jedes Agenten, der den Bereich sieht) und **nur im Bild bestimmter Agenten** (wird nur in deren Bild komponiert, nie auf den Bildschirm, nie in das Bild anderer).
Ein einziger Zeichner (`zeichnen_render.py`, Pillow) erzeugt alles, was jemand sieht: die Komposition in den Agentenbildern, die Anzeige auf dem Bildschirm und die Vorschau im Editor.

| Forderung | Stand | Beleg oder Lücke |
|---|---|---|
| Bilder, Text per Klick und Enter, Freihand, Marker, Farben, Strichstärken, Linien, Pfeile, Rechtecke, Kreise (R046–R049) | belegt (Test, Wine) | `editor_logik.py` (30 Tests), Werkzeugleiste und Editorfläche unter Wine bedient (`probes/zeichnen_smoketest.py`: Werkzeug gewählt, Rechteck mit Maus gezogen, Strg+Z). Bilder aus Dateien über „Bild …“. |
| Auswahl, Mehrfachauswahl, Gruppen, Resize, Z-Ordnung, Undo und Redo (R050) | belegt (Test) | Klick, Umschalt-Klick, Gummiband; Ziehen und Skalieren an den Ecken als je EIN Befehl; Gruppen bewegen gemeinsam; Z-Ordnung vor/zurück/ganz; Rückgängig und Wiederholen (200 Schritte); Dokument- und Editortests. |
| Objekte bleiben, bis Daniel sie entfernt oder ausblendet; ein Agentenwechsel verschiebt sie nicht (R051) | belegt (Test) | Objekte gehören zum Gate, nicht zum Agenten; gespeichert in `arbeitsflaeche.json`, wiederkommen nach dem Neustart, sobald dasselbe Programm (Name der exe) gebunden wird; Ausblenden statt Löschen möglich. |
| Gate, einzelner Agent, Daniel, Kombinationen und Ausschlüsse pro Objekt (R043, R113) | belegt (Test) | „Sichtbar für …“: Bildschirm ja/nein und je Agent „nur im Bild von …“, für die Auswahl oder für neue Objekte. Test mit dem echten Bilderstrom: Agent A bekommt das rote Rechteck im Bild, Agent B nicht. |
| Privates leckt weder in Basis-Capture noch Chat, Replay oder Export (R044) | belegt (Test), nativ offen | Komposition nur im Bild des Empfängers; die Anzeige auf dem Bildschirm zeigt nie Privates; Editor und Werkzeugleiste sind aus der Aufnahme ausgenommen, **und wo Windows das nicht kann, zeigt der Editor Privates gar nicht** (das ist unter Wine der Fall und getestet). Ob die Ausnahme bei Daniel wirkt, zeigt der Selbsttest. Export und Replay gibt es noch nicht. |
| Mindestens drei Empfänger erhalten verschiedene Inhalte | belegt (Test) | Zwei Agenten mit verschiedenen Objekten plus ein dritter ohne: jeder bekommt nur seins, der dritte das Basisbild unverändert. |
| Ein mehrfach markiertes Objektset bleibt speicherbar | belegt (Test) | Speichern und Laden inklusive Bildern, Gruppen, Empfängern; kaputte Dateien ergeben ein leeres oder teilweises Dokument, nie einen Absturz. |
| Objekte folgen dem Zielfenster | belegt (Test, Wine) | Relative Koordinaten; die Anzeige folgt Ort und Größe, verschwindet beim Minimieren und Schließen, kommt zurück. |
| Keine ungewollte Eingabe in die Anwendung darunter; Esc verlässt den Modus (UQ04) | belegt (Test) | Die Editorfläche fängt alle Maus- und Tastenereignisse; Esc bricht Zeichnen, Text und Auswahl der Reihe nach ab und beendet erst dann den Modus. |
| Eigenes Fenster je Teil (R118) | Entscheidung | Statt vieler kleiner Fenster steht je Gate **ein** durchklickbares Pixel-Alpha-Fenster über dem Gate (nur dort, wo Objekte auf dem Bildschirm stehen), und beim Zeichnen die Editorfläche. Das ist keine feste Vollbildfläche, aber eine Fläche über dem Ziel. Wenn Daniel kleinere Einzelfenster will: nachbauen. |
| Tastaturbedienung der Werkzeugleiste (UQ08) | Lücke | Die Leiste bedient man mit der Maus; Tastenkürzel gibt es für die wichtigsten Befehle. |
| Zeichnen auf KDE 1/2 | offen | Gehört zu G06 (Linux-Oberfläche), nicht gebaut. |

## Entscheidung (Daniel)

- G07: ☐ abgenommen mit Ausnahme (Mikrofon, Replay) ☐ erst nach der Prüfliste
- R020: ☐ abgenommen ☐ erst nach der Prüfliste
- G08 (Windows): ☐ abgenommen mit Ausnahme (R118-Frage, Export/Replay) ☐ erst nach der Prüfliste

## Nachtrag 0.9.1 (2026-10-02): Daniels Änderungswünsche nach dem Lesen der Prüfliste

Anlass: „Bilddatei an Agenten senden“ war meine Deutung von R038 „Einzeldatei“, nicht Daniels Wunsch; er wollte ein schwebendes, größenverstellbares, transparent einstellbares Bild-Element, dauerhaft im Gate und für einzelne oder mehrere Agenten einstellbar (der alte Menüpunkt bleibt zusätzlich). Zum Malen: sichtbare Werkzeuge, Ziel-Wahl wie beim Fensterscanner, Text, Radierer, Markieren, Rechtsklick-Menüs, Größe, Dicke, Fett/Kursiv/Unterstrichen/Schriftgröße, Transparenz.

| Wunsch | Stand | Beleg |
|---|---|---|
| Bild-Element (Menü „Bild einblenden …“) mit Größe, Deckkraft, Sichtbar-für | belegt (Test), nativ offen | `test_koerper_g08_erweiterung.py` (`test_bild_element_…`), Deckkraft im Renderer und Komposition |
| Werkzeuge mit Symbolen | belegt (Wine-Probe), nativ offen | `probes/zeichnen_smoketest.py` |
| Ziel-Wahl wie Fensterscanner | belegt (Test), nativ offen | Menü „Ziel …“, Fensterliste aus der Scanner-Aufzählung |
| Radierer, Markieren | belegt (Test) | Radierer löscht beim Loslassen als EIN Befehl; Auswahl = Markieren; Marker = Textmarker |
| Text: Fett, Kursiv, Unterstrichen, Größe, vorher einstellbar und nachträglich änderbar | belegt (Test, Wine für die Leiste) | Renderer mit Schriftvarianten (Windows: Segoe UI, sonst Arial/DejaVu), Zeilenaufbau für Rahmen und Zeichnen gleich |
| Rechtsklick-Menü für Gemaltes und Voreinstellungen | belegt (Test) | `Editor.kontext_eintraege/-ausfuehren`; Größer/Kleiner, Strich, Deckkraft, Farbe, Reihenfolge |
| Rechtsklick mit Strg+Alt „wie bei allem“ | belegt (Test, Wine), nativ offen | Zeichenfläche und Bild-Element öffnen das Menü nur mit gehaltener Bedientaste (Wine-Probe: ohne Taste kein Menü, mit Taste eins). Daniel hat meine erste Auslegung (ohne Bedientaste) ausdrücklich abgelehnt. |
| Bild-Element schwebend, immer direkt anfassbar | belegt (Test, Wine), nativ offen | Eigenes Fenster je Bild (`bild_element_fenster.py`, Abgleich in `bild_elemente.py`): Kopf zum Verschieben, Kanten für die Größe (Seitenverhältnis rastet ein), Prozent-Knopf und Mausrad für Deckkraft (kein X auf Daniels Wunsch, zu leicht versehentlich), Rechtsklick-Menü mit Sichtbar-für. Das Dokument bleibt die Wahrheit (Rückgängig, Speichern, Komposition); Objekte nur für Agenten stehen nur dort als Fenster, wo Windows sie aus der Aufnahme ausnimmt. Ausgeblendete Bilder kommen im Zeichenmodus über „Alle ein“ zurück. |
