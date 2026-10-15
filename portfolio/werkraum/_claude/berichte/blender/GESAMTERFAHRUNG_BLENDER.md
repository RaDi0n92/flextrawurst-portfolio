# Blender-Arbeit über MCP — Gesamterfahrung

Stand: 2026-09-06. Deckt alles ab, was seit dem 05.09. über die Blender-MCP-Brücke
gebaut wurde: vier Charaktere, eine Baumaschine, ein Autoscooter.

Diese Datei ist kein Bauprotokoll, sondern das, was davon übrig bleibt: Werkzeugfallen
mit Reproduktion, Arbeitsmuster die getragen haben, und die Grenzen, die sich gezeigt
haben.

---

## 1. Was gebaut wurde

### Charaktere (05.09.)

Vier Stände, alle unter `/root/werkraum/_backups/daniel_char_checkpoints/` gesichert
(doppelt: auch im Container unter `/root/daniel_char_checkpoints/`).

| Datei | Was es ist | Zustand |
|---|---|---|
| `01_opa.blend` | erster Charakter, Visier-Maske, lila Puffschultern | voll geriggt, 17 Vertex-Gruppen |
| `02_zweiter_versuch.blend` | 7 Objekte: Kopf, Hals, Referenzbild | abgebrochener Frühstand, optisch fast leer |
| `03_daniel_frau_vor_join.blend` | 61 Einzelteile: Maske, Haare, Robe, Krabbenklauen-Hände, Becher | ungeriggt |
| `04_daniel_frau_final_gerigged.blend` | dasselbe gejoint + Armature | Gewichte per ENVELOPE |
| `05_maennlicher_zwischenstand.blend` | eigenständiger männlicher Charakter, aus einem Autosave geborgen | geriggt, 3 Animationen |

Drei davon sind im Spiel deployt und über ein Dropdown wählbar
(`daniel_char_opa.glb`, `daniel_char_maennlich_v1_rigged.glb`,
`daniel_char_frau_v2_rigged.glb`).

**Fund am Rande:** Der männliche Charakter existierte nur noch in einer
Autosave-Datei (`daniel_char_scene_2665806_autosave.blend`). Ohne gezielte Suche in
`/tmp` wäre er verloren gewesen. Autosaves sind eine echte Rettungsquelle, aber
`/tmp` ist keine Ablage — sofort wegkopieren.

### Baumaschine (05.09.)

`berichte/blender/schrottplatz-baumaschine/` — Radlader mit Baggerarm, Magnetkran und
Gabelstapler-Gabeln. Referenz war ein 6-Panel-Composite.

Gebaut aus Primitiven, iterativ nach Nutzerkritik korrigiert. Nie deployt.

### Autoscooter (06.09.)

`berichte/blender/schrottplatz-autoscooter/` — Endzeit-Autoscooter mit Perllack,
offenem Cockpit, Totenkopfflagge. Erster Bau mit Bauplan und Auditor von Anfang an.

---

## 2. Werkzeugfallen — reproduzierbar, jede real passiert

### `transform_apply` verdoppelt die Position

Wird `bpy.ops.object.transform_apply(scale=True)` auf ein Objekt angewendet, das
schon eine Nicht-Null-`location` hat, landet die Position doppelt in der Weltmatrix.
Sichtbar erst beim nächsten `execute_blender_code`-Aufruf.

**Regel:** Erst bei `(0,0,0)` skalieren und backen, dann verschieben.
**Besser:** Über die gemessene Bounding-Box positionieren, dann ist der Origin egal:

```python
def setze_mitte(obj, zx=None, zy=None, zz=None):
    mn, mx = welt_aabb(obj)
    ist = [(mn[i]+mx[i])/2 for i in range(3)]
    for i, ziel in enumerate([zx, zy, zz]):
        if ziel is not None:
            obj.location[i] += ziel - ist[i]
```

### `bound_box` ist lazy — ohne `view_layer.update()` veraltet

Zwischen zwei Bridge-Aufrufen liefert `bound_box`/`matrix_world` alte Werte. Vor
jeder Messung `bpy.context.view_layer.update()`.

### Material-Duplikate durch Neubau-Zyklen

