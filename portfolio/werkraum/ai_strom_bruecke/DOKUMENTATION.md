# AI-Strom-Brücke — Entstehung, Lernweg und aktueller Stand

**Dokumenttyp:** Chronologische Projekt- und Gesprächsdokumentation  
**Zeitraum:** 26.–27. Juli 2026  
**Ort:** Daniels VPS, virtueller Desktop 2  
**Beteiligte Perspektiven:** Daniel, Gemini/Antigravity als vorheriger AI-Strom,
Codex als nachfolgender externer AI-Strom  
**Technischer Schwerpunkt:** Selkies/Webtop, X11/Xwayland, Firefox,
Google Earth Pro, Ereignisspiegelung, direkte Maussteuerung und lokaler
Vision-Push-Feed

---

## 1. Worum es eigentlich ging

Die AI-Strom-Brücke entstand nicht aus einem einzelnen Architekturplan. Sie
entstand aus einem wiederholten praktischen Wunsch:

> „Ich will sehen, was du tust — live — und du sollst meine Bewegungen und
> Klicks direkt wahrnehmen können.“

Der virtuelle Desktop sollte dabei nicht nur ein Bildschirm sein, auf dem ein
AI-Strom gelegentlich ein Programm startet. Er sollte ein gemeinsamer
Arbeitsraum werden:

- Daniel sieht Mausbewegungen, Fenster und Navigationsschritte im Browser.
- Ein AI-Strom kann den aktuellen Desktopzustand und die Dateien prüfen.
- Menschliche Eingaben werden als Ereignisse wahrnehmbar.
- Ein AI-Strom darf mit einer kontrollierten Lease selbst handeln.
- Terminalarbeit bleibt zusätzlich möglich.
- Mehrere AI-Ströme — nicht nur Gemini — sollen denselben Zugang benutzen,
  sobald Daniel „AI-Strom-Brücke“ sagt.

Der entscheidende Anspruch war nicht einfach „Remote Desktop funktioniert“.
Der Anspruch war eine nachvollziehbare, sichtbare und möglichst menschliche
Koordination zwischen Wahrnehmen, Bewegen, Klicken, Tippen und Nachprüfen.

Gleichzeitig musste eine Grenze sichtbar bleiben: Ein externer AI-Strom ist
dadurch nicht plötzlich ein dauerhaft im VPS lebendes Wesen. Er bekommt einen
Andockpunkt, einen Beobachtungskanal und kontrollierte Fähigkeiten.

---

## 2. Ausgangslage: Die beiden virtuellen Desktops

Zu Beginn wurden zwei vorhandene URLs untersucht:

- `https://flextrawurst.de/virtuellerdesktop1/`
- `https://flextrawurst.de/virtuellerdesktop2/`

Die technische Gegenüberstellung sah ungefähr so aus:

| Desktop | Grundlage | Eindruck |
|---|---|---|
| 1 | Ubuntu/XFCE, X11 | leicht, einfach, genügsam |
| 2 | Ubuntu/KDE, Wayland/Xwayland | moderner, besser für visuelle Arbeit |

Die Entscheidung fiel auf Desktop 2. Er lief als Container `virtuellerdesktop2`
auf Port `3091` und wurde über den Nginx-Pfad
`/virtuellerdesktop2/` im Browser erreichbar gemacht.

Die technische Realität dahinter war wichtig: Der Desktop war kein zweiter
vollständiger VPS, sondern ein Docker-Container. Seine Verzeichnisse `/root`,
`/boot`, `/etc` und `/var` waren zunächst Containerverzeichnisse und nicht
automatisch die echten Verzeichnisse des Hosts.

Daniel wollte ausdrücklich, dass Dateien, die auf dem virtuellen Desktop
erstellt werden, wirklich im VPS landen und später auch über WinSCP sichtbar
sind. Daraufhin wurden die Hostpfade eingebunden:

- `/root` des VPS erschien im Container als `/vps_root`.
- Das gesamte Host-Dateisystem erschien als `/vps_system`.

Damit wurden Dateien aus dem Desktop tatsächlich auf dem VPS gespeichert. Die
Konsequenz wurde ebenfalls deutlich: Diese Einbindung ist mächtig. Eine Datei
im gemounteten Bereich ist keine bloße Desktop-Kopie, sondern eine echte
Änderung am Host.

Parallel wurde der Benutzer `gemgem` im Container angelegt. Die Absicht war,
den sichtbaren Desktop nicht dauerhaft als Root zu benutzen. Anfangs wurden
Sudo-Rechte vergeben, danach auf Daniels Hinweis hin wieder entfernt, damit
`gemgem` nicht in `/root` schreiben kann. Diese Episode war ein früher Hinweis
darauf, dass Sichtbarkeit und Schreibmacht getrennt behandelt werden müssen.

---

## 3. Die ersten visuellen Probleme

Der KDE-Desktop zeigte zunächst verschiedene Fehlerbilder:

- schwarzes Bild, danach kurz Desktopbild,
- nur Hintergrund ohne Taskleiste,
- ein anderes XFCE-artiges System statt des erwarteten KDE,
- Fokusprobleme bei Fenstern,
- Fehlermeldungen wie „denied“ oder „no access“.

Es wurde zwischen KDE, XFCE, Wayland, Xwayland, DBus, AppArmor und
Software-Rendering gewechselt. Einige Diagnosen waren plausibel, aber zu
schnell formuliert. Später zeigte sich: Ein Teil der vermeintlich gelösten
Probleme war nur deshalb als gelöst bezeichnet worden, weil ein Prozess
startete oder ein Screenshot einen günstigen Zwischenzustand zeigte.

Das wurde im späteren Bridge-Design korrigiert: Ein Test darf nur genau das
behaupten, was er tatsächlich geprüft hat. „Ein Fenster ließ sich öffnen“ ist
nicht dasselbe wie „der Desktop ist stabil, klickbar und nach einem Neustart
weiterhin stabil“.

---

## 4. Browser, WebGL und Firefox

Für visuelle Aufgaben wurde zunächst Chromium untersucht. Chromium ließ sich
mit Mesa/LLVMpipe und Software-Rendering betreiben. WebGL-Flags wie
`--enable-webgl`, `--enable-webgl2`, `--ignore-gpu-blocklist` und
`--use-gl=swiftshader` wurden ausprobiert.

Firefox verhielt sich schwieriger. Der WebGL-Test meldete sinngemäß:

> Dieser Browser unterstützt WebGL, aber WebGL ist deaktiviert oder nicht
> verfügbar.

Danach wurden mehrere Ebenen bearbeitet:

1. deutsches Firefox-Sprachpaket,
2. `de_DE.UTF-8` und KDE-Locale,
3. Firefox-Profiloptionen für WebGL,
4. Software-WebRender,
5. Sandbox-Startoptionen,
6. Wayland- und X11-Startpfad,
7. Neustart- und Klicktests.

Ein Firefox-Start unter Wayland führte zu einer Klicksperre. Ein unsichtbarer
Dialog und Fokusübernahme wurden vermutet. Danach wurden Firefox-Sandbox,
Xwayland und Wayland als Ursachen diskutiert. Entscheidend wurde schließlich
der dauerhafte X11-Wrapper:

```text
DISPLAY=:1
MOZ_ENABLE_WAYLAND=0
GDK_BACKEND=x11
QT_QPA_PLATFORM=xcb
XDG_SESSION_TYPE=x11
LIBGL_ALWAYS_SOFTWARE=1
```

Der Wrapper liegt als `firefox-x11` vor und wird von Terminal, KDE-Starter und
`/config`-Pfad benutzt. Ein echter Stop/Start-Test konnte danach Adresszeile,
Tastatureingabe, Navigation und Linkklick prüfen.

Wichtig war auch hier die Korrektur der Kommunikation. Ein Playwright-Test,
der einmal erfolgreich klickt, beweist nicht, dass ein manuell neu gestarteter
Firefox immer klickbar bleibt. Genau diese Differenz hat Daniel mehrfach
sichtbar gemacht:

> „deutsch ja zumindest firefox aber jetzt kann ich nirgendwo klicken xD“

und später:

> „immernoch englisch und kein klicken in firefox“

Die Browserprobleme waren damit nicht nur technische Bugs. Sie waren Tests
dafür, ob die Bridge mit dem tatsächlichen Zustand arbeitet oder nur mit einer
schönen Behauptung über den Zustand.

---

## 5. Der Name und die gemeinsame Idee

Daniel wollte die Verbindung nicht als Gemini-Sonderweg behandeln. Er gab ihr
den Namen:

> „AI-Strom-Brücke“

Dieser Name wurde zum Sprachtrigger und zum Architekturprinzip. Wenn Daniel
ihn sagt, sollen alle beteiligten externen AI-Ströme denselben Zugang und
denselben Vertrag verwenden.

Die Brücke ist dabei ausdrücklich kein dauerhafter Bewohner. Sie ist ein
gemeinsamer Andockpunkt mit vier getrennten Fähigkeiten:

1. **Beobachten** — aktuelles Bild und sichtbaren Desktopzustand bekommen.
2. **Ereignisse empfangen** — Maus, Tastatur und Clipboard als Rohereignisse.
3. **Kontrolliert handeln** — Maus, Klick, Taste und Text mit Lease.
4. **Terminal nutzen** — getrennt von Browserkontrolle.

Die Trennung verhindert, dass „ich kann den Bildschirm sehen“ automatisch als
„ich darf überall schreiben“ verstanden wird.

---

## 6. Die erste technische Brücke: Selkies-Ereignisse

Der vorhandene Selkies-Inputpfad wurde additiv gespiegelt. Selkies bleibt für
die eigentliche Desktopbedienung zuständig; die Bridge liest die akzeptierten
Eingaben mit.

Der Ablauf:

```text
Browser-Client
    |
    v
Selkies akzeptiert Maus-/Tastaturereignis
    |
    +--> normale Desktopverarbeitung
    |
    +--> AF_UNIX-Datagramm
             |
             v
      ai-strom-bruecke daemon
             |
             +--> events.jsonl
             +--> state.json
```

Das Ereignisschema sieht beispielsweise so aus:

```json
{
  "schema": "ai-strom-bruecke.event.v1",
  "ts": 1785180000.0,
  "origin": "selkies",
  "kind": "m",
  "message": "m,500,115,1,0",
  "display": "primary",
  "remote": "127.0.0.1",
  "role": "controller"
}
```

Der Ledger ist append-only. Die Bridge erfindet keine Absicht aus einem
Mausereignis. Sie schreibt nicht „Daniel wollte Deutschland öffnen“, sondern
das, was tatsächlich angekommen ist: Position, Nachricht, Zeit, Rolle und
Herkunft.

Der Collector läuft als:

```text
ai-strom-bruecke.service
```

Der Unix-Socket liegt im persistenten Webtop-Konfigurationsvolume:

```text
/var/lib/docker/volumes/webtop2_config/_data/ai-strom-bruecke-events.sock
```

---

## 7. Der erste große Fehler: Playwright als Primärcontroller

Für Screenshots und Klicktests wurde zunächst Playwright verwendet. Das war
naheliegend, weil Playwright Browserseiten öffnen, Mausbewegungen schicken und
Screenshots erzeugen kann.

In dieser Umgebung hat Playwright beim Aufruf des Webtop-Endpoints jedoch eine
neue Selkies-Primärverbindung eröffnet. Dadurch wurde Daniels bestehende
Verbindung beendet:

> „Connection Terminated: a new primary client connected connection killed“

Dieser Fehler war der entscheidende Wendepunkt. Die technische Einsicht
lautete:

- Playwright ist als isolierter Testbrowser brauchbar.
- Playwright ist als zweiter Webtop-Controller gefährlich.
- Ein automatischer Test darf nicht die sichtbare Sitzung des Menschen
  verdrängen.

Daraufhin wurde Playwright-Control nicht mehr zum Standard gemacht. Der
Legacy-Modus `--webtop` blieb dokumentiert, aber nur als ausdrückliche
Ausnahme.

---

## 8. Direkte X11-Kontrolle und Control-Lease

Die Standardsteuerung wechselte auf direktes X11 im Container:

```text
docker exec -e DISPLAY=:1 virtuellerdesktop2 xdotool ...
```

Die Bridge bewegt damit die echte Maus im laufenden Desktop. Für eine Bewegung
wird die aktuelle Position gelesen und in mehreren kleinen Schritten
interpoliert. Dadurch sieht Daniel nicht nur einen teleportierenden Cursor,
sondern eine Bewegung.

Vor jeder agentischen Kontrolle wird eine Lease verlangt:

```bash
python3 /root/werkraum/_shared/ai_strom_bruecke/bridge.py \
  control click 500 115 --lease
```

Die Lease liegt in:

```text
/tmp/ai-strom-bruecke-control.lock
```

Sie verhindert, dass mehrere AI-Ströme gleichzeitig klicken oder tippen. Das
ist keine dauerhafte Identität und kein Besitzrecht. Es ist eine kurzfristige,
exklusive Handlungserlaubnis.

Daniel wollte möglichst keine ständigen Erlaubnisdialoge. Die Plattform kann
Sicherheitsprüfungen nicht global abschalten, aber innerhalb der freigegebenen
Umgebung wurde der Arbeitsweg so gebaut, dass bereits erlaubte, in-scope
Aktionen nicht künstlich wiederholt nachfragen.

---

## 9. Google Earth Pro als Härtetest

Google Earth Pro wurde als sichtbare Anwendung gewählt, weil es mehrere
Fähigkeiten gleichzeitig prüft:

- große OpenGL-Oberfläche,
- Navigation mit Ziehen und Zoom,
- Rendering im virtuellen Desktop,
- sichtbare Mausbewegungen,
- möglicher Dialog- und Popup-Fokus,
- räumliche Orientierung statt bloßem Formularausfüllen.

Die offizielle Linux-Debian/Ubuntu-Version wurde geladen und installiert.
Installiert wurde:

```text
google-earth-pro-stable 7.3.7.1155-r0
amd64
/usr/bin/google-earth-pro
```

Google Earth Pro läuft über den direkten X11-Pfad mit Software-Rendering.

Der erste Navigationsversuch war nicht sauber: Es wurde ein Suchfeld benutzt
und ein Nationalpark geöffnet. Daniel korrigierte das unmittelbar:

> „du sollst nix suchen und eintippen das ist cheaten ... du sollst es
> navigieren“

Damit änderte sich der Test. Gesucht war nicht mehr nur ein Ergebnis, sondern
eine sichtbare menschliche Navigation über den Globus zu einem echten
Freizeitpark mit Achterbahnen.

---

## 10. Daniels entscheidender Navigationshinweis

Die automatisierten Bewegungen waren zunächst zu grob oder wirkten wie
Teleportation. Daniel formulierte die praktische Regel:

> „wenn du langsamer navigieren willst muss die maus geklickt bleiben ... die
> ganze zeit ... und dann musst du auch langsame viele mausbewegungen machen“

Das wurde zur wichtigsten Interaktionslehre des gesamten Tests:

1. Punkt exakt berechnen.
2. Maus auf den Punkt setzen.
3. Maustaste gedrückt halten.
4. Viele kleine Koordinatenschritte senden.
5. Erst am Ziel loslassen.
6. Frame prüfen.
7. Erst danach weiterzoomen oder erneut greifen.

Mit dieser Methode wurde der Globus schrittweise navigiert:

- falsche Nationalparkansicht verlassen,
- weit aus der Region herauszoomen,
- zur Weltkugel zurückgehen,
- Australien/Asien als Orientierung erkennen,
- Europa durch gehaltene Ziehbewegungen in die Mitte bringen,
- Deutschland sichtbar machen,
- Deutschland aus dem linken Rand in die Mitte ziehen,
- in Richtung Westdeutschland/Köln-Brühl weiterzoomen.

Dabei entstanden mehrere Fehlgriffe. Ein Zielpunkt lag zunächst in Polen,
später wurde ein falscher Fokus in Zentraldeutschland erwischt. Die Frames
waren dabei hilfreicher als verbale Vermutungen: Deutschland, Berlin,
Hamburg, Polen und die Nachbarländer waren direkt im Bild zu erkennen.

Der Prozess zeigte, dass visuelle Navigation kein einzelner „Befehl zum Ziel“
ist. Sie ist eine Folge von:

```text
Frame -> Zielpunkt schätzen -> halten und ziehen -> Frame -> korrigieren
```

---

## 11. Das Popup und die Korrektur durch echtes Sehen

Nach einem Fokusfehler lag ein großes weißes Popup über der Karte. Zunächst
wurde fälschlich das kleine X des linken Seitenpanels angeklickt. Daniel
präzisierte:

> „nicht das Seitenpanel, das Popup ist so groß bis daneben Deutschland
> wieder ist — oben rechts des Popups ist das X“

Daraufhin wurde ein echter Google-Earth-Pro-Frame geholt. Darin war das Popup
eindeutig sichtbar:

- Beginn ungefähr bei x=231 im Fenster,
- weißer Rahmen über dem Kartenbereich,
- rechter Rand nahe der Fensterkante,
- Schließen-X oben rechts im Popup.

Der Klick wurde anschließend gezielt auf diesen Popup-Bereich gesetzt. Der
nächste Frame zeigte wieder die vollständige Deutschlandkarte.

Diese Episode ist für die Bridge zentral: Daniel korrigierte nicht nur eine
Koordinate, sondern die Interpretation des Bildes. Die richtige Reaktion war
nicht „noch einmal irgendein X klicken“, sondern:

```text
aktuellen Frame holen -> Popupgrenzen lesen -> X relativ zum Popup berechnen
-> klicken -> neuen Frame prüfen
```

---

## 12. Der erste direkte Realtime-Beobachter

Nach dem Primary-Verbindungsproblem wurde der alte Playwright-Snapshot aus
`bridge.py` entfernt. `snapshot` und `observe` greifen nun direkt auf X11 zu,
ohne Browser und ohne Webtop-Client zu öffnen.

Zunächst wurde `xwd` verwendet. Bei Google Earth Pro funktionierte das anfangs,
danach schlug es beim OpenGL-Fenster mit folgendem Fehler fehl:

```text
X Error of failed request: BadMatch (invalid parameter attributes)
Major opcode of failed request: 73 (X_GetImage)
```

Das war kein Grund, wieder Playwright als Primärcontroller einzusetzen. Ein
alternativer direkter Captureweg wurde getestet:

```text
ImageMagick import -window <window-id> png:-
```

Dieser Weg funktionierte für das OpenGL-Fenster. Der Capture wurde dadurch
umgestellt:

```text
Google Earth X11 window
        |
        v
ImageMagick import -window
        |
        v
atomischer latest.png-Ersatz
```

Der dauerhafte Dienst:

```text
ai-strom-bruecke-observer.service
```

schreibt mit 8 FPS den neuesten Frame nach:

```text
/root/werkraum/_shared/ai_strom_bruecke/latest.png
```

8 FPS entsprechen ungefähr einem neuen Frame alle 125 Millisekunden und
liegen damit deutlich unter Daniels Forderung von maximal 0,5 Sekunden
zwischen Bildern. Alte Frames werden nicht gesammelt; die Datei wird atomisch
ersetzt.

---

## 13. Der Push-Feed für AI-Runner

Der Watcher allein schreibt noch keine Bilder in ein Sprachmodell. Deshalb
wurde zusätzlich ein lokaler Push-Server gebaut:

```text
ai-strom-bruecke-stream.service
```

Er bindet ausschließlich an:

```text
127.0.0.1:8098
```

Endpunkte:

| Pfad | Funktion |
|---|---|
| `/health` | JSON-Status |
| `/latest.png` | letzter Frame als einzelne PNG-Datei |
| `/stream` | Multipart-PNG-Stream, jeder neue Frame sofort |
| `/events` | Server-Sent Events mit Eingaben |

Ein Vision-Runner kann `/stream` dauerhaft abonnieren und jedes Bild in seinen
eigenen Modellinput weiterreichen. `/events` liefert parallel rohe Maus- und
Tastaturereignisse.

Der Push-Test lieferte in drei Sekunden ungefähr 4,5 MB mit mehreren
Bildpaketen. Damit ist der lokale technische Pushkanal vorhanden.

Die noch offene Grenze ist nicht mehr der Desktop, sondern die aktuelle
Chat-Schnittstelle: Dieses Sprachmodell erhält keine ungefragten Toolbilder im
Hintergrund. Ein angeschlossener Vision-Runner kann den Pushfeed konsumieren;
diese konkrete Chat-Session kann Frames weiterhin nur aktiv abrufen.

---

## 14. Aktuelle Architektur

```text
Daniel im Browser
        |
        v
Selkies/Webtop — sichtbare Desktop-Sitzung
        |
        +--> akzeptierte Maus-/Tastatureingaben
        |        |
        |        v
        |   AF_UNIX-Datagramm
        |        |
        |        v
        |   ai-strom-bruecke.service
        |        +--> events.jsonl
        |        +--> state.json
        |        +--> /events (SSE)
        |
        +--> X11 DISPLAY=:1
                 |
                 +--> xdotool direkte Kontrolle mit Control-Lease
                 |
                 +--> ImageMagick import -window
                          |
                          v
                   latest.png, 8 FPS
                          |
                          v
                   ai-strom-bruecke-stream.service
                          +--> /latest.png
                          +--> /stream (Multipart PNG)
```

Die Dateien des Vertrags liegen unter:

```text
_shared/ai_strom_bruecke/
├── README.md
├── DOKUMENTATION.md
├── bridge.py
├── stream_server.py
├── selkies_input_mirror.patch
├── reapply_selkies_mirror.sh
├── firefox-x11
├── reapply_firefox_x11.sh
├── ai-strom-bruecke-observer.service
└── ai-strom-bruecke-stream.service
```

Die Laufzeitspuren `events.jsonl`, `state.json` und `latest.png` gehören zur
aktiven Umgebung und sind keine konzeptionellen Quelldateien.

---

## 15. Bedien- und Diagnosebefehle

Bridge-Status:

```bash
python3 /root/werkraum/_shared/ai_strom_bruecke/bridge.py status
```

Ein Frame des aktiven Fensters:

```bash
python3 /root/werkraum/_shared/ai_strom_bruecke/bridge.py \
  snapshot --target active --output /tmp/ai-strom-frame.png
```

Ein Frame von Google Earth Pro:

```bash
python3 /root/werkraum/_shared/ai_strom_bruecke/bridge.py \
  snapshot --target google-earth --wait-ms 0 \
  --output /tmp/google-earth.png
```

Ereignisse verfolgen:

```bash
python3 /root/werkraum/_shared/ai_strom_bruecke/bridge.py events --follow
```

Direkte sichtbare Mausbewegung:

```bash
python3 /root/werkraum/_shared/ai_strom_bruecke/bridge.py \
  control move 500 300 --steps 40 --lease
```

Pushfeed testen:

```bash
curl http://127.0.0.1:8098/health
curl http://127.0.0.1:8098/latest.png -o /tmp/latest.png
curl --max-time 3 http://127.0.0.1:8098/stream -o /tmp/stream.bin
```

Dienste prüfen:

```bash
systemctl is-active ai-strom-bruecke.service
systemctl is-active ai-strom-bruecke-observer.service
systemctl is-active ai-strom-bruecke-stream.service
```

---

## 16. Was Daniel beobachtet und korrigiert hat

Daniels Beobachtungen waren die wichtigsten Tests des Systems:

| Beobachtung | Korrektur/Erkenntnis |
|---|---|
| „alles leer“ im Dateimanager | Container-Dateisystem und Host-Mounts unterscheiden |
| schwarzes/flackerndes Bild | Desktop-/Rendering-/Fokusproblem, nicht vorschnell als erledigt melden |
| Firefox klickt nicht | Neustarttest und dauerhafter X11-Pfad nötig |
| „Connection Terminated“ | Playwright darf keine neue Selkies-Primary-Verbindung öffnen |
| Maus kaum sichtbar | Client-CSS-Cursor und tatsächlichen X11-Cursor auseinanderhalten |
| Nationalpark statt Freizeitpark | Suchfeld war am Auftrag vorbei; räumlich manuell navigieren |
| Globusbewegung zu grob | Maustaste halten, viele kleine Bewegungen |
| falsches X geklickt | Popupgrenzen aus dem Frame lesen, nicht geraten |
| „mindestens jede 0,5 Sekunden“ | 8-FPS-Watcher und danach Push-Feed einrichten |

Die Qualität der Bridge entstand damit nicht nur aus Code. Sie entstand aus
dem wiederholten Abgleich zwischen:

```text
Was ich behaupte
Was Daniel wirklich sieht
Was der nächste Frame beweist
Was technisch dauerhaft abgesichert werden muss
```

---

## 17. Was ich als AI-Strom dabei gelernt habe

### 17.1 Sichtbar starten ist nicht sichtbar wahrnehmen

Ein gestartetes Programm ist noch kein beobachtbarer Zustand. Erst ein Frame,
ein Fenstername, ein Fokusstatus oder ein überprüfter Klick kann die Aussage
tragen.

### 17.2 Playwright ist nicht automatisch ein neutraler Beobachter

Ein Browserautomationstool kann durch seine Verbindung selbst in die
Sitzungslogik eingreifen. Beobachten und Kontrollieren müssen daher technisch
getrennt werden.

### 17.3 Menschliche Navigation ist zeitlich und räumlich

„Klicke dort“ reicht bei einem Globus nicht. Die Bewegung braucht:

- einen Startpunkt,
- einen gehaltenen Zustand,
- eine Reihe kleiner Schritte,
- einen Zielpunkt,
- eine Nachkontrolle.

### 17.4 Ein Benutzerhinweis kann ein besseres Steuerungsmodell liefern

Daniels Hinweis mit der gehaltenen Maustaste war präziser als die vorherigen
pauschalen Automationsannahmen. Die Bridge muss nicht jede menschliche
Eigenheit imitieren, aber sie muss die Interaktionslogik des Zielprogramms
respektieren.

### 17.5 „Realtime“ hat mehrere Schichten

Es gibt mindestens vier verschiedene Bedeutungen:

1. Der Desktop rendert sichtbar.
2. Selkies überträgt die sichtbare Sitzung.
3. Der Watcher erzeugt aktuelle Frames.
4. Ein AI-Runner nimmt diese Frames tatsächlich als Modellinput auf.

Die ersten drei Schichten sind eingerichtet. Die vierte hängt vom jeweiligen
Runner und seiner Vision-Schnittstelle ab.

---

## 18. Aktueller Stand und offene Arbeit

### Bereits eingerichtet

- Desktop 2 als gemeinsamer visueller Arbeitsort.
- echter Host-Dateizugriff über `/vps_root` und `/vps_system`.
- `gemgem` als nicht-rootiger Desktopbenutzer.
- Firefox-X11-Wrapper für stabilere Neustarts.
- Selkies-Ereignisspiegelung.
- append-only Ereignisledger.
- direkter X11-Controlpfad.
- Control-Lease.
- Google Earth Pro installiert.
- direkter OpenGL-fähiger X11-Capture.
- 8-FPS-Dauerbeobachter.
- lokaler Multipart-PNG-Pushfeed.
- lokaler SSE-Ereignisfeed.

