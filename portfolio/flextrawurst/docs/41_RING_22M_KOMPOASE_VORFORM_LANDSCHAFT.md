# Ring 22M — KompOase-Vorform: Landschaftskörper

**Status:** aktiv  
**Schutzsatz:** Atmosphäre darf stark sein. Echte Quellen müssen markiert sein. Wo keine Quelle vorhanden ist, sagt die Karte ehrlich: atmosphärischer / modellierter Bereich.

---

## Was dieser Ring baut

Einen ersten erlebbaren Screen der flextrawurst-Welt.

Nicht als fertiges Feature. Nicht als echte KompOase-Logik.  
Sondern als visuelle Bühne: zoombare Landschaft mit Gebirgen, Schluchten, Lava, Wasser,  
Nebel, Splitterfeldern und pflanzenartigen Formen — über die Prozessschichten und GENI liegen.

---

## Schichtmodell

```
[Sterne / Himmel]
[Ferngebirge — atmosphärisch]
[Mittelgebirge — atmosphärisch]
[Nahgelände — atmosphärisch]
[Lava-Zone — atmosphärisch, rechte Seite]
[Wasser-Zone — atmosphärisch, linke Seite]
[Nebel-Overlay — atmosphärisch]
[Splitterfeld — atmosphärisch, Mitte-Süd]
[Wachstums-Zone — atmosphärisch, links-südlich]
[GENI-Gitternetz — 3 Ebenen, LOD-adaptiv]
[namelessAI-Prozessschicht — echte Quelle: kernel/process_registry.ts]
[dak+gord Navigator — fixiertes Panel, rechts]
[UI-Overlay — Zoom-Controls, Click-Info]
```

---

## GENI-Gitternetz (LOD-adaptiv)

- Ebene 1 (400 WE): sichtbar wenn weit herausgezoomt → große Kacheln
- Ebene 2 (100 WE): sichtbar bei mittlerem Zoom
- Ebene 3 (25 WE): sichtbar wenn stark hineingezoomt → Mikropapier-Raster

---

## Ehrlichkeitsprinzip

Jeder Pixel der Karte hat eine Ortsauskunft (Klick-Info):
- Zone / Schicht
- Atmosphärisch oder echte Quelle?
- Wenn atmosphärisch: expliziter Hinweis
- Wenn echte Quelle: Quell-Referenz

namelessAI-Knoten sind die einzige Zone mit echter Quell-Referenz  
(`kernel/process_model/process_registry.ts`).

---

## Technisch

- Statisches HTML, kein Framework
- Terrain: Überlagerung von Sinuswellen (deterministisch, kein RNG)
- Zoom/Pan: CSS transform auf #world-Container
- Kein fetch, kein WebSocket, keine externen Bibliotheken

URL: `http://[SERVER-IP]:8787/kompOase_vorform.html`
