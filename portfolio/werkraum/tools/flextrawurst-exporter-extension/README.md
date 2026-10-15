# Flextrawurst Exporter

Eine eigene Chromium-MV3-Erweiterung für lokale Gesprächsexporte aus ChatGPT, Claude, Gemini und Grok.

## Installation

1. `chrome://extensions` öffnen.
2. Entwicklermodus aktivieren.
3. „Entpackte Erweiterung laden“ wählen.
4. Dieses Verzeichnis auswählen: `tools/flextrawurst-exporter-extension/`

## Bedienung

Auf einer unterstützten Gesprächsseite das Erweiterungs-Popup öffnen, „Gespräch lesen“ klicken, Format auswählen und anschließend exportieren. Der Export wird automatisch im normalen Chromium-Downloads-Ordner abgelegt; es öffnet sich kein Speichern-Dialog. Die PDF nutzt eine feste, harmonische Flextrawurst-Palette aus Lila, Flieder, Bubblegum-Pink, Giftgrün und Dunkelgrün gemeinsam in derselben Datei; es gibt keine fünf getrennten Grafikstile.

Die Erweiterung liest ausschließlich den sichtbaren DOM-Inhalt nach einer bewussten Nutzeraktion. Sie navigiert nicht, scrollt nicht automatisch und ruft keine Provider-API auf. Der Download wird über `chrome.downloads` automatisch gestartet und sein Zustand im Background-Service-Worker beobachtet; der tatsächliche Downloadpfad wird ebenfalls zurückgelesen. Der erzeugte Byte-Hash und der Quell-Hash werden in der Downloadspur gespeichert.

Provider-DOMs ändern sich. Wenn ein Gespräch nicht erkannt wird, bleibt der Zustand sichtbar als Fehler; es gibt keinen stillen Fallback auf erfundene Daten.
