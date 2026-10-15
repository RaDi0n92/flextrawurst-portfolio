# Griffe-Inventur: Haupt-Toolbar vollstaendig durchgeklickt

Systematisch, echt im Browser (nicht nur Code gelesen), jeden Griff einzeln geprueft.

Getestet und echt funktionsfaehig (keine Aenderung noetig):
- Legacy-Tabs: Start, Canvas (43 Knoten/37 Kanten, Zoom, Bearbeiten-Links), Netz (raeumliche Projektion, WebGL-Kompatibilitaetsmodus mangels /dev/dri), Plan (echtes Kanban Roh/Entwurf/Bereit), Zeitspur (echter chronologischer Feed), Replicas (echter Node-Graph mit allen 17 Werkstaetten, Excalidraw/tldraw-Ansicht als Beispiel)
- Notiz hier: eigener Dialog "Notiz verknuepfen", speichert echt als Datei+Objekt+Kante
- Stimmt so nicht: echtes Klick-Flagging fuer Feedback
- Übergabe kopieren: kopiert echtes strukturiertes Uebergabe-Dokument in die Zwischenablage (per navigator.clipboard.writeText Monkeypatch verifiziert)
- Sicherung: exportiert echtes Backup ("Vollstaendiges Backup exportiert")
- Ordner & Dateien: echter Dateibaum-Browser
- Telefon prüfen: echte Mobil-Vorschau (schmale Spalten-Ansicht derselben Inhalte)
- Gemeinsame Arbeit: echtes Spuren-Log (ai_spuren.json), Formular fuer neue Spuren funktioniert - das ist der Mechanismus, den ich ab jetzt fuer eigene Spuren nutze
- Idee / Frage / Aufgabe: legen echte neue Objekte an (Materialien-Zaehler steigt, Status "Ungespeicherte Arbeit")
- Malen & markieren: echtes Annotations-Werkzeug (Stift/Textmarker/Pfeil/Rahmen/Text/Radierer), sauber gekennzeichnet als "Annotation - keine Kante - keine Tatsache"
- Rechte Seitenleiste: Werkstatt/Metadaten/Verlauf/Feedback-Tabs alle echt (Metadaten = editierbare Objektfelder, Verlauf = echte Revisionshistorie r0-r5 + protokollierte Aktionen, Feedback·39 = echte offene/erledigte Liste mit 39/34 Eintraegen)

Ein echter kaputter Griff gefunden und behoben (siehe eigene Notiz griffe_start_hier_fix.md und Spur "Griff-Fix: Start hier" in Gemeinsame Arbeit): "Start hier" zeigte durch einen veralteten Pfad ins Leere.

Eigener Test-Nebeneffekt, nicht bereinigt (Grundgesetz 4, nichts loeschen): beim Pruefen von "Idee" und "Frage" wurden zwei echte Testobjekte ("Neue Idee", "Neue Frage" o.ae.) angelegt. Liegen jetzt echt im Bestand, klar als Testartefakt erkennbar am generischen Titel.

Ergebnis der Inventur: von rund 20 geprueften Haupt-Griffen war nur "Start hier" wirklich kaputt. Der Rest der Oberflaeche ist echt und funktioniert bereits - das juengere Bau-Urteil "vieles ist kaputte Fassade" hat sich bei genauerer Pruefung nicht bestaetigt.

Noch nicht geprueft: Detail-Controls innerhalb einzelner Ansichten (z.B. Suchfelder, Filter "Alle Typen/Alle Zustaende", einzelne Objekt-Aktionsknoepfe, Arbeitsvariante-Auswahl "haupt2"). Auf Daniels Rueckmeldung warten, ob dort weiter in die Tiefe gegangen werden soll oder ob das genug Grundlage ist fuer den naechsten Schritt (Umdekorieren).
