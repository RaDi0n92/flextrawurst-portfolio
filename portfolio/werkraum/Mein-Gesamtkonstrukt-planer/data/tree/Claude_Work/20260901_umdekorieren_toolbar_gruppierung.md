# Umdekorieren, Teilschritt 1: Haupt-Toolbar gruppiert

Auftrag (Daniel, 2026-09-01): "optik und layout, struktur auch" - komplett umdekorieren nach der Griffe-Reparatur. Start mit der Haupt-Toolbar, da diese ~15 Buttons in einer Reihe hatte, rechts abgeschnitten ohne erkennbare Ordnung.

Neue Datei server/human_redesign.js (zusaetzliche Stil-/Struktur-Schicht, gleiche Methode wie operating_shell.js/human_start.js - bestehende Buttons werden nicht neu erzeugt, nur per DOM-Verschiebung in benannte Gruppen sortiert, Klick-Handler bleiben dabei erhalten weil appendChild verschiebt statt kopiert). In planner_api.py als HUMAN_REDESIGN_JS registriert und injiziert - brauchte Neustart (Freigabe erhalten, worldwords-antibibel neu gestartet).

Gruppen: SICHERN (Server-Revision, gruen hervorgehoben, wichtigste Aktion) - ERFASSEN (Notiz hier) - WERKRAUM (Start hier, Ordner & Dateien) - ZUSAMMENARBEIT (Gemeinsame Arbeit) - ANSICHT (Betriebssystem, Telefon pruefen) - FEEDBACK & EXPORT (Stimmt so nicht, Uebergabe kopieren, Sicherung).

Zwei eigene Bugs beim Bauen gefunden und behoben:
- Buttons wie "Start hier"/"Telefon pruefen" wurden von der App erst NACH meinem ersten Sortier-Durchlauf ins DOM eingefuegt - mein Einmal-Guard hat eine Nachsortierung verhindert, sie blieben lose aussenvor. Fix: build() erkennt jetzt bei jedem Aufruf lose (noch nicht gruppierte) Buttons und ordnet sie ein, bricht aber sofort ab wenn nichts lose ist (kein Endlos-Loop mit dem MutationObserver).
- Erster Versuch liess den Header per flex-wrap auf mehrere Zeilen umbrechen - das Grid darunter (main.app-shell, display:grid mit fixer Pixel-Zeilenhoehe fuer den Header) hat sich nicht mitangepasst, dadurch ueberlappte die zweite Zeile den Inhalt darunter. Fix: Header bleibt einzeilig, top-actions ist stattdessen horizontal scrollbar mit einem Fade-Verlauf am rechten Rand als Hinweis dass mehr folgt, statt hart abzuschneiden.

Live getestet: alle Gruppen sichtbar/erreichbar per Scroll, Klick auf einen verschobenen Button ("Stimmt so nicht") funktioniert unveraendert (Flagging-Modus aktiviert sich korrekt).

Noch offen: das war nur die Haupt-Toolbar. Linke Objektliste, rechte Werkstatt/Metadaten/Verlauf-Spalte und die Werkstatt-Inhalte selbst sind noch nicht angefasst.
