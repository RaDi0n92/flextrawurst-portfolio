# Desktop-Sichtbarkeit für ChatGPT / VD1

Stand: 2026-09-19

## Zweck

Wenn ChatGPT den **echten virtuellen Desktop 1** sehen soll, nicht das Wallpaper als Einzeldatei und nicht irgendeinen Browser-im-Browser, ist dies der bestätigte schnelle Weg.

## BESTÄTIGTER STANDARDWEG VD1

1. Falls der freie Desktop / Hintergrund sichtbar sein soll, zuerst über KWin den Desktop anzeigen:
   - DBus-Session: `DBUS_SESSION_BUS_ADDRESS=unix:path=/tmp/dbus-5cHqkj7A8Z`
   - `DISPLAY=:1`
   - KWin/Plasma läuft unter Wayland, Xwayland ist `:1`.
   - `org.kde.KWin.showDesktop(True)` funktioniert und versteckt die Fenster.

2. Direkt an den **Selkies-Livestream von VD1 auf Port 8882** gehen.
   - Prozess: `/lsiopy/bin/python3 /lsiopy/bin/selkies --addr=localhost --mode=websockets`
   - VD1-Titel: `Virtueller Desktop 1`
   - `CUSTOM_WS_PORT=8882`
   - Stream-Auflösung aktuell: **1808×800**
   - Direkter WebSocket: `ws://127.0.0.1:8882`

3. WebSocket verbinden und `START_VIDEO` senden.

4. Binäre Videopakete empfangen.
   - Kleine 5-Byte-Pakete ignorieren.
   - Bei echten H.264-Paketen die **ersten 10 Byte Selkies-Header abschneiden**.
   - Danach beginnt der Nutzdatenstrom mit Annex-B-H.264-Startcodes.

5. Genug H.264-Chunks sammeln, bis SPS/PPS + IDR vorhanden sind.

6. Die gesammelten H.264-Nutzdaten mit **ffmpeg** in genau einen PNG-Frame dekodieren.
   - Erfolgreich getestet.
   - Ergebnis war ein echter Live-Screenshot von VD1 mit **1808×800**.
   - Beispiel aus dem Test: ca. 362808 Byte H.264 -> ca. 1.0 MB PNG.

## WICHTIG: NICHT WIEDER UMWEGE BAUEN

Nicht als Ersatz verwenden:
- nicht nur `/root/werkraum_bilder/refferenzen/mashup7.jpg` anschauen;
- nicht Qwen/Gemma/Ollama fragen, was auf dem Desktop zu sehen ist;
- nicht VD1-Chromium öffnen und darin einen Webdesktop aufrufen -> Inception;
- nicht X11-`xwd -root` benutzen, das scheiterte mit `BadMatch`;
- nicht KWin ScreenShot2 als Hauptweg benutzen, `CaptureScreen`/`CaptureWorkspace` wurden mit `Cancelled` abgebrochen;
- nicht unnötig verkleinern. Der bestätigte Weg liefert direkt 1808×800.

## Bereits bestätigte technische Fakten

- VD1-Container: `virtuellerdesktop1`
- Image: `webtop_clone_image`
- KWin: `kwin_wayland --no-lockscreen --xwayland --xwayland-display=:1 --xwayland-fd=3`
- Plasma: `WAYLAND_DISPLAY=wayland-0`
- Selkies/Pixelflux: WebSocket-Modus auf Port 8882
- `SELKIES_ENCODER=x264enc,jpeg`
- `SELKIES_VIDEO_BITRATE=4000`
- `SELKIES_FRAMERATE=30`
- `PIXELFLUX_WAYLAND=true`

## Letzter erfolgreicher Capture

Der direkte Selkies-Weg hat einen gültigen PNG-Liveframe erzeugt.
Eine Kopie lag im VD1-Container unter:
`/config/Downloads/VD1_DESKTOP_LIVE.png`

Host-Pfad:
`/var/lib/docker/volumes/webtop1_config/_data/Downloads/VD1_DESKTOP_LIVE.png`

Damals bestätigter SHA256:
`d7ab3dfebb13a46cd24d92cf36b90321badbdb776a8c976e495a2cc47cbfdbca`

## Noch bestehendes Übergabeproblem

Der **Capture selbst funktioniert**. Das damalige Problem war nur die Übergabe des erzeugten Bildes an ChatGPT:
`assets_get_file` / `assets_preview` lieferten im Tool-Harness Base64-Text statt einer für das Modell sichtbaren Bildvorschau.

Also bei künftigem Debugging zuerst unterscheiden:
- **Desktop-Capture kaputt?** -> nein, Selkies-Weg ist bestätigt.
- **Bildübergabe an ChatGPT kaputt?** -> war am 2026-09-19 der eigentliche Fehler.

## Kurzform

**VD1 sehen = KWin showDesktop(True) optional -> ws://127.0.0.1:8882 -> START_VIDEO -> je H.264-Paket 10 Byte Selkies-Header weg -> H.264 sammeln -> ffmpeg -> echter 1808×800-Frame.**
