# Social Media Safe-Zone Guide (TikTok, Instagram Reels, YouTube Shorts)

Dieses Dokument definiert die verbindlichen Sperrzonen für 9:16 Hochkantvideos, um zu verhindern, dass UI-Elemente der Plattformen wichtige visuelle Inhalte oder Typografie verdecken.

---

## 📐 Safe-Zone Koordinaten (Referenz 480 x 854 & 1080 x 1920)

```text
+---------------------------------------------+  Y = 0%
|  [SPERRZONE OBEN] Tabs, Suche, Akku-Leiste  |  (Höhe: 10% / ~85px bei 854h)
+---------------------------------------------+  Y = 10%
|                                          |S |
|                                          |P |
|                                          |E |
|            GRÜNE SAFE-ZONE               |R |  Rechte Sperrzone:
|                                          |R |  (Breite: 14% / ~67px bei 480w)
|       (Hauptinhalt, Kinetic Lyrics,      |Z |  Like, Kommentar, Bookmark,
|          Wesentliche Protagonisten)      |O |  Audio-Disc, Teilen-Button
|                                          |N |
|                                          |E |
+------------------------------------------+--+  Y = 78%
|  [SPERRZONE UNTEN] Username, Captions,   |  |  (Höhe: 22% / ~188px bei 854h)
|  Audio-Titel, Fortschrittsbalken         |  |
+---------------------------------------------+  Y = 100%
```

---

## 🎯 Pixel-Werte für unsere Standard-Auflösungen

| Auflösung | Safe-Breite ($X$) | Safe-Höhe ($Y$) | X-Start ($X_{min}$) | Y-Start ($Y_{min}$) |
| :--- | :--- | :--- | :--- | :--- |
| **$480 \times 854$** | $390\text{ px}$ | $580\text{ px}$ | $24\text{ px}$ ($5\%$) | $85\text{ px}$ ($10\%$) |
| **$1080 \times 1920$** | $875\text{ px}$ | $1305\text{ px}$ | $54\text{ px}$ ($5\%$) | $192\text{ px}$ ($10\%$) |

---

## 🛠️ FFmpeg Debug-Overlay (Prüfmaske für Test-Renders)

Mit diesem Filtergraph kann während des Testens eine halbtransparente rote Maske über das gerenderte Video gelegt werden, um sofort zu sehen, ob Text oder wichtige Objekte abgeschnitten werden:

```bash
# Legt rote Markierungsboxen über die Sperrzonen (nur für Preview!)
[in]drawbox=x=0:y=0:w=480:h=85:color=red@0.4:t=fill,\
drawbox=x=413:y=85:w=67:h=581:color=red@0.4:t=fill,\
drawbox=x=0:y=666:w=480:h=188:color=red@0.4:t=fill[safe_debug_out]
```

### Faustregel für den Schnitt:
* **Kinetic Typography:** Immer zentriert im Bereich `Y = 40%` bis `Y = 55%` platzieren (perfekte Augenhöhe beim mobilen Scrollen).
* **Divider / HUD:** Zwischen `Y = 42%` und `Y = 50%` einbetten.
* **Unterer Bildbereich:** Nur Hintergrund-Ambiente oder sekundäre Texturen in den unteren 22 % platzieren.