Nach mehreren Lösch-/Neubau-Runden hießen die tatsächlich verwendeten Materialien
`Chassis_Dunkelgrau.003`, während die Originale verwaist danebenlagen. Eine
Farbkorrektur am Original wirkte am sichtbaren Modell **nicht**.

**Prüfung:** `obj.data.materials` direkt abfragen, nicht `bpy.data.materials` nach
Namen durchsuchen.

### Boolean kann alles löschen

Ein zu großer Schneidkörper hat einen Schädel von 847 Polygonen auf **0** reduziert —
ohne Fehlermeldung. Nach jedem Boolean die Polygonzahl prüfen:

```python
vorher = len(obj.data.polygons)
# ... Boolean anwenden ...
if len(obj.data.polygons) < erwartet_min:
    print("ZU VIEL WEGGESCHNITTEN")
```

### Blender-Euler ist extrinsisch

`rotation_euler = (rx, ry, rz)` rotiert um die **Welt**achsen, nicht um die
mitgedrehten lokalen. Eine Y-Rotation nach einer X-Rotation ändert die
Y-Komponente einer Normalen also nicht.

**Konsequenz:** Orientierungen vorher ausrechnen und per Matrix verifizieren, statt
per Screenshot zu raten:

```python
mw3 = obj.matrix_world.to_3x3()
normale = (mw3 @ mathutils.Vector((0,0,1))).normalized()
print("zeigt nach:", tuple(round(v,2) for v in normale))
```

Das hat bei der Schriftzug-Orientierung acht Screenshots gespart — der Fehler fiel
in der ersten Prüfung auf.

### Achsenverwechslung: Blenders FRONT ist nicht die Fahrzeugfront

`view_axis(type='FRONT')` blickt entlang Y. Liegt die Fahrzeuglängsachse auf X, zeigt
diese Ansicht eine **Seitenansicht**. Für Front/Heck dann `RIGHT`/`LEFT` verwenden.

### `shade_auto_smooth` entscheidet über Hochglanz

Ein aufwendiger Perllack-Shader (Layer-Weight-Farbumschlag, Coat, Thin-Film) sah
stumpf aus, weil flache Facetten jede Reflexion brechen. Erst
`bpy.ops.object.shade_auto_smooth(angle=radians(38))` machte ihn glänzend.

**Merksatz:** Ein Shader ist wertlos, wenn die Geometrie ihn nicht trägt.

### Shrinkwrap projiziert entlang **lokaler** Achsen

Bei einem rotierten Objekt ist `use_project_z` nicht die Welt-Z. `NEAREST_SURFACEPOINT`
wickelt Geometrie um Kanten herum. `PROJECT` mit beidseitiger Richtung schießt durch.

**Verlässlicher:** Raycast pro Vertex, deterministisch und kontrollierbar:

```python
ok, ort, nrm, idx = ziel_obj.ray_cast(start_lokal, richtung_lokal)
```
Vertices ohne Treffer bleiben stehen — die müssen nachträglich abgefangen werden,
sonst ragen sie durchs Objekt.

---

## 3. Rigging und Export

### Automatic Weights scheitert an Primitiv-Suppe

`parent_set(type='ARMATURE_AUTO')` erzeugte bei einem aus vielen Einzelprimitiven
gejointen Mesh **0 gewichtete Vertices von 6800** — bei nur einer generischen
Warnung. Die Heat-Diffusion braucht zusammenhängende Topologie.

**Lösung:** `type='ARMATURE_ENVELOPE'` — arbeitet über Knochennähe, unabhängig von
Topologie.

### glTF verwirft Skin-Daten still

Trotz korrektem Armature-Modifier und gefüllten Vertex-Gruppen exportierte glTF ohne
Skin ("has no skin, skipping"). Ursache: `mesh.parent_type` war `'OBJECT'`.

```python
mesh.parent = arm_obj
mesh.parent_type = 'ARMATURE'          # <-- entscheidend
mesh.matrix_parent_inverse = arm_obj.matrix_world.inverted()
```

### Animationen brauchen NLA-Tracks

