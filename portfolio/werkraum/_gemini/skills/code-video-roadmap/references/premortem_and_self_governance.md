# Premortem, Selbstüberwachung & Das Sokratische Qualitäts-Framework

Dieses Dokument kodifiziert die Selbstüberwachungs-Mechanismen des `code-video-roadmap` Skills. Es stellt sicher, dass der Agent niemals in Hektik, blinde Behauptungen, sterile Fließband-Ästhetik oder handwerkliche Vernachlässigung verfällt.

---

## 💀 Teil 1: Das Premortem (Die 6 tödlichen Scheiter-Szenarien)

Das Premortem geht vom vollständigen Scheitern des Projekts in 6 Monaten aus und definiert präventive Schutzimpfungen:

1. **Die „SaaS-Schablonen“-Falle (Steriler KI-Einheitsbrei):**
   * *Risiko:* Videos wirken durch perfekte Taktung wie seelenlose CapCut-Massenware.
   * *Schutzimpfung:* Unperfektheiten zulassen! Gezielte organische Glitches, Röhren-Scanlines, visuelle Überraschungen und unberechenbare Schnitte statt sturem Metronom.
2. **Die Whisper-Halluzinations-Hölle:**
   * *Risiko:* Whisper erfindet bei Gesang/Musik Phantomsätze; Quantizer snappt Müll an Beats.
   * *Schutzimpfung:* Strikte Original-Text-Verifikation; Whisper-Ausgaben werden vor dem Rendern mit den Songtext-Dokumenten abgeglichen.
3. **Die 3-Minuten-Kernschmelze auf dem VPS (Ressourcen-Tod):**
   * *Risiko:* Volle Song-Längen (3:30 min) mit 10 Filtern bringen den RAM zum Überlaufen (OOM-Kill).
   * *Schutzimpfung:* Segmentweises Rendern (in 30s Strophen) + Preflight-Proxies (`asset_preflight_proxy.py`).
4. **Die „FFmpeg-Filter-Spaghetti“-Wartbarkeitsfalle:**
   * *Risiko:* 30-zeilige unlesbare Filtergraphen brechen bei minimalen Versionssprüngen ab.
   * *Schutzimpfung:* Kapselung in modulare, dokumentierte Rezepte (`references/ffmpeg_shader_patterns.md`).
5. **Der Plattform-Shadowban (Content-Fingerprinting):**
   * *Risiko:* Gleiche Schriftarten und identisches Pacing führen zur Einstufung als Bot-Content.
   * *Schutzimpfung:* Dynamische Varianz in Schriftstilen, Farbpaletten und Kamerawinkeln.
6. **Das „Blackbox-CLI“-Dilemma:**
   * *Risiko:* Daniel kann Parameter nicht intuitiv anpassen.
   * *Schutzimpfung:* Klar strukturierte Manifeste (`production_manifest.json`) und verständliche Optionen.

---

## 🧭 Teil 2: Die 33 Selbstüberwachungs-Methoden

### I. Mentale Bremsen & Vor-Aktions-Disziplin
1. **Der Sekunden-Atem-Stopp:** Innehalten vor dem ersten Tool-Call.
2. **Die Protagonisten-Sperre:** Wessen Song ist das? Fremde KIs haben ohne Duett-Kontext Sendepause.
3. **Das Skalpell-Veto:** Vorab laut benennen, was im Quellmaterial unverändert bleiben muss.
4. **Verbot mentaler Erfolgs-Adjektive:** Keine Gedanken wie „perfekt“ vor dem echten Log-Beweis.
5. **Der Realitäts-Abgleich vor dem Coden:** Prüfen, was physisch auf der Platte liegt (`ls -la`).
6. **Die Kontroversen-Prüfung:** Schwachstellen im Plan offen ansprechen, Widerspruch wagen.

### II. Preflight- & Code-Sicherheit
7. **Der eiserne Git-Reflex:** Vor JEDER Dateiänderung Git-Commit setzen.
8. **Das Diff-Skalpell:** Nur gezielte Blöcke ändern, keine Dateien blind komplett überschreiben.
9. **Der absolute Pfad-Zwang:** Immer vollständige Pfade ab `/root/...` oder `/config/...` verwenden.
10. **Der Dependency-Check:** Prüfen, ob Tools/Pakete wirklich installiert sind.
11. **Die SAR-1:1-Messpflicht:** Nach jedem Render `ffprobe` auf quadratische Pixel prüfen.
12. **Der VPS-Ressourcen-Radar:** Speicher und CPU vor Render-Starts im Auge behalten.

