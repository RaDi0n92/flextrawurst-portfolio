# Gemeinsame Arbeit · Protokoll

Dieses Protokoll ist die lesbare Schicht neben `data/ai_spuren.json` und den Ereignissen. Es hält nur belegte Arbeit fest; Entwürfe und Grenzen werden als solche benannt.

## Arbeitsregel

Für jede Änderung gilt: Gegenstand → echte Nutzerhandlung → Beleg → Persistenz/Reload, falls gespeichert → 3× Sokrates/Redteam → Folgefeedback → erst dann erledigt.

## 2026-08-22 · Arbeitskörper erneut verankert

**Anlass:** Der bisherige Bauauftrag und die Zusatzregeln wurden zwar einzeln dokumentiert, aber der Ordnerbaum war noch nicht ausdrücklich als zusammenhängender Arbeitskörper lesbar.

**Verankert:**
- `00_Start/01_AKTIVER_ARBEITSKOERPER.md` ordnet den bestehenden Baum als Material, Gedächtnis, Nervenbahnen, kontrollierte Reflexe, Übergaben und Redteam-Immunsystem.
- Der feste Feedbackzustand und die verpflichtende Folgefrage sind dort als Ablaufzustände festgehalten.
- `01_Material`, `04_Automationen` und `05_Übergaben` erhalten knappe Rollenbeschreibungen, damit sie keine anonymen Ordner bleiben.
- `07_AI-Spuren` bleibt ausdrücklich Altbestand. Eine Migration/Bereinigung ist nicht behauptet.

**Bekannte offene Verbindung:** Die neuen/aktualisierten Dateien sind real im VPS-Baum. Ihre bewusste Übernahme als Planerobjekte und die zugehörigen Kanten/Ereignisse müssen anschließend in der Live-UI mit Playwright angelegt und nach Reload geprüft werden. Bis dahin sind sie Dateien mit klarer Funktion, nicht fälschlich als bereits verbundene Objektstruktur markiert.

**Nächste Arbeit:** Den Live-Planer wieder nutzbar anbinden, dann diese Einstiegsknoten bewusst als Arbeitsobjekte übernehmen und ihre Herkunfts-/contains-Kanten sichtbar prüfen.

## 2026-08-23 · Architekturbruch benannt

Die globalen Sichten Start, Canvas, Netz, Plan, Zeitspur und Replicas sind noch keine Gesamtbetriebssystem-Werkzeuge, sondern globale Lesarten eines offenen Planerzustands. Die Baugeschichte dazu liegt in `BAUGESCHICHTE_GESAMTBETRIEBSSYSTEM.md`.

Ab jetzt ist der reale Arbeitskontext (Datei oder Ordner) die erste Achse. Seine Auswahl wird in den kanonischen Planerzustand geschrieben und im Kopf der Oberfläche angezeigt. Die Werkzeugfamilien müssen danach einzeln an diesen Kontext gebunden werden; der bloße sichtbare Kontextbalken ist noch kein Abschluss dieses Umbaus.