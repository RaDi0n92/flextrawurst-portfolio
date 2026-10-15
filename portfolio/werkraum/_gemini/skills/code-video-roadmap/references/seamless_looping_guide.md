# Seamless Looping Guide (Endlos-Schleifen für 100%+ Retention)

Wenn ein Video nahtlos in sich selbst zurückläuft, schaut der Nutzer das Video oft 1,5 bis 2 Mal an, bevor er bemerkt, dass es bereits von vorne begonnen hat. Dies katapultiert die algorithmische Bewertung in die Höhe.

---

## 🔁 1. Das Prinzip des Seamless Loops

Ein perfekter Loop besteht aus drei synchronen Schichten:
1. **Auditorischer Fluss:** Der Ausklang am Ende verbindet sich ohne Knacksen mit dem ersten Beat.
2. **Visueller Match-Cut:** Das letzte Frame geht in das allererste Frame über.
3. **Narrative Satz-Schleife:** Der letzte gesprochene Halbsatz schließt sich syntaktisch an den allerersten Satz an.

---

## 🎙️ 2. Die narrative Satz-Schleife (Beispiele)

### Beispiel für „Maximal noch 3 Sekunden“:
* **Letzter Satz am Video-Ende:**
  * *„...und wenn die Uhr abgelaufen ist, siehst du wieder nur...“*
* **Video springt zu Sekunde 0:00:**
  * *„...DREI PUNKTE AUF DEM SCHIRM!“*
* **Wirkung:** Der Satz ist erst komplett, wenn das Video von vorne beginnt! Der Zuschauer realisiert erst nach 2 Sekunden im zweiten Durchlauf, dass er wieder im Intro ist.

---

## 🎛️ 3. Audio-Crossfade am Loop-Punkt (FFmpeg-Rezept)

Verhindert Knackser oder plötzliche Pausen zwischen Ende und Anfang:

```bash
# Legt die letzten 250ms des Audios als weichen Reverb-Schleier über den Anfang:
ffmpeg -y -i input.mp4 \
  -filter_complex "[0:a]asplit[a1][a2];\
   [a1]atrim=start=0:end=24.75[main_a];\
   [a2]atrim=start=24.75:end=25.0,afade=t=out:st=24.75:d=0.25[tail];\
   [tail][main_a]acrossfade=d=0.25[looped_a]" \
  output_looped.mp4
```

---

## 👁️ 4. Visueller Match-Cut

* **Ursache & Wirkung:**
  * Bei Sekunde `24:28` schlägt der Soldat auf den roten Auslöser.
  * Bei Sekunde `00:00` zuckt der weiße Blitz (Mündungsfeuer / Monitorblitz) auf.
  * Die Bewegung vollendet sich nahtlos über den Loop-Punkt hinweg.
