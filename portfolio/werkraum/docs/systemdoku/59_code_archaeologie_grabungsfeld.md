# Grabungsfeld: simulierter Ordnerbaum für die Code-Archäologie

Entstanden am 17.08.2026, direkt im Anschluss an den Dropdown/Suche-Ausbau
(`58_code_archaeologie_tab_dropdown_suche.md`), gleiche Session. Reine Faktenchronik.

---

## Ursprung

Daniel, 1:1: "ich will eig so ne art eigenes simuliertes ordnerbaum ähnlich wie vps z.b
nur selbstgewählte ordnernamen und pfade weil es ja archäologisch ist etc". Auf
Rückfrage geklärt: der Baum folgt **echter Chronologie**, nicht frei erfundenen Ordnern
und nicht 1:1 dem echten Dateisystem-Pfad — ein simulierter Baum, dessen "Ordner"
tatsächliche Zeitabschnitte sind, mit archäologischer Namensgebung.

## Konzept

- **Fundstätte** = `agent/dak_gord_system` (aktuell einzige, könnte später erweitert werden).
- **Schicht** = ein Kalendermonat, gebildet aus den echten `mtime`-Werten aller `.py`/`.md`-
  Dateien darunter. Älteste Schicht zuerst (wie bei einer echten Grabung: die tiefste,
  älteste Schicht wird zuerst freigelegt).
- **Fund** = eine einzelne Datei. Zwei Zustände: **ausgegraben** (schon in
  `docs/code_archaeologie_historiendoku.md` unter einer "Datei N"-Überschrift
  dokumentiert) oder **unausgegraben** (existiert, aber noch nicht archäologisch
  aufgearbeitet).

## Gebaut

### Backend (`welt/api.py`)

- `GET /code-archaeologie/baum` — läuft `agent/dak_gord_system` rekursiv ab, bucketet
  nach `YYYY-MM`, gibt pro Schicht Titel, Fundzahl, ausgegraben-Anzahl und die einzelnen
  Funde zurück.
- `_ca_ausgegrabene_pfade()` — parst `historiendoku.md` nach `## Datei N — ...`-
  Überschriften und backtick-zitierten Pfaden. **Zweistufig**, weil Daniels eigener
  Schreibstil oft nur den Dateinamen nennt, nicht den vollen Pfad (z.B. Datei 4, die
  sieben "Organ"-Fragmente: nur `` `beziehungsnaehe.md` `` im Text, nicht der volle
  relative Pfad): erst volle Pfade direkt aus der Überschrift, dann Basisnamen-Abgleich
  gegen die Liste echter Dateien — nur bei eindeutigem Treffer (genau eine Datei mit
  diesem Namen) wird zugeordnet. Ergebnis nach dem Fix: Schicht März 2026 zeigt 12/21
  ausgegraben statt vorher nur 5/21 mit der einfachen Variante.
- `GET /code-archaeologie/rohdatei?pfad=...` — liest den Rohinhalt eines unausgegrabenen
  Fundes. Bewusst eng begrenzt (nur Pfade unterhalb von `agent/dak_gord_system`, per
  `resolve()` gegen Pfad-Traversal geprüft), kein allgemeiner Datei-Lese-Endpunkt.

### Frontend (`scripts/build_surface.ts`)

Modus-Umschalter im Tab: "Fund-Strom" (bestehende Ansicht) vs. "Grabungsfeld" (neu).
Grabungsfeld zeigt aufklappbare Schichten, jeder Fund mit Symbol (◆ ausgegraben, ◇
unausgegraben) und bei ausgegrabenen Funden die Fund-Nummer. Klick auf einen Fund öffnet
je nach Status entweder die passende Historiendoku-Stelle (Volltextsuche nach dem Pfad)
oder den rohen Dateiinhalt über den neuen `/rohdatei`-Endpunkt — im selben Popup-Mechanismus
wie die bestehenden "Original-Dateien"-Links.

## Getestet, mit einem echten Fund unterwegs

Playwright-Lauf deckte einen echten Fehler auf: der neue `/rohdatei`-Endpunkt lieferte
zunächst 404, weil `welt-api.service` nach dem Hinzufügen der Route nicht neu geladen war
— kein Logikfehler, ein vergessener Neustart. Nach Neustart erneut getestet: funktioniert.
4 neue dauerhafte Tests in `tests/surface_ring_23.test.ts` (Modus-Umschalter im DOM, echter
Baum-Endpunkt statt fester Liste, beide Fund-Zweige rufen echte Endpunkte auf,
JS-Syntaxprüfung) — 107/107 Tests grün.

## Was noch fehlt

- Nur eine Fundstätte (`dak_gord_system`) — sobald weitere Systeme archäologisch
  aufgearbeitet werden, müsste `_CA_ARCHAEOLOGIE_WURZEL` zu einer Liste werden.
- Kein Live-Update speziell für den Baum-Modus verdrahtet — er lädt sich neu, wenn der
  Tab aktiv ist und sich eine der vier Archäologie-Dateien ändert (über den bestehenden
  `system.codearchaeologie`-Watcher), aber nicht wenn sich eine *rohe* Fund-Datei selbst
  ändert (dafür bräuchte es einen zweiten Watcher auf `agent/dak_gord_system/**`, nicht
  gebaut, kein Auftrag).