`export_animations=True` allein exportiert nur die aktive Action (als "Animation").
Für mehrere benannte Animationen: NLA-Tracks anlegen und
`export_animation_mode='NLA_TRACKS'` setzen.

### GLB-Verifikation ohne Vertrauen auf Exportmeldungen

```python
import json, struct
with open(pfad,'rb') as f: data = f.read()
laenge, typ = struct.unpack('<II', data[12:20])
gltf = json.loads(data[20:20+laenge])
print('skins:', gltf.get('skins'))
print('animations:', [a['name'] for a in gltf.get('animations', [])])
```

---

## 4. Das MCP-Werkzeug selbst

### Fehlende Tools sind oft nur nicht exponiert

Codex' Skill verlangt `ping`, `get_addon_info`, `get_world_state_snapshot`. Diese
existieren bei Claude Code nicht als eigene MCP-Tools — **aber** das laufende Addon
implementiert sie. Zugriff über die Server-Instanz:

```python
server = bpy.types.blendermcp_server
snapshot = server.get_world_state_snapshot()   # location, rotation, scale,
                                               # aabb_min/max, materials, mesh-stats
```

Ich hatte daraus einen Fähigkeitsunterschied konstruiert, wo nur ein Zugriffspfad
fehlte. Dokumentiert in
`/config/.claude/skills/blender-live-reference-qa/CLAUDE-BRIDGE-NOTIZ.md`.

### Context nach `read_homefile` unbrauchbar

`bpy.context.active_object` wirft direkt nach `bpy.ops.wm.read_homefile()` einen
Fehler. Aufruf in einen eigenen Bridge-Call trennen.

### Deutsche Blender-Oberfläche

Node-Namen sind lokalisiert (`Material-Ausgabe` statt `Material Output`). Nodes über
`node.type` suchen, nie über `nodes["Material Output"]`.

---

## 5. Die Harness (Knoten/Kanten-Auditor)

Entstanden am 06.09. auf die Frage, wie Geradlinigkeit ohne Auslassungen
sicherzustellen sei. Ehrliche Antwort damals: durch Vorsätze gar nicht — nur durch
Strukturen, die Auslassungen sichtbar machen.

**Aufbau:** Ein Bauplan (JSON) beschreibt Knoten (Bauteile mit Soll-Attributen) und
Kanten (prüfbare räumliche Beziehungen). `auditor.py` rechnet beides gegen die
laufende Szene nach. Der Auditor ist generisch — nur der Bauplan ist objektspezifisch.

**Geprüfte Kantentypen (Stand 06.09.):**

| Typ | prüft | entstand aus |
|---|---|---|
| `sitzt_auf` | kein Spalt zur Oberkante | Kabine schwebte über Chassis |
| `beruehrt` | AABB-Kontakt | Flagge 12 cm neben dem Mast |
| `symmetrisch_zu` | Mittelpunkte heben sich auf | Lampenpaare |
| `hoehe_unter` | Höhengrenze | Lenkrad über Kopfhöhe |
| `mindestmass` | Mindestausdehnung | Sitztiefe 0,28 — unbenutzbar |
| `mindestabstand` | Abstand zweier Teile | Beinraum 0,22 — Lenkrad im Schoß |
| `freiraum` | Quader bleibt leer | Muldenwand-Rest über dem Sitz |
| `kollidiert_nicht` | keine Durchdringung | Schlauch quer durchs Cockpit |
| `liegt_auf_oberflaeche` | klebt auf statt davor | Schriftzug schwebte |
| `erstreckt_sich_nach` | Richtung stimmt | Flagge wehte nach vorn |
| `beidseitig_an` | auf beiden Seiten vorhanden | Totenkopf nur einseitig |

**Was sie tatsächlich leistet:** Sie erzwingt Disziplin. Kein Teil ohne Bevel, kein
Material ohne echte Nodes, keine schwebenden Teile, alle Symmetriepaare exakt. Sie
hat mehrfach verhindert, dass der Maßstab gesenkt statt Arbeit nachgelegt wird.

