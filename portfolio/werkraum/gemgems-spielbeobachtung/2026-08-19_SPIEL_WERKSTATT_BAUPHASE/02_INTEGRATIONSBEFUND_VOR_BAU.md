# Integrationsbefund vor dem ersten Werkstattbau

Datum: 2026-08-19

## Tatsächlich gelesene relevante Körper

- `gemgems-spielbeobachtung/NEU_AB_2026-08-17_SPIELWEITERBAU_CHATGPT/01...06`
- `gemgems-spielbeobachtung/spiel/13_ct_scan_godot_vertical_slice.md`
- `17_ct_scan_godot_provenienz_und_session_analyse.md`
- `19_master_index_und_gesamtsystemkarte.md`
- `21_ct_scan_gordslider_anatomie.md`
- `23_prospektion_zeitstrom_claims_und_session_spielspuren.md`
- `30_deep_scan_1337_loops_und_gesamtbeschreibung.md`
- `34_kosmos_geodaten_casino_und_gordslider.md`
- `35_game_engine_und_prototypen_stammbaum.md`
- Tiefenbergungen zu v21-Modulen, Godot-Runtime, Backend-Brücke und offenen Wunden
- Primärcode `v21_creator_events.js`
- Primärcode `v21_modular_workshop.js`
- Primärcode `engine/godot-vertical-slice/scripts/world_bridge.gd`
- Primärcode `engine/godot-vertical-slice/deploy/world_bridge_server.py`
- Primärcode `ring_002/.../persistence_store.gd`
- `engine/godot-vertical-slice/project.godot`
- aktueller systemd-Status und Logs der Godot-World-Bridge

## Harte Befunde

1. v21 besitzt bereits echte Creator-Gene: stabile Objekt-UIDs innerhalb eines Kartenkörpers, create/edit/remove, History und `publishMap21()`.
2. Diese v21-Creator-Zustände sind historisch echter Code, aber der Zustand ist im damaligen Spielkörper primär In-Memory und nicht der heutige gemeinsame persistente Werkstattkörper.
3. Godot besitzt echte 3D-Runtime, bekannte Weltatom-ID für Gordslider, lokale Persistenz und eine bidirektionale HTTP-Event-Bridge.
4. Der bestehende Godot-Client ist kein Dauerprozess und es liegt aktuell kein Godot-Webexport (`.html`/`.wasm`) im Projekt vor.
5. Die bestehende Bridge bindet nur `127.0.0.1:18092`; ihr Server implementiert GET/POST, aber kein `OPTIONS`. Browser-Versuche vom 13.08. erzeugten deshalb wiederholt HTTP 501 auf OPTIONS. Eine Browserkopplung ist also noch real zu bauen, nicht nur zu behaupten.
6. Der geplante Spiel-Kontextinjektor existiert aktuell als Dokument-/Systemkonzept, nicht als gefundenes ausführbares `SPIEL_KONTEXTINJEKTOR`-Programm.
7. Die Werkstatt darf deshalb nicht so tun, als seien Godot-Webexport, AI-Injektion und ein kanonischer Gesamt-Weltstore bereits fertig.

## Reale Integrationsentscheidung für den ersten Werkstattkörper

Der erste Werkstattkörper wird als **isolierte neue Werkstatt-Schicht neben dem bestehenden Godot-Projekt** gebaut, ohne vorhandene Spiel-Glue-Dateien umzuschreiben.

Er bekommt einen eigenen persistenten Store und API/UI, die bereits folgende echte Kernlogik ausführen:
- stabile Spielkörper-IDs,
- aktuelle Auswahl und Pins,
- getrennte Arbeitszustände je Akteur,
- bewusst gemeinsamer Arbeitszustand,
- Arbeitsänderungen ohne sofortige Weltwirkung,
- explizites Speichern,
- unverlierbare Vorversionen,
- Herkunft und Änderungsereignisse,
- geschützte Entwürfe,
- Historienansicht,
- eindeutige unabhängige Feldänderungen mergebar,
- Konfliktstatus statt stillem Last-Write-Wins,
- Zuordnung eines Spielkörpers zu realen Quellpfaden und vorhandenen Verkörperungen.

Der erste Körper importiert zunächst reale bekannte Spielidentitäten und Pfade aus dem vorhandenen Bestand, statt erfundene Demoobjekte als Welt auszugeben. `OBJEKT_GORDSLIDER_0001` / `ORT_WUPPERTAL_CASINO_0001` dienen als erster direkt belegter Objektanker.

3D bleibt im ersten Bau als **reale Integrationsstelle mit Wahrheitsstatus** sichtbar: vorhandener Godot-Körper ja, Webexport aktuell nein. Kein Fake-3D. Der nächste echte 3D-Schritt kann danach den Browserexport und die browserfähige Bridge auf denselben Identitäts-/Arbeitszustandskörper setzen.
