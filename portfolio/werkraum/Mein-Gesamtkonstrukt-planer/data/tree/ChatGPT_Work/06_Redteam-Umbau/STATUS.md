# Redteam-Umbau · belastbarer Status

Nur mit `[x]` markierte Punkte haben einen konkreten Bau- und Prüfnachweis. Sichtbarkeit oder UI-Reaktion allein zählt nicht.

## Bestätigt

- [x] VPS ist die gemeinsame Wahrheit für den Planerzustand; Browserzustand ist nur Oberfläche/Cache.
- [x] Echter Arbeitsbaum mit Erstellen, Bearbeiten, Verschieben, Umbenennen, Arbeitsobjekt-Übernahme und Papierkorb existiert.
- [x] Feedback kann Belegfelder und eine gespeicherte Markierungs-ID tragen.
- [x] Eine von Feedback referenzierte Markierungsansicht wird beim Leeren geschützt.
- [x] Persistenzfehler durch zu großes `keepalive`-Speichern wurde in `server/sync.js` entfernt; ein PUT-200 und nachfolgender Serverstand wurden geprüft.

## Nicht abgeschlossen / Gegenbeweise bleiben aktiv

- [ ] Freies Feedback auf beliebige Stellen und Selbstbezug ist nicht vollständig als reale Nutzerhandlung geprüft.
- [ ] Entkopplung einer Markierung mit Grund/Autor/Ereignis wurde umgebaut, aber wegen blockierter Browserautomation noch nicht live geprüft.
- [ ] Konflikthinweis und echte feldweise Konfliktauflösung sind nicht ausreichend.
- [ ] Mobile 390×844 und jede Replica-Kernhandlung sind nicht vollumfänglich geprüft.
- [ ] `07_AI-Spuren` nach `03_Gemeinsame_Arbeit` ist nicht bereinigt/migriert; Altbestand bleibt bis zum Vergleich erhalten.
- [ ] Die neuen Arbeitskörper-Dateien sind noch nicht als bewusste Planerobjekte/Kanten über die UI verankert.
- [ ] Die sichtbare Cloud-Browser-Automation war beim direkten UI-Test nicht erreichbar (Tab-Auflistung lief in ein Zeitlimit). Die URL liefert den neuen Einstiegscode aus; die menschliche Durchklick-Prüfung bleibt deshalb offen statt behauptet.

## Verbindlicher nächster Test

Live-UI/Playwright wiederherstellen → `00_Start/01_AKTIVER_ARBEITSKOERPER.md` öffnen → als Arbeitsobjekt übernehmen → Herkunft und Kante nach Reload prüfen → daraus Folgefeedback nach der vollständigen Schleife erzeugen.