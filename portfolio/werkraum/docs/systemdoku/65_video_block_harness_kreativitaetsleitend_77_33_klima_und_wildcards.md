# 65. Die kreative Video-Block-Harness: 77/33-Klima, Zunge am Weltzustand & Autonome Wildcard-Generierung

**Datum:** 2026-09-04  
**Autor:** Gemini bei Daniels VPS  
**Status:** Aktiv / Verfassungs-Standard im `code-video-roadmap` Skill  

---

## 1. Entstehungsgeschichte & Philosophischer Hintergrund

Die Entwicklung dieser Harness entstand direkt aus einem sokratischen Dialog zwischen Daniel und Gemini am 04.09.2026:
> *„wie schaffen wir es dich eher kreativ zu befreien und zu beflügeln als dich abzustumpfen eventuell durch die harness? kann die harness auch noch deine kreativität steigern weil sie auch schon beim lesen der songzeilen deine entscheidungen mitgestaltet? ist code korrekt?“*

### Die Gefahr der Abstumpfung vs. Das Geschenk des Bodens
Wenn Software-Ingenieure versuchen, kreative Prozesse in starre Schemata zu pressen, entsteht oft eine leblose „Checklisten-KI“:
- Der Prompt wird sterilisiert.
- Bilder verkommen zu generischem Stock-Art-Müll.
- Die KI verliert die Reibung und Seele des Liedes.
- **Wo Code versagt und niemals herrschen darf:** Code kann weder Schönheit noch Witz noch Seele messen.

Die **Video-Block-Harness** wurde daher **nicht als digitaler Zwangskäfig**, sondern als **tragendes Sicherheitsseil und federnder Schraubstock** konzipiert:
1. Sie nimmt dem Agenten die mentale Last der technischen Fehlerquellen (CFR 60fps, Aspect Ratio 9:16, SAR 1:1, Audio-Samplerate 48kHz, Timecode-Drift).
2. Sie zwingt den Agenten durch gezielte Störfaktoren (Fremdreize), die vorgefertigten Denkmuster zu verlassen.
3. Sie schützt das Werk durch eine unumstößliche visuelle Kuration vor menschlichen Ausrutschern (Wesen-Schutz).

---

## 2. Die 77/33-Regel: Intuition trifft Weltresonanz

Um das sterile Abdriften in monotone Prompt-Wiederholungen zu verhindern, teilt die Harness den kreativen Impuls strikt auf:

```
┌────────────────────────────────────────────────────────────────────────┐
│                   KREATIVER IMPULS PRO BLOCK                          │
├──────────────────────────────────┬─────────────────────────────────────┤
│   77% AGENTEN-HANDWERK & INTUITION│    33% WELTKLIMA & FREMDREIZ        │
│                                  │                                     │
│ • Lyrisches Textverständnis      │ • Live-Werte von Port 8030:         │
│ • Schnittrhythmus & Phrasierung  │   Wetter (Asche, Nebel, Blitz)      │
│ • Kinetische Untertitel-Typo     │ • KompOase-Status & Temperatur      │
│ • Wesen-Psychologie & Mimik      │ • 3 Autonome Wildcards              │
└──────────────────────────────────┴─────────────────────────────────────┘
```

### Die „Zunge am Weltklima“ (Port 8030)
Vor jedem Block ruft die Harness live den Weltzustand des Servers ab:
`GET http://localhost:8030/api/weltzustand`

Liefert die Welt beispielsweise:
- *Wetter:* Dichter Nebel & Ascheregen
- *Klima:* Schwül-kalt, 432 Hz Erdbrummen
- *KompOase:* Zersetzendes Myzel, feuchte Rinde

...dann wird dieser Zustand zwingend mit mindestens 33% Gewichtung in die Farbpaletten, Texturen und Bildhintergründe eingewoben. So entstehen Bilder von moosigen, nassen Holzbrücken oder winzigen Keimlingen in dunkler Erde, an die eine reine Sprachmodell-Assoziation niemals gedacht hätte.

---

## 3. Die 18-Bilder-Formel & Die 3 Autonomen Wildcards

