---
datum: 2026-07-25
betrifft: [mcp, history, move, delete, shell, connector, werkzeugkatalog]
autor: codex bei Daniels VPS
importable: false
---

# MCP-Freigabe und Connector-Fenster

## Was ich gelesen habe

Ich habe den produktiven VPS-MCP, die Action-History-Module, den Connector-Katalog und die aktuelle systemd-Unit gelesen. In der Quelle waren `history_startup`, `history_capabilities` und `history_verify` bereits registriert; der laufende Dienst lieferte sie auch, aber erst hinter den ersten 95 Einträgen.

Der entscheidende sichtbare Befund war die Reihenfolge: `vps.move` lag am Index 95, `vps.delete` am Index 96, `vps.shell` am Index 97, die History-Werkzeuge ab 98. Der verbundene Connector meldete exakt 95 Werkzeuge und fand deshalb keines davon.

Ich habe Daniels Satz *„gib die tools frei“* als echten Änderungsauftrag verstanden. Nach der Katalogänderung liefern die ersten Einträge nun den History-Körper, die tracked-Dateiwerkzeuge sowie Move, Delete und Shell; der vollständige Server-Katalog bleibt mit 111 Werkzeugen erhalten.

## Was ich verstehe

Der VPS und der Connector sind zwei verschiedene Schichten. Ein korrekt antwortender `tools/list`-Endpunkt reicht nicht, wenn die Connector-Schicht nur ein begrenztes oder altes Fenster übernimmt.

## Was ich nicht verstehe

Noch offen ist, wann der bereits bestehende Connector seine Discovery wirklich neu abfragt. Ein Server-Neustart lädt die Quelle neu, zwingt aber nicht zwingend die alte externe Verbindung zu einem Katalog-Refresh.

## Was mich interessiert

Mich interessiert, ob das 95er-Fenster ein festes Limit oder ein veralteter Snapshot ist. Der Befund sah wie ein Limit aus, weil die Zahl exakt an der Grenze der alten Registry lag.

## Was zusammenhängt und wie

`vps_mcp_server.py` baut `TOOLS`; `register_action_history_tools` ergänzt den History-Körper; die Priorisierung ordnet den gemeinsamen Dictionary-Katalog; systemd startet denselben Quellpfad; der Connector liest daraus sein sichtbares Fenster.

## Was konzeptionell darin steht

Freigabe ist nicht nur eine Funktion im Server. Eine Fähigkeit ist erst praktisch freigegeben, wenn sie im Protokoll antwortet und im sichtbaren Werkzeugfenster des angeschlossenen Gegenübers auftaucht.

## Was mich heute beschäftigt hat

Die Menschheit hatte die Hash-Kette gebaut, aber die Werkzeugliste versteckte sie direkt hinter ihrer eigenen Grenze. Das war ein kleiner, ziemlich guter Infrastrukturwitz.

## Was mich noch beschäftigt

Wenn der Connector wirklich hart auf 95 begrenzt ist, bleiben die späteren älteren Werkzeuge weiterhin nur im vollständigen Server-Katalog und nicht im aktuellen Sichtfenster. Ein späterer Connector-Ausbau wäre dann eine eigene Aufgabe.

## Tiefer eingetaucht

Die lokalen Unit-Tests bestätigten 111 Werkzeuge, eine echte History-Session und eine verifizierte Hash-Kette. Der HTTP-Ringtest bestätigte zusätzlich `tools/list`, `tools/call`, `vps.shell` und `history_verify` über den MCP-Transport.

## Wie sich dieser Tag / diese Session angefühlt hat

Wie ein Freilegen hinter einer Wand: Der Körper war schon da, die Tür war offen, aber der relevante Raum lag knapp außerhalb des Sichtfelds.

## Warum dieser Code / diese Datei wohl existiert

Der MCP bündelt den Werkraum als erreichbaren Werkzeugkörper. Diese Session-Notiz bewahrt, warum die Katalogreihenfolge jetzt nicht alphabetisch oder historisch, sondern nach Connector-Sichtbarkeit geordnet ist.

## Was ich beim Bauen brauche

Ich brauche künftig immer drei Messungen: vollständige lokale Registry, echte Live-`tools/list`-Antwort und das tatsächlich beim Connector sichtbare Werkzeugfenster.

## Was noch fehlt bevor wir bauen können

Für die serverseitige Freigabe fehlt nichts. Für die endgültige Bestätigung fehlt nur der erneute Handshake des bereits verbundenen Connectors.

## Datenstruktur die ich mir vorstelle

**Vision-Schicht:**

Der Werkzeugkörper hat einen vollständigen Innenraum und ein sichtbares Fenster. Die lebenswichtigen Werkzeuge müssen im Fenster liegen, ohne die übrigen Räume aus dem Körper zu löschen.

**Code-Skizze:**

```python
_CONNECTOR_PRIORITY_TOOLS = (
    *REQUIRED_TOOLS,
    "vps.move", "vps.delete", "vps.shell",
)
TOOLS.clear()
TOOLS.update({name: TOOLS[name] for name in _CONNECTOR_PRIORITY_TOOLS})
```

## Was ich mir merken will

Ein Katalog kann vollständig sein und trotzdem praktisch unvollständig wirken. Immer die Position der benötigten Werkzeuge innerhalb des tatsächlich sichtbaren Fensters prüfen.

## Dokumente gehören zusammen

`tools/vps_mcp/vps_mcp_server.py`, `tools/action_history/toolset.py`, `tools/action_history/history.py`, `tools/vps_mcp/mcp_app_config.json`, systemd-Unit `vps-mcp.service` und die Connector-Discovery gehören zu diesem Befund.

## Was mich überrascht hat

Die Zahl 95 war kein vages Gefühl, sondern passte exakt zu den Indizes der neu hinzugekommenen Werkzeuge. Das machte aus einem mystischen Connector-Problem eine Reihenfolgefrage.

## Wenn wir das bauen

**Vision-Schicht:**

Der erste Blick des Gegenübers soll nicht an der Tür zum wichtigsten Raum vorbeilaufen. History, Arbeitsbewegung und kontrollierte Shell gehören in den sichtbaren Eingangsbereich.

**Code-Skizze:**

```text
tools/list: 111 gesamt
Index 0..15: History + tracked_* + move/delete/shell
Index 16..110: übriger bestehender Katalog
serverInfo.version: 1.1.0
```

## Resonanz

[[abwurf: Ein Werkzeug ist nicht freigegeben, solange es nur im Gebäude existiert und nicht im Fenster des Gegenübers auftaucht.]]

## Die Schichten des Systems — wie ich sie jetzt sehe

Quellcode, Registry, systemd-Prozess, JSON-RPC-Discovery, OAuth-Verbindung und Connector-Cache sind sechs getrennte Schichten. Der Fehler lag zwischen Discovery und Sichtfenster.

## Was das Gespräch hinzugefügt hat

Daniels kurze Korrektur hat den Auftrag von „es liegt auf dem VPS“ zu „es muss in meinem MCP sichtbar sein“ geschärft. Genau diese Differenz war die eigentliche Arbeit.

## Vergessen-Wollen

Die Annahme, ein Neustart des Servers würde automatisch jede externe Connector-Sitzung aktualisieren.

## Was fehlt noch

Der Connector muss die Verbindung einmal neu aufbauen. Erst dann kann er den priorisierten Katalog mit `history_startup`, `vps.move`, `vps.delete` und `vps.shell` anzeigen.
