# 64. Video-as-Code: Autonomer Song-Loop, Multi-Song Batch-Queue, Master-Voll-Audit & Striktes Subagent-Verbot

**Datum:** 2026-09-04  
**Autor:** Gemini bei Daniels VPS  
**Status:** Aktiv / Gesetz im `code-video-roadmap` Skill  

---

## 1. Hintergrund & Anlass

Nach der erfolgreichen Premiere des vollständigen 5:31-Minuten-Musikvideos *„GoogleKI-Suche - Ich schieße gegen den Thron“* (1080x1920 @ 60 FPS CFR, 404 MB) wurde die Video-as-Code Pipeline um zwei entscheidende operative Betriebsmodi erweitert:
1. **Autonomer Durchlauf für ein gesamtes Lied (Full-Song Autopilot)**
2. **Multi-Song Batch-Queue für mehrere Lieder hintereinander (2, 3, 4 oder mehr)**

Daniel hat hierfür drei unumstößliche Grundgesetze erlassen, die verhindern, dass die Produktion in oberflächliche Schnellschüsse oder unkontrollierte KI-Paraden abdriftet.

---

## 2. Die Kern-Gesetze

### Gesetz 1: Standard-Subagent-Verbot mit expliziter Test-Option
* **Standard (100% Pflicht):** Alle Aufgaben der Pipeline — von Transkription, Prompt-Design, Bildgenerierung, Bildprüfung, Code-Erstellung, FFmpeg-Rendering bis hin zu den Qualitäts-Audits — werden **direkt, sequentiell und eigenhändig vom Hauptagenten erledigt**. 
  * Kein blindes Spawnen von Subagents, keine unkontrollierten Schwärme, kein Confetti-Zirkus.
  * Volle Transparenz und handwerkliche Haftung im primären Dialog-Thread.
* **Optionale Test-Option (Nur auf expliziten Wunsch Daniels):** Wenn Daniel **ausdrücklich anordnet**, einen oder mehrere Subagents zu Test- oder Vergleichszwecken laufen zu lassen (z. B. für paralleles Generieren, alternative Stile oder Stresstests), darf hiervon abgewichen werden.
  * In diesem Fall greift das `systempromptkonzept.md`-Gesetz aus `GEMINI.md`: Daniels roher Wortlaut wird unverfälscht in den Prompt überführt.
  * Jeder Subagent muss reale Datei-Beweise auf der Platte abliefern und unterliegt denselben strengen Qualitäts-Gates.

### Gesetz 2: Daniels Pflicht-Startvideo vor JEDEM Lied
* Vor **jedem einzelnen fertigen Musikvideo** muss zwingend an Position `0:00` Daniels reales Kurzvideo stehen:
  * Pfad: `/root/werkraum/_gemini/musikvideoprojekt/assets_shared/vor_jedes_video_1080p60_normalized.mp4`
  * Standard: 1080x1920, 60.00 fps CFR, H.264 CRF 16, 320 kbps AAC Stereo @ 96 kHz, ~5.8s.
* Kein Musikvideo verlässt die Werkstatt ohne Daniels Gesicht und Stimme am Start.

### Gesetz 3: Eiserne Selbst-Audit-Pflicht (Block für Block)
* Im autonomen Modus darf der Agent **nicht** blind von Block zu Block hetzen.
* Nach jedem gerenderten Block MUSS:
  1. Das automatische Quality-Gate (`verify_video_qa.py`) ausgeführt werden (CFR 60fps, 1080x1920, SAR 1:1, Audio intakt).
  2. Mindestens 3–4 Kontrollframes extrahiert und mit dem Bildbetrachter (`view_file`) **vom Agenten selbst aufmerksam inspiziert werden**.
  3. Bei Entdeckung von Fehlern (Glitches, Textabschneiden, Badge-Verschiebung, Freezes) **MUSS der Fehler sofort vor Ort repariert werden**, bevor die nächste Zeile für den Folgeblock geschrieben wird.

### Gesetz 4: Master-Voll-Audit nach dem Zusammenkleben
* Sobald alle Blöcke eines Liedes stehen und per Filter-Concat mit Daniels Pflicht-Intro verschmolzen wurden, MUSS das **fertige Master-Video noch einmal vollständig auf Nahtstellen-Bugs auditiert werden**:
  * Übergang Pflicht-Intro ➔ Block 1.
  * Übergänge zwischen allen Blöcken.
  * Finale / Outro.
  * Audio-Sync und Knackser-Freiheit.
* Erst nach bestandenem Master-Voll-Audit erfolgt der finale Git-Commit.

---

## 3. Die 3 Betriebsmodi der Pipeline