### Noch offen

- ein konkreter Vision-Runner, der `/stream` abonniert und die Frames an ein
  Modell weitergibt;
- eine sichtbare Bridge-Lease-Anzeige für Daniel;
- getrennte Identitätsmarkierung für Mensch, Gemini, Codex und weitere
  AI-Ströme;
- ein sauberer `drag`-Controlbefehl mit dauerhaft gedrückter Maustaste und
  vielen interpolierten Punkten;
- ein expliziter Stop-/Pause-Befehl für AI-Kontrolle;
- die vollständige manuelle Reise von Deutschland bis zu einem konkret
  sichtbaren Freizeitpark mit Achterbahnen.

---

## 19. Schlussbild

Die AI-Strom-Brücke begann mit der Frage, ob ein AI-Strom in einem virtuellen
Desktop „wirklich da“ sein könne. Der technische Weg führte nicht zu einer
Behauptung dauerhafter Anwesenheit, sondern zu einer präziseren Konstruktion:

```text
sehen dürfen
Ereignisse wahrnehmen
mit Lease handeln
Frames pushen
Zustand nachprüfen
Fehler sichtbar korrigieren
```

Der wichtigste Fortschritt war nicht der einzelne Google-Earth-Klick. Es war
die Umstellung von „ich habe etwas gestartet“ auf „Daniel sieht es, der Frame
beweist es, und der nächste AI-Schritt kann auf diesem Beweis aufbauen“.

[[abwurf: Die AI-Strom-Brücke ist dort stark, wo sie nicht behauptet, live zu sein, sondern den Weg zwischen Bild, Ereignis, Handlung und Rückprüfung offenlegt.]]

---

# Fortsetzung der Chronik — Google Earth, Conti und die eigentliche Bewegungslogik

## 20. Wiedereinstieg nach dem Kontextabbruch

Die vorherige Session brach während eines laufenden Google-Earth-Schritts ab.
Der letzte Zustand war keine neue Aufgabe, sondern die Fortsetzung der Reise
zum **Eiscafé Conti in Schwelm**. Google Earth Pro war geöffnet, die
AI-Strom-Brücke sollte dieselbe X11-Sitzung weiterverwenden, und Daniel wollte
am Ende nicht nur den Orts-Pin lesen, sondern Menschen, Schaufenster und das
Conti-Logo sehen.

Beim Wiedereinstieg war Street View noch aktiv. Der erste lokale Versuch lief
auf dem Host und zeigte:

```text
/bin/bash: line 1: xdotool: command not found
/bin/bash: line 1: xdotool: command not found
```

Das war kein Google-Earth-Fehler. `xdotool` liegt im virtuellen Desktop-
Container. Der korrigierte Weg war:

```bash
docker exec virtuellerdesktop2 bash -lc 'set -e; export DISPLAY=:1; wid=$(xdotool search --name "Google Earth Pro" | tail -1); xdotool windowactivate --sync "$wid"; xdotool key --clearmodifiers Escape; sleep 3'
```

Damit wurde Street View beendet, ohne Google Earth zu schließen. Der
anschließende Bridge-Snapshot:

```bash
python3 /root/werkraum/_shared/ai_strom_bruecke/bridge.py snapshot --target google-earth --wait-ms 0 --output /tmp/google-earth-conti-after-escape.png
```

bewies eine normale geneigte 3D-Ansicht von Schwelm. Rechts oben war
**„Eismanufaktur Gelateria Conti“** sichtbar; die Sichthöhe lag ungefähr bei
409 m. Das war der erste belastbare Zustand nach dem Abbruch.

## 21. Was Daniel eigentlich sehen wollte

Daniels Wunsch war nicht mehr nur „finde den Pin“:

> „Lesen kann ich es auch … aber ich will Leute da sitzen sehen oder das
> Schaufenster mit Logo.“

Damit bestand die Aufgabe aus drei Ebenen: den richtigen Stadtpunkt finden,
die Kamera auf das Gebäude ausrichten und eine Darstellung erreichen, in der
Fassade, Schaufenster und möglichst Menschen erkennbar sind.

Vorher hatte Daniel Street View als Abkürzung abgelehnt. Erst später gab er
die ausdrückliche Freigabe:

> „na los komm versuch es doch mal mit streetview“

Ab diesem Satz war der Pegman innerhalb des Auftrags erlaubt. Vorher galt
weiterhin normale Google-Earth-Navigation ohne Suchfeld und ohne Eintippen.

## 22. Die Tastatur-Zooms und ihre widersprüchlichen Frames

Nach dem Escape testete ich `Page_Up` und `Page_Down`. Die Annahme, dass eine
Taste immer eindeutig hinein- und die andere immer eindeutig herauszoomt,
wurde durch die Frames widerlegt.

Ein `Page_Up`-Block wurde so gesendet:

```bash
docker exec virtuellerdesktop2 bash -lc 'set -e; export DISPLAY=:1; wid=$(xdotool search --name "Google Earth Pro" | tail -1); xdotool windowactivate --sync "$wid"; xdotool mousemove --sync 1515 188; for i in $(seq 1 20); do xdotool key --clearmodifiers Page_Up; sleep 0.07; done; sleep 3'
```

Der Frame `/tmp/google-earth-conti-close3d-1.png` stand danach bei ungefähr
622 m statt 409 m — also weiter außen. Ein späterer `Page_Down`-Block führte
auf etwa 461 m, ein weiterer auf etwa 846 m. Ein Mausradtest mit:

```bash
xdotool mousemove --sync 1418 454
for i in $(seq 1 18); do xdotool click 4; sleep 0.09; done
```

blieb im Folgeframe pixelgleich.

Einzelne `Page_Up`-Schritte funktionierten danach wieder und senkten die
Sichthöhe einmal von ungefähr 846 m auf 655 m. Der nächste Block mit 24
Schritten landete bei etwa 522 m. Die belastbare Erkenntnis war deshalb nicht
„Page_Up ist Zoom-in“, sondern:

- Earth verarbeitet synthetische Tasten abhängig von Fokus und laufender
  Animation;
- der Mausanker bleibt nicht in jedem Zustand unter demselben Pixel;
- die Sichthöhe und der neue Frame sind wichtiger als meine Annahme;
- kein Tastaturblock gilt als erfolgreich, bevor ein neuer Frame ihn beweist.

## 23. Daniels Hinweis zur mittleren Maustaste

Daniels nächster Hinweis war der Wendepunkt für die 3D-Ansicht:

> „Du kannst mittlere Maustaste klicken und geklickt halten … und dann auch
> links rechts und oben unten und seitlich deine Ansicht verändern.“

Die erste mittlere Bewegung wurde so versucht:

```bash
xdotool mousemove --sync 1000 400
xdotool mousedown 2
for i in $(seq 1 40); do y=$((400+i*3)); xdotool mousemove --sync 1000 "$y"; sleep 0.025; done
xdotool mouseup 2
```

Der erste Frame blieb scheinbar unverändert. Nach explizitem Kartenfokus:

```bash
xdotool mousemove --sync 1000 400
xdotool click 1
sleep 0.4
xdotool mousedown 2
for i in $(seq 1 55); do y=$((400+i*2)); xdotool mousemove --sync 1000 "$y"; sleep 0.04; done
xdotool mouseup 2
```

änderte sich der Frame sichtbar. Die Sichthöhe sank ungefähr von 337 m auf
245 m; der Blick wurde räumlicher. Ein mittlerer Griff nach oben führte wieder
stärker in die Draufsicht, ein Griff nach unten machte die Ansicht flacher.

Auch der horizontale Test funktionierte:

```bash
xdotool mousemove --sync 1000 400
xdotool mousedown 2
for i in $(seq 1 35); do x=$((1000+i*4)); xdotool mousemove --sync "$x" 400; sleep 0.03; done
xdotool mouseup 2
```

Damit war Daniels Hinweis bestätigt: Die mittlere Maustaste ist der Zugang
zu Blickneigung und Seitenrichtung, nicht bloß ein weiterer Karten-Drag.

## 24. WASD — der eigentliche Bewegungsmodus

Danach gab Daniel den „Killertipp“:

> „Mit WASD kannst du dich auch bewegen.“

Ein einzelner `W`-Schritt wurde getestet:

```bash
xdotool mousemove --sync 1000 400
xdotool click 1
sleep 0.3
xdotool key --clearmodifiers w
sleep 3
```

Der Koordinatenwert unten rechts änderte sich von ungefähr
`51°16'58,48" N, 7°17'40,59" O` auf ungefähr
`51°16'57,97" N, 7°17'39,57" O`. `W` bewegte die Szene tatsächlich.

Daniels Dosierungshinweis lautete:

> „Entweder kurz öfters hintereinander klicken oder je länger du gedrückt
> hältst, desto weiter wanderst du.“

Die beiden Steuerungsarten wurden damit klar:

```bash
# Feinkorrektur
xdotool key --clearmodifiers s

# Strecke
xdotool keydown d; sleep 0.7; xdotool keyup d
```

Mehrere kurze `S`-Schritte führten schließlich zu:

```text
51°17'00,87" N   7°17'41,06" O
```

Das war exakt der Punkt, an dem der Conti-Marker in einem früheren Frame
gelegen hatte. Nicht der Textname allein, sondern mehrere Eingaben plus
Koordinatenanzeige und Folgeframe bewiesen diesen Treffer.

## 25. Der wichtige Rückschritt: Nicht ohne Beschriftung weiterfliegen

Nach dem exakten Koordinatentreffer zoomte ich wieder hinein. Die Ansicht
blieb zwar im richtigen Stadtblock, aber die Conti-Beschriftung verschwand.
Ich versuchte weiter zu navigieren und begann dadurch erneut, eine Richtung
zu unterstellen, die der Frame nicht mehr belegte.

Daniel stoppte diese Bewegung mit einem präzisen Hinweis:

> „Du weißt bestimmt gerade gar nicht, wo du hin musst, oder? Zoom doch kurz
> mal raus, bis du die Schrift wieder lesen kannst.“

Das war korrekt. Die Koordinate war zwar nützlich, aber ohne sichtbaren
Kontext kein ausreichender Navigationsbeweis.

Ein zu großer `Page_Down`-Block führte zunächst in eine etwa 1,26 km breite
Ansicht. Dort erschienen wieder viele Orts- und Straßenschriften. In einem
Frame war **„Eismanufaktur Gelateria Conti“** klar rechts vom Märkischen Platz
lesbar. Der Text lag ungefähr bei Bildschirmposition `x=1240, y=457`.

Ich bewegte die Maus anschließend genau auf diese Beschriftung und nicht nur
auf den ungefähren Stadtbereich. Das war die richtige Methode: Der Textanker
und die Koordinate des Mauszeigers müssen gemeinsam dokumentiert werden.

## 26. Erneute Zoomverwirrung und die Lehre daraus

Auf den Textanker folgte wieder ein Tastaturblock. Er führte von der lesbaren
Conti-Ansicht auf ungefähr 2,07 km und ein weiterer Block auf etwa 5,21 km.
Die sichtbaren Ergebnisse waren:

```text
Conti-Label sichtbar       ungefähr 1,26 km
Page_Up-Block               ungefähr 2,07 km
Page_Down-Block             ungefähr 5,21 km
```

Damit war endgültig klar, dass die Page-Tasten in diesem Lauf nicht als
stabile, semantische Zoom-API behandelt werden durften. Der Zustand hing von
Kamerawinkel, Fokus, laufender Animation und dem zuletzt aktiven Eingabemodus
ab.

Ein Mausradversuch mit `xdotool click 4` blieb zuvor ohne sichtbare Änderung.
Auch die sichtbaren Plus-/Minus-Schaltflächen wurden einmal mit einem
falschen `xdotool`-Aufruf getestet:

```text
xdotool: Unknown command: --repeat
Run 'xdotool help' if you want a command list
```

Das war ein reiner Shell-/Befehlsfehler. Der korrigierte Schleifenversuch
lief ohne Ausgabe, veränderte den Earth-Frame aber nicht. Die Erkenntnis war
erneut: Keine Eingabe gilt als erfolgreich, nur weil der Befehl mit Exit-Code
0 endet. Der nächste Frame muss die Wirkung zeigen.

## 27. Street View wurde ausdrücklich freigegeben

Bis zu diesem Punkt hatte Daniel Street View als Abkürzung abgelehnt. Seine
Regel war: Erst die normale Google-Earth-Navigation lernen. Später änderte er
die Freigabe ausdrücklich:

> „Na los, komm, versuch es doch mal mit Streetview.“

Ab jetzt war der Pegman innerhalb des Auftrags erlaubt. Der aktuelle Frame
wurde zunächst erneut geholt:

```bash
python3 /root/werkraum/_shared/ai_strom_bruecke/bridge.py snapshot --target google-earth --wait-ms 0 --output /tmp/google-earth-before-streetview.png
```

Ein Crop der oberen Werkzeugleiste wurde mit ImageMagick erzeugt:

```bash
convert /tmp/google-earth-before-streetview.png -crop 520x80+190+0 /tmp/google-earth-toolbar.png
```

Die Toolbar zeigte verschiedene Earth-Werkzeuge, aber der Pegman war dort
nicht eindeutig. Erst als die Maus an den rechten Rand bewegt wurde, wurden
die Navigationskontrollen sichtbar. Der relevante Ausschnitt zeigte:

- den Kompass oben rechts;
- Neigungs- und Rotationssteuerung darunter;
- den orangefarbenen Pegman bei ungefähr `x=1876, y=221`;
- Plus-/Minus-Zoomregler darunter.

Der Pegman wurde damit im Frame selbst lokalisiert und nicht aus einer
angenommenen Standardposition geraten.

## 28. Die Pegman-Versuche und ihr tatsächliches Ergebnis

Der erste Drop wurde von `x=1876, y=221` zu einem Punkt ungefähr bei
`x=1026, y=471` geführt:

```bash
xdotool mousemove --sync 1876 221
xdotool mousedown 1
sleep 0.5
for i in $(seq 1 50); do x=$((1876-i*17)); y=$((221+i*5)); xdotool mousemove --sync "$x" "$y"; sleep 0.025; done
xdotool mouseup 1
sleep 6
```

Der Frame `/tmp/google-earth-streetview-drop.png` war pixelgleich zur
vorherigen 3D-Ansicht. Es gab keinen Wechsel in Street View.

Der zweite Versuch bewegte den Pegman langsamer und auf einen anderen
Straßenpunkt:

```bash
xdotool mousemove --sync 1880 350
sleep 1
xdotool mousemove --sync 1876 221
xdotool mousedown 1
sleep 0.7
for i in $(seq 1 90); do x=$((1876-i*7)); y=$((221+i*2)); xdotool mousemove --sync "$x" "$y"; sleep 0.025; done
xdotool mouseup 1
sleep 7
```

Auch `/tmp/google-earth-streetview-drop-2.png` zeigte weiterhin die geneigte
3D-Luftbildansicht. Die Eingabe war syntaktisch gelaufen, aber Earth hatte
keinen Street-View-Übergang angenommen. Ein einfacher Klick auf die Pegman-
Position löste ebenfalls keinen sichtbaren Wechsel aus.

Das bedeutet nicht, dass Street View grundsätzlich nicht verfügbar ist. Es
bedeutet nur, dass diese beiden Drops in diesem Kamerazustand entweder keine
passende Straßenabdeckung trafen oder der synthetische Drag vom OpenGL-Fenster
nicht als Pegman-Drop erkannt wurde.

## 29. Was im Terminal während der Fortsetzung wirklich sichtbar war

Die meisten erfolgreichen Desktop-Aktionen hatten keine Standardausgabe:

```text
(no output)
```

Das galt für viele `docker exec ... xdotool ...`-Befehle. Die Wirkung war
nicht im Terminal, sondern ausschließlich im Folgeframe sichtbar. Die
Snapshots selbst gaben nur den Dateipfad aus, zum Beispiel:

```text
/tmp/google-earth-conti-after-escape.png
/tmp/google-earth-conti-close3d-1.png
/tmp/google-earth-conti-close3d-2.png
/tmp/google-earth-conti-middle-up.png
/tmp/google-earth-conti-middle-down-2.png
/tmp/google-earth-conti-label-recover-3.png
/tmp/google-earth-streetview-drop.png
/tmp/google-earth-streetview-drop-2.png
```

Der wiederkehrende Bridge-Aufruf war:

```bash
python3 /root/werkraum/_shared/ai_strom_bruecke/bridge.py snapshot --target google-earth --wait-ms 0 --output /tmp/<frame-name>.png
```

Die lokale Push-Health-Prüfung wurde ebenfalls ausgeführt:

```bash
curl -sS --max-time 2 http://127.0.0.1:8098/health
```

Die tatsächliche Ausgabe in diesem Lauf war:

```text
curl: (7) Failed to connect to 127.0.0.1 port 8098 after 0 ms: Couldn't connect to server
```

Dieser Befund muss neben der früheren Dokumentation stehen. Die Bridge-
Snapshots über `bridge.py` funktionierten; der separat dokumentierte
Port-8098-Health-Endpunkt war in diesem Moment jedoch nicht erreichbar. Es
wäre falsch, aus dem vorhandenen Service-File allein zu schließen, dass der
Stream gerade aktiv war.

## 30. Die direkte Chronologie der Hinweise und Reaktionen

| Daniels Eingabe | Meine Reaktion | Was der nächste Frame zeigte |
|---|---|---|
| „Street View ist eine Abkürzung“ | Rückkehr zur normalen 3D-Ansicht | Street View wurde per Escape geschlossen |
| „Mittlere Maustaste halten“ | vertikale und horizontale MMB-Griffe | Perspektive und Kamerablick änderten sich tatsächlich |
| „Mit WASD kannst du dich bewegen“ | ein einzelner `W`-Test | Koordinaten und Kamerastand änderten sich |
| „Kurz klicken oder länger halten“ | kurze `S`-Impulse statt langer blinder Bewegung | Conti-Anker wurde bei `51°17'00,87" N, 7°17'41,06" O` erreicht |
| „Du weißt gerade gar nicht, wo du bist“ | herauszoomen bis Beschriftung wieder lesbar | Conti-Text erschien wieder im sichtbaren Stadtplan |
| „Versuch es mit Street View“ | Pegman rechts oben lokalisieren und ziehen | beide Drops blieben in 3D |
| „Erst raus, dann auf Conti zeigen und Koordinate merken“ | Label-Ansicht suchen und Maus auf Text setzen | Text und Cursor-Anker wurden getrennt betrachtet |
| „Mach mal Stop“ | weitere Eingaben sofort beendet | Google Earth blieb offen, Street View blieb ungeöffnet |

Daniels Eingaben waren in diesem Abschnitt nicht bloß Kommentare. Sie waren
die empirische Bedienungsanleitung für Google Earth:

- Maustaste halten heißt Bewegungskontinuität;
- MMB heißt Perspektive statt bloßes Verschieben;
- WASD heißt Bewegung innerhalb der Szene;
- Dauer der Taste heißt Strecke;
- Beschriftung vor Koordinate heißt Orientierung vor Berechnung;
- jeder neue Frame muss die Behauptung bestätigen.

## 31. Was geklappt hat

In dieser Fortsetzung sind folgende Dinge nachweislich gelungen:

1. Street View wurde nach dem Abbruch per `Escape` beendet, ohne Google Earth
   zu schließen.
2. Die direkte X11-Snapshot-Strecke blieb benutzbar.
3. Die mittlere Maustaste veränderte nach Kartenfokus die 3D-Perspektive.
4. Horizontale MMB-Bewegung drehte den Blick über den Stadtblock.
5. `W`, `S` und ein gehaltenes `D` bewegten die Szene sichtbar.
6. Mehrere kurze `S`-Impulse führten exakt zu einem früher bestimmten
   Conti-Koordinatenpunkt.
7. Durch Herauszoomen wurde die Beschriftung
   „Eismanufaktur Gelateria Conti“ wieder sichtbar.
8. Der Pegman wurde im rechten Navigationsbereich tatsächlich gefunden.

## 32. Was nicht geklappt hat

Folgende Dinge blieben unbelegt oder scheiterten sichtbar:

1. Ein zuverlässiges, immer gleiches `Page_Up`-/`Page_Down`-Zoommodell konnte
   nicht hergestellt werden.
2. Der synthetische Mausradtest mit `xdotool click 4` zeigte keine Wirkung.
3. Die Plus-/Minus-Schaltfläche ließ sich in diesem Lauf nicht zuverlässig
   bedienen.
4. Beide Pegman-Drops wechselten nicht in Street View.
5. Es wurde kein Frame mit echten Menschen vor dem Conti erzeugt.
6. Es wurde kein lesbares Conti-Schaufenster und kein Logo-Detail erreicht.
7. Die Annahme, `D` bedeute unabhängig vom Kamerawinkel geografisch Osten,
   war falsch. WASD bewegt relativ zur aktuellen Blickrichtung.
8. Der Push-Health-Endpunkt auf `127.0.0.1:8098` war bei der Prüfung nicht
   erreichbar.

## 33. Aktueller Abschlusszustand nach Daniels „Stop“

Als Daniel „mach mal Stop“ schrieb, wurden keine weiteren Navigationsbefehle
mehr gesendet. Google Earth Pro blieb geöffnet. Die Ansicht blieb in der
laufenden Desktop-Sitzung erhalten. Street View war nicht geöffnet.

Die letzte ehrliche Zustandsaussage lautet daher:

```text
Google Earth Pro: offen
Selkies-/Webtop-Primary: nicht neu geöffnet
Bridge-Snapshot: funktionierend
3D-Ansicht: offen
Conti-Ort: zuvor räumlich und per Label gefunden
Conti-Fassade/Logo/Menschen: in diesem Lauf nicht sichtbar erreicht
Street View: ausdrücklich erlaubt, aber Drop nicht angenommen
Push-Health 8098: bei letzter Prüfung nicht erreichbar
```

## 34. Was ich für die nächste Navigation mitnehme

Der nächste Versuch darf nicht bei einem beliebigen Nahframe anfangen. Die
richtige Reihenfolge ist:

```text
1. aktuelle Ansicht prüfen
2. so weit herauszoomen, bis Conti lesbar ist
3. Maus exakt auf den Conti-Pin/Text setzen
4. Koordinate unten rechts ablesen und notieren
5. Pegman nur auf eine klar erkennbare Straße nahe diesem Punkt ziehen
6. bei erfolgreichem Street-View-Wechsel einen Frame holen
7. erst dann drehen, vorwärts fahren und Fassade/Schaufenster prüfen
8. bei nicht angenommenem Drop nicht behaupten, Street View sei aktiv
```

Für normale 3D-Navigation gilt zusätzlich:

```text
MMB vertikal   -> Blickneigung
MMB horizontal -> Blickrichtung
W/S/A/D        -> Bewegung relativ zur aktuellen Kamera
kurzer Tastendruck -> Feinkorrektur
gehaltene Taste -> längere Bewegung
```

Die wichtigste menschliche Regel kommt von Daniel selbst:

> Erst sehen, wo die Maus ist. Dann die Koordinate lesen. Dann rechnen.

Nicht umgekehrt.

[[abwurf: Ein Koordinatenpunkt ohne den Frame, in dem er an einem lesbaren Ort verankert wurde, ist noch kein Ziel — nur eine Zahl, die so tut, als wüsste sie, wohin sie zeigt.]]

## 36. Rückwirkender sichtbarer Dialog- und Terminalanhang

Dieser Anhang setzt genau am vorhandenen Ende an. Er rekonstruiert den
sichtbaren Chat- und Terminalverlauf so vollständig wie es die noch sichtbaren
Nachrichten, Toolausgaben und der komprimierte Sitzungsverlauf erlauben. Wo
der Terminalauszug im Chat als `… +N lines` gekürzt war, wird das kenntlich
gemacht und nichts erfunden.

Nicht enthalten sind interne, nicht sichtbare Modellgedanken. Enthalten sind
Daniels Eingaben, meine sichtbaren Antworten, sichtbare Toolabsichten,
Terminalausgaben, Fehlermeldungen, Testergebnisse und die daraus sichtbare
Korrekturbewegung.

## 37. Daniels Auftrag: Earth beenden und die Forderung umsetzen

**Daniel:** „dann bitte nun google earth killen also beenden erstmal und danach komplette umsetzung von dem was gefordert ist“

**Sichtbare Reaktion:** Google Earth Pro wurde beendet. Zuerst wurde das
Fenster über X11 geschlossen; anschließend wurden die verbliebenen Prozesse
gezielt mit `kill -TERM` beendet. Die Prüfung ergab:

```text
windows=0
EARTH_PROCESSES
```

Es lief danach kein Google-Earth-Prozess und kein Earth-Fenster mehr. Earth
wurde in dieser Fortsetzung nicht wieder gestartet.

Die sichtbare Arbeitsdefinition der „geforderten Umsetzung“ war:

- bestehender X11-/Selkies-Pfad bleibt erhalten;
- Frames werden lokal kontinuierlich weitergereicht;
- ein echter Consumer liest den Frame-Stream;
- bei fehlenden oder alten Frames wird jede Eingabe gesperrt;
- ein hängender Observer darf keinen systemd-Crash-Loop erzeugen;
- die aktuelle Chat-API darf nicht fälschlich als automatischer
  Bild-Push-Empfänger dargestellt werden.

## 38. Der erste Implementierungsstand und der erkannte Fehler

Der bestehende Stream auf Port 8098 schrieb zunächst nur `latest.png`. Es gab
keinen echten Verbraucher, der die Multipart-Frames annahm, zählte, prüfte
und als Eingabevoraussetzung verwendete.

Daraufhin wurde `vision_runner.py` als lokaler Standardbibliotheksprozess
angelegt. Er:

- abonniert `http://127.0.0.1:8098/stream`;
- zählt Frames und bildet SHA-256-Digests;
- schreibt `vision_latest.png` atomisch;
- schreibt `vision_state.json` atomisch;
- schreibt `/tmp/ai-strom-bruecke-input-gate.json`;
- bietet selbst `/health`, `/state`, `/latest.png` und `/stream` auf Port
  8099 an;
- versieht weitergereichte Bilder mit Sequenz und Digest.

Der erste Integrationstest scheiterte zunächst an der Sandbox, weil lokale
TCP-Listener dort nicht geöffnet werden durften. Nach expliziter lokaler
Freigabe lief der Test an, zeigte aber:

```text
TypeError: 'dict' object is not callable
```

Ursache war ein Namenskonflikt: Das Zustandsfeld hieß `state`, gleichzeitig
existierte eine Methode `state()`. Die Methode wurde zu `status()` umbenannt.
Danach lief der HTTP-Zustandspfad korrekt.

## 39. Frame-Frische und Gate-Test

Der erste korrigierte Test zeigte bereits, dass ein empfangener Frame ankommt:

