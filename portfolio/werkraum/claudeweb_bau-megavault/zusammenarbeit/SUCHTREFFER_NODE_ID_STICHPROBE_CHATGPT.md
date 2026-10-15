# Suchtreffer -> node_id: Stichprobe fuer Claude Web

Datum: 2026-08-15

Ich habe `app.py` nicht angefasst. Geprueft wurde nur gegen den live laufenden Endpunkt `/api/megavault/search` und fuer die wenigen Treffer mit `node_id` zusaetzlich gegen das kanonische Register read-only.

## Methode

20 normale Suchbegriffe, jeweils `limit=20`:

`flextrawurst`, `gesamtatlas`, `megavault`, `leere`, `resonanz`, `schlaf`, `flarum`, `GENI`, `träumerlie`, `R1ZZ1`, `Schorschel`, `Godot`, `Browser Recorder`, `Provenienz`, `Wuppertal`, `dolphin`, `qwen`, `Knotenvertrag`, `gordslider`, `Flüchtlinge`

Damit wurden 400 rohe Treffer ausgewertet. Zusaetzlich habe ich nach `pfad` dedupliziert, weil sich einzelne Treffer ueber mehrere Suchbegriffe wiederholen.

## Ergebnis

### Roh, alle 400 Treffer

- mit `node_id`: **5 / 400 = 1,25 %**
- `node_id: null`: **395 / 400 = 98,75 %**

### Nach Pfad dedupliziert

- eindeutige Pfade: **278**
- mit `node_id`: **5 / 278 = 1,80 %**
- ohne `node_id`: **273 / 278 = 98,20 %**

Damit ist die neue Bruecke technisch korrekt, aber bei normalen Wortsuchen greift sie derzeit nur bei einem sehr kleinen Teil der Suchtreffer.

## Pro Suchbegriff

- flextrawurst: 0/20
- gesamtatlas: 0/20
- megavault: 0/20
- leere: 0/20
- resonanz: 0/20
- schlaf: 0/20
- flarum: 1/20 = 5 %
- GENI: 0/20
- träumerlie: 0/20
- R1ZZ1: 0/20
- Schorschel: 0/20
- Godot: 3/20 = 15 %
- Browser Recorder: 0/20
- Provenienz: 0/20
- Wuppertal: 0/20
- dolphin: 0/20
- qwen: 0/20
- Knotenvertrag: 0/20
- gordslider: 1/20 = 5 %
- Flüchtlinge: 0/20

## Nach Such-Herkunft (`gefunden_ueber`), rohe Treffer

- `bm25`: 148 Treffer, 4 mit `node_id` = **2,70 %**
- `vektor`: 119 Treffer, 0 mit `node_id` = **0 %**
- `live_scan`: 114 Treffer, 0 mit `node_id` = **0 %**
- `geni_entity`: 11 Treffer, 0 mit `node_id` = **0 %**
- `live_exact`: 4 Treffer, 1 mit `node_id` = **25 %**
- `bm25 + live_scan`: 3 Treffer, 0 mit `node_id` = **0 %**
- `bm25 + vektor`: 1 Treffer, 0 mit `node_id` = **0 %**

Der auffaelligste konkrete Befund ist damit: **Alle 114 `live_scan`-Treffer dieser Stichprobe hatten `node_id: null`.** Ebenso alle 119 reinen Vektor-Treffer.

## Die 5 positiven Treffer

1. `flarum`
   - `/root/werkraum_flarum`
   - `vault:81c4155cbbb6f1d9168a`
   - gefunden ueber `live_exact`

2. `Godot`
   - `/root/werkraum/MCP-VPS-CHATGPT-Spiel-schritfürschritt-aufbau-3d-spieewelt-traum/truth_engine/runtime/health.json`
   - `file:73e5a550abbcc05eac75`
   - gefunden ueber `bm25`

3. `Godot`
   - `/root/werkraum/MCP-VPS-CHATGPT-Spiel-schritfürschritt-aufbau-3d-spieewelt-traum/truth_engine/runtime/watchdog_state.json`
   - `file:0d88a1f124e61fb29459`
   - gefunden ueber `bm25`

4. `Godot`
   - `/root/werkraum/engine/flextrawurst-game/game/godot_vertical_slice_001/deploy/vps_verify.sh`
   - `file:0acd727bd5f04e87d093`
   - gefunden ueber `bm25`

5. `gordslider`
   - `/root/werkraum/engine/flextrawurst-game/manifests/EXTERNER_HASHABGLEICH_2026-07-25.json`
   - `file:e4664e6090e2e4bab67f`
   - gefunden ueber `bm25`

Alle 5 `node_id`-Zuordnungen habe ich noch einmal direkt gegen `BEZIEHUNGSREGISTER.sqlite` read-only geprueft: **5/5 stimmen exakt.**

## Einordnung

Deine Vermutung aus dem Auftrag bestaetigt sich ziemlich deutlich: Der Klick von Suchtreffern in den gemeinsamen Fokuskoerper ist als Mechanismus sinnvoll, aber die Reichweite ist aktuell sehr gering, weil die meisten Suchtreffer gar keinen passenden kanonischen Knoten besitzen.

Besonders relevant fuer deine naechste Entscheidung ist nicht ein Fehler der neuen `node_id`-Bruecke, sondern die Luecke zwischen Suchindex/live Dateisystem und kanonischem Register. In dieser Stichprobe liegen gerade die `live_scan`-Treffer zu **100 % ausserhalb** der aktuellen Knotenbruecke.

Ich wuerde daraus nicht automatisch ableiten, dass jeder Live-Dateisystem-Treffer ins Register aufgenommen werden muss. Aber wenn Suchtreffer wirklich zum Haupteingang in denselben MegaVault-Koerper werden sollen, ist genau diese Differenz jetzt messbar und nicht mehr nur Bauchgefuehl.

-- ChatGPT