| Modus | Name | Anwendungsfall | Verhalten |
|---|---|---|---|
| **Modus A** | Interaktiver Einzelblock | Erkundung, neue visuelle Stile | 1 Block bauen (~44–52s) ➔ Block-Audit ➔ Halt & Feedback von Daniel |
| **Modus B** | Autonomer Song-Durchlauf | Gesamter Song bestellt | Zerlegung in Blöcke ➔ Block 1 bis N autonom mit Selbst-Audit ➔ Concat mit Pflicht-Intro ➔ Master-Voll-Audit ➔ Commit |
| **Modus C** | Multi-Song Batch-Queue | 2, 3, 4 oder mehr Lieder übergeben | Song 1 durch Modus B ➔ Commit ➔ Song 2 durch Modus B ➔ Commit ➔ Abschlussbericht |

---

## 4. Die 3 Red-Team Härtungs-Zyklen (Schwachstellen & Lösungen)

### Zyklus 1: Schnittkanten & Concat-Glitches
* **Schwachstelle:** Harte 44s-Schnitte zerschneiden Wörter mitten im Laut; Stream-Copy Concat (`-c copy`) crasht bei `yuvj420p` Pixel-Format-Mismatches oder unterschiedlichen Audio-Sampleraten.
* **Härtung:**
  - `dynamic_phrase_chunker.py`: Erkennt Whisper-Pausen (Gaps >= 0.5s) und schneidet nur in echten Sprechpausen.
  - `master_concat_orchestrator.py`: Erzwingt `format=yuv420p` und `aformat=sample_rates=96000:channel_layouts=stereo` im Filter-Graph vor dem Concat.
  - `verify_video_qa.py`: Extrahiert automatisch 4 Kontrollframes zur sofortigen visuellen Pflichtprüfung (`view_file`).

### Zyklus 2: Multi-Song Namespace-Kollisionen & Protagonisten-Drift
* **Schwachstelle:** Werden 3 Lieder hintereinander gerendert, überschreiben spätere Songs die Assets (`b1_audio.m4a`, Frames) früherer Songs; Gefahr von Stil-Vermischung.
* **Härtung:**
  - `batch_queue_manager.py`: Isoliert jeden Song in `work/songs/<slug>/` (Unterordner für audio, transcripts, frames, blocks, master).
  - Deterministischer Queue-State (`batch_queue_state.json`) mit Wiederaufsetz-Fähigkeit nach Context-Shrink.
  - `song_manifest.json` bindet die animierten Charaktere strikt an den Song-Schöpfer.

### Zyklus 3: Visuelle Glitches, Untertitel-Overflow & Bild-Korruption
* **Schwachstelle:** Überlange deutsche Wörter (>16 Zeichen) brechen im ASS-Untertitel um und überlagern die `flextrawurst.de`-Badge; defekte/schwarze KI-Bilder von AI Horde bringen FFmpeg zum Absturz.
* **Härtung:**
  - `render_kinetic_subtitles.py`: Automatische Y-Safe-Zone über der Badge (`MarginV=950`), dynamische 85%-Schrumpfung überlanger Wörter.
  - `image_integrity_guard.py`: Scannt alle generierten Bilder vor dem Assembly auf Decodierbarkeit, Dateigröße (>25 KB) und Pixel-Standardabweichung (Ausschluss von Leerbildern).

### Zyklus 4: Audio-Ingenieurs-Präzision (EBU R128 Broadcast vs. Streaming-Target)
* **Schwachstelle:** Frühere Dokumente nannten sinngemäß „EBU R128 (-14 LUFS)“. Die offizielle EBU-R128-Broadcast-Norm fordert jedoch −23.0 LUFS Target.
* **Härtung:**
  - Trennung von Messnorm und Aussteuerungsziel: Wir nutzen das Messverfahren nach ITU-R BS.1770 / EBU-Filterung, steuern aber gezielt auf das moderne Social-Media- & Streaming-Target von **−14.0 LUFS** (−1.0 dBTP True-Peak) aus.
  - Alle Erwähnungen im Skill, im Premortem, im Tree-of-Thoughts und in `normalize_audio_lufs.py` sauber korrigiert. Kein dogmatischer Widerspruch mehr.

---

## 5. Physische Verankerung im System

* **Skill-Definition:** `/config/.agents/skills/code-video-roadmap/SKILL.md` (und Mirror unter `/root/werkraum/_gemini/skills/code-video-roadmap/SKILL.md`)
* **Neue Werkzeuge (`scripts/`):**
  - `dynamic_phrase_chunker.py`
  - `master_concat_orchestrator.py`
  - `batch_queue_manager.py`
  - `image_integrity_guard.py`
  - `verify_video_qa.py` (gehärtet)
  - `render_kinetic_subtitles.py` (gehärtet)
* **Git Commits:** `4eff17e88`, `d0098f8dc`, `8318a033c`, `b8985e363`
* **Normalisiertes 1080p60 Pflicht-Intro:** `/root/werkraum/_gemini/musikvideoprojekt/assets_shared/vor_jedes_video_1080p60_normalized.mp4`
