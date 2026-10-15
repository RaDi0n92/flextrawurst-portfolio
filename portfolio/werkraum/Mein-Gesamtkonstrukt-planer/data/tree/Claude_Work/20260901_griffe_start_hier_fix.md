# Griffe reparieren, Schritt 1: "Start hier"

Neuer Arbeitsauftrag (2026-09-01): nicht Daniels Grundauftrag war die ChatGPT-Roadmap, sondern die urspruengliche Bitte, kaputte/generische Einstiegspunkte ("Griffe") zu reparieren, ohne die bestehende Struktur neu zu bauen. Arbeitsweise: im echten Browser alles anklicken, ansehen, Notizen/Spuren hinterlassen, dann erst weitergehen.

Systematisch durchgeklickt: Plan, Zeitspur, Replicas, Notiz hier, Stimmt so nicht, Übergabe kopieren, Telefon prüfen. Alle funktionieren echt (Plan = echtes Kanban, Zeitspur = echter Feed, Replicas = echter Node-Graph mit allen 17 Werkstaetten, Notiz hier = eigener Dialog, Stimmt so nicht = Klick-Flagging-Modus, Telefon prüfen = Mobil-Vorschau).

Ein echter kaputter Griff gefunden: "Start hier" (server/workspace.js) hatte einen hartcodierten Pfad "00_Start/README.md", der nicht mehr existiert (echte Datei liegt seit der Umstrukturierung unter ChatGPT_Work/00_Start/README.md). find(tree, pfad) lieferte null, wodurch "Start hier" stillschweigend genau dieselbe generische Wurzelansicht zeigte wie der Button "Ordner & Dateien" - zwei unterschiedlich beschriftete Buttons mit identischem, nicht-informativem Ergebnis.

Fix: start.onclick prueft jetzt beide moeglichen Pfade (neuer echter Pfad zuerst, alter als Fallback) und zeigt bei Fehlschlag eine ehrliche Fehlermeldung statt stumm ins Leere zu laufen. Live getestet: "Start hier" oeffnet jetzt korrekt die echte README.md mit dem tatsaechlichen Einstiegstext, Statuszeile zeigt den richtigen Pfad.

Naechster Schritt: weitere Einstiegspunkte pruefen (rechte Seitenleiste: Metadaten/Verlauf/Feedback-Tab, "Sicherung", "Gemeinsame Arbeit" und was noch rechts abgeschnitten ist), jeweils einzeln testen und dokumentieren bevor weitergegangen wird.
