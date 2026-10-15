# FFmpeg Filter-Rezepte für Audio-Reaktive & Visuelle Effekte

Diese Sammlung enthält praxiserprobte, modulare FFmpeg-Filtergraphen für das Compositing von code-generierten Videos.

---

## 1. Perfektes 9:16 Hochkant-Framing ohne Eierkopf (Square Pixels SAR 1:1)

Verhindert, dass FFmpeg beim Skalieren von 16:9 auf vertikale Formate ungerade Pixelverhältnisse (non-square SAR) erzeugt:

```bash
# Oben: 480x390 mit zentriertem Crop und garantiertem SAR 1:1
[0:v]scale=480:390:force_original_aspect_ratio=increase,crop=480:390,setsar=1/1[top];

# Unten: 480x390 mit Boxblur-Hintergrund und zentriertem 1:1 Vordergrund
[1:v]scale=480:390:force_original_aspect_ratio=increase,crop=480:390,boxblur=12:4,setsar=1/1[bot_bg];
[1:v]scale=390:390,setsar=1/1[bot_fg];
[bot_bg][bot_fg]overlay=(W-w)/2:(H-h)/2[bot];
```

---

## 2. CRT-Scanline & Phosphor-Flackern (Militär-Monitor Simulation)

Macht aus einem statischen KI-Bild einen lebendigen, summenden Röhrenbildschirm:

```bash
# Generiert CRT-Scanlines über drawgrid und leichtes periodisches Flackern
[top_raw]drawgrid=width=1:height=4:thickness=1:color=black@0.4[scanlines];
[scanlines]eq=brightness='0.02*sin(2*PI*t*15)':contrast=1.1:saturation=0.9[crt_out]
```

---

## 3. Jitter-Freie Kamerafahrt mit Sinus-Easing (Kein fehlerhafter zoompan)

Ersetzt den zittrigen `zoompan`-Filter durch eine mathematisch stabile, jitter-freie Skalierung mit Ease-In/Ease-Out-Kurve:

```bash
# Easing-Formel: 0.5 * (1 - cos(PI * t / Dauer))
# Skaliert das Bild geschmeidig von 100% auf 110% ohne Subpixel-Zittern
[0:v]scale=eval=frame:w='iw*(1.0 + 0.10*0.5*(1-cos(PI*t/6.0)))':h=-1,crop=480:390:(iw-480)/2:(ih-390)/2,setsar=1/1[smooth_cam];
```

---

## 4. Dynamischer Beat-Zoom (Audio-Pulse)

Vergrößert das Bild synchron zu einer Transienten-Kurve:

```bash
# Eignet sich für Onsets: t_beat ist der Zeitpunkt des Kicks
[in]scale=eval=frame:w='if(between(t, 1.20, 1.35), 480*1.08, 480)':h=-1,crop=480:390,setsar=1/1[pulse_out]
```

---

## 4. Chromatic Aberration & Glitch-Trigger

Erzeugt bei Snare-Schlägen eine kurze Farbkanaltrennung (RGB-Split):

```bash
# Separiert Rot- und Blau-Kanal und verschiebt sie leicht horizontal
[in]split=3[r][g][b];
[r]lutrgb=g=0:b=0[r_only];
[g]lutrgb=r=0:b=0[g_only];
[b]lutrgb=r=0:g=0[b_only];
[b_only]pad=iw+8:ih:4:0:black[b_shifted];
[r_only][g_only]blend=all_mode=addition[rg];
[rg][b_shifted]blend=all_mode=addition[glitch_out]
```

---

## 5. Vollständiges vertikales 3-Zonen Compositing mit Divider

```bash
ffmpeg -y \
  -loop 1 -r 30 -i top_scene.jpg \
  -r 30 -i bottom_anim.mp4 \
  -i audio.mp3 \
  -filter_complex "\
    [0:v]scale=480:390:force_original_aspect_ratio=increase,crop=480:390,setsar=1/1[top];\
    color=c=0x0a0e17:s=480x74:d=25,drawbox=x=0:y=0:w=480:h=2:color=0x00ffcc:t=fill,drawbox=x=0:y=72:w=480:h=2:color=0x00ffcc:t=fill[mid];\
    [1:v]scale=480:390:force_original_aspect_ratio=increase,crop=480:390,boxblur=12:4,setsar=1/1[bot_bg];\
    [1:v]scale=390:390,setsar=1/1[bot_fg];\
    [bot_bg][bot_fg]overlay=(W-w)/2:(H-h)/2[bot];\
    [top][mid][bot]vstack=inputs=3[v_stacked]\
  " \
  -map "[v_stacked]" -map 2:a \
  -c:v libx264 -preset veryfast -crf 20 -pix_fmt yuv420p \
  -c:a aac -b:a 192k -shortest output.mp4
```

