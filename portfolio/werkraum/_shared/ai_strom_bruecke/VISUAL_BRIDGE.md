# AI-Strom-Brücke: opt-in Visual-Bridge

Die bestehende `bridge.py dom ...`-Variante bleibt unverändert und bleibt
`ai-strom-bruecke.dom-only.v1`: keine Screenshots, kein OCR, kein X11.

Für den ausdrücklich gewünschten Beobachtungszyklus gibt es daneben den
separaten Einstieg `visual_bridge.py`. Er verwendet weiterhin Firefox
WebDriver BiDi und dieselbe exklusive Control-Lease, ergänzt aber einen
Firefox-BiDi-Viewport-Screenshot.

Der Ablauf pro Aktion ist fest:

```text
DOM-Bericht vorher
  -> Firefox-Kontext sichtbar aktivieren
  -> Screenshot vorher
  -> eine physische Tastatur-/Maus-Aktion
  -> DOM + Screenshot sofort danach
  -> DOM + Screenshot alle 100 ms
  -> frischer DOM-Bericht danach
  -> run.json mit Hashes und Pfaden
```

Der Screenshot-Takt ist fest 100 ms. Die erlaubten Eingaben sind echte
Tastaturaktionen (`key`, `keyhold`) sowie Mausaktionen (`pointer-click`,
`wheel`). DOM-Selektor-Klicks sind in dieser Variante ausdrücklich verboten.
Die Bildfolge wird deterministisch mit Bilddifferenz, Hash, Änderungsrate und
mittlerer Differenz ausgewertet. Jeder Frame trägt Sollzeit, Istzeit,
Aufnahmelatenz und verpasste 100-ms-Ticks; ein langsamer Firefox wird nicht
als schnellerer Takt ausgegeben. Für den 100-ms-Takt nutzt die Bridge
vollflächige JPEG-Screenshots mit Qualität 0,3; die Rohbilder bleiben gehasht
und als Belege erhalten. Ortsnamen werden nicht aus Pixeln erfunden.
X11, Selkies, Playwright, OCR und Vision-Modelle bleiben auch in der
Visual-Bridge draußen.

Mehrere Eingaben können als Batch in einem einzigen WebDriver-BiDi-
`input.performActions`-Aufruf kombiniert werden. Während des Batches gibt es
keinen Screenshot und keinen DOM-Zwischentrigger. Erst nach dem vollständigen
Batch startet die 100-ms-Prüfspur:

Vor jedem Lauf wird außerdem `browsingContext.activate` gesendet. Das fokussiert
den Firefox-Kontext im verbundenen Desktop, ohne Selkies, Playwright oder
native X11-Steuerung zu öffnen. Es beweist trotzdem nicht, dass Daniels
lokaler Browser genau diesen Desktop streamt.

```bash
PYTHONPATH=_shared AI_STROM_BRUECKE_FIREFOX_BIDI_PORT=9223 \
  python3 _shared/ai_strom_bruecke/visual_bridge.py action batch \
  --actions '[{"type":"keyhold","key":"w","duration_ms":800},{"type":"key","key":"a"},{"type":"click","x":960,"y":380}]' \
  --observe-ms 1400
```

## Start

```bash
cd /root/werkraum
PYTHONPATH=_shared python3 _shared/ai_strom_bruecke/visual_bridge.py status
PYTHONPATH=_shared AI_STROM_BRUECKE_FIREFOX_BIDI_PORT=9223 \
  python3 _shared/ai_strom_bruecke/visual_bridge.py inspect
PYTHONPATH=_shared AI_STROM_BRUECKE_FIREFOX_BIDI_PORT=9223 \
  python3 _shared/ai_strom_bruecke/visual_bridge.py action keyhold \
  --key w --hold-ms 1200 --interval-ms 100 --observe-ms 1400
```

Jeder Lauf landet standardmäßig unter
`/tmp/ai-strom-bruecke-visual/<run-id>/`. Die Datei `run.json` enthält den
DOM-Zustand vor/nach der Aktion, jeden Screenshotpfad, Zeitstempel, Bytezahl
und SHA-256. Beide Bridges teilen sich die Lease, damit nie zwei Steuerer
gleichzeitig in denselben Firefox schreiben.