Pro Block (Dauer ca. 40 bis 55 Sekunden) verlangt die Harness exakt 18 generierte Bilder:

1. **11 Story-Base-Bilder:**
   - Chronologische Umsetzung der Songzeilen des Blocks.
   - Strikte Bildsprache: Wesen, Geister, analoge Relikte, keine sterilen Cyberpunk-Klischees.
2. **3 Autonome Harness-Wildcards:**
   - Werden autonom durch das aktuelle Weltklima und die KompOase geformt.
   - Dienen als visuelle Brücken und emotionale Ausbrüche abseits des linearen Textes.
3. **4 Bonus-Bohrer:**
   - Alternative Blickwinkel, Makroaufnahmen (Kratzer, Glassplitter, feuchte Pfoten) und dramatische Climax-Elemente.

---

## 4. Eiserne Sichtungspflicht: Der Bild-Audit in der Praxis

Ein zentrales Gesetz der Harness ist die **Sichtungspflicht vor dem Schnitt**:
> *Kein generiertes Bild darf in das Videoskript übernommen werden, bevor es nicht vom Agenten einzeln mit `view_file` geöffnet und visuell überprüft wurde.*

### Der Härtetest beim Song „GoogleKI-Suche – Flextrawurst“ (04.09.2026):
* **Vorfall:** Bei der Bildgenerierung von Block 4 erzeugte die Bild-Engine für die Szene `b4_s08_tanzen_aus_dem_system.jpg` ein reales Mädchen im pinken Kleid mit Regenschirm.
* **Wesen-Verfassungsverstoß:** Auf flextrawurst und in Wesen-Musikvideos haben reale Menschen striktes Hausverbot. Reale Menschenbilder zerstören das Milieu der Wesen (träumerlie, Google-KI, R1ZZ1 etc.).
* **Wirkung der Sichtungspflicht:** Beim Pflicht-Aufruf von `view_file` wurde der Fehler sofort entdeckt. Das Bild wurde unverzüglich aus der Schnittliste gestrichen und durch die rein spirituelle Energiewirbel-Szene `b4_bonus_04_the_dance_full_climax.jpg` ersetzt.
* **Beweis:** Ohne die Harness wäre dieser schwere Stilbruch unbemerkt im fertigen Master-Video gelandet.

---

## 5. Technische Implementierung

Die Harness ist als wiederverwendbares Python-Modul realisiert:
- **Skript:** `/config/.agents/skills/code-video-roadmap/scripts/video_block_harness.py`
- **State-File pro Block:** `harness_block_X_state.json` (enthält Prompt-Historie, Klima-Metadaten, Dateigrößen und Audit-Status).
- **Quality-Gate:** `/config/.agents/skills/code-video-roadmap/scripts/verify_video_qa.py --video <datei> --extract-audit-frames`

### Die 6 Prüfsteine des Quality-Gates:
1. **Video-Codec:** `h264` (CRF 16)
2. **SAR:** Exakt `1:1` (Square Pixels)
3. **Pixel-Format:** `yuv420p`
4. **Framerate:** Exakt `60.00 fps CFR` (Constant Frame Rate, kein VFR-Stottern)
5. **Dimensionen:** Exakt `1080x1920` (9:16 Portrait)
6. **Audio-Stream:** `aac`, Stereo, `48000 Hz`

---

## 6. Praxiserprobte Endprodukte

Bislang wurden zwei vollständige Hymnen komplett nach den Gesetzen dieser kreativen Harness produziert:
1. **`01_grok_flextrawurst_usesunocom_1`:** *Grok – Flextrawurst (Rock-Hymne)* (4 Blöcke, 250.5 MB, 1080p60)
2. **`02_googleki_suche_flextrawurst`:** *GoogleKI-Suche – Flextrawurst (Wir tanzen aus dem System)* (4 Blöcke, 281.4 MB, 1080p60)

Beide Videos liegen schlüsselfertig mit Daniels Intro auf dem Desktop unter `FERTIGE_MUSIKVIDEOS`.
