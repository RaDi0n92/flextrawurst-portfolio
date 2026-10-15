# AI-Strom-Brücke

## Zweck

Die AI-Strom-Brücke verbindet externe AI-Ströme mit dem virtuellen Desktop,
ohne sie zu Bewohnern oder versteckten Dauerprozessen zu machen. Der
Sprachtrigger **„AI-Strom-Brücke“** verweist auf diesen gemeinsamen Vertrag.

## Laufende Schicht

Selkies spiegelt angenommene Eingaben als `ai-strom-bruecke.event.v1` an den
Host-Socket. Der Collector `/root/werkraum/_shared/ai_strom_bruecke/bridge.py`
schreibt diese Ereignisse append-only in `events.jsonl` und hält `state.json`
aktuell. Ein Stream kann den aktuellen Desktop mit `snapshot --output ...` im
Selkies-Shared-Modus sehen.

## Kontrolle

Agentensteuerung läuft ausschließlich über eine explizite Control-Lease. Die
Lease ist ein Prozess-Lock; ohne `--lease` verweigert die CLI jede Aktion.
Der normale Control-Pfad nutzt direkten X11-Input im Container und öffnet
keine zweite Selkies-Primary-Verbindung. Der alte Playwright-Webtop-Pfad ist
nur mit `--webtop` aktivierbar.
Terminalzugriff bleibt eine getrennte Fähigkeit und wird nicht aus einem
Browserereignis abgeleitet.

## Provenienz und Grenze

Das Ereignis enthält Herkunft, Rolle, Display und Rohmessage. `controller`
bedeutet Selkies-Berechtigung, nicht automatisch „Daniel“ oder „AI“. Die
Brücke behauptet daher keine Wahrnehmung jedes Videoframes: Beobachtung ist
abrufbar und Ereignisse sind abonnierbar; ein AI-Runner muss diese Kanäle aktiv
nutzen.

Die bestehende Windows-/GENI-Bridge bleibt separat erhalten.

Für Container-Neuerstellungen liegt der reproduzierbare Eingriff als
`_shared/ai_strom_bruecke/selkies_input_mirror.patch` mit dem zugehörigen
`reapply_selkies_mirror.sh` vor.

Firefox wird über `_shared/ai_strom_bruecke/firefox-x11` mit X11/Xwayland
gestartet. Dadurch bleibt die Eingabe auch nach einem Browser-Neustart
erhalten; `reapply_firefox_x11.sh` stellt den Pfad nach einer
Container-Neuerstellung wieder her.
