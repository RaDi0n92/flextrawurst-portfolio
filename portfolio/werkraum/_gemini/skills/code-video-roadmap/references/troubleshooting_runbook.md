# Troubleshooting & Fehlerbehebungs-Runbook

Dieses Handbuch dokumentiert die häufigsten technischen Fehler beim programmatischen Rendern mit FFmpeg / Python und liefert sofort anwendbare Reparatur-Befehle.

---

## 1. Fehler: `width/height not divisible by 2`
* **Symptom:** `[libx264 @ 0x...] width not divisible by 2 (481x854)` oder Absturz beim Enkodieren.
* **Ursache:** Der H.264/H.265-Codec benötigt für Chroma-Subsampling (YUV 4:2:0) geradzahlige Dimensionen.
* **Sofort-Lösung:**
  Hänge ans Ende der Videofilterkette immer diesen Rundungs-Filter:
  ```bash
  scale=trunc(iw/2)*2:trunc(ih/2)*2
  ```

---

## 2. Fehler: `No usable fontconfig configuration found` / Font-Absturz
* **Symptom:** `[subtitles @ 0x...] No usable fontconfig configuration found` oder Schriftarten werden nicht gerendert.
* **Ursache:** Fehlender Fontconfig-Cache oder falscher Pfad in Linux.
* **Sofort-Lösung:**
  1. Font-Cache aktualisieren:
     ```bash
     fc-cache -f -v
     ```
  2. Im Filter immer absolute Fontdateien referenzieren:
     ```bash
     drawtext=fontfile='/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf':text='...'
     ```

---

## 3. Fehler: Audio-Video Desynchronisation (Drift nach 20+ Sekunden)
* **Symptom:** Zu Beginn sitzt der Beat, aber nach 30 Sekunden hinkt das Bild hinterher.
* **Ursache:** Die Quell-Videos haben Variable Frame Rate (VFR) statt Constant Frame Rate (CFR), oder Timebases weichen ab.
* **Sofort-Lösung:**
  Erzwinge vor der Filterung immer feste Frameraten und synchrone PTS-Timestamps:
  ```bash
  -r 30 -i input.mp4 -vf "fps=30,settb=AVTB,setpts=PTS-STARTPTS"
  ```

---

## 4. Fehler: Anamorphic SAR/DAR Verzerrung (`SAR 129:128`)
* **Symptom:** Gesichter oder Schriften wirken in manchen Playern vertikal gestaucht oder in die Länge gezogen.
* **Ursache:** FFmpeg hat beim Skalieren das Sample Aspect Ratio (SAR) ungleich 1:1 gesetzt.
* **Sofort-Lösung:**
  Setze am Ende der Filterkette explizit quadratische Pixel:
  ```bash
  setsar=1/1
  ```

---

## 5. Fehler: Out of Memory (OOM Kill) bei komplexen Filterketten
* **Symptom:** `Killed` im Terminal während des Renderings auf Linux/VPS.
* **Ursache:** Zu viele gleichzeitige `boxblur`-, `lenscorrection`- oder `vstack`-Operationen im RAM.
* **Sofort-Lösung:**
  1. Preset auf `veryfast` oder `ultrafast` stellen.
  2. Thread-Limitierung setzen:
     ```bash
     ffmpeg -threads 2 ...
     ```
  3. Zweistufig rendern: Erst Hintergründe/Effekte vorrendern, dann Typografie im zweiten schnellen Durchgang einbrennen.
