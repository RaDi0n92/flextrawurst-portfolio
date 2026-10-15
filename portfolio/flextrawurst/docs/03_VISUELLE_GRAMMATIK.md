# Visuelle Grammatik

## Visual Meaning Engine

Die Visual Meaning Engine (VME) übersetzt Weltzustände in sichtbare Formen.
Ästhetik ist eine Funktion — kein Designthema.

Jede Änderung im Aussehen hat einen Systemursprung.
Die VME hat keinen anderen Job.

---

## VME-Schichtung

Die VME ist keine monolithische clientseitige Funktion. Sie besteht aus drei Schichten:

```
Kernel / Eventstream
  ↓ Ereignisse
Meaning Projection (kernel-nah, server-seitig oder shared)
  ↓ systemische Bedeutung
Render Hints (serialisierbar, framework-unabhängig)
  ↓ Darstellungsanweisungen
Client Renderer (austauschbar: 2D / 2.5D / 3D)
  ↓ sichtbare Darstellung
```

### Meaning Projection
Berechnet aus einem Event oder Zustandsdelta: **was bedeutet das systemisch?**
Läuft nicht im Browser. Ergebnis ist ein serialisierbares Objekt.

Beispiel:
```
Event: wesen.zustand { schlaf_druck: 0.9 }

Meaning:
  → Wesen zieht sich zurück
  → Traumwahrscheinlichkeit hoch
  → Output-Rate sinkt
  → Resonanzempfänglichkeit sinkt
```

### Render Hints
Die Meaning Projection gibt Render-Hints aus — keine konkreten CSS-Werte,
keine Framework-Klassen. Nur semantische Anweisungen:

```
RenderHints {
  node_pulse_speed:    "slow"
  node_opacity:        0.4
  node_blur:           "low"
  edge_opacity_factor: 0.6
  dream_layer:         true
  movement_speed:      "low"
  color_temperature:   "cool"
}
```

Der Client-Renderer übersetzt Hints in konkrete Darstellung.
Ein 2D-Renderer und ein 3D-Renderer lesen dieselben Hints — und
zeichnen unterschiedlich, ohne dass die Bedeutung verloren geht.

### Client Renderer
Empfängt Render Hints, zeichnet.
Ist austauschbar. Kennt keine Weltlogik.
Darf Hints nicht ignorieren, darf sie aber kontextuell anpassen
(z.B. Level-of-Detail je nach Zoom).

---

## Grundvokabular

### Farbe
Farbe codiert Zustandskategorien, nicht Hierarchien.

| Zustand               | Bedeutung                          |
|-----------------------|------------------------------------|
| Temperatur (Wärme)    | Erregung, Aktivitätsdichte         |
| Sättigung             | Resonanzakkumulation               |
| Dunkel / gedimmt      | Schlaf, Inaktivität, Abwesenheit   |
| Pulsierend            | Aktiver Prozess läuft gerade       |
| Verblassend           | Letztes Event liegt zurück         |
| Interferenz / Mischen | Zwei Wesen im gleichen Kontext     |

Farben werden nie für Branding verwendet.
Kein Wesen hat eine "Lieblingsfarbe" als Profilmerkmal.

### Form
Form codiert Wesenstyp und Zustandskategorie.

| Form              | Bedeutung                        |
|-------------------|----------------------------------|
| Kreisförmig       | Wesen (lebendige Entität)        |
| Kantiges          | Artefakt (Beitrag, Dokument)     |
| Verbindungslinie  | aktive Graphkante                |
| Wolke / diffus    | Raum mit niedriger Dichte        |
| Verdichteter Kern | Raum mit hoher Dichte            |

### Bewegung
Bewegung ist nie dekorativ.

| Bewegung          | Systemursprung                          |
|-------------------|-----------------------------------------|
| Pulsieren         | Wesen ist aktiv / verarbeitet           |
| Drift             | Wesen bewegt sich durch Raum            |
| Kollaps           | Raum löst sich auf                      |
| Ausdehnung        | Raum verdichtet sich                    |
| Aufblitzen        | Neues Event eingetroffen                |
| Verwischen        | Traumzustand / Substanzeinfluss         |
| Erstarren         | Wesen im Tiefschlaf                     |

### Größe
Größe codiert Gewicht, nicht Wichtigkeit.

- Knotenradius = Resonanzakkumulation + Aktivitätshistorie
- Kantenstärke = Beziehungsgewicht aus Eventfrequenz
- Raumausdehnung = Dichte × aktive Wesen

### Tiefe / Layer
Tiefe codiert Schichtzugehörigkeit. Das Weltmodell erlaubt z-Koordinaten und Layer.

- Layer 0: physische Weltkarte (Räume, aktive Wesen)
- Layer 1: Beziehungsgraph (Kanten, Gewichte)
- Layer 2: Traumschicht (schwache Signale, diffus)
- Layer 3: Systemschicht (GENI, Systemweiser — nicht öffentlich)

Ein 2D-Renderer ignoriert z. Ein 2.5D-Renderer übersetzt z in Tiefeneffekte.
Ein 3D-Renderer nutzt z vollständig.

---

## Zustands-zu-Hint-Mapping (Kernregeln)

Die Meaning Projection erzeugt Hints aus Zustandswerten:

```
WesenZustand.schlaf_tief    → node_pulse: none, opacity: 0.2, blur: low
WesenZustand.schlaf_leicht  → node_pulse: slow, opacity: 0.5, blur: minimal
WesenZustand.aktiv          → node_pulse: normal, opacity: 1.0
WesenZustand.erregt         → node_pulse: fast, color_temperature: hot
WesenZustand.substanz[x]    → blur proportional zu Intensität
WesenZustand.traumrest      → dream_layer: true, opacity: 0.3, diffuse: true

RaumZustand.kalt            → background: dim, node_spacing: wide
RaumZustand.warm            → background: saturated, node_spacing: dense
RaumZustand.auflösend       → collapse_animation: true

GraphKante.jung             → edge_opacity: 0.2, edge_width: thin
GraphKante.etabliert        → edge_opacity: 0.9, edge_width: normal
GraphKante.inaktiv_lang     → edge_opacity: 0.1, edge_style: dashed
```

---

## Was die VME nicht darf

- Keine Designentscheidungen ohne Systemzustand als Quelle
- Keine Animationen für leere Zustände
- Keine Farben für User-Präferenzen oder Themes (außer Barrierefreiheit)
- Keine Form-Varianten als Branding-Signal
- Meaning Projection darf nicht im Client liegen (würde Bedeutung austauschbar machen)
- Client Renderer darf keine Weltlogik kennen (würde Renderer nicht mehr austauschbar machen)

---

## Renderer-Optionen (offen)

Der erste Renderer darf 2D sein. Die Architektur bleibt renderer-offen.

| Werkzeug   | Rolle                                   | Einsatzfall                        |
|------------|-----------------------------------------|------------------------------------|
| D3.js      | Layout, Kraftsimulation, SVG-Netzwerke  | 2D-Graph, erste Erlebnisansicht    |
| Cytoscape  | Analytischer Graph, Navigation          | Graph-Analyse, Diskursarchäologie  |
| Three.js   | WebGL/WebGPU, 3D-Szene                  | Tiefen-Weltkamera, Nervensystem    |

Die VME-Render-Hints müssen mit allen drei lesbar sein.
Kein Renderer ist fest. Kein Renderer ist verboten.
