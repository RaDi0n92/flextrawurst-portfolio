# Ordnerbaum + Chronologie-Fix für die Code-Archäologie

Entstanden am 17.08.2026, direkt im Anschluss an das Grabungsfeld
(`59_code_archaeologie_grabungsfeld.md`), gleiche Session. Reine Faktenchronik.

---

## Ursprung

Nach dem ersten Blick auf Grabungsfeld meldete Daniel zwei getrennte Dinge:

1. Verwirrung über die Daten selbst: "warum ist im Juni Mai was drin, da haben wir keine
   Datei angefasst" — berechtigte Frage, kein Missverständnis seinerseits.
2. Die eigentliche Vorstellung, die er von Anfang an hatte, wurde nicht erfüllt: "das
   sollte ein neuer Tab daneben sein ... mit einem Ordner Baum kann man Ordner und
   Unterordner hat und einzelne Dateien dann findet."

## Teil 1 — Chronologie-Fix

Nachgeprüft statt vermutet: sowohl Datei-mtime als auch "erster Git-Commit" erwiesen sich
als unzuverlässig.

- `zustand.py`: mtime zeigt August 2026, `git status` zeigt aber keine Änderung seit
  Juli/März — ein Hintergrundprozess berührt mtimes ohne Inhaltsänderung (vermutlich
  Obsidian-Vault-Sync o.ä.).
- Derselbe Datei erster Git-Commit im `/root/werkraum`-Pfad-Alias: 2026-04-04. Im
  `/root/werkraum_agent`-Alias (physisch derselbe Ordner, anderer Symlink-Pfad):
  2026-07-21. Beides falsch — die Historiendoku hatte schon 2026-03-24 händisch
  verifiziert.

**Fix:** dreistufige Datumsquelle, gestaffelt nach Verlässlichkeit —
1. Historiendoku-„Entstehungsdatum" (verifiziert, aus `**Entstehungsdatum:**`-Zeilen
   geparst) für bereits „ausgegrabene" Dateien.
2. Erster Git-Commit als Fallback (besser als mtime, weil ein Commit nicht ohne echte
   Aktion entsteht).
3. mtime als letzter Ausweg.

Nur Fall 1 gilt als gesichert — Fall 2/3 werden mit `datum_geschaetzt: true` markiert.
Ergebnis: März 2026 zeigt jetzt korrekt 21/22 ausgegraben (vorher fälschlich in mehrere
Monate verstreut), alle unsicheren Einträge sind ehrlich sichtbar statt falscher Präzision.

**Performance-Nebenfund:** der zugrundeliegende `git log`-Aufruf + Regex-Parse dauerte
~2,85s pro Anfrage — beim Playwright-Review fiel auf, dass ein kurzer Seitenaufruf dadurch
wie ein kaputter, ewig ladender Tab wirkte. 60s-Cache eingebaut, zweiter Aufruf: 0,009s.

## Teil 2 — echte Lesbarkeit im Grabungsfeld

Nach dem Datumsfix, mit Playwright wirklich angeschaut (Screenshots, nicht nur DOM-Checks):
volle Pfade (`agent/dak_gord_system/aufforderungen/beziehungsnaehe.md`) wiederholten sich
105-mal in der April-Schicht, die "geschätzt"-Markierung (`~`) war winzig und leicht zu
übersehen. Fix: gemeinsamer Präfix weggekürzt, Ordner-Teil vom Dateinamen optisch getrennt
(abgeblendet vs. hervorgehoben), Tilde durch lesbares "GESCHÄTZT"-Badge ersetzt (auch als
Zusammenfassung im Schicht-Kopf, z.B. "105 geschätzt").

## Teil 3 — echter Ordnerbaum (neuer dritter Modus)

Neuer Endpunkt `/code-archaeologie/verzeichnisbaum`: rekursiver, echter Verzeichnisbaum von
`agent/dak_gord_system`, keine Simulation — Ordner bleiben Ordner (`graph/nodes/`,
`graph/tools/`, `graph/evals/` usw.), alphabetisch sortiert, Ordner vor Dateien, leere
Ordner ausgeblendet. Frontend: dritter Modus-Button "Ordnerbaum" neben Fund-Strom und
Grabungsfeld, rekursives Aufklappen pro Ordner, Klick auf Datei öffnet denselben Popup-
Mechanismus wie überall sonst.

**Dabei gefundener Datenfehler:** `beziehungsnaehe.md` (gehört zu "Datei 4", den sieben
Organ-Fragmenten) wurde fälschlich "Datei 2" zugeordnet — Datei 2s eigener Text erwähnt sie
nur beiläufig in einer Komma-Aufzählung, bevor Datei 4 sie richtig definiert, und das
bisherige Basisname-Matching nahm den ersten Treffer statt der echten Definition. Fix: nur
Doppelpunkt-Definitionen zählen (`` `name.md`: ... ``), keine bloße Erwähnung.

## Getestet

8 neue dauerhafte Tests insgesamt über beide Feature-Commits (Grabungsfeld-Lesbarkeit +
Ordnerbaum), 113/113 Tests grün. Playwright-Screenshots von allen drei Modi angeschaut
(nicht nur DOM-Existenz geprüft) — dabei zwei echte Bugs gefunden: einen Escaping-Fehler
im Regex-Literal (derselbe Bug-Typ wie beim `\'`-Fund vorher, diesmal `\/` in einem
Regex-Pattern innerhalb des großen Template-Literals) und die 2,85s-Ladezeit.

## Was noch fehlt

- Nur eine Fundstätte — sobald weitere Systeme archäologisch aufgearbeitet werden, müsste
  sowohl `/baum` als auch `/verzeichnisbaum` mehrere Wurzeln unterstützen.
- Kein Live-Update für den Ordnerbaum-Modus (Cache-TTL 60s reicht für jetzt, kein Auftrag
  für einen eigenen Watcher).