**Was sie nicht leistet — die wichtigste Erkenntnis:** Sie prüft, was über das Modell
*behauptet* wird, nicht wie es *aussieht*. Fast alle Funde waren Fehler im Plan, nicht
im Modell. Sie meldete "0 Verstöße", während das Cockpit unbenutzbar war, der
Schriftzug unlesbar, die Flagge falsch herum. Diese Fehler fand ausschließlich Daniel.

**Deshalb:** Der Bauplan enthält eine Liste `sichtpruefung` mit Punkten, die keine
Maschine beurteilen kann (Gestaltwirkung, Lesbarkeit, Referenztreue). Der Auditor
druckt sie nach jedem Lauf, damit "0 Verstöße" nicht als "fertig" missverstanden wird.

**Ein echter eigenständiger Fund:** Der neue `freiraum`-Check fand sofort einen
Tankkasten, der in der Sitzlehne steckte — der einzige Fehler der gesamten Arbeit,
der auffiel, ohne dass Daniel ihn benannte.

---

## 6. Arbeitsmuster — was getragen hat und was nicht

### Was verlässlich funktioniert

- **Messen statt schauen.** Die Ergonomie-Zahlen (Sitztiefe 0,28 / Beinraum 0,22)
  haben ein Urteil in Sekunden belegt, das sonst Diskussion geworden wäre.
- **Rechnen statt raten bei Orientierungen.** Matrix-Verifikation vor dem Screenshot.
- **Nach jeder Baugruppe zwei Zeugen:** strukturierter Readback UND Bild. Keiner
  ersetzt den anderen — der Screenshot zeigte einmal "Sitz fehlt", wo nur eine
  Karosseriewand davorstand.
- **Datei auf Platte als Rettungsanker.** Nach einer verkorksten Gesamtdrehung war
  der letzte gespeicherte Stand schneller wiederhergestellt als repariert.

### Was wiederholt schiefging

- **Reaktives Patchen statt Design.** Über Stunden Teil für Teil nach Kritik
  korrigiert, statt einmal ein Zielbild festzulegen und konsequent zu bauen. Das war
  der Hauptunterschied zu Codex, der dieselbe Aufgabe in einem Bruchteil der Zeit
  kohärenter löste — mit demselben Werkzeug.
- **Aufgaben zu global lesen.** Beim Auftrag "Front und Heck tauschen" wurde das
  ganze Fahrzeug um 180° gedreht; danach saß der Fahrer verkehrt herum. Gemeint waren
  nur die beiden Gesichter.
- **Eigene Fehler nicht selbst sehen.** Praktisch jeder Mangel wurde von außen
  benannt. Die Harness hat das einmal durchbrochen, nicht als Regel.

### Zum Modellvergleich

Der Wechsel von Sonnet auf Opus fiel mit der Einführung der Harness zusammen — zwei
Änderungen gleichzeitig, also nicht trennbar. Zuordenbar ist: Alle Auditor-Funde sind
Werkzeugleistung, kein Modellverdienst. Die Werkzeugwahl in Sackgassen (Raycast statt
Shrinkwrap, Prüfung nach jedem Boolean) war Vorgehen, nicht Plan.

Der saubere Test steht aus: dasselbe Vorgehen mit Sonnet, auf ein neues Objekt.

---

## 7. Wo was liegt

```
/root/werkraum/_claude/berichte/blender/
    schrottplatz-autoscooter/     Bauplan, auditor.py, evidence.md, .blend
    schrottplatz-baumaschine/     Manifest, evidence.md, .blend
    maennlich-v1-qa/              Referenz-Manifest des Charakter-Tests
/root/werkraum/_backups/daniel_char_checkpoints/   die fünf Charakter-Stände
/root/werkraum/Mein-Gesamtkonstrukt-planer/static/models/   deployte GLBs
/config/.claude/skills/blender-live-reference-qa/  Codex' Skill (wortgleich) + Brückennotiz
/config/.claude/skills/blender-mcp-vision/         eigener Skill aus der Charakterphase
```

**Deploy-Hinweis:** Der Schrottplatz hat keinen generischen Static-Mount. Jedes
Charaktermodell braucht eine eigene Route in `worldwords/urls.py` plus einen Eintrag
in der Allowlist von `schrottplatz_character_glb` in `planner_api.py`. Danach
gunicorn per `kill -HUP` neu laden.
