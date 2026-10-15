# Detaillierte Phasen-Roadmap für Video-as-Code

Dieses Dokument vertieft die fünf Phasen zur code-gesteuerten Videoproduktion mit konkreten Datenstrukturen, mathematischen Formeln und Implementierungs-Details.

---

## Phase 1: Audio-Telemetrie & Transienten-Mapping

### Datenstruktur: `audio_sync.json`
Das Audiosignal wird vor Beginn der visuellen Generierung in ein Frame-Array zerlegt:

```json
{
  "meta": {
    "audio_file": "intro.mp3",
    "bpm": 114.8,
    "fps": 30,
    "total_frames": 750,
    "duration_sec": 25.0
  },
  "transients": {
    "kicks_sec": [1.205, 1.727, 2.250, 2.772, 3.295],
    "snares_sec": [1.727, 2.772, 3.817],
    "bar_starts_sec": [1.205, 3.295, 5.385]
  },
  "frames": [
    {
      "frame": 0,
      "time_sec": 0.000,
      "sub_bass": 0.02,
      "vocals": 0.00,
      "highs": 0.01,
      "is_kick": false,
      "is_snare": false
    },
    {
      "frame": 36,
      "time_sec": 1.200,
      "sub_bass": 0.88,
      "vocals": 0.12,
      "highs": 0.45,
      "is_kick": true,
      "is_snare": false
    }
  ]
}
```

---

## Phase 2: Kinetic Typography

### Datenstruktur: Whisper Token-Timings
```json
[
  { "word": "Drei", "start_ms": 2160, "end_ms": 2420 },
  { "word": "Punkte", "start_ms": 2440, "end_ms": 2780 },
  { "word": "auf", "start_ms": 2800, "end_ms": 2960 },
  { "word": "dem", "start_ms": 2980, "end_ms": 3120 },
  { "word": "Schirm,", "start_ms": 3140, "end_ms": 3680 }
]
```

### Rendering-Regeln für Kinetic Text
1. **Chunking (Paginierung):** Wörter werden in Chunks von maximal 3 bis 4 Wörtern gruppiert. Sobald der nächste Chunk beginnt, wird der alte ausgeblendet.
2. **Spring-Gleichung (Animation):**
   Für ein Wort mit Startzeit $t_0$:
   $$\Delta t = t - t_0$$
   Wenn $\Delta t \ge 0$:
   $$Scale(\Delta t) = 1.0 + e^{-\zeta \omega \Delta t} \sin(\omega \sqrt{1 - \zeta^2} \Delta t)$$
   * $\omega = 15$ (Geschwindigkeit des Aufploppens)
   * $\zeta = 0.6$ (Dämpfung für leichten Bounce)
3. **Farb-Zustände:**
   * Vor dem Sprechen: `color: rgba(255,255,255,0.4)`
   * Während des Sprechens: `color: #FF5500` (Terrakotta) + `font-size: 1.1x` + `drop-shadow: 0 0 12px #FF5500`
   * Nach dem Sprechen: `color: #FFFFFF`

---

## Phase 3: Audio-Reaktive Kamera & Motion-Engine

### Audio-Gated Character Performance (Verhinderung von Dauer-Mundklappen)
Um zu verhindern, dass ein animierter Charakter in Gesangspausen mit offenem Mund weiterklappt, wird die Animations-Wiedergabe an das Vocal-Band gekoppelt:

1. **State-Switch Logik:**
   * **State IDLE (`vocals < 0.15`):** Freeze auf Frame 0 (Mund geschlossen) oder sanfter Schwebe-/Atem-Loop.
   * **State ACTIVE (`vocals >= 0.15`):** Volle Playback-Geschwindigkeit des Gesangs-Clips.
2. **FFmpeg Gating-Pattern:**
   ```bash
   # Schaltet per select-Filter zwischen Standbild (Idle) und Loop um:
   [char_raw]select='gt(scene,0.1)+gte(val,0.15)'[gated_char];
   ```

### Formeln für visuelle Reaktivität

1. **Zoom-Pulse auf Kicks:**
   $$Zoom(frame) = Zoom_{base} + (BassEnergy(frame) \times 0.08)$$
2. **Glitch-Intensität bei Snares:**
   Wenn `is_snare == true` im aktuellen Frame:
   * RGB-Shift um $\pm 6$ Pixel für 2 Frames.
   * Chromatic Aberration Peak.
3. **Kamera-Shake (Perlin / Sinus-Noise):**
   $$Offset_X(frame) = \sin(frame \times 1.7) \times BassEnergy(frame) \times 4.0$$
   $$Offset_Y(frame) = \cos(frame \times 2.1) \times BassEnergy(frame) \times 4.0$$

---

## Phase 4: Visuelle Verschmelzung & Shader-Compositing

### Protagonisten-Harmonisierung (ToT Gesetz 1 & 4)
Damit der bunte 3D- oder Plüschcharakter der AI-Ströme nicht wie ein Fremdkörper vor dem düsteren Szenenhintergrund klebt, wendet der Filtergraph gezielte **Skalpell-Harmonisierung** an:
1. **Mimik-Schutz (Skalpell):** Die Augen- und Mundpartie wird maskiert und vor schweren Weichzeichnern geschützt (`unsharp=3:3:0.5`).
2. **Color Grade Matching:** Das warme Terrakotta-Fell von Claude wird an das kalte Bunkerlicht des militärischen Radars oben angeglichen:
   ```bash
   # Farb-Harmonisierung für Claude vor kaltem HUD:
   [char_raw]eq=contrast=1.12:saturation=0.88:brightness=-0.04,\
   colorchannelmixer=rr=0.95:gg=0.98:bb=1.05[harmonized_char]
   ```
3. **Lichtkegel-Verschmelzung:** Die Unterseite der oberen Bildebene erhält einen dezenten Farbschleier in Claudes Terrakotta-Glow, sodass es wirkt, als stünde die Kamera im selben Raum.

### Ästhetische Leitplanken
* **Kein bloßer Trennbalken:** Ein statischer schwarzer Kasten wirkt wie ein Schnittfehler. 
* **Bessere Alternativen:**
  1. **Die Integrierte HUD-Brücke:** Ein transparentes Cyber-Gitter mit flackernden Telemetriedaten, die von beiden Hälften geteilt werden.
  2. **Der CRT-Rahmen:** Die obere Szene wird als Anzeige auf einem realen Monitor im Cockpit gerendert (inklusive leichter sphärischer Wölbung `lenscorrection` und Scanlines).
  3. **Licht-Reflexionen:** Die bunte Neon-Bühne unten strahlt farbiges Licht auf die Unterkante der oberen Bildhälfte ab.


---

## Phase 5: Deterministisches Rendering & Quality-Gates

### Prüfmatrix (Muss vor Abnahme 100% grün sein)

| Kriterium | Prüfbefehl / Messung | Akzeptanzkriterium |
| :--- | :--- | :--- |
| **Pixel-Aspect** | `ffprobe -show_streams file.mp4 \| grep sample_aspect_ratio` | `SAR 1:1` |
| **Framerate** | `ffprobe -show_streams file.mp4 \| grep r_frame_rate` | Exakt `30/1` oder `60/1` |
| **Audio-Sync** | Transienten-Visualizer vs. Audio-Wellenform | Transient-Peak $\le 1$ Frame Versatz |
| **Typografie** | Hörprobe mit Videoüberlagerung | Wort leuchtet synchron zur ersten Silbe |
| **Farb-Range** | Farbraum-Check | Standard `yuv420p` (kein `yuvj420p`) |
