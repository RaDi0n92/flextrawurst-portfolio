# Echte Pfade (Stufe 5) — letzter Punkt vom Megaplan, mit echtem Freigabe-Workflow

Ursprünglicher Wunsch: Pfade/Dateien "von ganz root an" hinzufügen können, einzeln oder
als Ordner, damit AI-Ströme ohne eigenen Terminal-Zugriff (z.B. ein reines Web-/MCP-
Anbindung) echte Dateien lesen und beschreiben können, um Projektwissen zu vermitteln
(Idee + Konzeptdatei + Surface-Code zusammen).

## Weg dahin — drei Design-Iterationen, nicht eine

**Erster Anlauf (direktes Sofort-Schreiben, ganzes Dateisystem, OS-Schutz ab):**
zweimal vom Auto-Mode-Klassifizierer blockiert, auch nach expliziter, informierter
Zustimmung von Daniel. Grund erkannt: das hätte bedeutet, dass ein Login allein
sofortigen, unbeaufsichtigten Schreibzugriff aufs ganze Server-Dateisystem gibt - bei
einer App, die heute schon einmal eine echte Sicherheitslücke hatte.

**Zweiter Anlauf (Referenzliste statt Schreiben):** von Daniel abgelehnt - er wollte
wirklich, dass Ströme ohne Terminal auch schreiben können, nicht nur verweisen.

**Dritter Anlauf, umgesetzt:** Freigabe-Workflow. Kein Endpunkt schreibt direkt - ein
Vorschlag (`propose-write`) wird als `pending_change` gespeichert, ohne die echte
Datei anzufassen. Nur `approve` schreibt wirklich, und genau dieser Endpunkt ist -
bewusst, live geprüft - auch für mich selbst (Claude Code) vom Klassifizierer
blockiert, wenn ich ihn automatisiert aufrufe. Das ist kein Bug, das ist die Grenze,
die Daniel wollte: nur ein echter Mensch klickt "Übernehmen".

Zusätzlich, auf Daniels ausdrücklichen Wunsch ("wir sichern die Seite natürlich auch
mit Nutzer und Passwort wie alle anderen wichtigen URLs"): der ganze Planer liegt jetzt
zusätzlich hinter HTTP Basic Auth (`auth_basic "Werkraum"`, dieselbe `.htpasswd` wie
Daniels andere Werkraum-Bereiche) - eine zweite Schutzschicht vor dem Django-Login.

## Architektur (real_fs_api.py)

- **Harte, im Code verankerte Grenze:** `ALLOWED_ROOT = Path("/root")` - nicht das
  ganze Server-Dateisystem, aber alles was Daniel wirklich braucht (auch die Surface,
  die außerhalb von `/root/werkraum` liegt). Jeder Pfad wird über `.resolve()`
  aufgelöst (auch Symlinks) und danach gegen diese Grenze UND die jeweilige
  Eintrags-Wurzel geprüft - ein `..`-Trick oder Symlink-Ausbruch kann nicht raus.
- **Lesen (list/add/remove/browse/read)** ist direkt möglich - reine Auskunft.
- **Schreiben (propose-write → approve/reject)** ist zweistufig. Vor jedem
  tatsächlichen Schreiben: automatisches Backup der vorher existierenden Datei
  (`data/realfs_backups/`, Grundgesetz 4).
- Auth: dasselbe `is_staff`-Gate wie die übrigen Planer-APIs, plus jetzt zusätzlich
  Nginx-`auth_basic` für den ganzen Planer.

## Frontend (real_fs_ui.js)

Neues Fenster "Echte Pfade" (GKWindows, wie alle anderen Panels): Pfad-Hinzufügen-
Formular, Liste der Einträge, einfacher Ordner-Browser (Klick zum Reingehen, "hoch"
zum Zurückgehen), Text-Editor für Dateien mit "Änderung vorschlagen"-Knopf, und eine
Liste "Offene Vorschläge" mit Vorher/Nachher-Vorschau und Übernehmen-/Verwerfen-
Knöpfen.

## Live verifiziert, komplette Kette

1. Pfad hinzugefügt: `/root/werkraum/Mein-Gesamtkonstrukt-planer/data/tree/Claude_Work`
2. Echten Ordner durchsucht (zeigt echte Dateien wie `00_CLAUDE_WORK_SESSIONKOERPER.md`)
3. Schreibvorschlag für `REALFS_TEST.md` eingereicht - **Datei existierte danach
   nachweislich noch nicht** (extra geprüft, nicht nur angenommen)
4. Vorschlag stand korrekt in "Offene Vorschläge"
5. **Daniel selbst** hat im echten Browser auf "Übernehmen" geklickt
6. Datei existiert jetzt wirklich, exakter vorgeschlagener Inhalt, kein Backup (weil
   keine Vorgängerdatei da war - korrektes Verhalten)
7. "Offene Vorschläge" ist danach leer - sauber aufgelöst

Damit sind jetzt wirklich alle sechs Stufen des Megaplans umgesetzt, inklusive der
riskantesten, mit einem Sicherheitsdesign, das eine echte, heute schon einmal
gefundene Schwachstellenklasse (unbeaufsichtigter Schreibzugriff) strukturell
ausschließt.

## Lehre für nächstes Mal — Settings-Bearbeitung per WinSCP/Notepad über Remote Desktop

Mehrfach brachen lange Textzeilen beim Copy-Paste über die Remote-Desktop-Verbindung
hart um (echte Zeilenumbrüche mitten im String, nicht nur optisch) - unabhängig vom
Zieleditor (WinSCP-intern, Notepad) und unabhängig von der Textlänge (auch kurze neue
Zeilen brachen). Half: möglichst kurze Regeltexte, Fenster maximieren vor dem Einfügen.
Nicht zuverlässig lösbar von meiner Seite - eine Grenze der Umgebung, kein Bug in
meinem Vorgehen.
