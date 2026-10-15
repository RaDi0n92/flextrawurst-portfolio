# Übergabekörper · Claude Work

Stand: 2026-09-01
Geltung: Dieser Text ist eine belegte Übergabe, kein Abschluss und kein Behauptungsersatz.

## Wofür dieser Körper da ist

Lies diese Datei zuerst, wenn du die bisherige Claude-Work-Session übernehmen willst.
Direkte Fortsetzung von ChatGPTs eigener Übergabe
(ChatGPT_Work/00_CHATGPT_WORK_SESSIONKOERPER.md) — die dort genannte Warnung
"keine neue globale UI vor Kernhandlung" wurde in dieser Session zuerst
übersehen, dann gefunden und befolgt.

## Was tatsächlich passiert ist, chronologisch und ehrlich

- Als "Claude Code" registriert in data/ai_spuren.json (Eintrag kind=uebergabe).
- Einen echten Backend-Bug gefunden und gefixt: BUILD_LOG-Pfad zeigte seit der
  ChatGPT_Work-Umstrukturierung ins Leere, jede create-Aktion im ganzen Tool
  schlug mit 500 fehl. Fix: Pfad korrigiert, plus defensives mkdir.
- Global neue Overlays gebaut (Start/Canvas/Netz als eigenständige
  Vollbild-Ansichten) — noch bevor die Warnung in ChatGPTs Übergabedatei
  gelesen war.
- Canvas und Netz wieder entfernt, nachdem sich zeigte: der native Canvas-
  und Netz-Tab funktionieren bereits. Nativer Canvas: 43 Knoten, 37 Kanten,
  Zoom, Bearbeiten-Links. Nativer Netz: räumliche Projektion, aktuell im
  WebGL-Kompatibilitätsmodus, weil der Container virtuellerdesktop1 kein
  /dev/dri durchgereicht bekommt — echte Infrastruktur-Lücke, kein Bug im
  nativen Code.
- Start (Schnellerfassung) behalten, aber von Vollbild-Overlay zu einer
  schmalen, immer sichtbaren Leiste direkt unter dem Header umgebaut, ohne
  den nativen Start-Tab zu überschreiben.
- Eigenen Fehler live verursacht und selbst wieder behoben: JS-Dateien vor
  dem zugehörigen Python-Neustart gelöscht, dadurch kurzzeitig ein echter
  500er auf der Live-Seite. Sofort per Neustart behoben.
- Danach ChatGPT_Work/00_CHATGPT_WORK_SESSIONKOERPER.md gefunden und
  gelesen — zu spät für den globalen UI-Umweg, aber rechtzeitig für den Rest.

## Was noch nicht als gebaut gilt

- Skizze, Reference, Cluster, Knowledge und die übrigen Werkstätten haben
  weiterhin keine eigene Kernhandlung — das war schon vor dieser Session
  offen und ist es weiterhin.
- Die Start-Leiste ist neu, aber nur eine schmale Schnellerfassung, kein
  Ersatz für eine echte Werkstatt.

## Sinnvolle nächste Reihenfolge

Übernommen von ChatGPTs Übergabe, nicht neu erfunden:

1. Skizze vollständig machen: sichtbare Zeichenfläche, Elementpositionen,
   Auswahl, Verschieben, gruppierbare Beziehungen, Reload-Test.
2. Reference, Cluster, Knowledge als zusammenhängendes
   Mehrfachcontainer-System bauen.
3. Jede weitere Werkstatt einzeln anhand ihrer eigenen Kernhandlung bauen,
   nicht 17 Oberflächen parallel vortäuschen.
4. Erst danach den globalen Wechsel von Tabs zu Werkzeugen am gewählten
   Bestand durchziehen.

## Arbeitsregel für Übernahme

Dieselbe wie in ChatGPTs Übergabe: keine Abschlussbehauptungen ohne
Browser- und Reload-Beleg, keine neue globale UI vor der nächsten
Kernhandlung einer Werkstatt, keine Datei ohne echten Einstiegs-, Beleg-
oder Übergabewert.