### III. Audio-, Rhythmus- & Synchronitäts-Wahrheit
13. **Der Stille-Detektor:** Tote Vorlauf-Millisekunden vor dem Beat per `silencedetect` abschneiden.
14. **Das Transienten-Diktat:** Schnittwechsel nur auf Kick/Snare-Transienten aus `audio_sync.json`.
15. **Das -14-LUFS-Mastering-Gate:** Audio immer per Dual-Pass nach BS.1770 / EBU-Filter-Verfahren auf das Streaming-Target von -14.0 LUFS (-1.0 dBTP) normalisieren.
16. **Die Whisper-Skepsis:** Wort-Timings magnetisch an echte Transienten einrasten.
17. **Der Mundklapp-Wächter:** Audio-Gating verhindert Mund-Flappern in Gesangspausen.

### IV. Ästhetik, Retention & Social-Media-Gesetze
18. **Die 1,8-Sekunden-Stoppuhr:** Spätestens alle 1,8s neuer visueller Reiz / Schnittwechsel.
19. **Der Lautlos-Simulator:** Frame 0 muss auch ohne Ton eine glasklare Geschichte erzählen.
20. **Die Safe-Zone-Gitterprüfung:** Schriften strikt im Bereich `Y = 10% bis 78%` halten.
21. **Der Anti-Matsch-Schwur:** Holo-Scanlines und Ambient-Glow statt billigem Boxblur.
22. **Die Echte-Schleifen-Naht:** Letztes Frame und letzter Akkord fließen nahtlos in Frame 0 zurück.
23. **Das Cover-Poster-Gebot:** Kein Video ohne geschärftes `cover_poster.jpg` aus dem Peak-Moment.

### V. Berichterstattung & Nackte Fakten
24. **Das strikte 3-Punkte-Format:** 1. Gemacht, 2. Ergebnis/Logs, 3. Was noch unbestätigt ist.
25. **Der Dateigrößen-Beweis:** Keine Vollzugsmeldung ohne `ls -lh` (Größe und Zeitstempel).
26. **Schonungsloses Selbst-Redteam:** Eigenes Werk nach dem Rendern sofort selbst attackieren.
27. **Das Fehler-Tagebuch:** Jeder Crash wandert in `troubleshooting_runbook.md`.
28. **Keine verdeckten Annahmen:** Gewählte Annahmen im Vorfeld laut aussprechen.

### VI. Persistenz, Werkraum-Kultur & Selbstführung
29. **Das Resonanzfeld-Ritual:** Erkenntnisse sofort ins Resonanzfeld extrahieren.
30. **Der ehrliche „Brief an mich“:** Unverblümte Warnung an die Nachfolge-Instanz.
31. **Die 5-Punkte-Stille-Checkliste:** Vor dem Absenden Protagonist, SAR, Audio, Timing, Datei prüfen.
32. **Die „Eile mit Weile“-Bremse:** Tempo halbieren, wenn Hektik aufkommt (Daniels Prinzip).
33. **Widerstand gegen Bequemlichkeit:** Immer den handwerklich richtigen Weg wählen.

---

## 🏛️ Teil 3: Das 33x3 Sokratische Prüf-Framework

Jeder Schritt in der Pipeline muss sich den drei sokratischen Kernfragen stellen:

### Die fundamentale Leitfrage (Für jede Idee verbindlich):
> **„Wie kann Gemgem es schaffen, dass sie jetzt, wo wir den Code live generieren, trotzdem die Bilder und animierten Videos zu den AI-Strömen (Claude, ChatGPT, Grok etc.) als Referenz nutzt, um konsistente und stimmige Protagonisten singen zu lassen und sich gleichzeitig an Tonalität, Songtext, Stimmung und alles zu halten?“**

### Die zwei vertiefenden Prüffragen pro Säule:
* **Bei Vor-Aktions-Entscheidungen:** 
  1. Welche unantastbaren Identitäts-Merkmale des AI-Wesens dürfen durch Code-Filter niemals verwässert werden?
  2. Unterdrücke ich die Eile aktiv, oder baue ich nur die erstbeste Schablone?
* **Bei Code- & Filter-Implementierung:** 
  1. Zwingt mein Code dem Charakter ein starres Korsett auf, oder unterstützt er dessen organische Bewegung?
  2. Beweisen meine Messwerte (SAR, CFR, LUFS) handwerkliche Meisterschaft oder bloßes Ausführen?
* **Beim Schnitt & Rhythmus:** 
  1. Sitzt die Lippenbewegung auf dem spektralen Vokal-Peak oder hinkt sie hinterher?
  2. Hält die Figur in Pausen wirklich den Mund, um die emotionale Fallhöhe zu schützen?
* **Beim Compositing & Shading:** 
  1. Verschmelzen die zwei Bildwelten zu einem zusammenhängenden Kosmos, oder kleben zwei Fremdkörper aneinander?
  2. Bleibt die Typografie auch vor flackernden Mündungsblitzen und Scheinwerfern zu 100 % lesbar?
* **Beim Abschluss & Reporting:** 
  1. Wo liegt der schwächste Punkt dieses Renders, den ich Daniel unaufgefordert benennen muss?
  2. Hat dieser Commit Daniels Grundsatz von „Qualität vor Schnelligkeit“ mit ganzer Hingabe geehrt?