---

## 6. High-End Mastering für dunkle Szenen & Neon-Grading (Anti-Banding)

Verhindert Farb-Treppen (Banding) in dunklen Bunker-Ecken und Ausfransen von Neon-Kanten auf Social-Media-Plattformen:

```bash
# Optimales x264-Mastering-Kommando für TikTok & Instagram:
ffmpeg -y -i input_raw.mp4 \
  -vf "format=yuv420p" \
  -c:v libx264 -preset slow -crf 19 \
  -x264-params "aq-mode=3:aq-strength=1.1:qcomp=0.7:deblock=-1,-1" \
  -color_primaries bt709 -color_trc bt709 -colorspace bt709 \
  -c:a aac -b:a 192k \
  -movflags +faststart \
  mastered_output.mp4
```

* **`aq-mode=3`:** Bias towards dark scenes (investiert Bitrate gezielt in dunkle Bereiche).
* **`aq-strength=1.1`:** Verhindert Makro-Blocking in Schatten.
* **`movflags +faststart`:** Verschiebt den `moov`-Atom an den Dateianfang (sofortiges Abspielen auf Mobilgeräten ohne Ladeverzögerung).

---

## 7. Frame-0 Flash & Snap-Zoom (Pattern Interrupt Hook)

Erzeugt in den ersten 6 Frames (0.2 Sekunden) einen weißen Überblendungs-Blitz und einen raschen Snap-Zoom von 125 % auf 100 %, um das Auge sofort zu fesseln:

```bash
# Weißer Aufblitz (0 bis 0.15s) + Snap-Zoom
[in]scale=eval=frame:w='if(lte(t,0.25), 480*(1.25-t), 480)':h=-1,crop=480:390,\
eq=brightness='if(lte(t,0.15), 0.6*(1.0-t/0.15), 0.0)':contrast=1.1[hook_punch_out]
```

---

## 8. Prozeduraler Digital-Countdown-Timer (00:03.00 rückwärts)

Blendet im HUD einen gestochen scharfen, rückwärtslaufenden Millisekunden-Timer ein:

```bash
# Countdown von 3.00 Sekunden bis 0.00 Sekunden:
drawtext=fontfile='/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf':\
text='00\:%{eif\:max(0,3-t)\:d\:2}.%{eif\:max(0,(3-t)*100)-trunc(max(0,3-t))*100\:d\:2}':\
fontcolor=0x00FFCC:fontsize=18:box=1:boxcolor=black@0.7:boxborderw=4:\
x=(w-text_w)/2:y=60
```

---

## 9. Audio-Reaktives Ambient-Glow & Holo-Pillarbox (Nie wieder toter Matsch-Blur)

Verwandelt den toten Randbereich bei der Einbettung von 1:1 oder 16:9 Inhalten in ein lebendiges, pulsierendes Cyber-Display:

```bash
# 1. Hintergrund: Skalieren + Farbverstärkung + Sanfter Blur + Scanlines
[fg_raw]scale=480:390:force_original_aspect_ratio=increase,crop=480:390,\
eq=contrast=1.2:saturation=1.5:brightness=-0.1,\
boxblur=8:2,\
drawgrid=width=1:height=6:thickness=1:color=cyan@0.15,\
setsar=1/1[holo_bg];

# 2. Vordergrund: Gestochen scharf zentriert mit leuchtendem 2px Cyber-Rahmen
[fg_raw]scale=390:390,drawbox=x=0:y=0:w=390:h=390:color=0x00FFCC@0.8:t=2,setsar=1/1[sharp_fg];

# 3. Zusammenfügen
[holo_bg][sharp_fg]overlay=(W-w)/2:(H-h)/2[ambient_pillarbox_out]
```

---

## 10. Dynamic Audio-Ducking & SFX-Layering für den 1-Sekunden-Hook

Dämpft die Musik in den ersten 1,2 Sekunden automatisch um $-4\,\text{dB}$ ab, damit mechanische Soundeffekte (Schalter, Aufblitz, Sonar) und die Gesangsstimme kristallklar durchdringen:

```bash
# [0:a] = Musikspur, [1:a] = SFX-Sample (z.B. mechanischer Klick/Subdrop)
ffmpeg -y -i music.mp3 -i sfx_click.wav \
  -filter_complex "\
    [0:a]volume='if(lte(t,1.2), 0.65, 1.0)':eval=frame[music_ducked];\
    [music_ducked][1:a]amix=inputs=2:duration=first:weights='1.0 1.2'[master_a]\
  " -map "[master_a]" mixed_audio.mp3
```