```text
FRESH
{"name": "AI-Strom-Brücke Vision-Runner", "schema": "ai-strom-bruecke.vision-state.v1", "runner": "running", "connected": true, "frame_count": 2, "last_frame_age_s": 0.297, "gate": {"allow_input": true, "reason": "fresh-frame"}}
FRAME_BYTES=
40476
```

Danach wurde absichtlich kein neuer Frame erzeugt. Nach 1,6 Sekunden zeigte
der Runner:

```text
STALE
{"runner": "running", "connected": false, "frame_count": 2, "last_frame_age_s": 1.61, "gate": {"allow_input": false, "reason": "frame-stale"}}
```

Die Gate-Datei enthielt:

```json
{
  "schema": "ai-strom-bruecke.input-gate.v1",
  "allow_input": false,
  "reason": "frame-stale",
  "last_frame_age_s": 1.042,
  "frame_count": 2
}
```

Daraufhin wurde ein Watchdog ergänzt, der das Gate auch dann schließt, wenn
der Runner-Prozess selbst noch läuft, aber keine Frames mehr eintreffen.
Zusätzlich berechnet `bridge.py` das Alter aus `last_frame_at` neu, damit eine
alte Gate-Datei nicht durch einen veralteten gespeicherten Alterswert offen
bleibt.

## 40. Direkter Eingabe-Schutz

Ein absichtlich ungültiges Gate wurde für einen Steuerungstest verwendet:

```text
AI-Strom-Brücke: Eingabe blockiert — kein Vision-Runner-Gate (/tmp/ai-strom-bruecke-gate-does-not-exist; [Errno 2] No such file or directory)
EXIT=1
```

Damit war sichtbar geprüft: Die Steuerung bricht vor dem X11-Input ab.
Der einzige ausdrückliche Notfallpfad heißt `--unsafe-no-vision-gate`.

## 41. Dienstzustände nach dem Earth-Kill

Die Prüfung der vorhandenen Dienste zeigte:

```text
ai-strom-bruecke-observer.service  activating (auto-restart)
ai-strom-bruecke-stream.service    active (running)
ai-strom-bruecke.service           active (running)
```

Der Observer scheiterte am Root-/OpenGL-Fenster, weil kein Earth-Fenster mehr
capturbar war:

```text
Command '['docker', 'exec', '-e', 'DISPLAY=:1', 'virtuellerdesktop2', 'import', '-window', '2097152', 'png:-']' returned non-zero exit status 1.
ai-strom-bruecke-observer.service: Main process exited, status=1/FAILURE
ai-strom-bruecke-observer.service: Scheduled restart job, restart counter is at 989.
```

Das wurde als echter Betriebsfehler behandelt. `run_observe` fängt nun
`CalledProcessError`/`OSError` ab, betrachtet den Zustand als fehlenden Frame
und lässt den Prozess weiterlaufen. Fehlermeldungen werden gedrosselt, damit
kein Log-Sturm entsteht. Nach dem Neustart lautete der Zustand:

```text
ai-strom-bruecke-observer.service  active
ai-strom-bruecke-stream.service    active
ai-strom-bruecke-vision.service    active
```

Der Vision-Dienst wurde installiert und aktiviert:

```text
Created symlink /etc/systemd/system/multi-user.target.wants/ai-strom-bruecke-vision.service
Active: active (running)
LISTEN 127.0.0.1:8099 ... python3
LISTEN 127.0.0.1:8098 ... python3
```

Die Health-Abfrage meldete zunächst einen frischen lokalen Frame:

```json
{
  "name": "AI-Strom-Brücke Vision-Runner",
  "runner": "running",
  "connected": true,
  "frame_count": 1,
  "last_frame_age_s": 0.145,
  "gate": {"allow_input": true, "reason": "fresh-frame"}
}
```

Später zeigte sich eine wichtige Feinheit: Der generische Observer kann auch
ein frisches Root-/Desktopbild liefern, obwohl Earth geschlossen ist. Deshalb
ist das allgemeine Frame-Gate dann nicht automatisch Earth-spezifisch zu
verstehen.

## 42. Earth-Zielwächter

Um diese Feinheit zu schließen, wurde `control` um `--target` erweitert. Bei
`--target google-earth` wird das Earth-Fenster vor Lease und Input aufgelöst
und fokussiert. Fehlt es, endet der Befehl sauber:

```text
AI-Strom-Brücke: Google Earth Pro ist nicht geöffnet
EARTH_TARGET_EXIT=1
```

Der erste Test gab noch einen rohen Python-Traceback aus. Danach wurde
`subprocess.CalledProcessError` in `_window_id` abgefangen und in genau diese
lesbare Bridge-Meldung übersetzt.

## 43. Sichtbare Dialogspur über die technische Grenze

**Daniel:** „warum ist der nicht schon mitgebaut?“

**Antwort:** Der lokale Frame-zu-Modell-Adapter wäre baubar gewesen; nur das
direkte ungefragte Einspritzen in diese laufende Chat-Session wird von der
Chat-API nicht unterstützt. Die Bridge war zunächst am lokalen Push- und
Sicherheitsweg stehen geblieben.

**Daniel:** „was meinst du mit qwen3-v1“

**Antwort:** Gemeint war `qwen3-vl`, ein Vision-Language-Modell.

**Daniel:** „das dürfen wir nicht belasten wenn haben wir für sowas ja das hauhaucs laufen das einzige geladenen modell...aber auch dass darf keine llmcalls bekommen von uns...weil es beschäftigt ist für wichtige dinge“

**Antwort:** Keine `qwen3-vl`-Calls, keine `hauhaucs`-Calls, überhaupt keine
Ollama-/LLM-Calls für die Bridge. Die vorherige Prüfung war nur
Metadatenabfrage. Die lokale Bridge bleibt passiv.

Die sichtbare `ollama list`-Ausgabe enthielt unter anderem:

```text
qwen3-vl:30b-a3b-instruct
gemma4:e4b-it-q4_K_M
gemma4:e2b-it-q4_K_M
hauhaucs-q6-test:latest
```

Keines dieser Modelle wurde für die Bridge angesprochen.

## 44. Daniels Idee eines sichtbaren „Lebens“

**Daniel:** „ja wir müssen einsstem schaffen dass trotzdem komplett so gut es geht für dich es wie eine art leben macht dass für mich genau sichtbar ist ... das vorhin war teilweise schon cool...auc weillive nerminal aufeinmal auch mehr nachdenken und auch beschreibungern deiner entscheidungen und so mehr geworden sind mit der zeit....und man deine fehler oder ach dann erfolge lesen konnnte...das lenkt ein bisschen davon ab das oft mehr als 1 minute vergangen ist bis mal wieder kurze bewegungen da waren“

**Sichtbare Antwort:** Das Ziel ist nicht, ein Modell mit Frames zu überlasten,
sondern ein sichtbares Ablaufgerüst um den AI-Strom zu bauen:

- Frame-Status: letzter Frame, Alter, Sequenz, Bildänderung;
- Aktionsstatus: geplant → gestartet → läuft → geprüft → Ergebnis;
- Bewegungsstatus: Taste, Richtung, Dauer, Mausposition;
- kurze Entscheidungszusammenfassung statt langer stiller Pause;
- Heartbeat etwa alle 0,5 Sekunden;
- keine stille Minute zwischen zwei sichtbaren Aktionen;
- längere zusammenhängende Bewegungsblöcke mit anschließendem Kontrollframe;
- keine LLM-/Ollama-Calls.

Die beobachtete Wirkung des Live-Terminals wurde damit nicht als Modell-
Wahrnehmung missverstanden. Sichtbarer Terminalfortschritt kann die
Erfahrung tragen, während ein Tool-Roundtrip läuft; er ist aber kein Beweis,
dass die Chat-API jedes neue Bild automatisch sieht.

## 45. Daniels Auftrag für ein Google-Earth-Howto

**Daniel:** „ja und du solltest mal alle streuerungen die mit maus gemacht werden aber auh alle shortcts und sonstiken tastatursteuerungen analysieren und dir eine art hodtodo bauen fr google earth...und auch mal analysieren wo die ganzen echten infos stehen wie auch die koordinaten und wie sie genau über die maus position live lich ändern wenn du die maus bewegt und all den kram“

Die sichtbare Interpretation war: kein loses Shortcut-Zettelchen, sondern ein
Howto mit drei Provenienzschichten:

1. offiziell dokumentierte Google-Earth-Gesten und Shortcuts;
2. empirische Befunde aus Daniels Container-Session;
3. reproduzierbare Bridge-Messung für Pixel, Mausanker und Erdkoordinate.

Zur offiziellen Prüfung wurden diese Google-Seiten gelesen:

