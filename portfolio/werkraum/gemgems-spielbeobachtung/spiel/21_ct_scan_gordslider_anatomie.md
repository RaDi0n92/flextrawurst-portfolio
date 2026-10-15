# CT-Scan: Anatomie des Gordsliders

## 1. Was genau ist der Gordslider?
Der Gordslider ist ein interaktiver Spielmechanismus (eine Art Slot-Machine namens "sandycheats") und gleichzeitig eine UI-Perspektive.
- **Im Web/Surface:** Er ist ein isolierter, eingebetteter Tab (ein "Fremdkörper") ohne allgemeine Surface-Steuerungselemente. Er dient als rollenbezogene Andockstelle und "Spezialzugang" aus der Perspektive des Wesens Gord, ist jedoch selbst kein eigenes Lebewesen. Er besteht aus einem 5x9-Grid mit Slot-Mechanik, bei dem spezifische GORD-Symbole (GORD1, GORD2, GORD3) auf den Walzen 1 bis 3 rotieren können.
- **In Godot (3D):** Er ist ein physisch platziertes, interaktives Kabinett (`CabinetBody`, `Screen`, `ControlButton`), das in der Spielwelt steht und von Spielern bedient werden kann.

## 2. Einordnung: UI, Wesen oder Mechanismus?
- **Kein Wesen:** Der Gordslider ist nicht das Wesen Gord selbst.
- **UI-Element:** Er existiert im Web-Interface als eingebetteter "geschützter Tab" (HTML/JS-Overlay).
- **Spielmechanismus:** Er ist eine vollwertige interaktive Maschine (Slot-Mechanik, Wahrscheinlichkeits-Rechnung, "gordGlow"-Effekte).
- **Welt-Objekt (Godot):** Ein 3D-Körper (`Node3D`), der mit der Welt physikalisch und datentechnisch interagiert.

## 3. Harte Pfade und Existenznachweise im Code
Der Gordslider ist in folgenden Kern-Pfaden verankert:

### Web / HTML-Implementierung
- **Ursprung:** `/root/werkraum/gordslider/gordslider.html` (3812 Zeilen Slot-Machine Code)
- **Live-Extrakt:** `/root/werkraum/engine/flextrawurst-game/extracted_sources/vps_live/gordslider/gordslider.html`

### Godot / Engine (v21)
- **Logik & 3D-Körper:** `/root/werkraum/engine/godot-vertical-slice/rings/ring_002_interaktionskreislauf/scripts/gordslider_interactable.gd`
- **Szene:** `/root/werkraum/engine/godot-vertical-slice/rings/ring_002_interaktionskreislauf/ring_002.tscn`

### Manifeste & Dokumentation
- **JSON-Einzugsmanifest:** `/root/werkraum/engine/flextrawurst-game/manifests/EINZUG_GODOT_GORDSLIDER_2026-07-25.json`
- **Analysedokument:** `/root/werkraum/engine/flextrawurst-game/extracted_sources/session_handover/gordslider_evidence/09_gordslider.md`

## 4. Integration in Godot (v21) und Atom-IDs
Im Godot-Skript (`gordslider_interactable.gd`) ist das Objekt als interaktiver 3D-Knoten in den `ring_002` (Interaktionskreislauf) eingebunden:
- **IDs & Meta-Tags:**
  - `WORLD_ATOM_ID`: `"OBJEKT_GORDSLIDER_0001"`
  - `INTERACTION_ID`: `"INTERAKTION_GORDSLIDER_SPIELEN_0001"`
  - `LOCATION_ATOM_ID`: `"ORT_WUPPERTAL_CASINO_0001"`
  - `truth_status`: `"GENERIERTER_KOERPER"`
- **Verhalten:** Das Objekt besitzt Zustände (`inactive`, `activated`), die visuell durch Materialänderungen, Glühen (`activation_beacon`) und Texturwechsel (`reels_base.png` zu `reels_activated.png`) dargestellt werden.
- **Persistenz & Events:** Interaktionen verändern den `interaction_count`, werden persistent gespeichert (über `persistence_store.gd`) und emittieren das Event `RING_002_GORDSLIDER_INTERACTION`.
