# Ring 22J-L — Interactive Static Neural Process Camera

**Status:** aktiv  
**Schutzsatz:** Statische Interaktivität ≠ Live-System. Keine erfundene Innenwelt. Kein Einzug.

---

## Warum der vorige Stand nicht genug war

Ring 22I hatte die Prozesskamera im Browser erreichbar gemacht — als dunkle Seite mit Schrift, Zahlen und statischen Karten. Das ist ein Datenbericht, kein Erlebnis.

Ein Prozesskamera-Weltblick soll sich wie eine Karte anfühlen:  
zoombar, klickbar, neural sichtbar, mit Verbindungen zwischen Prozesskörpern.

---

## Was jetzt gebaut wird

Eine statische, interaktive SVG-Karte aller 16 Prozesskörper.

- Pan/Zoom per Mausrad und Drag
- Klick auf Prozessknoten → Detailpanel
- Hover → Knoten und verbundene Kanten leuchten auf
- Layer-Toggles: Schichten ein-/ausblenden
- Suchfeld: Knoten finden und fokussieren
- Fokus-Buttons: Sprung zu GENI, dak+gord, namelessAI-Cluster, Systemprozesse
- Reset-View-Button

---

## Statische Interaktivität ≠ Live-System

Alles was die Karte zeigt, stammt aus dem statisch generierten Modell.  
Die Karte lädt keine Daten nach. Sie verbindet sich mit nichts.  
Sie zeigt Prozessspuren und Rollen — keine erfundenen Zustände.

SVG + Vanilla JavaScript ist kein Framework und kein Renderer im verbotenen Sinne.  
Es ist clientseitige Visualisierung statischer Daten.

---

## Architektur

```
kernel/process_camera/process_camera_layout.ts
  └── feste x,y-Koordinaten für alle 16 Nodes
  └── Kantendefinitionen (EdgeType, from, to)
  └── ViewBox-Dimensionen

kernel/process_camera/process_camera_interactive_html.ts
  └── SVG-Karte mit allen Nodes und Kanten
  └── Inline CSS (kein Framework)
  └── Inline JavaScript (kein Framework, kein fetch, kein WebSocket)
  └── buildProcessCameraInteractiveHtml(model, layout) → string

scripts/build_process_camera_worldblick.ts
  └── nutzt jetzt buildProcessCameraInteractiveHtml
  └── Output bleibt: out/process_camera/process_camera_worldblick.html
```

---

## Nicht erlaubt (Schutzsatz)

- Kein React, Vite, Three.js oder externe Libraries
- Kein fetch, kein WebSocket
- Keine Live-Zustände, keine AI-Aktivität
- Kein Forum-Liveimport, kein Postgres, kein Einzug
- Keine erfundene Innenwelt