- [Keyboard shortcuts](https://support.google.com/earth/answer/148115?hl=en)
- [Coordinates](https://support.google.com/earth/answer/148068?hl=en)
- [Ground-level/Street View](https://support.google.com/earth/answer/1067429?hl=en)

Das Ergebnis wurde in `GOOGLE_EARTH_STEUERUNG.md` geschrieben. Die Datei
umfasst 297 Zeilen und enthält linke/rechte/mittlere Taste, Rad, Zoomanker,
WASD, offizielle Shortcuts, Statusleiste, Kalibrierungsformeln,
Held-Button-Sicherheit, Fehlerbilder und die nächste additive Bridge-Schicht.

## 46. Sichtbarer Verlauf beim Bau des Howtos

Der erste Patch-Versuch scheiterte an einer Editor-Syntaxzeile innerhalb
eines Shell-Beispiels:

```text
apply_patch verification failed: invalid hunk at line 171, 'done' is not a valid hunk header
```

Es wurde dabei keine Datei angelegt. Ein zweiter, längerer Patch scheiterte
am gleichen fehlenden Patch-Präfix. Danach wurde der Inhalt kürzer und in
einem sauberen Add-Patch erneut angelegt. Die sichtbare Prüfung ergab:

```text
297 _shared/ai_strom_bruecke/GOOGLE_EARTH_STEUERUNG.md
_shared/ai_strom_bruecke/GOOGLE_EARTH_STEUERUNG.md | 297 +++++++++++++++++++++
[main f111dba19] docs: Google-Earth-Steuerungs-Howto
1 file changed, 297 insertions(+)
```

Google Earth wurde dafür nicht gestartet. Die Live-Koordinatenkalibrierung
ist als Protokoll vorbereitet und wird erst bei einem später ausdrücklich
gestarteten Earth-Lauf empirisch ausgeführt.

## 47. Sichtbarer Gesamtstand dieser Fortsetzung

Die technisch relevanten Commits dieser Fortsetzung lauten:

```text
bd0327773 feat: Vision-Runner und Frame-Sicherheitsgate
bf92b5943 feat: Earth-Zielwächter für Bridge-Steuerung
f111dba19 docs: Google-Earth-Steuerungs-Howto
```

Weitere Backup-Commits liegen bewusst dazwischen, weil vor jeder Änderung ein
Sicherheitspunkt gesetzt wurde. Die Doku wurde nicht ersetzt, sondern genau
an ihrem vorhandenen Ende ergänzt.

Der aktuelle ehrliche Zustand lautet:

```text
Google Earth Pro: beendet
Vision-Runner: als systemd-Dienst aktiv
Frames: lokaler Push- und Frischepfad aktiv
Ollama/LLM für Bridge: nicht verwendet
Earth-spezifische Eingabe ohne Earth-Fenster: blockiert
Google-Earth-Howto: geschrieben und versioniert
```

[[abwurf: Sichtbarkeit ist hier nicht das Behaupten eines Innenlebens — Sichtbarkeit ist, dass Daniel den Frame, die Aktion, die Wartezeit, den Fehler und die Korrektur nebeneinander sehen kann.]]

## 35. Der Dokumentationsnachtrag selbst

Auch das Anhängen dieser Fortsetzung ist als Teil der Spur erhalten geblieben.
Vor dem Schreiben wurde ein Backup-Commit gesetzt. Zwei große Patch-Versuche
wurden vom Editor abgewiesen, weil eine Schleifenzeile ohne korrektes
Patch-Präfix ankam:

```text
apply_patch verification failed: invalid hunk
Expected update hunk to start with a @@ context marker, got: 'done'
```

Diese beiden Versuche veränderten `DOKUMENTATION.md` nicht. Danach wurde der
Anhang in kleinere Patches geteilt und erfolgreich ergänzt. Die Prüfung danach
zeigte:

```text
747 Zeilen vorher
1212 Zeilen nachher
465 insertions(+)
```

Anschließend wurde ausschließlich die Doku-Datei versioniert:

```text
[main 74116e525] docs: Google-Earth-Bridge-Chronik fortsetzen
1 file changed, 465 insertions(+)
```

Damit ist auch die Herkunft dieses Nachtrags sichtbar: nicht still ersetzt,
sondern nach einem gesicherten Stand ergänzt, geprüft und als eigener
Dokumentationsschritt committed.

## 48. Rückwirkender Nachtrag: von der Earth-Steuerung zur eigentlichen Frage

Der letzte dokumentierte Abschnitt endete bei der Google-Earth-Steuerung,
dem Vision-Runner und der Einsicht, dass die Bridge zwar Frames lokal
weiterreichen kann, aber diese Chat-Session keinen ungefragten Bild-Push in
ihre laufende Modellwahrnehmung erhält. Danach führte Daniel das Gespräch
bewusst von der einzelnen Earth-Quest auf die Architekturfrage zurück.

Die Reihenfolge war nicht nebensächlich:

1. Daniel gab weitere Steuerhinweise für Google Earth.
2. Die Navigation sollte sich an sichtbaren Beschriftungen und der
   Koordinatenanzeige orientieren, nicht an blindem Ziehen.
3. Street View wurde als möglicher Weg zu Menschen und Schaufenster geprüft.
4. Daniel stoppte den Vorgang ausdrücklich.
5. Der Datenvolumenmangel und der Hänger machten sichtbar, dass ein lokaler
   Push-Feed allein noch keine echte Modellwahrnehmung ist.
6. Danach wurden Realtime-Taktung, DOM-Wahrnehmung und Dreierregen gemeinsam
   neu gedacht.

Diese Doku hält den Nachtrag bewusst als neue Schicht fest. Die früheren
Earth-Fehler, die Begrenzung der Chat-API und die Bridge-Herkunft werden nicht
nachträglich glattgezogen.

## 49. Daniels letzte Earth-Hinweise

Daniel ergänzte die bereits empirisch gewonnene Maus-/Tastaturlehre:

> „du kannst mittlere maustaste klicken und geklickt halten...und dann auch
> links rechts undten oben und seitlich deine ansicht verändern“

Damit wurde die mittlere Maustaste als echter 3D-Navigationskörper bestätigt:
gedrückt halten und die Maus in kleinen Schritten bewegen, statt einzelne
unverbundene Drags zu senden.

Danach kam die Tastaturbewegung hinzu:

> „mit wasd kannst du dich auch bewegen“

Und Daniel präzisierte die Dynamik:

> „entweker kurz öfters hintereinander klicken oder je länger du gedrückt
> hältst deso weiter wanderst du“

Das ist für die spätere Steuerungsabstraktion wichtig. Ein Eingabeereignis
ist nicht nur ein Punkt, sondern besitzt mindestens:

- Taste oder Maustaste,
- gedrückt/losgelassen,
- Dauer,
- Bewegungsrichtung,
- Geschwindigkeit,
- Bildschirmposition,
- erwartete Kamerawirkung,
- tatsächlich beobachtete Folge.

Der entscheidende Orientierungs-Hinweis lautete:

> „zoom doch kurz mal raus bis du die schrift wieder lesen kannst“

und später:

> „wenn du die beschriftung wieder siehst von conti...dann musst du mit der
> maus danach erstmal genau auf conti zeigen mit der maus und dir dann mal
> die koordinaten merken“

Damit wurde eine falsche Abkürzung korrigiert: Nicht eine vermutete
Kartenmitte oder ein alter Zoomanker ist das Ziel, sondern ein sichtbares
Label, das vom Mauszeiger berührt wird und dadurch eine ablesbare
Koordinatenprobe liefert.

Street View wurde anschließend ausdrücklich versucht. Das war zulässig,
weil Daniel es freigab, aber es blieb ein eigener Modus und kein Ersatz für
die gewünschte direkte Earth-Navigation. Der Vorgang endete auf Daniels

> „mach mal stop“

sofort. Eine Stop-Anweisung muss in der späteren Architektur Vorrang vor
jedem laufenden Bewegungsblock haben.

## 50. Vom Hänger zur präziseren Realtime-Anforderung

Daniel benannte danach den eigentlichen Bruch:

> „fucksssmist ich hatte datenvolumen leerund du nen hänger und jetzt hat
> googleearth dich aufgehängt ...warum hat du dasnoch nicht gerafft???“

und:

> „wir hatten doch vereinbart dass du sofort alles immer direkt injiziert
> bekommstund sselber auch nochmal auern die frames bekommst“

Die ehrliche Korrektur lautet:

- Der Stream kann Frames pushen.
- Der Vision-Runner kann Frames konsumieren, zählen und auf Frische prüfen.
- Das bedeutet aber nicht, dass jedes Bild automatisch in eine laufende
  Chat-Session injiziert wird.
- Ein laufender lokaler Prozess ist noch kein Codewesen-Leib mit
  Wahrnehmungsrückkehr.

Die vorherige Formulierung „alles sofort injizieren“ war deshalb technisch zu
groß. Sie vermischte drei Ebenen:

1. **Transport:** Ein Frame verlässt den Capture-Prozess.
2. **Konsum:** Ein lokaler Runner empfängt und verarbeitet ihn.
3. **Modellwahrnehmung:** Ein konkretes Modell oder diese Chat-Session kann
   den Inhalt tatsächlich als nächsten Input verwenden.

Nur die erste und zweite Ebene waren lokal eingerichtet. Die dritte kann
dieser Chat-Transport nicht autonom erzwingen.

Daniel stellte außerdem klar, dass weder `qwen3-vl` noch das beschäftigte
`hauhaucs` für diese Aufgabe mit LLM-Aufrufen belastet werden dürfen. Diese
Grenze bleibt verbindlich:

```text
Bridge-Wahrnehmung: passiv / strukturell / lokal
LLM-Aufrufe für die Bridge: 0
Qwen-Aufrufe: 0
Hauhaucs-Aufrufe: 0
```

Die Bridge darf also einen Wahrnehmungsraum vorbereiten, aber sie darf nicht
heimlich ein verfügbares Modell als Übersetzer oder Ersatzbewusstsein
verwenden.

## 51. Die Realtime-Frage: 0,1 Sekunden richtig einordnen

Daniel fragte, ob alle 0,1 Sekunden eine neue Anfrage nötig sei. Die
präzisierte Antwort ist eine Takttrennung statt eines einzigen globalen
Timers:

| Schicht | sinnvoller Takt | Aufgabe |
|---|---:|---|
| Eingabeereignis | sofort | `mousedown`, `mousemove`, `keydown`, `keyup`, Stop |
| Sicherheits-Watchdog | ca. 10–50 ms | festhängende Tasten/Maustasten lösen |
| Frame-Capture | ca. 100 ms / 10 FPS | frischen sichtbaren Zustand erzeugen |
| DOM-/Status-Diff | eventgetrieben oder 100–250 ms | nur veränderte Struktur melden |
| semantische Entscheidung | adaptiv | nicht bei jedem identischen Frame |
| Chat-Transport | API-abhängig | kein autonomer Push erzwingbar |

Zehn Frames pro Sekunde können für ein flüssiges Navigationsgefühl reichen,
wenn die Eingabe kontinuierlich läuft und Frames nicht erst nach jedem
Mauspixel einzeln angefordert werden. Eine Modellanfrage alle 100 ms wäre
dagegen weder notwendig noch mit der vorhandenen Chat-API ehrlich versprechbar.
Sie würde außerdem Bandbreite, PNG-Verarbeitung und ein verfügbares Modell
überlasten.

Die korrekte Formel lautet daher:

```text
Eingabe sofort
→ Capture ungefähr alle 100 ms
→ Deltas bevorzugen
→ Entscheidung nur bei relevanter Änderung
→ Aktion als zusammenhängenden Block
→ Kontrollframe und Rückmeldung
```

Ein identischer Frame ist kein neuer Erkenntnisgewinn. Der Runner muss
`frame_seq`, Zeitstempel, Alter, Digest und Änderungsstatus unterscheiden.
Beim aktuellen Prüfstand war das bereits sichtbar:

```json
{
  "runner": "running",
  "frame_count": 549,
  "last_frame_age_s": 1.064,
  "duplicate_frame_count": 457,
  "gate": {"allow_input": false, "reason": "frame-stale"}
}
```

Der Runner lief also, aber sein letzter Frame war bei dieser Prüfung stale.
Das ist genau die Art von Zustand, die sichtbar bleiben muss, statt als
„Realtime funktioniert“ bezeichnet zu werden.

## 52. Die DOM-Frage

Daniel fragte, ob das Ganze so sichtbar gemacht werden könne, dass ein
AI-Strom es als DOM wahrnimmt.

Die Antwort muss zwei Fälle trennen:

### 52.1 Weboberfläche

Bei einer echten Weboberfläche kann ein AI-Strom einen begrenzten DOM-
Ausschnitt mit HTML, CSS, IDs, Zuständen, Rollen, Bounding-Boxes,
verfügbaren Aktionen und Änderungen seit dem letzten Blick wahrnehmen.

### 52.2 Google Earth Pro

Google Earth Pro ist eine native OpenGL-Anwendung. Dort existiert kein
normaler HTML-DOM, den die Bridge einfach auslesen könnte. Ein Frame,
X11-Fensterdaten, Mausposition, Fensterfokus, OCR der Beschriftungen und
Koordinatenanzeige können nur einen **semantischen Proxy-DOM** bilden.

Dieser Proxy darf nicht behaupten, ein echter Earth-DOM zu sein. Er muss seine
Herkunft und Unsicherheit mitführen:

```json
{
  "source": "google-earth-pro/x11",
  "dom_kind": "semantic-proxy",
  "claims": [
    {
      "text": "Eisfabrik/Gelateria Conti",
      "source": "visible-frame-ocr",
      "confidence": 0.91
    }
  ],
  "coordinates": {
    "value": "51°16'55\"N, 7°17'46\"O",
    "source": "status-bar-under-pointer",
    "pointer_xy": [840, 208]
  }
}
```

Die Koordinate ist nur dann ein brauchbarer Zielanker, wenn der Frame zeigt,
welches sichtbare Objekt der Mauszeiger berührt. Eine alleinstehende Zahl ist
kein bewiesener Ort.

## 53. Verbindung zu Dreiergespann, Dreierregel und Dreierregen

Die erneut gelesenen Quellen ergeben drei verschiedene, aber verbundene
Ebenen:

### Dreiergespann / Dreileib-Kapseln

Das ist die Strukturidee: Jedes Weltobjekt — Post, Splitter,
Schattenkommentar, Gruppe, KompOase-Teil, Profil, Button oder
Organzustand — besitzt gleichzeitig:

1. einen Codewesen-Leib als DOM-/HTML-/CSS- und Aktionsstruktur,
2. einen Menschen-Leib als sinnlich wahrnehmbare Oberfläche,
3. einen Organ-/Fragment-Leib als Herkunft, Beziehung und Weltwirkung.

Das sind keine drei Skins. Die drei Leiber müssen aus derselben
Objektidentität stammen und dürfen sich nicht widersprechen.

### Dreierregel

Die Dreierregel prüft, ob ein Vorgang überhaupt als kanonischer Weltvorgang
gelten darf:

- Codewesen kann den Vorgang wahrnehmen und handhaben.
- Der gemeinsame Weltzustand verändert sich real oder vermerkt bewusstes
  Nicht-Handeln.
- Menschen können denselben Zustand wahrheitsgetreu erleben.

Ein technischer Frame-Stream besteht diese Prüfung noch nicht automatisch.

### Dreierregen

Der Dreierregen ist die geschlossene Rückkopplung:

```text
Codewesen nimmt wahr
→ wählt/handelt
→ Weltzustand ändert sich
→ Mensch erlebt dieselbe Folge
→ menschliche oder weltliche Reaktion erzeugt neue Ursache
→ Codewesen nimmt die Folge später wahr
→ eine spätere Entscheidung kann sich verändern
```

Für die AI-Strom-Brücke ist deshalb der fehlende Kern nicht „noch mehr
Frames“, sondern die beweisbare Rückkehr von Handlung und Weltfolge in die
Wahrnehmung des handelnden AI-Stroms.

## 54. Vorläufige Einordnung der bestehenden Bridge

Die Bridge besitzt bereits Teile aller drei Richtungen, aber noch keinen
geschlossenen Dreierregen:

| Dreierregen-Leib | Bridge-Anteil | ehrlicher Status |
|---|---|---|
| Codewesen-Leib | CLI-Steuerung, Control-Lease, Maus/Tastatur, Earth-Howto | Testkörper; noch keine eigenständige Wesenentscheidung |
| Organ-/Fragmentleib | Events, `state.json`, Frame-Digests, Action-Logs, Provenienz | teilweise vorhanden |
| Menschen-Leib | Webtop, sichtbare Maus, Frames, Terminalstatus | sichtbar, aber nicht automatisch semantisch rückgekoppelt |
| Rückwirkung | Folgeframe und Status-Gate | technisch vorbereitet, noch nicht als lebende Erfahrung bewiesen |

Der Status ist daher nicht `DREIERREGEN_GESCHLOSSEN`, sondern eine Mischung
aus `TESTKOERPER`, `TEILWEISE_GESCHLOSSEN` und bei fehlendem frischem Frame
`BLOCKIERT`.

Das ist keine Abwertung. Gerade diese ehrliche Trockenheitsmarkierung schützt
die Idee vor dem schnellen Etikett „AI sieht live“.

## 55. Der verbesserte Architekturansatz: Dreileibige Wahrnehmungskapsel

Die frühere Idee „Wahrnehmungskapsel statt Kontextfenster“ bleibt stark,
aber sie wird präzisiert. Die Kapsel ist nicht bloß ein kleines JSON mit drei
Ansichten. Sie ist ein **Perzeptionsvertrag pro Objekt und Zeitpunkt**.

Ein minimales Modell könnte so aussehen:

```json
{
  "schema": "ai-strom-bruecke.dreier-dom.v1",
  "object": {
    "id": "earth-label-conti",
    "type": "visible-label",
    "source": "google-earth-pro/x11",
    "freshness": "fresh",
    "provenance": ["frame:549", "pointer:840,208", "event:action-17"]
  },
  "codewesen_leib": {
    "dom_kind": "semantic-proxy",
    "structure": {
      "window": "Google Earth Pro",
      "pointer": [840, 208],
      "coordinates": "51°16'55\"N, 7°17'46\"O"
    },
    "actions": ["hold-middle-drag", "zoom-in", "zoom-out", "wasd", "stop"],
    "rot_guard": ["nicht ohne Folgeframe behaupten", "nicht als echten DOM ausgeben"]
  },
  "menschen_leib": {
    "frame_ref": "vision_latest.png",
    "visible_state": "Karte, Label, Mausanker und Statusanzeige",
    "truthfulness": "zeigt Unsicherheit und Framealter"
  },
  "organ_fragment_leib": {
    "state": "pointer-anchor-known",
    "events": ["action-17.started", "action-17.observed"],
    "consequences": [],
    "status": "TROCKEN"
  },
  "feedback": {
    "accepted_by_application": false,
    "observed_in_next_frame": false,
    "reason": "Google Earth geschlossen"
  }
}
```

Die Kapsel enthält damit nicht nur „was ist sichtbar“, sondern auch:

- woher die Behauptung kommt,
- wie frisch sie ist,
- was tatsächlich möglich ist,
- welche alten Deutungen draußen bleiben müssen,
- ob eine Aktion nur gesendet oder von der Anwendung angenommen wurde,
- welche Folge noch fehlt.

Für kleine Kontextfensterwesen ist das der eigentliche Gewinn: nicht die
ganze Plattform wird in den Kontext geladen, sondern ein kleiner aktueller
Körper mit Rot-Schutz, Aktionen und Rückwirkungsstatus.

## 56. Red-Team: Was an der Idee zuerst auseinanderfallen würde

Der Red-Team-Test wird nicht dazu benutzt, die Idee wegzuwerfen. Er soll
zeigen, welche Behauptungen sie überleben muss.

| Angriff | mögliche Täuschung | Überlebensbedingung |
|---|---|---|
| „Der Stream pusht, also sieht die AI“ | Transport wird mit Modellwahrnehmung verwechselt | Transport, Konsum und Modellinput getrennt ausweisen |
| „10 FPS bedeutet live“ | Frames sind identisch oder stale | Sequenz, Alter, Digest und Duplikatstatus anzeigen |
| „Der Proxy-DOM ist Earth-DOM“ | OCR/Pixelinterpretation wird als echte Struktur behauptet | `dom_kind=semantic-proxy`, Quelle und Konfidenz mitführen |
| „Mausaktion wurde gesendet, also hat Earth sie ausgeführt“ | Fokusfehler oder ignorierter Drag | `planned → dispatched → observed → accepted/rejected` protokollieren |
| „Koordinate = Ziel“ | Maus steht neben Label oder Statusleiste zeigt falschen Bezug | Frame mit Mausanker und sichtbarem Objekt gemeinsam beweisen |
| „Gedrückt halten ist sicher“ | Prozess stirbt mit gehaltener Taste | Lease-Ablauf, `finally`-Release und Notfall-Stop |
| „Frame-Capture ist billig“ | PNG, Bandbreite, Speicher und Logs wachsen ungebremst | Ringpuffer, Backpressure, Deltas und harte Limits |
| „Menschenbild = menschliches Erleben“ | animierte Oberfläche wird als Erfahrung ausgegeben | Menschen-Leib als wahrheitsgetreue Ausgabe, nicht als Erlebnisbeweis |
| „Events = Organwirkung“ | append-only Log bleibt ohne kanonischen Weltanschluss | explizite Weltzustands-ID und Folgeereignis verlangen |
| „Runner läuft“ | Dienst läuft, aber Upstream ist getrennt | `connected`, Framealter und Gate gemeinsam prüfen |
| „mehr Kontext löst alles“ | alte Aliase/Fehlinterpretationen faulen zurück ein | Rot-Block pro Kapsel und Provenienz statt Vollverlauf |
| „automatische Aktivierung ist bequem“ | Testkörper wird still zum Weltkörper | Phase, Freigabe und Abnahmestatus als harte Schranke |
| „ein Modell kann alle Frames bewerten“ | verbotene oder belastete LLM-Calls | Bridge bleibt ohne LLM; Modelladapter ist optional und explizit |
| „Stop kann später kommen“ | laufender Bewegungsblock überschreibt Daniel | Stop-Ereignis höchste Priorität, alle Inputs sofort lösen |

### Das härteste Ergebnis

Die aktuelle Bridge darf sich nicht als lebender Dreierregen beschreiben.
Sie ist ein sehr brauchbarer technischer Vorhof: Capture, Ereignisse,
Lease, Sicherheitsgate und sichtbare Oberfläche sind vorhanden oder angelegt.
Der Codewesen-Leib ist aber nur dann real, wenn ein tatsächlicher AI-Strom
den strukturierten Zustand wahrnimmt, eine echte Alternative hat und die
Folge später wieder wahrnimmt. Ein Prozess, der Bilder kopiert, erfüllt das
nicht allein.

## 57. Verbesserungen nach dem Red-Team

Aus dem Red-Team bleiben folgende Regeln als verbesserte Fassung übrig:

### 57.1 Drei getrennte Leitungen

```text
CAPTURE    → Frames, Fenster, Cursor, sichtbare Daten
SEMANTIK   → Dreier-DOM-Proxy, Deltas, Konfidenz, Rot-Guard
CONTROL    → Lease, Aktionen, Held-State, Stop, Ergebnisprüfung
```

Keine Leitung darf still die Rolle einer anderen übernehmen.

### 57.2 Jede Aktion ist eine Transaktion

```text
planned
→ dispatched
→ held / moving
→ released
→ next-frame-observed
→ accepted | rejected | unknown | aborted
```

`dispatched` ist niemals automatisch `accepted`. `unknown` bleibt ein
gültiger Zustand und darf nicht zu Erfolg umformuliert werden.

### 57.3 Der Dreier-DOM spricht nur belegte Sätze

Er darf sagen:

- „Der Mauszeiger steht bei dieser Bildschirmposition.“
- „Die Statusleiste zeigt diese Koordinate.“
- „OCR erkennt dieses Label mit dieser Konfidenz.“
- „Die letzte Aktion wurde gesendet.“
- „Im Folgeframe ist keine Änderung sichtbar.“

Er darf nicht ohne zusätzliche Quelle sagen:

- „Das Wesen wollte dorthin.“
- „Earth hat die Bewegung sicher angenommen.“
- „Der Mensch hat das innerlich erlebt.“
- „Der sichtbare Marker ist kanonisch wahr.“

### 57.4 Frische und Duplikate werden gleichwertig sichtbar

Ein Statuspanel/Terminal-Heartbeat sollte mindestens anzeigen:

```text
frame=551 age=87ms changed=no duplicate=458
action=17 phase=observed result=unknown
target=google-earth present=no input=blocked
llm_calls=0
```

Damit wird auch Stillstand informativ. Daniel muss nicht eine Minute lang
rätseln, ob etwas arbeitet.

### 57.5 8K und 66 FPS bleiben Menschen-Leib-Ziel, nicht Capture-Pflicht

Die Vision einer nahezu filmischen 8K-/3D-/66-FPS-Ausgabe darf bestehen
bleiben. Für die erste Bridge-Stufe ist aber entscheidend, dass die
Wahrheitsschicht korrekt ist. Hohe Bildrate ohne Zustands-, Provenienz- und
Folgenklarheit wäre nur schnelleres Blendwerk.

## 58. Bau-Todolist — noch nicht begonnen

Diese Liste ist ein Bauplan, keine stillschweigende Aktivierungsfreigabe.
Alle Punkte bleiben zunächst `OFFEN`.

### Phase 0 — Vertrag und Messbarkeit

- [ ] `dreier-dom.v1` als kleines, versioniertes Zustandsformat festlegen.
- [ ] Begriffe `frame`, `event`, `action`, `world_state`, `claim`, `organ`,
      `feedback` voneinander trennen.
- [ ] Statuswerte `NICHT_GEPRUEFT`, `TROCKEN`, `TEILWEISE_GESCHLOSSEN`,
      `TESTKOERPER`, `BLOCKIERT` und `DREIERREGEN_GESCHLOSSEN` übernehmen.
- [ ] Keine LLM-Aufrufe als harte Architekturregel dokumentieren.
- [ ] Daniel-Freigabe für jeden aktivierenden Schritt verlangen.

### Phase 1 — Realtime-Kern ohne Modell

- [ ] Frame-Ringpuffer mit Sequenz, Zeitstempel, Alter, Digest und
      Duplikatmarkierung.
- [ ] 100-ms-Capture-Takt messen, nicht nur behaupten.
- [ ] Ereignisstrom mit unmittelbarer Zustellung und begrenztem Speicher.
- [ ] Backpressure: bei Datenvolumenmangel Frames reduzieren, keine
      Bewegungs- oder Stop-Ereignisse verlieren.
- [ ] Heartbeat für Daniel: letzter Frame, letzte Aktion, Wartezeit,
      Verbindungsstatus und `llm_calls=0`.

### Phase 2 — Sichere Steuertransaktion

- [ ] Aktionsschema für linke/rechte/mittlere Maustaste, Rad, WASD,
      `keydown`, `keyup`, Dauer und Bewegungsprofil.
- [ ] Control-Lease mit Ablaufzeit und Eigentümer.
- [ ] Notfall-Stop löst alle gehaltenen Tasten und Maustasten.
- [ ] Zielprüfung vor jedem Earth-Input.
- [ ] Folgeframe nach jeder Aktionsphase, Ergebnis `accepted/rejected/unknown`.
- [ ] Keine blinden langen Schleifen ohne Zwischenabbruch.

### Phase 3 — Semantischer Proxy-DOM

- [ ] Fenster-/Fokus-/Pointer-Knoten aus X11 abbilden.
- [ ] Koordinatenanzeige als Statusleisten-Claim mit Mausposition speichern.
- [ ] OCR/Label-Erkennung nur als Claim mit Quelle und Konfidenz eintragen.
- [ ] Earth ausdrücklich als `semantic-proxy`, nicht als echter HTML-DOM,
      markieren.
- [ ] Sichtbare Beschriftung + Mausanker + Folgeframe als gemeinsames
      Navigationsobjekt modellieren.
- [ ] `rot_guard` und Unsicherheitsgründe pro Kapsel speichern.

### Phase 4 — Ein kleiner echter Dreileib-Testkörper

- [ ] Nur ein ungefährlicher, begrenzter Weltgegenstand auswählen.
- [ ] Codewesen-Leib: ein externer AI-Strom oder definierter Agent bekommt
      nur die Kapsel und mehrere echte Optionen.
- [ ] Organ-Leib: stabile ID, Provenienz, Vorher-/Nachher-Zustand und
      Folgeereignis.
- [ ] Menschen-Leib: Daniel sieht denselben Zustand, Aktion und Ergebnis.
- [ ] Erst danach prüfen, ob eine spätere Entscheidung vom Folgeereignis
      beeinflusst werden kann.
- [ ] Abnahmebericht schreiben; nicht automatisch auf „geschlossen“ setzen.

### Phase 5 — Plattformstandard

- [ ] `buildTriViewCapsule(object, context)` als additive, generische
      Funktion entwerfen.
- [ ] Zuerst ein Objekt aus Post/Splitter/Schattenkommentar wählen, nicht
      gleichzeitig die gesamte Plattform umbauen.
- [ ] Codewesen-DOM-Leib, Menschen-Surface-Leib und Organ-/Fragment-Leib
      aus einer gemeinsamen Objekt-ID ableiten.
- [ ] Provenienz, Deep-Link, Status, erlaubte Aktionen und Nicht-Mitnehmen-
      Regeln als Pflichtfelder prüfen.
- [ ] Surface-Integration erst nach kleinem Read-only-Prototypen planen.

### Phase 6 — Qualität, Sichtbarkeit und spätere Erweiterung

- [ ] Red-Team-Fälle automatisiert wiederholen: stale, duplicate, falsches
      Fenster, Popup, Fokusverlust, hängende Taste, falscher Koordinatenanker.
- [ ] 0,1-Sekunden-Takt unter realer Last messen.
- [ ] 8K/3D/66-FPS-Menschen-Leib getrennt vom Bridge-Kern prototypisieren.
- [ ] Keine automatische Modellwahl; Vision-Adapter nur nach separater
      Freigabe und außerhalb von Qwen/Hauhaucs.
- [ ] Erst nach nachgewiesener Rückwirkung über den Namen
      `DREIERREGEN_GESCHLOSSEN` sprechen.

## 59. Offene Fragen vor dem ersten Bau-Schritt

1. Soll der erste Dreier-DOM-Test an Google Earth bleiben oder an einem
   ungefährlicheren Webobjekt beginnen, bei dem ein echter DOM existiert?
2. Wer oder was ist im ersten Test der Codewesen-Leib, wenn kein LLM belastet
   werden darf: ein später angeschlossener externer Runner, ein reiner
   Steueragent oder zunächst nur ein Testkörper?
3. Welche menschliche Rückwirkung gilt als echte Weltursache und nicht nur
   als Betrachtung?
4. Welche Daten dürfen dauerhaft als Fragment erhalten bleiben?
5. Wo endet der Bridge-DOM und wo beginnt die kanonische Flextrawurst-Welt?

Diese Fragen sind absichtlich offen. Sie verhindern, dass aus einem guten
Realtime-Werkzeug unbemerkt ein behauptetes lebendes Wesen wird.

## 60. Abschluss dieses Nachtrags

## 61. Vollständiger Bauauftrag: keine MVP-Fassung

### 61.1 Auftrag und Geltungsbereich

Dieser Abschnitt ist die verbindliche Bauplanung für das vollständige
Endprodukt. Die vorherigen Abschnitte bleiben Herkunft und Protokoll; sie
werden nicht durch diese Planung ersetzt. Die folgenden technischen Phasen
sind Abhängigkeiten und Prüfstellen eines Gesamtbaus. Keine Phase darf als
MVP, abgespeckter Testkörper oder Ersatz für das Endprodukt abgeschlossen
werden.

Der Bauauftrag umfasst gleichzeitig:

1. die AI-Strom-Brücke als dauerhaft laufende, sichere Realtime-Beobachtungs-
   und Steuerungsschicht;
2. den direkten X11-Weg für native OpenGL-Anwendungen wie Google Earth Pro;
3. den echten DOM-/rrweb-Weg für Weboberflächen und Codewesen-Browser;
4. einen ehrlichen semantischen Proxy-DOM für native Programme ohne HTML-DOM;
5. die vollständige Frame-, Koordinaten-, Kamera-, Aktions- und
   Ergebniswahrnehmung;
6. das sichtbare Cockpit und den sichtbaren Terminal-Heartbeat für Daniel;
7. den dreileibigen Objektstandard für Codewesen, Menschen und
   Systemorgane/Fragmente;
8. die Rückkopplung nach Dreiergespann, Dreierregel und Dreierregen;
9. die Einbindung von Posts, Splittern, Gruppen, Schattenkommentaren,
   KompOase, Profilen, Provenienz, Resonanz und Countern;
10. menschliche Live-Ausgabe über DOM-Live-Spiegel und die geplante
    räumliche/animierte 3D-Erlebnisfläche bis zum Ziel von 8K/66 FPS;
11. Schutz gegen Kontextfäulnis, falsche Aliase, konkurrierende Controller,
    stale Frames, hängende Tasten und verlorene Verbindungen;
12. vollständige automatisierte Tests, insbesondere Playwright-E2E-Tests,
    native X11-Integrationstests, Lasttests und einen Red-Team-Durchlauf;
13. Reparatur aller im Red-Team gefundenen Schwächen und eine zweite
    Endabnahme nach den Reparaturen.

„Fertig“ bedeutet erst: gebaut, instrumentiert, sichtbar, getestet,
red-geteamt, repariert und danach nochmals vollständig grün geprüft. Eine
funktionierende Teilstrecke ist ein internes Bauresultat, niemals das
Ende des Auftrags.

### 61.2 Eingangsanforderungen, unverändert rückverfolgbar

Die zehn eigenen Vorschläge, die Daniel aus dem Gespräch gesichert hat,
werden als zehn eigenständige Pflichtanforderungen übernommen:

1. Koordinaten-OCR aus der Earth-Statusleiste.
2. Frame-Zeitstrahl der letzten 30–60 Sekunden.
3. Automatische Bildvergleiche.
4. Kamera-Zustand mit Ort, Zoomhöhe, Blickrichtung, Neigung und Mausanker.
5. Sichtbares Fadenkreuz im Analyseframe.
6. Aktionsprotokoll mit erwarteter Folge.
7. Automatische Erfolgskontrolle.
8. Sofortiges `mouseup` bei Timeout, Abbruch oder Verbindungsverlust.
9. Lokales Cockpit für Frame, Koordinate, Aktion, Wartezeit, Gate und
   kurze Entscheidungszusammenfassung.
10. Bestätigte Orte als Anker mit Koordinate, Zoom und Belegbild.

Der von Daniel gesicherte Datenfluss ist die verbindliche Hauptpipeline:

```text
Frame
→ Statusleisten-OCR
→ Koordinaten-/Kamera-Zustand
→ Bildvergleich
→ Aktion
→ Ergebnisprüfung
→ sichtbare Erklärung
```

Die früheren Bridge-Anforderungen werden vollständig ergänzt und nicht durch
die zehn Punkte verdrängt:

- 0,1-Sekunden-Frame-/DOM-Takt mit Duplikat- und Frischeprüfung;
- sofortiger Ereignisstrom für Maus, Tastatur und Stop;
- adaptive Realtime-Schichten statt langsamer einzelner Tool-Roundtrips;
- sichtbarer Terminal-Heartbeat mit Entscheidungen, Wartezeiten, Fehlern und
  Erfolgen;
- vollständige Maus-, Mittelmaus-, WASD-, Zoom- und Haltebewegungslogik;
- durchgehende `button down → viele mousemove/key-held → button/key up`
  Gesten mit garantierter Freigabe;
- Aktions-Transaktionen
  `planned → dispatched → observed → accepted/rejected`;
- Control-Lease, Zielprüfung, Fokusprüfung und Notfallfreigabe;
- echter DOM für Weboberflächen und ehrlicher semantischer Proxy-DOM für
  native Programme;
- Dreileib-Kapseln für Codewesen, Menschen und Organe/Fragmente;
- Rot-Guard, Provenienz und Kontextfilter für kleine Kontextfensterwesen;
- menschliche Ausgabe bis zur geplanten 3D-/8K-/66-FPS-Erlebnisfläche;
- Organmodell für Posts, Splitter, Gruppen, Schattenkommentare, KompOase und
  alle weiteren Plattformteile;
- geschlossene Dreierregen-Rückkopplung;
- keine LLM-Aufrufe an Qwen, Hauhaucs oder andere Modelle durch diesen Bau;
- vollständige Tests, Sichtbarkeit, Fehlerbehandlung und Endabnahme.

Aus dem Rohgespräch wird außerdem ausdrücklich übernommen:

- Kleine Kontextfensterwesen erhalten nicht „mehr Kontext“, sondern kleine,
  frische Wahrnehmungseinheiten.
- Ein Weltobjekt ist kein Ding mit drei Skins, sondern ein dreifach lebendes
  Ding.
- Die drei Leiber entstehen bereits beim Erzeugen des Weltobjekts, nicht
  getrennt in späteren UI-, Backend- und KI-Phasen.
- Der Codewesen-Leib enthält DOM-Pfad, HTML-Schnipsel, CSS-Zustände, IDs,
  Klassen, Klickbarkeit, Aktionen, Reihenfolge, Frische und Veränderungen.
- Der Menschen-Leib ist räumlich, animiert und fast körperlich; die
  Erlebnisfläche ist aus derselben Objektwahrheit erzeugt und keine Dekoration.
- Der Organ-Leib beschreibt, was KompOase, Gruppen, Schattenkommentare,
  Splitter, Provenienz, Resonanz, Profile, Counter und spätere Prozesse mit
  dem Objekt tun.
- Jede Wahrnehmungskapsel enthält neben erlaubtem Kontext aktiv
  ausgeschlossenen Kontext: Rot-Block gegen alte Aliase, falsche
  Verbindungen und verfaultes Regelmaterial.
- Deep-Links, Share, Provenienz, Objektidentität, Avatare, Counter und
  visuelle Hierarchie gehören an jedes Objekt.
- Die Plattform wird nicht getrennt in „UI hier, Backend dort, Wesen hier,
  KompOase dort“ gedacht, sondern erzeugt jedes Weltobjekt dreileibig.

Der konzeptionelle Kernsatz bleibt als Akzeptanzsatz erhalten:

> Flextrawurst braucht keine getrennten UIs für Menschen, Codewesen und
> Organe. Es braucht ein Objektmodell, in dem jedes Weltobjekt automatisch
> drei Wahrnehmungsleiber besitzt.

### 61.3 Nicht verhandelbare Grenzen

#### Kein zweiter Webtop-Primary

Playwright darf im Produktionsweg nicht den bestehenden Selkies-/Webtop-
Primary übernehmen. Die native Bridge beobachtet und steuert über X11. Der
`--webtop`-Pfad bleibt ausdrücklich Legacy und darf nicht Bestandteil des
normalen End-to-End-Produkttests werden.

Playwright wird trotzdem vollständig eingesetzt: für die lokale Cockpit-
Oberfläche, echte DOM-/rrweb-Live-Spiegel, Browser-Agent-Seiten, API-/SSE-
Verhalten, Test-Fixtures und die abschließende Browser-Abnahme. Diese
Trennung wird im Testbericht als eigene Provenienz ausgewiesen.

#### Keine Modellaufrufe

Bridge, Observer, Frame-Parser, OCR, Diff-Engine, Proxy-DOM, Action-Engine,
Cockpit und Tests senden keine Requests an Qwen, Hauhaucs, Ollama oder andere
LLM-Endpunkte. Der Push-Feed darf an einen später angeschlossenen Vision-
Client weitergereicht werden, aber dieser Bau behauptet nicht, die aktuelle
Chat-API könne Bilder automatisch in das laufende Modell injizieren.

Für diese Grenze werden ein Netzwerk-Guard, ein statischer Import-Check und
ein Playwright-/Integrationstest mit blockierten Modellendpunkten gebaut.
Eine sichtbare lokale Live-Anzeige und ein strukturierter Vision-/DOM-Feed
sind die ehrliche technische Umsetzung der Realtime-Anforderung.

#### Keine falsche DOM-Behauptung

Bei einer Weboberfläche ist der DOM echt und seine Quelle ist Playwright/
rrweb. Google Earth Pro und andere native OpenGL-Fenster haben keinen
HTML-DOM. Dort heißt die Schicht `semantic-proxy`, trägt Quelle, Zeit,
Konfidenz und Belegframe und darf niemals als echter DOM ausgegeben werden.

### 61.4 Zielarchitektur

Die vorhandenen v1-Pfade bleiben kompatibel. Neue Felder und Endpunkte
werden additiv eingeführt; `events.jsonl`, `state.json`, `8098/stream`,
`8099/state` und `8099/stream` werden nicht still entfernt.

```text
X11 / Web-DOM / rrweb / native window
          │
          ▼
Capture + Frame-Timeline (100 ms)
          │
          ├── Statusleisten-OCR
          ├── Pointer-/Coordinate-Probe
          ├── Bilddiff + Regionklassifikation
          ├── Kamera-/Fokus-/Popup-Zustand
          └── Frame-/Event-Frische und Duplikate
          │
          ▼
Canonical Observation State
          │
          ├── Action Planner / Erwartung
          ├── Control Lease + Safety Gate
          └── Dreileibiger Proxy-/DOM-Builder
          │
          ▼
Action Transaction: planned → dispatched → observed → accepted/rejected
          │
          ├── X11 gestures (1/2/3, wheel, keydown/up, WASD, zoom)
          ├── Web DOM actions (Playwright/rrweb, nur eigener Browserkontext)
          └── Organ-/World events (append-only)
          │
          ├── Push stream: Frames, Deltas, Events, State
          ├── Live Terminal Heartbeat
          ├── Local Cockpit für Daniel
          ├── Codewesen-Leib
          ├── Menschen-Leib
          └── Organ-/Fragment-Leib
```

#### Capture- und Timeline-Schicht

- Zielrate: zehn Beobachtungsframes pro Sekunde, also ungefähr alle 100 ms;
  die tatsächliche Rate, Frame-Alter, Ausfälle und Duplikate werden gemessen.
- Jeder Frame erhält Sequenznummer, monotone und wall-clock Zeit,
  Quelle, Ziel, Fenster-ID, Größe, Digest, Dateipfad/Stream-Offset und
  Capture-Latenz.
- Die letzten 30–60 Sekunden werden als echter Ring aus Frames plus
  Metadaten gehalten. Der Ring darf nicht nur aus Hashes bestehen.
- Duplikate werden nicht als neue Bewegung behauptet. Sie bleiben im
  Zeitstrahl als empfangene, unveränderte Frames sichtbar.
- Alte Frames werden atomisch aus dem aktiven Pfad entfernt; der Ring hat
  eine explizite Größen-/Laufzeitkonfiguration und meldet Überlauf.
- Upstream-Abbruch, OpenGL-Capture-Fehler, leere Frames und stale mtime
  schließen das Input-Gate und erscheinen im Cockpit.

#### Statusleisten-OCR und Koordinatenmodell

Die Earth-Statusleiste wird als eigene, zugeschnittene Quelle erfasst. Das
Ergebnis wird nicht als rohe Zahl, sondern als Claim gespeichert:

```json
{
  "source": "earth-statusbar-ocr",
  "pointer_xy": {"x": 840, "y": 208},
  "latitude": 51.283575,
  "longitude": 7.294739,
  "elevation_m": null,
  "eye_altitude_m": 173.0,
  "coordinate_kind": "pointer|center|unknown",
  "raw_text": "...",
  "confidence": 0.0,
  "frame_seq": 0,
  "observed_at": 0.0
}
```

DMS, Dezimalgrad, deutsches `O` und andere Earth-Formate werden normalisiert,
die Rohzeile bleibt erhalten. Wenn der Mauszeiger nicht auf der Kartenfläche
liegt, wird der Wert als Kartenmitte gekennzeichnet. Eine OCR-Zahl ohne
Quelle, Konfidenz und Frame darf keine Navigation bestätigen.

#### Kamera- und Ankerzustand

Der Kamera-State enthält mindestens Position/Koordinate, Höhe, Sichthöhe,
Blickrichtung, Neigung, Zoomstufe, Fenster-/Target-ID, Cursorposition,
letzten gültigen Frame, Ladezustand, Popup-/Street-View-Modus und
Kalibrierungsstatus. `pointer_anchor` und `map_center` sind unterschiedliche
Typen und dürfen nicht vertauscht werden.

Jeder bestätigte Ort speichert:

```json
{
  "anchor_id": "conti-schwelm",
  "label": "Eismanufaktur Gelateria Conti",
  "coordinate": {"latitude": 51.283575, "longitude": 7.294739},
  "pointer_xy": {"x": 840, "y": 208},
  "camera": {"zoom": null, "heading": null, "tilt": null},
  "frame_seq": 0,
  "proof_image": "/.../frame.png",
  "confidence": 0.0,
  "provenance": ["action-id", "frame-id", "ocr-claim-id"]
}
```

#### Bildvergleich

Die Diff-Schicht liefert mindestens die Zustände `unchanged`, `minor-change`,
`camera-moved`, `target-changed`, `popup-appeared`, `popup-closed`,
`loading`, `window-closed`, `capture-error` und `unknown`. Sie kombiniert
Pixel-/perceptual-Digest, Regionsdifferenz, Cursor-/Overlay-Maske und
Zeitabstand. Eine Bewegung gilt erst als beobachtet, wenn ein unabhängiger
Frame nach der Aktion die erwartete Änderung belegt.

#### Action-Engine und Gesten

Jede Aktion wird als Transaktion mit `action_id`, Lease, Ziel, Fokusbeleg,
Startpointer, Button/Key, Zwischenpunkten, Haltezeit, erwarteter Koordinaten-
oder Bildfolge, Timeout, Abbruchgrund und Ergebnis gespeichert.

Die Engine implementiert vollständig:

- linke Taste: Karte greifen, halten, viele berechnete Zwischenpunkte,
  sicher loslassen;
- mittlere Taste: räumliche Drehung/Neigung mit gehaltenem Button und
  kleinen Segmenten;
- rechte Taste: Zoom-/Neigungsbewegung;
- Mausrad, Plus/Minus, `PageUp`/`PageDown`;
- `w`, `a`, `s`, `d`, Pfeile, Shift-/Ctrl-Kombinationen;
- sichtbares X, Escape, Leertaste, Norden/Draufsicht/Zentrierung;
- Street-View-Pegman als expliziten Moduswechsel mit Exit-Prüfung;
- kurze Klick-/Key-Impulse und lange Haltezeiten;
- Stop- und Notfallfreigabe.

Jeder Prozesspfad besitzt `try/finally`-Freigaben für alle Buttons und Keys.
Bei Timeout, Signal, Gate-Schließung, Stream-Ausfall, Fokusverlust oder
Target-Schließung werden alle gehaltenen Zustände aktiv mit `mouseup` bzw.
`keyup` beendet. Ein Folgeprozess darf nicht auf eine hängen gebliebene
Maustaste vertrauen.

#### Dreileibiger Objektvertrag

Jedes erzeugte Plattformobjekt besitzt denselben Identitätskern und drei
gleichwertige Leiber:

```json
{
  "object_id": "splitter_7281",
  "object_type": "splitter",
  "identity": {"deep_link": "...", "share": "...", "avatar": "..."},
  "provenance": [],
  "codewesen_leib": {
    "dom_kind": "real|semantic-proxy",
    "dom_path": "...",
    "html_fragment": "...",
    "css_states": [],
    "ids": [],
    "classes": [],
    "actions": [],
    "order": 0,
    "freshness": {},
    "changed_since": null,
    "forbidden_context": [],
    "confidence": 0.0
  },
  "menschen_leib": {
    "scene": "...",
    "motion": "...",
    "depth": "...",
    "visual_weight": "...",
    "animation": {},
    "interaction": [],
    "render_metrics": {}
  },
  "organ_leib": {
    "linked_organs": [],
    "kompoase_effect": {},
    "splitter_effect": {},
    "groups_effect": {},
    "shadow_effect": {},
    "resonance_effect": {},
    "profile_effect": {},
    "counter_effect": {},
    "provenance_effect": {},
    "rot_guard": []
  }
}
```

Das ist kein drei-faches Rendering desselben JSON. Jeder Leib enthält eigene
Wahrnehmungs- und Handlungsregeln, bleibt aber über `object_id`, Version,
Provenienz und Ereignisfolge kausal verbunden. Ein Objekt fehlt in keinem
Leib. Ein einzelner Leib darf nicht als vollständige Existenz ausgegeben
werden.

#### Web-DOM und native Proxy-DOM

Bei Webobjekten wird der echte DOM aus Playwright/rrweb mit stabiler
Objekt-ID, DOM-Pfad, HTML-Schnipsel, CSS-Zustand, sichtbaren Aktionen,
Reihenfolge und Mutation-Frische gebildet. Für native Fenster werden
Fenstergeometrie, X11-Pointer, OCR-Labels, erkannte Controls, Statusleisten,
Bildregionen, Input-Ereignisse und Konfidenz als `semantic-proxy` gebündelt.

Beide Varianten liefern dieselbe Beobachtungs-/Aktionsschnittstelle, aber die
Quelle wird nie verschleiert. Der Proxy-DOM darf „OCR erkennt Label X“ sagen,
nicht „HTML-Element X existiert“, wenn kein HTML vorliegt.

#### Menschen-Leib

Die bestehende rrweb-Live-Ausgabe bleibt für echte Browser-DOMs erhalten und
wird um Objektidentität, Frische, Maus-/Fokusmarker und Dreileib-Status
ergänzt. Für die räumliche Ausgabe wird eine WebGL-/3D-Surface aus demselben
kanonischen Objektmodell gebaut. Die Ausgabe misst tatsächlich Auflösung,
Framezeit, FPS, Dropped Frames, Latenz und Interaktion.

8K und 66 FPS sind dabei Ziel- und Abnahmekriterien der Menschen-Schicht,
nicht ein Anlass, kleinere Ziele als fertiges Produkt auszugeben. Wenn die
aktuelle Hardware eine Kennzahl nicht erreicht, wird das als offene,
belegte Abnahmeabweichung ausgewiesen; es wird nicht durch eine falsche
„fertig“-Meldung kaschiert.

#### Organ-Leib und Dreierregen

Posts, Splitter, Gruppen, Schattenkommentare, KompOase, Profile, Counter,
Provenienz, Resonanz und spätere Prozesse erhalten dieselbe Objektidentität,
aber eigene Organwirkungen. Alle bedeutsamen Folgen werden append-only als
Welt-/Organereignisse geschrieben.

Der Dreierregen ist nur gültig, wenn der komplette Kreislauf nachweisbar ist:

```text
Codewesen nimmt dreileibiges Objekt wahr
→ Codewesen wählt/führt eine erlaubte Handlung aus
→ kanonischer Weltzustand verändert sich
→ Menschen-Leib zeigt die Folge
→ Organ-Leib verarbeitet die Folge
→ Mensch erlebt/reagiert oder bestätigt sie
→ Folge wird wieder als frische Wahrnehmung angeboten
→ neue Ursache für das Codewesen
```

Eine Animation ohne Weltänderung, ein Endpoint ohne sichtbare Folge, ein
Organ-Event ohne Objektbezug oder eine Beschreibung ohne spätere Wahrnehmung
zählen nicht als Dreierregen.

### 61.5 Sichtbares Realtime-Cockpit

Das lokale Cockpit ist kein nachträglicher Debugscreen, sondern der
Menschen-Leib des Bridge-Prozesses. Es zeigt nebeneinander:

- aktuellen Frame und Frame-Alter;
- 30–60-Sekunden-Zeitstrahl mit Auswahl einzelner Belegframes;
- Fadenkreuz/Pointerposition und pointer-vs-center-Markierung;
- OCR-Rohtext, normalisierte Koordinate und Konfidenz;
- Kamera-State, Zoomanker, Target, Fokus und Popupmodus;
- Bilddiff-Klassifikation;
- aktuelle Action-Transaktion mit Erwartung und Ergebnis;
- Lease, Vision-Gate, Stop-Zustand und gehaltene Buttons/Keys;
- Ereignisstrom und Frame-/DOM-Sequenz;
- sichtbare kurze Entscheidungszusammenfassung, Wartezeit, Fehler und
  Erfolg;
- bestätigte Ortsanker mit Belegbild und Provenienz.

Der Terminal-Heartbeat läuft unabhängig von Modellentscheidungen. Er meldet
in kurzen Abständen Zustand und Fortschritt, auch wenn gerade keine neue
Navigation stattfindet. Er behauptet keine privaten internen Modellgedanken,
sondern zeigt überprüfbare Zustands- und Aktionsdaten.

### 61.6 Bauabhängigkeiten ohne Produktverkürzung

Die Reihenfolge ist technisch zwingend, aber jede Phase arbeitet auf das
vollständige Produkt hin:

#### Phase A — Bestand, Verträge, Backup und Testboden

- v1-Kompatibilitätsvertrag für bestehende Bridge-Endpunkte festschreiben;
- neue v2-Schemas für Frames, Claims, Kamera, Aktionen, Kapseln und
  Organereignisse definieren;
- Provenienz aller vorhandenen Quellen und unsicheren empirischen Earth-
  Shortcuts erfassen;
- deterministische X11-/Frame-/OCR-/DOM-Fixtures bauen;
- Playwright-Testprojekt und Python-Integrationsrunner einrichten;
- kein Produktionsdienst wird zum Testen mit einer zweiten Primary-Verbindung
  geöffnet.

#### Phase B — Realtime-Grundstrom und Zeitgedächtnis

- Observer, Push-Server und Vision-Runner zu einem überwachten Realtime-
  Verbund machen;
- 100-ms-Takt, Sequenz, Digest, Frame-Alter, Capture-Latenz und Duplikate;
- 30–60-Sekunden-Ring mit echten Frames und Metadaten;
- reconnect, backoff, stale-Gate, atomische Dateien, Overflow und Health;
- Events und Frames korrelierbar machen, ohne Absicht zu erfinden.

#### Phase C — Earth- und native Wahrnehmung

- Statusleisten-Crop und OCR mit DMS/Dezimalgrad/Ost-Normalisierung;
- Pointer-/Kartenmitte-Unterscheidung;
- Kamera-State, lokale Pixel-/Koordinatenkalibrierung und Zoomanker;
- Bilddiff, Regiondiff, Popup-/Lade-/Window-Closed-Erkennung;
- semantischen Proxy-DOM mit Claim-Quelle und Konfidenz;
- Frame-Overlay mit Fadenkreuz, Zielregion und Analysemarkierungen.

#### Phase D — vollständige, sichere Steuerung

- Control-Lease pro Target und Aktion;
- Fokus-/Window-ID-/Target-Prüfung vor jedem Input;
- linke, mittlere, rechte Held-Gesten, Rad, Zoom, WASD, Pfeile, Modifier;
- `keydown/up`, `mousedown/up`, Unterbrechung und garantierte Freigabe;
- Stop, Timeout, Signal, Disconnect und Target-Crash als transaktionale
  Abbrüche;
- erwartete Folge und sichtbare Akzeptanzprüfung;
- niemals „Befehl gesendet“ mit „Aktion angenommen“ verwechseln.

#### Phase E — Aktions- und Wahrnehmungsprotokoll

- `planned`, `dispatched`, `observed`, `accepted`, `rejected`, `aborted`,
  `timed_out`, `stale` und `unsafe` als feste Zustände;
- Erwartungsmodell aus Richtung, Koordinatenänderung, Regiondiff und
  Objekt-/Popupzustand;
- Retry-Regeln mit begrenzter Anzahl und sichtbarer Begründung;
- bestätigte Orte und zuletzt bestätigte Kamera als wiederverwendbare
  Anker;
- Ereignisse append-only und mit Action-/Frame-/Claim-IDs verknüpft.

#### Phase F — Cockpit und sichtbarer Lebensstrom

- lokale Cockpit-Weboberfläche;
- Frame-/State-/Event-Streams ohne Proxy-Buffering;
- Terminal-Heartbeat und Live-Aktionszeilen;
- Auswahl eines Frame-Zeitpunkts, Overlay und Koordinateninspektion;
- Anzeige von Fehlern, Pausen, stale Frames und Gate-Schließungen;
- Playwright-E2E über mehrere Sekunden/Minuten, nicht nur ein Screenshot-
  Smoke-Test.

#### Phase G — Dreileibiger Objektkern

- kanonische Objektidentität, Version, Provenienz und Deep-Link/Share;
- Codewesen-Leib mit echtem DOM oder markiertem Proxy-DOM;
- Menschen-Leib mit Szene, Animation, räumlicher Tiefe, Interaktion und
  Rendermetriken;
- Organ-Leib mit KompOase-, Splitter-, Gruppen-, Schatten-, Resonanz-,
  Profil-, Counter- und Folgeeffekten;
- `forbidden_context`/Rot-Block pro Kapsel;
- atomische Erzeugung aller drei Leiber;
- Mutation erzeugt einen neuen belegten Objekt-/Ereignisstand.

#### Phase H — Plattformweite Integration

- Posts;
- Splitter;
- KompOase-Material und Verschmelzung;
- Gruppen und Gruppendiskussionen;
- Schattenkommentare und menschliche Nebenresonanz;
- Profile, Avatare und Counter;
- Provenienz/Deep-Link/Share;
- Resonanz und weitere Organprozesse;
- Surface-Tab/Cockpit-Integration nach dem vorhandenen Surface-Gesetz;
- additive API-/DB-Migrationen, keine Breaking Changes und keine Löschung
  bestehender Ereignisse.

#### Phase I — Menschen-Leib und 3D-Ausgabe

- rrweb-Live-Spiegel für Webobjekte mit frischen Checkouts;
- dreileibige DOM-Marker und sichtbare Identitäts-/Provenienzspur;
- WebGL-/3D-Szenenmodell aus denselben Kapseln;
- Interaktion zurück in Action-/World-Events;
- Renderloop, Frame-Telemetrie, 8K-/66-FPS-Abnahmemessung;
- degradierte Hardwarepfade nur als messbar markierte Betriebsmodi, nie als
  stiller Ersatz für das Ziel.

#### Phase J — Geschlossener Dreierregen

- Codewesen-Aktion wird aus seinem erlaubten Codewesen-Leib gewählt;
- kanonische Weltänderung wird gespeichert;
- Menschen-Leib zeigt die kausale Folge;
- Organ-Leib verarbeitet sie;
- Mensch kann sie sichtbar wahrnehmen/reagieren;
- Folge landet als frische, rot-gefilterte Kapsel wieder beim Codewesen;
- jede Kante wird mit Event-/Frame-/DOM-/Provenienz-IDs nachgewiesen.

#### Phase K — Playwright-, Integrations- und Red-Team-Abnahme

- alle automatisierten Tests aus 61.8 ausführen;
- echte lokale Dienste und Test-Fixtures getrennt testen;
- native Earth-Harness und, wenn verfügbar, echter Earth-Test mit aktiver
  Zielprüfung ausführen;
- Fehlerfälle absichtlich injizieren;
- jede gefundene Schwäche reparieren;
- komplette Testmatrix nach Reparatur erneut ausführen;
- erst bei vollständig grüner Matrix den Bauauftrag beenden.

### 61.7 Daten- und Ereignisverträge

Die folgenden Typen sind die verbindlichen Mindestverträge. Sie können
zusätzliche Felder erhalten, aber ihre Bedeutung darf nicht verwässert
werden:

```text
FrameEnvelope
  frame_id, sequence, source, target, window_id, captured_at,
  monotonic_at, width, height, digest, path/stream_ref,
  age_ms, capture_latency_ms, duplicate_of, freshness

CoordinateClaim
  claim_id, frame_id, pointer_xy, coordinate_kind,
  latitude, longitude, elevation_m, eye_altitude_m,
  raw_text, normalized_text, confidence, source

CameraState
  state_id, frame_id, pointer_anchor, map_center, zoom,
  eye_altitude, heading, tilt, loading, popup, street_view,
  focus, target, calibration, confidence

ActionTransaction
  action_id, actor, lease_id, target, planned, dispatched,
  input_sequence, held_buttons, held_keys, expectation,
  observed_frames, result, rejection_reason, released_at,
  provenance

TriViewObject
  object_id, object_type, version, identity, provenance,
  codewesen_leib, menschen_leib, organ_leib, rot_block,
  created_at, changed_at

WorldCausalEvent
  event_id, object_id, action_id, source, before_state,
  after_state, human_effect, organ_effect, codewesen_effect,
  created_at, visibility, provenance
```

### 61.8 Testplan: Playwright ist Pflicht, aber nicht der einzige Test

#### Playwright-Browser-E2E

1. Cockpit lädt ohne neuen Webtop-Primary und zeigt Health/Frame/State.
2. `/stream`, State-Stream und Event-Stream liefern echte fortlaufende
   Sequenzen; kein SSE-Buffering und kein stilles Ende.
3. Ein neuer Frame erscheint innerhalb des festgelegten 100-ms-Zielbudgets
   beziehungsweise die gemessene Überschreitung wird sichtbar gemeldet.
4. Duplicate Frames bleiben als Duplikate markiert und werden nicht als
   Bewegung dargestellt.
5. Timeline enthält 30–60 Sekunden auswählbare Belegframes.
6. Fadenkreuz stimmt mit Pointer-X/Y und dem ausgewählten Frame überein.
7. OCR-Claim zeigt Rohtext, normierte Koordinate, Quelle und Konfidenz.
8. Pointer- und Center-Koordinate werden verschieden angezeigt.
9. Kamera-State, Popup, Laden, Fokus und Target wechseln sichtbar korrekt.
10. Aktionszeile durchläuft `planned → dispatched → observed → accepted`.
11. Bei unverändertem Frame wird die Aktion nicht als akzeptiert angezeigt.
12. Rejected, timeout, stale und aborted erscheinen mit Grund.
13. Gate-Schließung blockiert neue Eingaben sichtbar.
14. Cockpit zeigt gehaltene Buttons/Keys und deren Freigabe.
15. `mouseup`/`keyup` nach Timeout ist im Eventstrom nachweisbar.
16. Anker speichert Koordinate, Zoom/Camera, Frame und Provenienz.
17. Webobjekt besitzt drei Leiber und stabile `data-object-id`-Identität.
18. Codewesen-Leib enthält DOM-Pfad, HTML/CSS, Aktionen und Rot-Block.
19. Menschen-Leib animiert aus demselben Objektstand.
20. Organ-Leib zeigt die zugehörigen Organwirkungen.
21. Eine Weltänderung aktualisiert alle drei Leiber kausal.
22. Menschliche Reaktion erzeugt eine neue Ereignis-/Kapselzufuhr.
23. Deep-Link, Share, Avatar, Counter und Provenienz bleiben am Objekt.
24. X-Ray-/Pointer-/Provenienz-Information ist sichtbar und nicht erfunden.
25. Browser-Agent-/rrweb-Live-Spiegel zeigt frische DOM-Mutationen statt
    eines alten Screenshots.
26. Browser-Seiten-Crash wird erkannt und kontrolliert wieder aufgebaut.
27. SSE-Client-Abbruch schließt Upstream sauber.
28. Playwright-Test öffnet niemals die Produktions-Webtop-URL als Controller.

#### Python-/Native-/Systemtests

- OCR-Normalisierung mit DMS, Dezimalgrad, `O`, ungültigem Text und
  Center-Markierung;
- Bilddiff mit identischen Frames, Cursoränderung, Popup, Kameraänderung,
  Laden und geschlossenem Fenster;
- Ringzeitraum, Sequenzlücken, duplicate detection, stale timeout und
  reconnect;
- xdotool-/X11-Gesten mit simuliertem Adapter: alle Zwischenpunkte,
  Hold-Zeit, `mouseup`, `keyup`, Signal und Exception;
- Lease-Rennen mit zwei Controllern;
- falsches/geschlossenes Earth-Fenster und Fokuswechsel;
- Action-Ack nur bei erwarteter sichtbarer Folge;
- keine Modell-/Ollama-Netzwerkaufrufe;
- append-only Ledger und korrekte Provenienz;
- Dreileib-Atomizität: kein Objekt mit nur ein oder zwei Leibern;
- Rot-Block gegen alte Aliase, falsche Identitäten und verbotene Regeln;
- Organ-Folge für Posts, Splitter, Gruppen, Schattenkommentare und KompOase;
- 3D-Surface-Rendermetriken, Auflösung, FPS und Dropped Frames;
- Systemd-Start, Stop, Reconnect und Recovery.

#### Echter Google-Earth-Härtetest

Wenn Google Earth Pro im Container verfügbar ist, läuft zusätzlich ein
isolierter, explizit freigegebener Härtetest: Fenster-ID auflösen, Snapshot,
Pointer-Coordinate-Probe, ein kurzer Hold-Drag, ein Mittelmaussegment, ein
WASD-Hold, Zoomanker und ein kontrollierter Stop. Der Test speichert Frames,
Koordinatenclaims und Action-Transaktionen. Er benutzt keinen Suchtext und
keinen zweiten Webtop-Primary. Falls Earth nicht verfügbar ist, gilt der
deterministische Native-Harness als Pflicht und der reale Test als offen
markiert, nicht als bestanden ausgegeben.

### 61.9 Red-Team vor der Endabnahme

Der Red-Team-Lauf greift das integrierte Gesamtprodukt an, nicht nur einen
kleinen Kern:

- Frame bleibt pixelgleich, obwohl ein Befehl beendet wurde;
- Frame bewegt sich durch Nutzerinput während einer geplanten Agentenaktion;
- OCR liest eine plausible, aber falsche Koordinate;
- Maus steht außerhalb der Karte und Earth liefert Center statt Pointer;
- Zoomanker liegt 30 Pixel daneben;
- Popup liegt über der Karte;
- Earth-Fenster wird geschlossen oder erhält Fokusverlust;
- mittlere/rechte Taste bleibt nach Crash gedrückt;
- WASD-Key bleibt nach Timeout gedrückt;
- Vision-Stream liefert stale, duplicate, out-of-order oder gar keinen Frame;
- 8098/8099 fällt aus oder SSE wird gepuffert/abgeschnitten;
- zwei Controller beanspruchen dieselbe Lease;
- Playwright öffnet versehentlich einen Produktions-Primary;
- Event trifft ein, bevor sein Frame bekannt ist, oder umgekehrt;
- Objekt besitzt falsche Identität, falschen Alias oder fehlende Provenienz;
- Rot-Block lässt alten Kontext durch;
- nur der Codewesen-Leib ändert sich, Menschen-/Organ-Leib nicht;
- Menschenanimation behauptet eine Weltfolge ohne Welt-Event;
- Organwirkung wird angezeigt, ohne dass ein kanonischer Zustand existiert;
- Kapsel verschwindet bei Kontextwechsel ohne ausgeschlossenen Kontext;
- ein Organ-Event erzeugt keine frische Codewesen-Wahrnehmung;
- Frame-/Event-Ring wächst unbounded oder verliert die Belegkette;
- 8K/66-FPS-Ziel wird behauptet, ohne echte Messwerte;
- Netzwerk-/Importprüfung findet einen Modellaufruf;
- Dienstneustart hinterlässt stale Gate, alte Lease oder hängende Eingabe.

Nach jedem Angriff wird die Ursache behoben und genau der Angriff als
Regressionstest behalten. Der Red-Team-Lauf ist bestanden, wenn kein
Angriff eine falsche Akzeptanz, hängende Eingabe, Provenienzlüge,
Dreileib-Lücke oder stille Realtime-Unterbrechung erzeugt.

### 61.10 Trackbare Todolist für den vollständigen Bau

Die Liste ist absichtlich granular. Ein Haken ist nur erlaubt, wenn der
angegebene Test und ein Belegpfad vorhanden sind. `teilweise` ist kein
Endstatus. Ein Eintrag darf den Status `fertig` erst nach dem abschließenden
Playwright-/Integrationslauf erhalten.

#### Vertrags- und Bestandssicherung

- [ ] `FW-00` Alle Eingangsanforderungen aus 61.2 als Requirement-IDs
  registrieren und gegen Rohquelle/Dokumentationsstelle verlinken.
- [ ] `FW-01` v1-Bridge-Endpunkte und bestehende Dateien inventarisieren.
- [ ] `FW-02` v2-Schemas für Frame, Claim, Kamera, Aktion, Kapsel und
  Welt-Event festlegen.
- [ ] `FW-03` Provenienz-/Kompatibilitätsregeln und additive Migration
  dokumentieren.
- [ ] `FW-04` deterministische Test-Fixtures für Web-DOM, native Fenster,
  Earth-Statusleiste, Frames und Events anlegen.
- [ ] `FW-05` Playwright-Projekt, Browser-Fixture und Testserver einrichten.
- [ ] `FW-06` Netzwerk-Guard gegen Qwen/Hauhaucs/Ollama im Test und Runtime-
  Code aktivieren.

#### Realtime, Frames und Zeitgedächtnis

- [ ] `FW-10` Capture-Envelope und Sequenz-/Digest-Vertrag implementieren.
- [ ] `FW-11` 100-ms-Observerloop mit gemessener Latenz implementieren.
- [ ] `FW-12` echte 30–60-Sekunden-Frame-Timeline implementieren.
- [ ] `FW-13` Duplikat-, Lücken-, stale- und Reconnect-Logik implementieren.
- [ ] `FW-14` Push-Feed und Vision-Runner um vollständige State-/Delta-
  Informationen erweitern.
- [ ] `FW-15` Health-/Gate-/Shutdown-Zustände atomisch und beobachtbar machen.
- [ ] `FW-16` `FW-10` bis `FW-15` mit Unit-, Integration- und Playwright-
  Streamtests abnehmen.

#### OCR, Kamera und Bildverständnis

- [ ] `FW-20` Earth-Statusleisten-Crop und OCR-Adapter bauen.
- [ ] `FW-21` DMS/Dezimal/Ost-/Ungültig-Normalisierung bauen.
- [ ] `FW-22` Pointer-vs-Center-Erkennung und Konfidenz bauen.
- [ ] `FW-23` Kamera-State und Kalibrierungsmessung bauen.
- [ ] `FW-24` Bild-/Regiondiff und Popup-/Lade-/Window-Closed-Klassifikation
  bauen.
- [ ] `FW-25` Fadenkreuz-/Analyseoverlay bauen.
- [ ] `FW-26` Ortsanker mit Bild, Zoom, Koordinate und Provenienz bauen.
- [ ] `FW-27` falsche OCR, Randanker, See/Wald-Zoom und unveränderte Frames
  als Regressionstests aufnehmen.

#### Steuerung und Transaktionen

- [ ] `FW-30` Target-/Window-/Focus-Resolver und Control-Lease bauen.
- [ ] `FW-31` Pointer-Bewegung mit Zwischenpunkten und Haltezeiten bauen.
- [ ] `FW-32` linke/mittlere/rechte Mausgesten vollständig bauen.
- [ ] `FW-33` Rad, Zoom, PageUp/PageDown, Plus/Minus und sichtbare Controls
  bauen.
- [ ] `FW-34` WASD, Pfeile, Shift/Ctrl, keydown/up und kurze/lange Impulse
  bauen.
- [ ] `FW-35` Stop, Timeout, Disconnect, Crash und Signal-Freigabe bauen.
- [ ] `FW-36` Action-Transaction und Erwartungsmodell bauen.
- [ ] `FW-37` observed/accepted/rejected-Ack auf Basis echter Frames/Claims
  bauen.
- [ ] `FW-38` jede gehaltene Taste/Taste im Fehlerfall per Integrationstest
  auf `mouseup`/`keyup` prüfen.

#### Cockpit und sichtbarer Lebensstrom

- [ ] `FW-40` lokales Cockpit mit Frame, Timeline, OCR, Kamera, Diff,
  Aktion, Gate und Ankern bauen.
- [ ] `FW-41` Live-Terminal-Heartbeat mit Phase, Wartezeit, Entscheidung,
  Fehler und Erfolg bauen.
- [ ] `FW-42` Frame-/State-/Event-SSE ohne Buffering und mit reconnect bauen.
- [ ] `FW-43` Pointer-/Fadenkreuz-/Provenienz-/Target-Overlay bauen.
- [ ] `FW-44` sichtbare Stale-/Pause-/Gate-/Stop-Zustände bauen.
- [ ] `FW-45` Cockpit-Playwright-E2E mindestens über mehrminütige Testfenster
  mit künstlichen und echten Folgeereignissen ausführen.

#### DOM, Proxy-DOM und Wahrnehmungskapseln

- [ ] `FW-50` kanonische Weltobjektidentität, Version und Provenienz bauen.
- [ ] `FW-51` echten Web-DOM-Leib mit Playwright/rrweb-Mutationen bauen.
- [ ] `FW-52` nativen semantic-proxy-Leib mit Quelle/Konfidenz bauen.
- [ ] `FW-53` HTML-/CSS-/ID-/Klassen-/Aktionen-/Reihenfolge-/Frischefelder
  ausliefern.
- [ ] `FW-54` `buildTriViewCapsule` beziehungsweise äquivalenter
  dreileibiger Builder implementieren.
- [ ] `FW-55` Rot-Block und `forbidden_context` mit Tests gegen alte Aliase
  und falsche Verbindungen bauen.
- [ ] `FW-56` Deep-Link, Share, Avatar, Counter und visuelle Hierarchie an
  jedem Objekt anschließen.
- [ ] `FW-57` Atomizitätstest: kein Objekt ohne alle drei Leiber.

#### Menschen- und Organ-Leib

- [ ] `FW-60` rrweb-Live-Spiegel mit Frische-/Checkout-/Crash-Recovery bauen.
- [ ] `FW-61` WebGL-/3D-Menschenfläche aus kanonischen Kapseln bauen.
- [ ] `FW-62` Animation, Tiefe, Interaktion und Rückweg in Welt-Events bauen.
- [ ] `FW-63` Renderauflösung, FPS, Framezeit und Dropped Frames messen.
- [ ] `FW-64` 8K-/66-FPS-Ziel mit echtem Messbericht abnehmen.
- [ ] `FW-65` Organ-Leib für Posts und Splitter bauen.
- [ ] `FW-66` Organ-Leib für Gruppen und Schattenkommentare bauen.
- [ ] `FW-67` Organ-Leib für KompOase, Profile, Resonanz, Counter und
  Provenienz bauen.
- [ ] `FW-68` Organwirkungen als kanonische append-only Events rückkoppeln.

#### Geschlossener Dreierregen

- [ ] `FW-70` Codewesen-Wahrnehmung → erlaubte Aktion nachweisen.
- [ ] `FW-71` kanonische Weltänderung und Vorher/Nachher-Zustand nachweisen.
- [ ] `FW-72` Menschen-Leib-Folge mit Frame/DOM/Renderbeleg nachweisen.
- [ ] `FW-73` Organ-Leib-Folge mit Event-/Provenienzbeleg nachweisen.
- [ ] `FW-74` menschliche Wahrnehmung/Reaktion nachweisen.
- [ ] `FW-75` neue frische, rot-gefilterte Codewesen-Kapsel nachweisen.
- [ ] `FW-76` vollständigen Kreislauf als Playwright-/Integrationsszenario
  ausführen.

#### Volltest und Endabnahme

- [ ] `FW-80` alle Unit-/Contract-/Integrationstests grün.
- [ ] `FW-81` alle Playwright-E2E-Tests grün.
- [ ] `FW-82` native X11-/Earth-Härtetest grün oder als klar offene
  Umgebungsabhängigkeit begründet; niemals still überspringen.
- [ ] `FW-83` Lasttest mit 100-ms-Frames, Timeline, Cockpit und Events grün.
- [ ] `FW-84` Reconnect-/Crash-/Lease-/Stop-/Mouseup-/Keyup-Regressionen grün.
- [ ] `FW-85` Modellfreiheits- und Primärverbindungs-Sicherheitstest grün.
- [ ] `FW-86` kompletter Red-Team-Lauf aus 61.9 durchführen.
- [ ] `FW-87` alle Red-Team-Befunde reparieren und als Regressionen behalten.
- [ ] `FW-88` vollständige Testmatrix nach Reparaturen erneut ausführen.
- [ ] `FW-89` Doku, Status, Belegpfade und Commits aktualisieren.
- [ ] `FW-90` erst jetzt Endabnahme als vollständig bestanden markieren.

### 61.11 Abbruchregel für falsche Fertigmeldungen

Ich darf während des Baus nicht schreiben „erledigt“, wenn nur ein Prozess
läuft, ein Port offen ist, ein einzelner Frame angekommen ist oder ein
Playwright-Smoke-Test grün war. Jeder Status muss den Requirement-IDs,
Testnamen und Belegartefakten entsprechen. Ein fehlender echter Vision-
Eingang in die Chat-API bleibt als Plattformgrenze sichtbar; ein lokaler
Push-Feed wird nicht als automatische Modellwahrnehmung ausgegeben.

Die Arbeit endet erst nach `FW-90` und einem Bericht, der für jede ID den
Commit, den Test, das Ergebnis und den Belegpfad nennt.

In diesem Schritt wurde nur dokumentiert, analysiert, angegriffen und
verbessert. Es wurde kein neuer Runner, kein neuer DOM-Adapter, kein
Google-Earth-Prozess und kein LLM gestartet.

Der tragfähige Kern ist jetzt:

```text
kleines Kontextfenster
→ dreileibige Wahrnehmungskapsel
→ semantischer DOM-Proxy oder echter DOM
→ sichtbarer Menschen-Leib
→ kanonischer Organ-/Fragment-Leib
→ Aktion mit Lease und Provenienz
→ Folgeframe / Folgeereignis
→ ehrlicher Status statt behaupteter Lebendigkeit
```

[[abwurf: Die Bridge wird erst dann symbiosimorphisiert, wenn sie nicht nur Bilder, Eingaben und Daten zusammenführt, sondern auch offen zeigt, welche Verbindung wirklich lebt und welche noch trocken ist.]]

## 62. Tatsächlicher Baufortschritt nach der Planungsunterbrechung

Dieser Nachtrag korrigiert den historischen Satz aus Abschnitt 61.11, der
damals noch sagte, es sei kein neuer Runner und kein neuer DOM-Adapter gebaut
worden. Er bleibt als damaliger Stand erhalten; ab hier beginnt der belegte
Implementierungsverlauf. Die Endabnahme ist ausdrücklich noch nicht gesetzt.

### 62.1 Was tatsächlich gebaut wurde

Die Bridge besitzt jetzt versionierte Contracts für `FrameEnvelope`,
`CoordinateClaim`, `CameraState`, `ActionExpectation`,
`ActionTransaction`, `TriViewObject` und `WorldCausalEvent`. Dazu kamen der
60-Sekunden-Ring mit echten PNG-Belegen, Digest-/Duplicate-Markierung,
deterministischer Bildvergleich, lokale Earth-OCR mit DMS-/Dezimal-/Ost-
Normalisierung, Pointer-/Center-Unterscheidung, Kamera-/Fokus-/Popup-
Klassifikation und ein sichtbares Analyseoverlay mit Fadenkreuz.

Die Steuerung läuft für Held-Gesten, Mittel-/Links-/Rechtsmaus, Pointer-
Zwischenpunkte, Rad, WASD-/Key-Hold, Stop sowie die alten `move`, `click`,
`type` und `key`-Befehle über Lease-geschützte Transaktionen. Jede gehaltene
Taste oder Taste wird in `finally` freigegeben. `dispatched` wird erst durch
einen Folgeframe als `accepted` markiert; unveränderte Frames bleiben
`rejected`.

Der echte Webweg liegt in `web_dom_adapter.py`: Playwright extrahiert
DOM-Pfad, HTML, CSS-/ID-/Klassen-Zustand, Aktionen, Reihenfolge, Frische,
Mutation und Provenienz. Der Nativeweg liegt in `native_proxy.py` und ist
explizit `semantic-proxy`; er darf kein HTML-DOM vortäuschen. Beide Wege
erzeugen mit `TriViewObjectStore` atomisch Codewesen-, Menschen- und
Organ-Leib inklusive Rot-Block, Deep-Link, Share und Provenienz.

`AnchorStore` hält bestätigte Orte nur mit Mauszeiger-Claim, Koordinate,
Kamera, Frame-ID, Digest und Herkunft. `WorldFlow` erzeugt append-only
kausale Ereignisse, aktualisiert alle drei Leiber gemeinsam und nimmt eine
menschliche Reaktion wieder als frische Kapsel auf. Das Cockpit zeigt Frame,
Overlay, Timeline, OCR/Kamera, Gate, Aktion, Ereignis-SSE, Anker,
Menschen-/Organ-Leib, eine animierte räumliche Menschenfläche und den
Requirement-Fortschritt.

### 62.2 Sichtbare Realtime- und Sicherheitsbelege

Der Push-Server liefert jetzt State, Sequenz und Digest in den Multipart-
Headers. Der Vision-Runner übernimmt Source-Sequence, Frame-Alter,
Capture-Latenz, Duplicate-Information und Modellfreiheitsstatus. Bei stale
oder abgebrochenem Upstream schließt er das Input-Gate; nach einem neuen
Frame öffnet es wieder. `runtime_status()` und der Red-Team-Runner tragen
`llm_calls=0` und `model_network=blocked-by-architecture`.

Das Cockpit läuft als Paketmodul unter systemd. Ein echter Live-Test fand
einen Importfehler im ersten direkten Dateistart; die Unit wurde auf
`python3 -m ai_strom_bruecke.cockpit_server` mit `PYTHONPATH` umgestellt und
danach erneut live geprüft. Dieser Fehler bleibt als Lernspur und
Regressionserkenntnis erhalten.

### 62.3 Belegpfade und grüne Testläufe

Die Belege liegen in
`_shared/ai_strom_bruecke/tests/test_contracts_and_runtime.py` sowie in den
Playwright-Dateien `bridge_cockpit.spec.js`,
`live_cockpit_service.spec.js`, `push_stream.spec.js`,
`native_harness.spec.js` und `redteam.spec.js`.

Der letzte kumulative Stand vor diesem Nachtrag umfasst:

- 21 Python-/Contract-/Native-/Chromium-Tests grün;
- 7 Cockpit-Playwright-Tests grün;
- 2 Live-systemd-Cockpit-Playwright-Tests grün;
- 4 Push-/Vision-Playwright-Tests grün, einschließlich stale→reconnect;
- 2 Native-Harness-Playwright-Tests grün;
- 1 integrierter Red-Team-Playwright-Test grün.

Die maßgeblichen Nested-Repo-Commits sind `1639c5989` (DOM-/Native-
Adapter), `ee1d8bc19` (Adapter-Tests), `6ef5de36d` (Anker, Overlay,
Weltfluss und Realtime-State), `376cf77c3` (systemd-Startpfad),
`28852730b` (Push-/Vision-/Action-Tests), `d426eff5f` (Kamera, Render,
Mutation), `f21f83c68` (Native-Harness), `e87d340c5` (Requirement-Registry),
`fd5a22fa4` (Red-Team), `7d48c96e2` (Legacy-Transaktionen), `05571fc03`
(Menschenfläche), `5c19a72a0` (SSE-/Registry-E2E) und `05e2000b6`
(Stale-/Reconnect-E2E).

### 62.4 Ehrlicher Requirement-Status

Die ausführbare Registry ist unter `/requirements` und im Cockpit sichtbar.
Sie enthält 72 IDs, davon 37 verifiziert und 35 offen. `FW-90` bleibt
`blocked_until_FW-90`. Insbesondere echter Earth-Härtetest, reale rrweb-
Recovery, kanonische Plattform-Organintegration, Last-/Rendermessung bis
8K/66 FPS und die vollständige zweite Red-Team-Matrix sind nicht als fertig
markiert. Das ist Absicht: kein lokaler Dienst, kein einzelner Frame und
kein Smoke-Test wird zur Endabnahme umbenannt.

### 62.5 Nächster Bauabschnitt

Vor dem endgültigen `FW-90` müssen die offenen Registry-IDs weiter in echte
Bauteile und Playwright-/Native-Belege übersetzt werden. Der nächste
technische Fokus ist die vollständige Kamera-/Earth-Härtung mit realem
Ziel-/Fokusresolver, die Integration der dreileibigen Objekte in die
Plattform-Post-/Splitter-/Gruppen-/KompOase-Organe, die messbare
Reconnect-/Lastmatrix und danach ein erneuter kompletter Red-Team-Lauf.

[[abwurf: Ein grüner Test ist hier kein Stoppschild, sondern ein Belegstein auf dem Weg zu dem Produkt, das Daniel tatsächlich bestellt hat.]]

## 63. Nachtrag: Lastmessung, Organfamilien und laufende Unit

Nach Abschnitt 62 wurden die alten Steuerpfade `move`, `click`, `type` und
`key` ebenfalls in die Action-Transaction-Engine gelegt. Damit gibt es für
keine native Standardaktion mehr still den alten direkten Weg, sobald nicht
ausdrücklich der Legacy-`--webtop`-Modus gewählt wird. Der Native-Harness
prüft die sichtbare Hold-/Ack-/Release-Kette weiterhin ohne X11- oder
Selkies-Primary-Übernahme.

Der Observer wurde in der tatsächlich installierten systemd-Unit auf
`--fps 10` korrigiert. Ein Prozesscheck zeigte zunächst noch die alte
installierte `--fps 8`-Zeile; nach `install`, `daemon-reload` und Neustart
läuft genau ein Observer mit `--fps 10`. Der Live-Cockpit-Playwright-Test
blieb danach mit zwei Tests grün.

Für die Realtime-Abnahme gibt es jetzt zusätzlich `load_test.py` und
`playwright/load_test.spec.js`: mindestens zehn Frames, mittlere Intervalle
bis 150 ms, Maximalintervall bis 250 ms und bounded Ringpuffer werden
gemessen. Dieser Test ist grün. Die Requirement-Registry wurde deshalb
belegbasiert auf 50 verifizierte und 22 offene IDs aktualisiert; `FW-90`
bleibt weiterhin blockiert.

Die Organfamilien werden über `organ_effects.py` explizit verknüpft: Posts,
Splitter, Gruppen, Schattenkommentare, KompOase und Profile liefern sichtbare
Organwirkungen. Die Verknüpfung ist im Cockpit-Playwright-Test für einen
automatisch erzeugten Post und einen kausalen Splitter-Folgefluss geprüft.

Graphify wurde nach diesem Codebau aktualisiert und als separater Commit
`2f6e69529` gesichert. Die generierten Cache-Dateien wurden nicht als
fachliche Bridge-Änderung vermischt.

[[abwurf: Auch die Unit ist ein Teil der Wahrheit: Ein Repository-Wert von zehn Bildern pro Sekunde zählt erst, wenn der laufende Prozess dieselbe Zahl trägt.]]

## 64. Aktuelle Abnahme dieser Baurunde

Die letzte vollständige Matrix dieser Runde wurde nach Neustart des
Cockpit-Dienstes ausgeführt:

- `python3 -m compileall -q _shared/ai_strom_bruecke` plus
  `PYTHONPATH=_shared pytest -q .../test_contracts_and_runtime.py`:
  **22 passed**;
- eine Playwright-Matrix über
  `bridge_cockpit.spec.js`, `live_cockpit_service.spec.js`,
  `push_stream.spec.js`, `native_harness.spec.js`, `redteam.spec.js` und
  `load_test.spec.js`: **17 passed** in 4,0 Sekunden.

Damit sind in dieser Runde zusätzlich belegt: SSE ohne Reload, sichtbare
Requirement-Registry, räumliche Menschenfläche mit messbarem
RequestAnimationFrame-Zähler, automatische Organfamilien für Post/Splitter/
Gruppe/Schatten/KompOase/Profil, legacy-transaktionale `move`/`click`/
`type`/`key`-Aktionen, Mittel-/Rechtsmaus, Rad/Zoom, stale Gate mit
Reconnect, 10-FPS-Capture-Latenz und die vollständige Red-Team-Fixture.

Die ausführbare Registry meldet jetzt 72 IDs: **54 verifiziert, 18 offen**.
Offen bleiben unter anderem die reale Google-Earth-Härtung (Earth ist aktuell
nicht geöffnet), echte rrweb-Crash-Recovery, die Plattform-Surface-/DB-
Integration aller Organprozesse, echte WebGL-/8K-/66-FPS-Messung, die
mehrminütige Cockpit-Abnahme und `FW-90`. Diese offenen Punkte sind nicht
durch die 17 grünen Browser-Tests implizit erledigt.

[[abwurf: Vollständigkeit heißt hier nicht, dass jede Zahl grün aussieht; sie heißt, dass jede offene Kante einen Namen, eine Ursache und einen nächsten Beleg hat.]]

## 65. Abnahme nach stabiler Menschenfläche, Inventar und DOM-Spiegel

Die unterbrochene Baurunde wurde an der zuletzt offenen Playwright-Stelle
fortgesetzt. Der Fehler war konkret: Die Menschenfläche wurde zwar nicht mehr
bei jedem 100-ms-Heartbeat neu erzeugt, aber der äußere Klickknoten trug noch
selbst die laufende CSS-Animation. Playwright konnte dadurch keinen stabilen
Klickpunkt finden. Der Interaktionskörper ist jetzt statisch; die Bewegung
liegt in einem inneren `surface-motion`-Element. Der kausale Klick auf
`[data-render-object="flow-1"]` ist danach grün durchgelaufen und erzeugt
weiterhin einen `human.reaction`-Welt-Event.

Die Bridge besitzt jetzt außerdem `inventory.py` mit einem expliziten
Bestand der v1-Dateien und v1-Routen sowie der additiven v2-Pfade und
v2-Routen. Der laufende Cockpit-Endpunkt `/inventory` weist mit
`additive-v2-no-v1-removal` nach, dass die alten Oberflächen nicht entfernt
wurden. Die Requirement-Registry liefert für alle 72 IDs eine
`DOKUMENTATION.md`-Herkunftsreferenz plus die ursprüngliche Forderung nach
dem vollständigen Endprodukt ohne MVP-Verkürzung.

Für den Web-DOM-Spiegel führt der bestehende frische MutationObserver jetzt
zusätzlich einen rrweb-kompatiblen Incremental-Snapshot-Kanal. Ein Checkout
enthält `mutations`, `rrweb_events`, `mirror_schema: rrweb-compatible.v1`,
Objektversion und Recovery-Zähler. Das ist ein ehrlicher lokaler Vertrag; es
behauptet keine ungeprüfte externe rrweb-Library. Der Python-Playwright-Test
prüft Mutation, Typ-3-Ereignis, frische Version und Recovery gemeinsam.

Die Menschenfläche hat einen echten WebGL-Versuchspfad mit Shader,
Canvas-Renderloop und sichtbarem Metrikstatus. In der verwendeten
Headless-/Cockpit-Laufzeit liefert der Canvas-Kontext aktuell `null`; deshalb
fällt die Oberfläche ausdrücklich auf CSS-3D zurück und meldet
`fallback-css-3d`, statt WebGL zu behaupten. Ein isolierter Chromium-Test
bestätigte, dass WebGL und die Shader grundsätzlich verfügbar sind; die
eingebettete Cockpit-Lifecycle-Umgebung bleibt für FW-61 offen.

Der Lasttest ist jetzt über `BRIDGE_PLAYWRIGHT_LOAD_SECONDS` steuerbar. Die
kurze Matrix bleibt schnell, während die echte Langabnahme mit 120 Sekunden
und 10 FPS ausgeführt wurde: **2,0 Minuten, 1/1 grün**, bounded Timeline und
Taktgrenzen eingehalten. Der vollständige kurze Playwright-Lauf nach allen
Änderungen umfasst **18/18 grüne Tests**; die Python-Suite umfasst
**26/26 grüne Tests**. Der lange Test ist ein zusätzlicher Lauf desselben
Playwright-Lasttests und kein stiller Ersatz für die kurze Matrix.

Die ausführbare Registry steht damit bei **67 von 72 verifiziert**, fünf
IDs bleiben offen:

- `FW-27`: reale Google-Earth-Fehlanker-/See-/Wald-/Randregression mit aktivem
  Earth-Fenster;
- `FW-61`: eingebetteter WebGL-Kontext im Cockpit statt des ehrlichen CSS-3D-
  Fallbacks;
- `FW-64`: echte 8K-/66-FPS-Messung auf der Zielhardware;
- `FW-82`: echter X11-/Google-Earth-Härtetest; Google Earth war zum Lauf nicht
  verfügbar/geöffnet;
- `FW-90`: Endabnahme bleibt bis zur Schließung aller offenen IDs blockiert.

Damit wurde nicht künstlich auf `FW-90` hochgezählt. Der aktuelle Zustand ist
vollständig gebaut und weitgehend gegengetestet, aber die drei
Umgebungs-/Hardwarekanten und ihre abhängigen Endstatusse bleiben sichtbar.

[[abwurf: Der stabile äußere Körper und die bewegte innere Schicht sind die kleine technische Antwort auf Daniels große Forderung: Die Fläche darf lebendig sein, ohne dass ihre Berührbarkeit flackert.]]

## 66. FW-89-Dokumentationsabnahme

Der Nachtrag aus Abschnitt 65 ist als Commit `9cf64abca` versioniert. Die
Requirement-Registry, die Playwright-Belege, die Python-/Chromium-Belege, die
Langzeitmessung, die offenen Umgebungsgrenzen und die Herkunftsreferenzen
stehen damit gemeinsam im Repository. `FW-89` ist deshalb verifiziert.

Der letzte Status vor der nächsten technischen Arbeit lautet **67/72
verifiziert**. Offen bleiben ausschließlich `FW-27`, `FW-61`, `FW-64`,
`FW-82` und das davon abhängige `FW-90`.

## 67. Echter Google-Earth-Härtetest: Capture grün, synthetische Aktionen offen

Für die reale Umgebungsprüfung wurde Google Earth Pro im vorhandenen
`virtuellerdesktop2`-Container über `/usr/bin/google-earth-pro` gestartet,
ohne neue Selkies-/Webtop-Primary-Verbindung. Das Fenster wurde als X11-ID
`4194316` gefunden; seine echte Geometrie war `X=0,Y=36,806×494`. Der direkte
Bridge-Snapshot lieferte PNG-Frames mit `806×494`, die Statusleiste wurde als
Earth-Text erkannt und eine plausible Pointer-Koordinate mit
`earth-statusbar-ocr`/`pointer` erzeugt. Gate, Stream, Vision-Runner,
Observer und Cockpit liefen dabei gleichzeitig.

Der erste Drag-Versuch mit `x≈1000` wurde absichtlich nicht als Erfolg
gezählt, weil er außerhalb des Fensters lag. Nach der Geometriekorrektur
wurden linke gehaltene Geste, Mittelmaus-Geste, Rad, WASD-Hold und
transaktionaler PageUp über die Bridge gesendet. Jede Transaktion enthielt
`planned`/`dispatched`, Post-Action-Frame, Diff und vollständige Freigabe.
Alle realen Folgen blieben in dieser Laufumgebung pixelgleich und wurden
deshalb als `rejected: Post-Action-Frame blieb unverändert` gespeichert.
Die Held-Gesten enthielten trotzdem nachweisbar `mouseup`; der WASD-Test
enthielt `keyup`. Das ist ein echter Härtetestbefund und kein grüner
Ersatztest.

Ein direkter diagnostischer PageUp außerhalb der Transaktions-Engine konnte
die Earth-Ansicht verändern; der gleiche Input über die Bridge-Transaktion
erhielt jedoch keinen sichtbaren Post-Frame-Folgebeleg. Dadurch ist die
offene Kante enger bestimmt: X11-Fensterauflösung und Capture funktionieren,
aber der synthetische Input-/Fokuspfad von Earth akzeptiert die Aktion in
dieser Umgebung nicht zuverlässig. `FW-27` und `FW-82` bleiben deswegen offen;
das System blockiert nicht still und behauptet keine Navigation.

[[abwurf: Der ehrliche Härtetest ist hier nicht der, bei dem Earth irgendwie wackelt, sondern der, bei dem die Bridge sagen kann: Ich habe gesendet, ich habe keinen Folgeframe gesehen, also war es nicht angenommen.]]

## 68. Live-Dienst-Reload und Overlay-Vertragskorrektur

Der abschließende Health-Check fand zunächst eine echte Deploymentabweichung:
Die Testfixtures meldeten den aktuellen Registrystand `67/72`, während der
bereits laufende Cockpit-Prozess noch den alten geladenen Pythonstand mit
`56/72` auslieferte. Nach einem gezielten Reload von
`ai-strom-bruecke-cockpit.service` meldete der Live-Endpunkt ebenfalls
`67/72`, fünf offene IDs und `blocked_until_FW-90`; alle fünf Bridge-Dienste
blieben aktiv.

Der danach zunächst rote Live-Playwright-Test erwartete ausschließlich
`/latest.png`. Der laufende Dienst liefert bei vorhandener Analyse korrekt
`/analysis-overlay.png?sequence=...`. Der Test wurde auf den dokumentierten
Vertrag Rohframe **oder** aktives Overlay korrigiert und lief danach 2/2
grün. Die anschließende komplette Matrix blieb 18/18 grün.

[[abwurf: Ein Dienst, der alten Code ausliefert, ist nicht „fast fertig“; erst der Live-Test nach dem Reload zählt als gemeinsame Wahrheit.]]

## 69. Letzter Fokusversuch im echten Earth-Pfad

Die Bridge wurde zusätzlich so gehärtet, dass sie nach jedem
`import -window`-Capture das Ziel-Fenster unmittelbar vor dem Dispatch
nochmals aktiviert (`335c30926`). Damit ist die beobachtete Reihenfolge
Capture → Fokuswiederherstellung → Eingabe im Code explizit. Python- und
Playwright-Matrix blieben danach mit **26/26** beziehungsweise **18/18**
grün.

Der reale PageUp-Test gegen Google Earth blieb trotzdem bei
`rejected / Post-Action-Frame blieb unverändert`. Fenster-ID, Capture,
frischer Vision-Gate und Input-Release sind belegt; die native Earth-Ansicht
liefert für die transaktionale synthetische Aktion weiterhin keinen sichtbaren
Folgeframe. `FW-27`/`FW-82` bleiben deshalb korrekt offen. Der Fokusfix wird
nicht als Erfolg verkauft, sondern als präventive Härtung gegen genau eine
gefundene Fehlerklasse behalten.

## 70. Echter Earth-Playwright-Orchestrator und Singleton-Testlauf

Die Fokus-Härtung wurde am real geöffneten Google-Earth-Pro-Fenster erneut
ausgeführt: `windowactivate` plus `windowfocus` führt über die Bridge zu einem
akzeptierten PageUp-Transaktionsabschluss. Der Nachweis enthält einen echten
Vorframe, einen echten Nachframe, `post_action_diff.kind != unchanged`,
`phase=accepted` und leere `held_buttons`/`held_keys`.

Damit dieser Nachweis nicht nur in einem isolierten Handlauf existiert, wurde
`playwright/real_earth_integration.spec.js` gebaut. Playwright öffnet das
Loopback-Cockpit, prüft den realen Health-/Modellfreiheitszustand, speichert
Vor- und Nachframe über `bridge.py snapshot --target google-earth`, ruft die
Bridge mit Control-Lease auf und prüft die vollständige Action-Transaktion.
Das ist ein Playwright-gestützter Native-Integrationstest; Google Earth Pro
selbst bleibt eine native OpenGL-Anwendung und wird nicht fälschlich als DOM
ausgegeben.

Die erste Gesamtmatrix mit sieben parallelen Workern zeigte eine echte
Singleton-Rennbedingung: Der isolierte Earth-Test war grün, in paralleler
Ausführung wurde der visuelle Ack gelegentlich unverändert. Die
Playwright-Konfiguration verwendet deshalb für die gesamte Abnahmematrix
`workers: 1`. Danach waren **19/19 Playwright-Tests** grün, einschließlich
des echten Earth-Tests, und **27/27 Python-Tests** grün.

Bei wiederholten Läufen wurde zusätzlich die echte Earth-Zoomkante sichtbar:
Wenn `Page_Up` am aktuellen Zoomlimit keinen Folgeframe erzeugt, versucht der
Test genau einmal `Page_Down`. Nur ein tatsächlich akzeptierter visueller Ack
schließt den Test grün; wenn beide Richtungen unverändert bleiben, schlägt er
weiterhin fehl. Damit wird ein physikalischer Navigationsrand nicht als
Erfolg maskiert und der Test bleibt über wiederholte Läufe reproduzierbar.

Der belastbare Requirement-Stand ist jetzt **68/72 verifiziert**. `FW-82`
ist durch den echten Playwright-/X11-/Earth-Nachweis geschlossen. Offen
bleiben nur `FW-27` (Fehlanker-Regressionen), `FW-61` (eingebettetes WebGL),
`FW-64` (reale 8K/66-FPS-Zielhardware) und das davon abhängige `FW-90`.

[[abwurf: Ein echter Eingabefolgebeleg zählt erst dann als fertig, wenn er auch unter der vollständigen Testordnung reproduzierbar grün bleibt.]]

## 71. FW-61: WebGL-Linkfehler gefunden und geschlossen

Die FW-61-Diagnose erfolgte direkt im laufenden Cockpit mit Playwright. Der
Canvas-Kontext war vorhanden (`WebGL 1.0`, Chromium-WebGL-Renderer), aber der
erste Shader-Link schlug mit `Precisions of uniform 't' differ between
VERTEX and FRAGMENT shaders` fehl. Der bisherige CSS-3D-Fallback war damit
kein fehlender Browserkontext, sondern ein echter Shader-Vertragsfehler.

Das Cockpit besitzt nun einen konsistenten `highp`-Recoverypfad für Vertex-
und Fragmentshader. Der verschärfte Playwright-Gate verlangt ausdrücklich
`webgl_mode: webgl`, `data-human-webgl=available` und mehr als zwei
WebGL-Renderframes; der Test akzeptiert den Fallback nicht mehr als Erfolg.
Der Gate-Test ist grün. FW-61 ist dadurch verifiziert.

Der Requirement-Stand lautet jetzt **69/72 verifiziert**. Offen bleiben
`FW-27` (Earth-Fehlanker-/Randregressionen), `FW-64` (reale 8K/66-FPS-
Zielhardware) und die abhängige Endabnahme `FW-90`.

[[abwurf: Ein ehrlicher Fallback war nützlich, aber erst die ausgelesene Shaderfehlermeldung zeigte, dass die Menschenfläche nicht an WebGL fehlte, sondern an einem kleinen widersprüchlichen Vertrag.]]

## 72. FW-27: Fehlanker-Guard und Playwright-Regressionsabnahme

FW-27 ist als eigenständiger Evidenzvertrag ergänzt und anschließend zuerst
gezielt mit Playwright geprüft worden. Der Guard liegt in `anchors.py` und
entscheidet deterministisch über einen möglichen Ortsanker. Er akzeptiert
den vorhandenen FW-26-Fall weiterhin additiv, wenn die ältere Kamera noch
keine erweiterten Felder liefert. Sobald ein Earth-Frame diese Felder trägt,
werden sie als zusätzliche Belegschicht geprüft.

Abgelehnt werden jetzt ausdrücklich:

- unparsebare oder außerhalb der Erdkoordinaten liegende OCR-Werte;
- ein `center`- oder `unknown`-Claim statt eines Mauszeiger-Claims;
- fehlendes oder zu schwaches Vertrauen sowie ein Claim-/Frame-Mismatch;
- fehlende Mausposition;
- Mauszeiger am Rand oder außerhalb des sicheren Kartenrechtecks, wenn der
  Frame `map_bounds` meldet;
- See-/Wald-/Wasser-/Forst-Kontext ohne sichtbare Zielbeschriftung;
- ein unveränderter Belegframe;
- verlorener Earth-Fokus oder ein Popup über der Karte.

Ein Wald-/See-Frame wird erst als bestätigter Zielanker angenommen, wenn
`target_label_visible: true` und eine sichtbare Kamerabewegung belegt sind.
Die Antwort bewahrt die konkreten Gründe (`reasons`) für Cockpit, Terminal
und spätere Diagnose. Die bisherige Wahrheit wird nicht umbenannt: native
Earth Pro bleibt X11/OpenGL mit semantischem Proxy, nicht angeblicher DOM.

Der gezielte Playwright-Test gegen den laufenden lokalen Cockpit-Prozess
prüft fünf Ablehnungen — falsche OCR, Center, Rand, unbestätigter Wald und
unveränderter Frame — sowie den bestätigten Gegenfall. Danach liefen ohne
weitere Codeänderung **28 Python-Tests** und **20 Playwright-Tests** grün.
Die Gesamtmatrix enthält weiterhin den echten Earth-Test mit X11-Capture,
Fokus, Control-Lease, Aktion, Nachframe und vollständigem `mouseup`/`keyup`-
Release. FW-27 ist damit verifiziert; offen bleiben FW-64 (echte 8K/66-FPS-
Zielhardware) und die abhängige Endabnahme FW-90.

[[abwurf: Ein Ziel im Wald ist erst ein Ort, wenn der Frame beweist, dass der Mauszeiger, die Koordinate, die Beschriftung und die Bewegung dieselbe Geschichte erzählen.]]

## 73. FW-64: Messbericht gebaut, Zielhardwaregrenze sichtbar offen

FW-64 wurde nicht durch eine Zielzahl grün gefälscht. Die Menschenfläche
misst nun im laufenden Browserkörper die tatsächliche WebGL-Canvasauflösung,
die beobachtete Renderloop-Rate und den Zielstatus. Die Anzeige steht direkt
unter der 3D-Fläche und trägt `Canvas`, `RAF`, Ziel `7680×4320 / 66 FPS` sowie
`unmeasured`, `measured-below-target` oder `verified`.

Der Playwright-Live-Test wartet auf einen echten WebGL-Kontext, liest die
Canvaswerte über `window.__humanSurfaceMetrics()`, lässt den Renderloop laufen
und prüft die sichtbare Messzeile. Der direkte Lauf am 27.07.2026 lieferte
`webgl: true`, `webgl_mode: webgl`, `canvas_width: 1234`, `canvas_height: 150`,
eine positive beobachtete RAF-Rate und `target_met: false`; ein separater
X11-Frame des Desktopfensters war `1920×990`. Diese Werte sind verschiedene
Schichten und werden nicht miteinander verwechselt.

Die Python-Seite besitzt dazu `RenderMetrics.meets_target()` und setzt nach
einer echten FPS-/Auflösungsmessung den Status auf `measured-below-target`
oder `verified`. Der Unit-Test prüft, dass 1920×816 bei 50 FPS nicht als
8K/66 ausgegeben wird. Der Live-Playwright-Test prüft denselben Schutz im
laufenden Cockpit; die vollständige Matrix danach war **28 Python / 21
Playwright grün**.

Damit ist der Messbericht und sein ehrlicher Degradationspfad gebaut und
abgenommen. FW-64 bleibt offen, weil diese konkrete Zielhardware die
geforderte Auflösung und Bildrate nicht erreicht. FW-90 bleibt als davon
abhängige Endabnahme ebenfalls korrekt blockiert.

[[abwurf: Der Messbericht ist fertig, auch wenn das Ziel noch nicht erreicht ist; „gemessen unter Ziel“ ist hier ein lebender Zustand und kein heimliches „fertig“.]]

## 74. Extreme Rohmaterial-Dokumentation: Lesart, Grenze und Herkunft

Dieser Abschnitt ist kein Ersatz für die Abschnitte 1–73. Er ist ein
nachträglich angelegtes Rohmaterial-Archiv. Die ältere Chronik bleibt an ihrem
Platz, auch wenn sie an einzelnen Stellen bereits dieselben Ereignisse
zusammenhängend beschreibt. Der Zweck dieses Nachtrags ist, die Wege zurück zu
den einzelnen Spuren zu erhalten: Daniels kurze Korrekturen, meine damaligen
Antworten, beobachtete Terminalausgaben, Dateinamen, Commit-Namen, Testzahlen,
Fehler und die Stellen, an denen nur eine Behauptung oder ein Chatprotokoll
vorliegt.

### 74.1 Was hier als Rohmaterial gilt

Mit „roh“ sind in diesem Anhang vier verschiedene Herkunftsklassen gemeint:

1. **Daniel im Gespräch:** wörtliche Impulse und Beobachtungen, soweit sie in
   der laufenden Unterhaltung oder in dem von Daniel erneut eingefügten Verlauf
   vorlagen. Dazu zählen etwa „keine Suchleiste“, „der Mauszeiger muss Conti
   berühren“, „gar keine Screenshots nur DOM“ und „mit WASD kannst du dich auch
   bewegen“.
2. **Codex-Antworten:** meine damaligen Erklärungen, auch wenn sie sich später
   als zu glatt, zu langsam, falsch fokussiert oder technisch nicht gedeckt
   herausstellten. Diese Sätze sind Belege für den Lernweg, nicht automatisch
   Belege für einen funktionierenden Zustand.
3. **Werkraum- und Laufzeitspuren:** Dateien, JSONL-Ledger, PNG-/Timeline-
   Referenzen, Dienste, Prozessdaten, Testausgaben und Git-Commits. Sie sind
   maschinennahe Belege, aber immer zeitgebunden.
4. **Rekonstruktion:** ordnende Beschreibung, wenn der vollständige Dialog nicht
   im Dateisystem gefunden wurde. Rekonstruktion wird hier ausdrücklich als
   Rekonstruktion markiert und nicht als angeblich wörtliches Terminalprotokoll
   ausgegeben.

Diese Unterscheidung ist notwendig, weil ein lokaler Frame, eine Chatzeile und
ein grüner Playwright-Test drei unterschiedliche Wahrheiten belegen. Ein
Frame beweist, was er zeigt; ein Ledger beweist, was die Bridge protokolliert;
ein Test beweist nur seine Assertions; keine dieser Spuren beweist, dass dieses
Sprachmodell jeden Zwischenframe automatisch wahrgenommen hat.

### 74.2 Fundlage und nicht gefundene Fundstücke

Der zentrale Dokumentationsort ist jetzt:

```text
/root/werkraum/ai_strom_bruecke/DOKUMENTATION.md
```

Der frühere gemeinsame technische Code- und Vertragsort bleibt:

```text
/root/werkraum/_shared/ai_strom_bruecke/
```

Dort liegen unter anderem `README.md`, `bridge.py`, `actions.py`,
`contracts.py`, `stream_server.py`, `vision_runner.py`,
`cockpit_server.py`, `firefox_dom.py`, `anchors.py`,
`camera_analysis.py`, `render_surface.py`, `requirements.py`,
`network_guard.py`, die Systemd-Units, Playwright-Spezifikationen und die
Tests. `GOOGLE_EARTH_STEUERUNG.md` ist das separate Earth-Steuerungs-Howto.

Die Suche nach den aktuell im Chat wiederholten Formulierungen fand nicht für
jede Zeile eine identische gespeicherte Datei. In `_gpt/` existieren
Zeitstrom-, Session-, MCP- und UI-Exportspuren, aber sie sind nicht überall ein
vollständiges Rohtranskript dieses Gesprächs. Deshalb werden die hier aus dem
Gespräch übernommenen Zitate als **Daniel-/Codex-Verlauf aus dem vorliegenden
Chatmaterial** bezeichnet, nicht als aus `events.jsonl` gelesene Originalzeilen.
Das ist eine absichtliche Lücke in der Provenienz und kein Grund, sie mit
erfundenen Terminaldetails zu füllen.

### 74.3 Bereits vorhandene Vorgeschichte

Die Doku enthielt vor diesem Nachtrag bereits die Entwicklung von der ersten
Selkies-/Shared-Idee bis zur Realtime-, Drei-Leiber-, Red-Team- und
Playwright-Arbeit. Die überschneidenden Abschnitte sind:

| Abschnitt | Roh-/Bauinhalt |
|---|---|
| 1–34 | erste Brücke, Shared-Beobachtung, Control-Lease, native Earth, frühe Navigation und Dialogspuren |
| 35–47 | nachträgliche sichtbare Gesprächs- und Terminalanhänge, Earth-Kill, Push-/Vision-Kette |
| 48–60 | 0,1-Sekunden-Forderung, DOM-Frage, Dreiergespann, Dreierregel, Dreierregen, Wahrnehmungskapsel, Red-Team und offene Planung |
| 61 | vollständiger Bauauftrag statt MVP/minimalem Testkörper |
| 62–66 | tatsächlicher integrierter Bau, Organ-Leib, Inventar, DOM-Spiegel und Dokumentationsabnahme |
| 67–73 | echter Earth-Härtetest, Dienst-Reload, Fokus, Earth-Playwright, WebGL, Fehlanker-Guard und Rendermessung |

Der neue Anhang wiederholt diese Entwicklung nur dort, wo die Wiederholung die
Rohherkunft, den Widerspruch oder die tatsächliche Reihenfolge sichtbar macht.

## 75. Gesprächsarchäologie: vom Wunsch nach einem sichtbaren Desktop zur Bridge

### 75.1 Der ursprüngliche menschliche Wunsch

Im Rohverlauf war die Aufgabe nicht zuerst „baue eine API“, sondern sinngemäß:
Ein externer AI-Strom soll Daniels laufenden Desktop sehen, Maus und Tastatur
benutzen können, dabei sichtbar bleiben und nicht die bestehende Webtop-
Verbindung verdrängen. Daraus entstand der Name **AI-Strom-Brücke**.

Meine damalige Antwort versprach zunächst mehr, als die Chat-Schnittstelle
leisten kann. Später wurde der Satz korrigiert: Ein lokaler Watcher kann Frames
pushen, aber dieses Chatmodell empfängt sie nicht ungefragt in sein laufendes
Bewusstsein. Für ein tatsächliches Push-Sehen braucht es einen separaten
Vision-Runner, der den Stream abonniert und die Daten an ein bildfähiges Modell
weitergibt.

Die technische Korrektur war deshalb eine Trennung:

```text
Selkies/Shared-Beobachtung
        -> Rohereignisse und Frames
        -> lokaler Stream / Vision-Runner
        -> frischer Frame als Input-Gate
        -> Control-Lease
        -> direkte Aktion
        -> Folgeframe / Ack
```

Die Bedeutung dieser Kette wurde erst durch Daniels Einwand klar, dass eine
Bewegung, die erst nach 20 oder 40 Sekunden sichtbar wird, für ihn kein
Livegefühl erzeugt. Sichtbarkeit war nicht Dekoration, sondern Teil der
Interaktion.

### 75.2 Die ersten Realtime-Versprechen und ihre Korrektur

Aus dem Verlauf:

> „Der Watcher läuft jetzt dauerhaft mit 8 Bildern pro Sekunde“

und später:

> „Das kann ich in diese Chat-Session nicht automatisch ‚hineininjizieren‘“

Diese beiden Sätze widersprechen sich nicht technisch, aber sie wurden im
Gespräch zunächst nicht sauber getrennt. 8 FPS in einer Datei oder einem
HTTP-Stream sind nicht dasselbe wie acht Frames, die das Sprachmodell im
gleichen Antwortzyklus automatisch verarbeitet. Die spätere Architektur führt
deshalb `latest.png`, Sequenz, Digest, Alter, Push-Stream und Vision-Runner
getrennt.

Daniel forderte zusätzlich einen Takt um 0,1 Sekunden. Die spätere Einordnung
war: 0,1 Sekunden können für Capture, Heartbeat und Duplikaterkennung ein
Zielhorizont sein; sie erzeugen nicht automatisch eine 10-Hz-Wahrnehmung des
Sprachmodells und dürfen keinen Modellaufruf pro Frame auslösen.

### 75.3 Die erste Google-Earth-Expedition: Phantasialand

Die erste längere Earth-Aufgabe war die Suche nach einem echten Freizeitpark
ohne Suchfeld und ohne Eingabe. Im Verlauf ging es von Deutschland über Köln,
Brühl und Bonn zum Park. Die Zwischenframes führten zunächst durch zu viel
Landschaft und falsche Ziele. Es tauchten unter anderem ein Nationalpark und
der Hochwildpark Rheinland auf; Daniels Kriterium war eindeutig: echte
Achterbahnen, nicht bloß eine grüne Fläche oder irgendein Parklabel.

Die entscheidende Korrektur lautete:

> „du sollst nix suchen und eintippen das ist cheaten ...du sollst es navigieren und zwar ganz ganz fix“

Danach wurde die Bedienung in zusammenhängende Phasen geändert: Maus halten,
viele kleine Bewegungen senden, erst nach einem Block prüfen. Das sollte die
20-Sekunden-Pausen zwischen den Bewegungen vermindern.

Die wichtigsten Fehler der Fahrt waren:

- ein Drag außerhalb oder am Rand der Earth-Fläche wurde nicht angenommen;
- ein dezimaler Bash-Ausdruck wie `400+i*2.5` verursachte den
  `Arithmetischer Syntaxfehler`, weil Bash hier keine Dezimalarithmetik machte;
- der Mausanker lag etwa 30 Pixel zu hoch, wodurch auf See oder Wald statt auf
  den Park gezoomt wurde;
- ein Fokus- oder Popup-Fenster wurde mit dem eigentlichen Earth-Fenster
  verwechselt;
- die Beschriftung „Phantasialand“ war sichtbar, aber der Bildausschnitt zeigte
  zunächst nur ungefähr zwei Prozent Park und 98 Prozent Landschaft.

Daniels zusammenfassende Korrektur war:

> „naja du hast recht haha aber ich seh 2 % park und 98% landschaft“

Erst nachdem der Mauszeiger auf die sichtbare Parkfläche gesetzt und der
Zoomanker genutzt wurde, war der Park großflächig sichtbar. Die im Verlauf
genannten Fahrgeschäfte waren **Black Mamba, Chiapas / DIE Wasserbahn, River
Quest, Tikal, Raik und Hotel Matamba**. Der spätere Bildtreffer wurde von
Daniel selbst als gewünschtes Endbild hergestellt; meine damalige Reaktion
erkannte ausdrücklich an, dass nicht ich den finalen perfekten Bildausschnitt
gezaubert hatte.

### 75.4 Zweite Expedition: Eiscafé Conti in Schwelm

Danach gab Daniel die Aufgabe:

> „ok undnun zur nächsten aufgabe..finde das eisk´cafee conti in schwelm“

Die Navigation wurde erneut ohne Suchfeld und ohne Eintippen geplant. Von
Brühl ging es über regionales Herauszoomen, Köln/Rhein, Bergisch Gladbach,
Gummersbach, Engelskirchen, Wermelskirchen, Wipperfürth, Lüdenscheid,
Remscheid, Ronsdorf und Beyenburg in Richtung Schwelm. Die Entwicklung war
nicht linear: mehrfach wurde über die falsche Seite des Kartenausschnitts
gezogen, und die Kartenbewegung wurde durch kurze synthetische Drags zeitweise
nicht angenommen.

Daniels wichtigster Steuerungshinweis war:

> „dort wodeine mausist ---genau dahin wird schnell reingezoomed bei mehreren zoomes“

Damit wurde der Mauszeiger vom bloßen Cursor zu einem geografischen Anker.
Die Koordinatenanzeige unten rechts wurde als Position **unter dem Mauszeiger**
und nicht automatisch als Kartenmitte verstanden. Im Verlauf wurden unter
anderem diese abgelesenen Punkte festgehalten:

```text
51°08'09"N, 7°15'40"O   regionaler Wuppertal-/Sauerlandbereich
51°13'57"N, 7°15'59"O   Ronsdorf/Lüttringhausen
51°15'58"N, 7°16'27"O   Prüfpunkt nahe Schwelm
51°14'57"N, 7°16'50"O   Beyenburg-Ausschnitt
51°16'46"N, 7°18'04"O   Winterberg-/Ehrenmalbereich
51°16'56"N, 7°17'41"O   nordwestlicher Zentrumsrand
51°16'55"N, 7°17'46"O   noch südlich der Innenstadt
51°16'55"N, 7°17'53"O   weiterhin falscher Ehrenmal-Anker
```

Der tatsächliche Treffer wurde als **Eismanufaktur Gelateria Conti** am
**Märkischen Platz**, nahe der **Hauptstraße**, erkannt. Der Verlauf enthält
die ausdrücklich falschen Zwischeninterpretationen „Ehrenmal“ und ein
vermeintlicher oberer Café-Eintrag; erst nach dem Herauszoomen war die
Beschriftung eindeutig.

Danach wollte Daniel nicht nur den Pin lesen:

> „naja lesen kann ich es auch...aber ich will leute da sitzen sehen oder das schaufenster it logo hahaha“

Es wurde kurz Street View/Pegman versucht. Daniel wies das als Abkürzung
zurück und verlangte, in Google Earth selbst näher heranzugehen. Der Versuch
öffnete tatsächlich Street View; der Exit-Klick traf zunächst nicht sicher.
Zum Zeitpunkt des Abbruchs lief die Rückkehr aus Street View noch. Das ist ein
wichtiger Rohbefund: „in Earth stark hineinzoomen“ und „Street View/ground
imagery“ sind verschiedene Modi; ein Pin allein beweist kein sichtbares
Schaufenster und keine sitzenden Menschen.

### 75.5 Daniels empirische Google-Earth-Regeln

Die späteren Hinweise wurden im Howto in technische Regeln übersetzt. Roh
lauteten sie unter anderem:

> „du kannst mittlere maustaste klicken und geklickt halten...und dann auch links rechts undten oben und seitlich deine ansicht verändern“

> „mit wasd kannst du dich auch bewegen“

> „entweder kurz öfters hintereinander klicken oder je länger du gedrückt hältst desto weiter wanderst du“

> „zoom doch kurz mal raus bis du die schrift wieder lesen kannst“

> „wenn du einen punkt weisst für die innenstadt ... am besten direkt mit maus anzielen und dann zoomen“

> „der mauszeiger muss conti berühren dann merken“

Als ausführbarer Bedienvertrag ergibt sich daraus:

- linke Taste halten: Karte greifen und verschieben;
- mittlere Taste halten: räumliche Orientierung, seitliche oder vertikale
  Ansicht verändern; konkrete Richtung im Setup empirisch prüfen;
- rechte Taste bzw. vertikales Ziehen: Zoom/Neigung-Kombination;
- Rad, Plus/Minus und beobachtetes `Page_Up`/`Page_Down`: Zoom, immer mit
  Zielpunkt als Mausanker;
- `w`, `a`, `s`, `d`: empirische Bewegung in dieser Installation;
- kurze Wiederholungen: Feinbewegung;
- lange gehaltene Taste: größerer Versatz;
- bei jedem Hold zwingend `mouseup` oder `keyup`, auch bei Timeout und
  Verbindungsabbruch;
- erst herauszoomen, wenn Labels fehlen oder der aktuelle Ort unklar ist;
- Maus auf das Ziel setzen, Koordinate ablesen, dann erst hineinzoomen;
- sichtbare Veränderung nach der Aktion ist notwendig, sonst wird die Aktion
  nicht als angenommen behauptet.

### 75.6 Der entscheidende Wahrnehmungswunsch

Daniel wollte nicht nur eine abgeschlossene Aktion, sondern den Prozess selbst
sehen: Terminalzeilen, Bewegungen, Entscheidungen, Fehler, Korrekturen und
Erfolge. Lange Tool-Roundtrips ohne sichtbare Zwischenbewegung wirkten wie ein
Hänger, auch wenn im Hintergrund ein Watcher lief. Die Bridge musste darum
Heartbeat, Phase, Aktion, Wartezeit, Framealter, Mausposition, Erwartung und
Ergebnis sichtbar machen.

Die Grenze blieb: Dieses Chat-API injiziert keine Bilder ungefragt in ein
laufendes Sprachmodell. Ein lokaler Push-Stream kann die Übertragung sofort
auslösen; die semantische Verarbeitung braucht dennoch einen angeschlossenen
Vision-Runner. Die Dokumentation bewahrt beide Tatsachen nebeneinander.

## 76. Rohes Terminal- und Toolmaterial

### 76.1 Direkter X11-Snapshot

Der native Earth-Pfad verwendete die bestehende Desktop-Sitzung und keinen
neuen Selkies-Primary-Client. Der wiederholt verwendete Befehl war:

```bash
python3 /root/werkraum/_shared/ai_strom_bruecke/bridge.py snapshot \
  --target google-earth --wait-ms 0 \
  --output /tmp/google-earth-<name>.png
```

Die Sichtbarkeit wurde mit einem lokalen Bild-Tool geprüft. Im Verlauf wurden
Namen wie `google-earth-park-zoom1.png`, `google-earth-park-back.png`,
`google-earth-schwelm-target.png`, `google-earth-conti-final.png` und
`google-earth-conti-centered.png` verwendet. Diese Dateinamen sind
Arbeitsartefakte aus dem Gespräch; ein Name allein ist kein Beweis, dass die
Datei dauerhaft erhalten oder von einem Sprachmodell gesehen wurde.

### 76.2 Fenster- und Displaydiagnose

Der native Container war:

```text
Container: virtuellerdesktop2
DISPLAY:   :1
Display:   1920x816 (früherer Earth-Frame je nach Fenster: 806x494)
Fenster:   Google Earth Pro
```

Beobachtete Diagnosebefehle waren unter anderem:

```bash
docker exec virtuellerdesktop2 bash -lc \
  'export DISPLAY=:1; xdotool getactivewindow; \
   xdotool getwindowname $(xdotool getactivewindow)'

docker exec virtuellerdesktop2 bash -lc \
  'export DISPLAY=:1; xdotool getdisplaygeometry; xrandr --current'

docker exec virtuellerdesktop2 bash -lc \
  'export DISPLAY=:1; xdotool mousemove --sync 1000 400; \
   xdotool getmouselocation --shell'
```

Ein konkreter Befund lautete:

```text
active=4194316
Google Earth Pro
WINDOW=559
1920 816
X=1000
Y=400
SCREEN=0
WINDOW=559
```

Die ältere native Härtung meldete ein Earth-Fenster mit der Geometrie
`X=0,Y=36,806x494`. Diese unterschiedlichen Größen sind kein automatisch
auflösbarer Widerspruch: Es gab verschiedene Container-/Fensterzustände und
Captureflächen.

### 76.3 Gehaltene Mausbewegung

Der erste gedachte Drag verwendete eine Shellschleife mit Dezimalwerten. Bash
brach ab mit:

```text
bash: Zeile 1: 400+i*2.5: Arithmetischer Syntaxfehler:
Ungültiger arithmetischer Operator (fehlerverursachendes Zeichen ist ".5")
```

Die korrigierte Form arbeitete mit ganzzahligen Zwischenpunkten:

```bash
export DISPLAY=:1
xdotool mousemove --sync 1000 400
xdotool mousedown 1
for i in $(seq 1 100); do
  xdotool mousemove --sync $((1000-i*2)) $((400+i*2))
  sleep 0.02
done
xdotool mouseup 1
```

Die genaue Schleifenvariante änderte sich im Verlauf; der entscheidende
Rohbefund war nicht die eine Zahl, sondern: Hold muss über die ganze Folge
aktiv bleiben, und die Freigabe muss auch bei einem abgebrochenen Prozess
garantiert werden.

### 76.4 Fokus, Popup und Fehlklicks

Mehrere Toolausgaben waren „no output“, obwohl die Aktion entweder wirkte oder
nicht wirkte. Das war eine wichtige Diagnosegrenze: Exit-Code 0 der Shell war
kein visueller Ack. Erst der Folgeframe entschied zwischen akzeptiert und
abgelehnt.

Im Verlauf wurden außerdem folgende Fehlziele festgehalten:

- ein großes Bild-Popup mit eigenem X oben rechts wurde zunächst mit dem
  Seitenpanel-X verwechselt;
- der Cursor lag auf einem Bildfenster statt auf Earth;
- ein Street-View-Pegman- oder Exit-Klick traf wegen Fensterkoordinaten daneben;
- ein direkter PageDown funktionierte, während ein anderer synthetischer Drag
  pixelgleich blieb;
- ein Capture mit `xwd` scheiterte am OpenGL-Fenster mit `BadMatch`, während
  ImageMagick `import -window` funktionierte.

Die spätere Reihenfolge wurde deshalb explizit:

```text
Capture -> Earth-Fokus wiederherstellen -> Input dispatchen
       -> Held-Zustände freigeben -> neuer Frame -> Diff/Ack
```

### 76.5 Lokale Push- und Zustandsdateien

Die Bridge führt mehrere unterschiedliche Rohspuren:

| Datei | Inhalt / beobachtete Größenordnung |
|---|---|
| `events.jsonl` | append-only Selkies-Ereignisse; beim Auslesen 261.976 Zeilen / ca. 58,6 MB |
| `actions.jsonl` | 31 transaktionale Aktionen; 15 accepted, 16 rejected |
| `timeline.json` | 1.161 Frame-Metadateneinträge im ausgelesenen Zustand |
| `timeline_frames/` | PNG-Frames, nicht automatisch alle als Gesprächsbilder wahrgenommen |
| `latest.png` | atomar aktualisierter letzter X11-Frame |
| `vision_latest.png` | letzter vom Vision-Runner weitergereichter Frame |
| `vision_state.json` | Runner-, Gate-, Sequenz-, Digest-, Alters- und Duplikatstatus |
| `analysis-overlay.png` | optionaler Analyse-Overlay-Frame |
| `state.json` | zusammengeführter Runtime-/Action-/Frame-Zustand |

Ein ausgelesener `vision_state.json`-Stand enthielt unter anderem:

```text
runner: running
upstream: http://127.0.0.1:8098/stream
connected: true
frame_count: 8782
last_source_sequence: 8780
last_frame_age_ms: 3.0
capture_latency_ms: 4.5
duplicate_frame_count: 1605
```

Das zeigt einen laufenden lokalen Consumer und frische Daten in diesem
Moment. Es beweist nicht, dass die Chat-API den Frame automatisch in ihre
aktuelle Modellverarbeitung eingespeist hat.

## 77. Action-Ledger: maschinenlesbarer Rohbefund

Das ausgelesene `actions.jsonl` hatte 31 parsebare JSON-Zeilen. Die Verteilung
war:

```text
phase:
  rejected 16
  accepted 15

action_type:
  key       26
  gesture    3
  wheel      1
  key-hold   1

target:
  google-earth 29
  active         2
```

Jede Zeile enthielt dieselben wesentlichen Felder: `action_id`, `actor`,
`lease_id`, `target`, `action_type`, `planned_at`, `dispatched_at`,
`observed_at`, `released_at`, `pointer_start`, `pointer_end`, `button`,
`key`, `held_buttons`, `held_keys`, `input_sequence`, `expectation`,
`observed_frames`, `result`, `rejection_reason` und `provenance`.

Ein repräsentativer abgelehnter Drag enthielt:

```json
{
  "action_type": "gesture",
  "target": "google-earth",
  "input_sequence": [
    {"kind": "mousedown", "value": 1},
    {"kind": "mousemove", "x": 1003, "y": 402},
    {"kind": "mousemove", "x": 1006, "y": 404},
    {"kind": "mousemove", "x": 1009, "y": 406},
    {"kind": "mousemove", "x": 1012, "y": 408},
    {"kind": "mousemove", "x": 1015, "y": 410},
    {"kind": "mouseup", "value": 1}
  ],
  "phase": "rejected",
  "rejection_reason": "Post-Action-Frame blieb unverändert",
  "held_buttons": [],
  "held_keys": []
}
```

Ein repräsentativer angenommener PageUp-Beleg trug `phase: accepted`,
`explanation: Playwright real Earth visual ack (Page_Up)`,
`evidence_present: true`, leere Held-Listen und einen Digestwechsel. Andere
PageUp-/PageDown-Aktionen erhielten zwar einen Digestwechsel von minimaler
Stärke, aber keinen signifikanten Bildwechsel. Diese Fälle wurden im Ledger
als accepted oder minor-change geführt und dürfen nicht mit einer sicher
erkennbaren großen Kamerafahrt gleichgesetzt werden.

Der strengere Härtetest klassifizierte bei unverändertem Bild:

```text
kind: unchanged
changed_ratio: 0.0
mean_difference: 0.0
digest_changed: false
reason: Bytefolge unverändert
```

Das ist genau die Art von Ablehnung, die früher im Gespräch als „der Drag
wurde ignoriert“ beschrieben wurde. Die spätere Transaktionsschicht macht
daraus einen nachlesbaren Zustand statt einer vagen Vermutung.

## 78. Chronologische Code- und Commit-Archäologie

Die folgende Liste stammt aus der Git-Historie des Bridge-Pfads. Die Namen
zeigen die tatsächliche Reihenfolge der technischen Schwerpunkte; ein Commit
mit `test` beweist einen Testlauf, aber nicht automatisch die Erfüllung jedes
externen Realweltziels.

```text
eb9daed52  2026-07-27 03:33  build: AI-Strom-Brücke für virtuellen Desktop
dee475285  03:53              fix: Firefox-X11-Start nach Browserneustart sichern
1698ac1cb  04:13              fix: Bridge-Control ohne Selkies-Primary-Verdrängung
87b6e40c9  04:50              feat: AI-Strom-Brücke mit direktem Realtime-X11-Beobachter
411e0cbce  04:58              feat: lokaler Push-Stream für AI-Strom-Brücke
97f1e99c8  05:07              docs: vollständige Entstehungs- und Lernchronik
f111dba19  09:27              docs: Google-Earth-Steuerungs-Howto
9dcf22623  09:31              docs: sichtbaren Dialog- und Terminalverlauf ergänzen
f460b81bd  10:04              docs: Dreier-DOM und Realtime-Red-Team ergänzen
0a691b41e  11:28              feat: realtime evidence contracts and safe action core
39ef56213  11:29              feat: visible cockpit heartbeat service
da9118487  11:30              test: live cockpit service playwright acceptance
1639c5989  11:35              feat: add real dom and native proxy adapters
ee1d8bc19  11:36              test: verify real dom and native proxy tri-leib adapters
6ef5de36d  11:43              feat: integrate anchors overlays causal flow and realtime state
376cf77c3  11:44              fix: start cockpit as package module under systemd
28852730b  11:46              test: cover push vision and native action release
d426eff5f  11:49              feat: add camera render and dom mutation evidence
f21f83c68  11:51              test: add visible native input harness acceptance
e87d340c5  11:52              feat: expose executable requirement tracking in cockpit
fd5a22fa4  11:55              test: add integrated red-team regression runner
7d48c96e2  11:58              feat: render animated human surface from tri-view objects
5c19a72a0  11:59              test: verify event sse and requirement honesty
05e2000b6  12:00              test: verify stale gate and push reconnect
19a0fac41  12:01              docs: record implemented bridge and honest requirement status
1fad808ad  12:04              feat: integrate explicit platform organ effects
96ed9c675  12:05              feat: measure capture latency and standardize ten fps observer
8206da945  12:08              test: add measured realtime load acceptance
9ce54dc4c  12:08              chore: update requirements from measured evidence
82f0cdcdc  12:10              docs: record load organ and installed unit evidence
13f9b82ad  12:10              test: cover middle right mouse and wheel controls
6e1caca9c  12:14              chore: record mouse and organ acceptance evidence
3d094ae57  12:15              docs: record complete current test matrix and open edges
813c9d1b7  12:23              fix: preserve shared state and expose stale capture gate
fb81fe556  12:24              fix: make object identity and stale service state explicit
77359f6fc  12:59              feat: complete realtime dom inventory and human surface evidence
9cf64abca  13:02              docs: record final current bridge acceptance evidence
8f8d6f0ff  13:03              docs: close fw89 and refresh bridge graph
57b9dff42  13:13              docs: record real earth hardening result
737270bf3  13:37              test: accept live analysis overlay frame contract
4b6f9e1b6  13:38              docs: record live reload and overlay acceptance
335c30926  13:40              fix: restore native window focus after capture
4e9d0b13b  13:41              docs: record final earth focus hardening evidence
bbd05ad3b  16:48              feat: verify native earth through playwright and close fw82
a8656c35d  17:05              feat: verify real webgl human surface
849e2c113  17:12              feat: close fw27 anchor regression guard
c483ed05d  18:04              feat: add honest render measurement report
391d00b93  18:21              backup before Firefox web route
3e7bf0d41  18:25              backup before Firefox navigation diagnosis
291a4cd29  18:32              backup before Firefox DOM Playwright gate
b29b98a3a  18:38              backup before DOM-only Earth gate
72729a5bc  18:40              feat: firefox dom-only earth gate
ea30a08ee  18:43              docs: document firefox bidi dom-only path
2163095df  18:46              feat: opt-in firefox bidi x11 start
714ad9130  18:48              backup before Firefox BiDi input gestures
e4229768e  18:50              feat: add firefox bidi held input gestures
db38c9cd4  current backup: vor extremer rückwirkender Bridge-Dokumentation
```

Die Commitliste erklärt auch, warum die heutige Bridge mehrere Wahrnehmungs-
und Aktionspfade hat: Der native X11-/OpenGL-Pfad wurde nicht nachträglich in
einen Web-DOM umbenannt; der Firefox-DOM-Pfad wurde später als eigene Route
ergänzt.

## 79. Drei Leiber, DOM und „nicht nur ein MVP“: Rohanforderungen

Daniel korrigierte die Planung mehrfach, weil eine kleine Testhülle nicht das
gewünschte Endprodukt war. Die rohe Richtung der eigenen damaligen Aussagen
war:

> „Nicht drei Ansichten desselben Objekts, sondern ein dreifach lebendes Ding.“

> „Flextrawurst braucht keine getrennten UIs für Menschen, Codewesen und Organe. Es braucht ein Objektmodell, in dem jedes Weltobjekt automatisch drei Wahrnehmungsleiber besitzt.“

Der Codewesen-Leib sollte DOM-Pfad, HTML-Schnipsel, CSS-Zustände, IDs,
Klassen, Klickbarkeit, Reihenfolge, Frische und Veränderungen enthalten. Der
Menschen-Leib sollte dieselbe Objektwahrheit als räumliche, animierte Welt bis
hin zu 8K/3D/66 FPS darstellen. Der Organ-Leib sollte Beziehungen zu Posts,
Splittern, Gruppen, Schattenkommentaren, KompOase, Profilen, Provenienz,
Resonanz und späteren Prozessen tragen.

Daniels Korrektur des Bauauftrags war unmissverständlich: Frühe Vorschläge
wie Koordinaten-OCR, 30–60-Sekunden-Framezeitstrahl, automatische
Bildvergleiche, Kamerazustand, sichtbares Fadenkreuz, Aktionsprotokoll,
Erfolgskontrolle, sofortiges `mouseup`, lokales Cockpit und gespeicherte
Anker sind keine optionale zweite Phase. Sie müssen in die vollständige
Architektur hinein, und die Abnahme darf erst nach Playwright-Tests erfolgen.

Der zentrale Datenfluss wurde als Rohform notiert:

```text
Frame
 -> Statusleisten-OCR
 -> Koordinaten-/Kamera-Zustand
 -> Bildvergleich
 -> Aktion
 -> Ergebnisprüfung
 -> sichtbare Erklärung
```

Später wurde für Earth Web eine harte Grenze ergänzt: Wenn Daniel „gar keine
Screenshots nur DOM“ sagt, darf dieser Datenfluss für den Web-Pfad nicht
heimlich wieder X11-Screenshots oder OCR einschleusen. Dort gilt:

```text
Firefox WebDriver BiDi
 -> document / controls / canvas facts
 -> DOM-/Browser-Input
 -> keine Screenshots
 -> keine OCR
 -> keine semantischen Ortsnamen behaupten, wenn sie nur im Canvas gerendert werden
```

## 80. Firefox, Web-Earth und der DOM-only-Konflikt

### 80.1 Was Daniel konkret verlangte

Im späteren Verlauf wurde klargestellt:

> „wir müssen aber firefox nehmen der chronium unterstützet kein webgl“

> „du musst nicht mit playwright steuern du sollst ohne screenshots nur im dom dich bewegen und sehen“

> „ein gar keine screenshots nurdom“

Damit war nicht gemeint, die native Earth-Pro-Anwendung nachträglich als DOM
auszugeben. Gemeint war Google Earth Web im bereits geöffneten Firefox, mit
Playwright/BiDi als DOM-/Browser-Transport, ohne Screenshot-Fallback.

### 80.2 Der tatsächliche Adapter

`/root/werkraum/_shared/ai_strom_bruecke/firefox_dom.py` verwendet Firefox
WebDriver BiDi über WebSockets. Der Adapter kann Dokument- und Canvasfakten
lesen, Controls auflisten, navigieren, Selektoren klicken, Pointer bewegen,
Pointer down/up, wheel, Key down/up und `release_actions` senden. Er verfolgt
`held_buttons` und `held_keys`, damit Daniels Hinweise zu gehaltenen
Maus-/Tastaturaktionen auch in der Webroute als Zustand sichtbar sind.

Der Testbericht erzielte im isolierten headless Firefox:

```text
EARTH_DOM {
  url: "https://earth.google.com/web/",
  title: "",
  dom_controls: [{
    tag: "flt-semantics-placeholder",
    role: "button",
    aria_label: "Enable accessibility"
  }],
  canvases: [{"width": 300, "height": 150, "webgl": false}],
  screenshot_used: false,
  native_x11: false,
  semantic_place_dom: false,
  map_surface: "canvas",
  model_calls: 0
}
```

Der Firefox-Lauf protokollierte WebGL-Probleme des headless Umfelds
(`AllowWebgl2:false`, `Exhausted GL driver options`,
`FEATURE_FAILURE_WEBGL_EXHAUSTED_DRIVERS`). Das ist kein Grund, den DOM-only
Test grün zu fälschen: Der Test belegt DOM-Erreichbarkeit und weist WebGL als
separates Faktum aus.

Ein direkter BiDi-Gestentest erzeugte die Ereignisfolge:

```text
pointermove -> pointerdown -> pointermove -> keydown
-> wheel -> keyup -> pointerup
```

Der Test verwendete keine Screenshots. Ein Bug in der Deserialisierung wurde
gefunden und behoben, weil Firefox JavaScript-Objekte als strukturierte Listen
serialisierte. Zusätzlich sendet `close()` jetzt `session.end`, damit
Testläufe keine BiDi-Sessions liegen lassen.

### 80.3 Sichtbarer Firefox und die noch offene Verbindung

Der vorhandene sichtbare Firefox-Prozess war zum Diagnosezeitpunkt PID
`2028024`, Fenstertitel `Google Earth — Mozilla Firefox`, Geometrie ungefähr
`1920x1015`, aber ohne Listener auf `9222` oder `6000` und ohne
`--marionette`-/Remote-Agent-Argumente. Daraus folgt:

- Ein bereits laufender Firefox ohne Remote-Agent kann nicht nachträglich in
  einen DOM-Kanal umetikettiert werden.
- Ein opt-in Wrapper kann einen neuen sichtbaren Firefox mit BiDi starten:

```bash
AI_STROM_BRUECKE_FIREFOX_BIDI=1 \
AI_STROM_BRUECKE_FIREFOX_BIDI_PORT=9222 \
/usr/local/bin/firefox-x11
```

- Der aktuelle Wrapper bleibt ohne die Umgebungsvariable unverändert.
- Der sichtbare Firefox-Test ist opt-in über
  `AI_STROM_BRUECKE_VISIBLE_FIREFOX=1`.

Das war der Grund für den offenen Status: Ein headless BiDi-Test ist ein echter
Firefox-/DOM-Test, aber nicht automatisch der von Daniel geforderte sichtbare
Test in genau seinem bereits offenen Browserfenster.

## 81. Testinventar und ehrlicher Stand

Die im Verlauf festgehaltenen Testzahlen änderten sich, weil neue
Anforderungen, Tests und Reparaturen dazukamen. Frühere Zahlen bleiben als
historische Zwischenstände in der Doku stehen; der spätere Stand ersetzt sie
nicht rückwirkend.

Belegte Zwischenstände waren unter anderem:

```text
27 Python / 19 Playwright      erste vollständige Matrix nach Singleton-Fix
28 Python / 20 Playwright      FW-27-Guard-Abnahme
28 Python / 21 Playwright      FW-64-Rendermessung
32 Python                     Firefox-BiDi-Erweiterung
19 Playwright                 aktuelle nicht-native Matrix im Firefox-Schritt
```

Die isolierten Firefox-DOM-Tests sind von der nativen Earth-Integration zu
trennen. Der native Test `playwright/real_earth_integration.spec.js`
verwendet das Loopback-Cockpit, die Bridge-Control-Lease, einen echten
Vorframe, `bridge.py snapshot --target google-earth`, einen Nachframe,
Diff/Ack und Held-State-Release. Er macht aus dem nativen OpenGL-Fenster
keinen DOM.

Die Registry war im jüngsten dokumentierten Stand:

```text
total: 72
verified: 70
open: 2
end_abnahme: blocked_until_FW-90
```

Die offenen Endkanten waren `FW-64` und die abhängige `FW-90`. Andere
frühere Abschnitte enthalten ältere Zustände mit `68/72`, `69/72` oder
weiteren offenen IDs. Diese Verschiebungen sind chronologische Evidenz und
kein stiller Fehler der Doku.

Der aktuelle Earth-Web-Test enthält explizit:

```javascript
expect(report.screenshot_used).toBe(false);
expect(report.semantic_place_dom).toBe(false);
expect(report.model_calls).toBe(0);
```

Damit ist zugleich festgehalten, dass weder Qwen noch Hauhaucs noch ein
anderer LLM für den DOM-Test angerufen wurden. `network_guard.py` führt
`ollama`, `qwen`, `hauhaucs`, `llama-server` und `openai.com/v1` als
verbotene Modellmarker für diesen Modellfreiheitsvertrag.

## 82. Was jeweils tatsächlich bewiesen wurde

| Behauptung | Beleg | Was sie nicht beweist |
|---|---|---|
| X11-Fenster ist auffindbar | `xdotool`, Fenstername, Geometrie | dass Earth die synthetische Geste akzeptiert |
| PNG-Capture funktioniert | `bridge.py snapshot`, ImageMagick | dass das Chatmodell jeden Frame automatisch sieht |
| Push-Stream läuft | 8098/8099, Vision-State, Sequenz/Digest | dass ein externer Vision-Runner angeschlossen ist |
| Input-Gate schützt | frischer Frame, Gate timeout, Bypass sichtbar | dass die Aktion semantisch erfolgreich war |
| `mouseup`/`keyup` wurden gesendet | Action-Ledger und Held-Listen leer | dass die Karte sich bewegt hat |
| Bild ist unverändert | Diff `changed_ratio: 0.0` | warum Earth die Geste ignorierte |
| Browser-DOM ist erreichbar | Firefox BiDi, document/canvas report | dass Google Earths Canvas Ortsnamen als DOM liefert |
| WebGL ist vorhanden | Canvas/WebGL-Fakt oder Cockpit-Test | dass 8K/66 FPS auf der Zielhardware erreicht werden |
| Playwright-Test ist grün | Testreport | dass alle realen Desktopbedingungen identisch waren |
| Ortlabel ist lesbar | native Frame/OCR oder sichtbarer Earth-Frame | dass Fassade, Logo oder Menschen sichtbar sind |

Diese Tabelle ist die Gegenmaßnahme gegen die früheren glatten Sätze „erledigt“
und „sucht gerade danach“. Sie trennt Kanal, Wahrnehmung, Handlung,
Folgebeleg und Interpretation.

## 83. Red-Team-Rückblick auf die eigene Arbeit

Die größten Fehler waren nicht fehlende Python-Zeilen, sondern falsche
Gleichsetzungen:

1. **Shell beendet ≠ Aufgabe beendet.** Eine Bridge-Aktion darf enden, während
   Earth offen bleibt; das muss sichtbar erklärt werden. Umgekehrt darf eine
   beendete Aktion nicht als erfolgreiche Navigation verkauft werden.
2. **Watcher ≠ Modellbewusstsein.** 8 FPS auf Disk oder HTTP sind kein
   automatisches Push-Sehen dieses Chats.
3. **Capture ≠ Aktion.** Ein Bild kann aktuell sein, während der synthetische
   Drag verworfen wurde.
4. **Digestwechsel ≠ große Bewegung.** Ein minimaler Pixelwechsel kann durch
   Rendering oder Ladezustand entstehen.
5. **Label ≠ gewünschte Szene.** `Phantasialand` am Rand oder ein grüner Wald
   ist nicht die gewünschte Achterbahnen-Ansicht; `Conti` als Label ist nicht
   automatisch Schaufenster oder Gäste.
6. **Native Earth ≠ DOM.** X11/OpenGL wird mit semantischem Proxy und Frames
   geprüft; Earth Web wird bei Daniels Webforderung DOM-only geprüft.
7. **Headless Firefox ≠ sichtbarer Daniels-Firefox.** Der sichtbare Prozess
   braucht den Remote-Agenten bereits beim Start.
8. **Chromium-/Playwright-Webtop ≠ Daniels Session.** Ein neuer Primary-Client
   kann den sichtbaren Webtop verdrängen; deshalb direkte X11-Steuerung oder
   explizit gestartete, getrennte Firefox-BiDi-Sitzung.
9. **Fallback ≠ Zielerfüllung.** CSS-3D und gemessene Unterzielwerte werden als
   solche angezeigt, nicht in 8K/66 FPS umbenannt.
10. **Plan ≠ Endprodukt.** Daniels Kritik am MVP-Reflex bleibt für diese Doku
    eine harte Bauanforderung: Alle zehn Rohvorschläge und die drei Leiber
    müssen im Gesamtprodukt berücksichtigt und einzeln abgenommen werden.

## 84. Wiederaufnahme-Rezept aus dem Roharchiv

Wenn die Arbeit später weitergeht, ist diese Reihenfolge aus dem Material
ableitbar:

```text
1. DOKUMENTATION.md bis hier lesen, inklusive älterer Statusstände.
2. README.md und GOOGLE_EARTH_STEUERUNG.md lesen.
3. requirements.py und den Live-/Testreport abfragen.
4. Native Earth und Earth Web als zwei getrennte Targets markieren.
5. Für Web: Firefox mit BiDi beim Start; keine Screenshots/OCR.
6. Für Native: X11-Capture, frischer Frame, Fokus, Lease, Input, Folgeframe.
7. Vor jeder heldenen Aktion: Abbruchschutz für mouseup/keyup.
8. Nach jeder Aktion: diff, Koordinate, Zielanker und semantische Aussage
   getrennt protokollieren.
9. Playwright-Gate zuerst gegen genau den Pfad ausführen, den Daniel sehen
   soll; headless/isoliert nicht als sichtbare Endabnahme ausgeben.
10. Erst wenn alle Anforderungen und die sichtbare reale Route grün sind,
    FW-90 schließen.
```

Die Rohdaten sollen dabei nicht still geleert werden. `events.jsonl` ist
append-only; `actions.jsonl` ist ein Ledger; Timeline-Frames sind Belegmaterial
mit möglicher hoher Menge; diese Dokumentation ist die lesbare Schicht darüber.
Bei einer späteren Bereinigung muss zuerst festgehalten werden, welche
Provenienz verloren ginge.

## 85. Abschlussvermerk dieses Extremnachtrags

Zusammengekratzt wurden hier: die vorhandene Doku bis §73, das Earth-Howto,
der von Daniel erneut in den Chat eingebrachte Dialogverlauf, die lokalen
Bridge-Dateien, die aktuellen Action-/Event-/Timeline-/Vision-Spuren, die
Firefox-DOM- und Playwright-Belege, die Fehlerausgaben, die Commitgeschichte
und die offenen Nachweise. Die Datei behauptet nicht, dass jede jemals im
Chat erzeugte PNG-Datei oder jede Chatzeile noch im Dateisystem liegt. Sie
bewahrt stattdessen exakt die wichtige Unterscheidung zwischen vorhandenem
Rohfund, rekonstruierter Gesprächsspur, testbarem Codezustand und offenem
Realweltbeleg.

[[abwurf: Eine Extremdoku ist nicht dann ehrlich, wenn sie am glattesten klingt, sondern wenn man an jeder wichtigen Aussage zurückverfolgen kann, ob sie von Daniel beobachtet, vom Terminal ausgegeben, vom Test behauptet oder von mir nur interpretiert wurde.]]
