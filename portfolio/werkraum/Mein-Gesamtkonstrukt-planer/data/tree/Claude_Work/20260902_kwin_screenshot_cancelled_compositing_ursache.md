# KWin-Screenshot nach Neustart: "Cancelled" statt "NoAuthorized" — Ursache gefunden

Direkte Fortsetzung von `20260902_kwin_restart_screenshot_permission.md`.

## Ausgangslage nach dem Neustart

KWin läuft neu (PID 785 statt 781, seit 16:55). `KWIN_SCREENSHOT_NO_PERMISSION_CHECKS=1`
ist im Environment des neuen Prozesses bestätigt (`/proc/785/environ`). Der Fehler ist
dadurch tatsächlich ein anderer geworden — vorher `NoAuthorized`, jetzt:

```
dbus.exceptions.DBusException: org.kde.KWin.ScreenShot2.Error.Cancelled: Screenshot got cancelled
```

Getestet über `org.kde.KWin.ScreenShot2` (`CaptureWorkspace` und `CaptureScreen("WL-0", …)`)
per eigenem Python-Skript (`dbus-python`, Pipe-FD für die Bilddaten) — beide liefern denselben
Cancelled-Fehler.

## Ursache, per KWin-Quellcode verifiziert (nicht geraten)

`CaptureScreen`/`CaptureWorkspace` können laut KWin-6.6.5-Quelltext
(`src/plugins/screenshot/screenshotdbusinterface2.cpp`) aus genau zwei Gründen scheitern:
`NoAuthorized` (Berechtigung) oder `Cancelled` — Letzteres nicht nur bei abgebrochener
interaktiver Auswahl (`CaptureInteractive`), sondern auch wenn `m_effect->takeScreenShot()`
kein Bild liefert und der Sink daraufhin `cancel()` aufruft. Das Screenshot-Backend ist ein
KWin-**Compositing-Effekt** — ohne laufendes Compositing gibt es keine Szene, aus der der
Effekt ein Bild ziehen kann.

Und genau das ist hier der Fall: `/defaults/startwm_wayland.sh` deaktiviert Compositing
explizit und mit Absicht:
```
kwriteconfig6 --file $HOME/.config/kwinrc --group Compositing --key Enabled false
```
Kommentar im Skript: "Disable compositing and screen locking" — vermutlich Performance-
Entscheidung für den headless/GPU-losen Container. **Provenienz-Fund, nicht mein Vorschlag:**
dieser Wert wurde bewusst so gesetzt, bevor ich ihn anfasse, gehört er nach CLAUDE.md
(Provenienz-Prinzip) erst besprochen.

## Was trotzdem schon jetzt funktioniert, ganz ohne Screenshot

`xdotool` gegen `DISPLAY=:1` (KWins eigenes XWayland) funktioniert bereits:
`getdisplaygeometry` liefert `1632 816`, `xrandr` zeigt den echten Screen `WL-0`,
`xdotool search` findet reale Fenster-IDs. Echte Maus-/Tastatur-Interaktion (kein
Kommando-Ersatz) ist damit technisch schon möglich — nur die visuelle Rückmeldung
per Screenshot fehlt noch auf meiner Seite.

## Wie Selkies (die Technik, die Daniel im Browser sieht) das löst

`svc-selkies` (`/lsiopy/bin/selkies --wayland-socket-index=…`) streamt den Desktop
offenbar über einen tieferliegenden Wayland-Screencopy-Mechanismus, nicht über
`ScreenShot2`. Das würde auch ohne Compositing funktionieren, weil es nicht über den
KWin-Effekt-Stack läuft, sondern direkt am Compositor-Backend ansetzt.

## Zwei Wege, offen für Daniel, nicht selbst entschieden

1. **Compositing testweise/dauerhaft aktivieren** — würde `ScreenShot2` sofort nutzbar
   machen, kostet aber echte Ressourcen (CPU/RAM) in einem Container, in dem es laut
   Skript-Kommentar bewusst abgeschaltet wurde.
2. **Denselben Weg wie Selkies gehen** — ein eigener kleiner Wayland-Screencopy-Client
   (z.B. `wlr-screencopy`-Protokoll), unabhängig von Compositing, aber mehr Bauaufwand
   und ein neuer Codepfad statt der vorhandenen D-Bus-Schnittstelle.

Keine der beiden Optionen wurde umgesetzt. Rein diagnostiziert, dokumentiert, keine
KWin-Konfiguration über den bereits vorher (mit Daniel abgesprochenen) Neustart hinaus
verändert.
