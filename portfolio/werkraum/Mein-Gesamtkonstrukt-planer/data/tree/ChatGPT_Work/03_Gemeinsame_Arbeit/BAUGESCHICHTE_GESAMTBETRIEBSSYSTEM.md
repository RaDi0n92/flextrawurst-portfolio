# Baugeschichte · vom Ein-Datei-Planer zum Gesamtbetriebssystem

## 2026-08-23 · Ausgangslage

Der sichtbare Planer behandelte **Start, Canvas, Netz, Plan, Zeitspur und Replicas** als globale Sichten auf einen einzelnen, offenen Planerzustand. Das ist kein Gesamtbetriebssystem: reale Bestände, Ordner, Dateien, spätere Gesamtatlas-/Megavault-Orte und ihre eigenen Arbeitsräume werden dadurch nicht zu gleichwertigen Gegenständen.

## Beschlossene Umkehr

Nicht mehr: Ansicht wählen → dieselbe offene Plan-Datei anders ansehen.

Sondern: **Arbeitsbestand wählen → konkreten Gegenstand wählen → passendes Werkzeug öffnen → Ergebnis als Datei, Objekt, Kante oder Ereignis zurückschreiben.**

Die Ansichten werden deshalb schrittweise zu Werkzeugfamilien:

- Übersicht: Bestand, offene Fragen, nächste Handlungen.
- Raum: freie Skizzen, Referenzwände und Kartenräume des gewählten Bestands.
- Beziehungen: belegte Kanten, Quellrücksprünge, Filter und bewusstes Verbinden.
- Ablauf: Eingaben, Zustände, Bedingungen, Zuständigkeiten, Ergebnis und Stopps.
- Geschichte: Versionen, Ereignisse, Beiträge, Belege und Rückbau.
- Werkzeuge: eigenständige Replica-Arbeitsräume, jeweils am gewählten Material.

Keine dieser Familien darf bloß den globalen Knotenbestand umstylen. Ihre konkrete Kernhandlung wird einzeln gebaut, gespeichert und geprüft.

## Bereits am realen Arbeitskörper geändert

- Der Dateibaum besitzt einklappbare Zweige und **Alles einklappen**.
- Gemeinsame Arbeit verweist von einer Spur zurück in die referenzierte VPS-Datei.
- Der Einstieg und die Baugeschichte liegen als echte Dateien im Arbeitsbaum.

## Nächster echter Schnitt

Die aktuelle Auswahl (Datei/Ordner/Objekt) wird zu einem gespeicherten Arbeitskontext. Erst danach wird eine Werkzeugfamilie geöffnet. Der Kontext muss nach Reload wiederkommen und darf nicht nur Browserzustand sein.

## Grenze

Die bisherigen globalen Tabs sind noch vorhanden. Sie sind nicht durch Umbenennung gelöst; ihr Umbau zu kontextgebundenen Werkzeugen ist offen.