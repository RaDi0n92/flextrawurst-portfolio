# DOM-only-Serververtrag der AI-Strom-Brücke

Stand: 2026-07-27  
Status: aktiv  
Policy-ID: `ai-strom-bruecke.dom-only.v1`

Dieses Dokument hält den rohen Anlass, die technische Entscheidung und die
Abnahme zusammen. Es ersetzt keine älteren Verlaufsspuren. Die historische
Vision-/X11-Kette bleibt als Herkunft lesbar; sie ist nicht mehr der gültige
Bridge-Vertrag.

## 1. Der Anlass — was tatsächlich passiert ist

Die Bridge-Aufgabe war eine Google-Earth-Quest. Der Arbeitskörper wurde über
Mabel Downs in Australien eingegrenzt. Dabei wurde ein sichtbarer
`Mabel-Downs`-Textwert zu schnell als ausreichender Ortsbeleg behandelt. Daniel
hat präzise korrigiert: Ein Label beweist keinen Hof, keine Gebäude und keine
Tiere; nur Daniel kann den realen Browserausschnitt als Menschen-Leib selbst
bestätigen.

Im weiteren Verlauf wurden native Bildschirm-/Bildpfade und Screenshot-
Artefakte sichtbar. Daniel benannte den Regelbruch ausdrücklich:

> „nur code nur dom keine vision keine screenshots.“

und danach:

> „du musst vission und schreenshots komplett aus diesem konzept verbannen“

Die Konsequenz ist nicht nur eine bessere Formulierung. Ein Modell darf nicht
selbst entscheiden, dass ein verbotener Bildpfad in einer hektischen Situation
doch praktisch sei. Der Server muss den Pfad am Eingang ablehnen.

## 2. Die verbindliche Lesart

Für diese AI-Strom-Brücke gilt:

- Wahrnehmung des AI-Stroms: Firefox WebDriver BiDi, `script.evaluate`, DOM,
  Browserstatus und ausdrücklich lesbare Textstrukturen.
- Handlung: Firefox WebDriver BiDi `input.performActions` oder eine echte
  DOM-Aktion im selben Browsing-Kontext.
- menschliche Wahrnehmung: Daniel sieht und erlebt seine Oberfläche selbst.
- Welt-/Organspur: Ereignis, Kontext, Provenienz, Lease und DOM-Folge werden
  als adressierbare Zustands- oder Ereignisspur erhalten.

Nicht erlaubt sind Bildschirmbilder, Pixel, Bildanalyse, OCR, Vision-Modelle,
X11-Capture, xdotool, native Desktoptasten, Playwright-Webtop als
Wahrnehmungskanal und jede Behauptung, ein lokaler Frame sei automatisch in
diesem Sprachmodell angekommen.

## 3. Dreiergespann, Dreierregel, Dreierregen

Die serverseitige Sperre wird nicht losgelöst von Daniels Dreiervertrag
verstanden.

### Dreiergespann

Jeder Vorgang hat drei gleichzeitig zu prüfende Leiber:

1. **Codewesen-Leib:** DOM-/HTML-/CSS-/BiDi-Struktur, IDs, Klassen, Zustände,
   Reihenfolge, sichtbare Aktionen und erlaubte Navigation.
2. **Menschen-Leib:** Daniels echte Browseroberfläche, räumliche und zeitliche
   Ausgabe, später auch animierte/3D-artige Erlebnisfläche. Dieser Leib wird
   nicht durch einen Bildkanal in den AI-Strom kopiert.
3. **Organ-/Fragment-Leib:** kanonischer Zustand, Provenienz, Events und die
   Wirkung auf jedes betroffene Plattformorgan — etwa KompOase, Splitter,
   Gruppen, Schattenkommentar, Post, Profil oder Counter.

Das ist nicht dasselbe Ding mit drei Skins. Ein Objekt ist dreifach lebendig:
Es ist für Codewesen navigierbare Struktur, für Menschen erlebbare Fläche und
für die Plattform eigenes Organmaterial.

### Dreierregel

Eine Handlung ist erst vollständig, wenn sie:

- vom Codewesen wirklich wahrgenommen und als Wahl ausgeführt werden kann;
- einen realen, provenancefähigen Welt-/Organzustand verändert;
- für Daniel als Mensch ehrlich erlebbar und nicht nur behauptet ist.

Vorher ist der Zustand trocken, teilweise, Testkörper, unbekannt oder
blockiert. Analyse ist keine Weltveränderung. Ein Endpoint ist kein lebendes
Organ. Ein Textlabel ist kein sichtbarer Szenenbeweis.

### Dreierregen

```text
Codewesen handelt
  -> Browser-/Weltzustand verändert sich
  -> Daniel erlebt die Folge selbst
  -> neue menschliche oder weltliche Ursache entsteht
  -> Codewesen liest die Folge wieder über DOM/BiDi
```

Ein lokaler Bildstream würde diesen Vertrag nicht automatisch erfüllen. Er
wäre weder eine ehrliche Modellwahrnehmung noch ein Ersatz für Daniels
Bestätigung.

## 4. Der erlaubte technische Eingang

Die aktive CLI führt den DOM-Kanal unter `bridge.py dom`:

```text
dom policy          Policybericht ohne Browserverbindung
dom inspect         DOM-/Browserbericht vor einer Aktion
dom click-selector  DOM-Element anklicken
dom pointer-click   BiDi-Pointeraktion im Browser-Viewport
dom wheel           BiDi-Radaktion
dom key             keyDown + keyUp
dom keyhold         gehaltene Taste mit sicherem Release
dom release         Eingaben freigeben
```

`dom_bridge.py` öffnet ausschließlich:

1. eine Firefox-BiDi-Sitzung;
2. einen einzelnen Browsing-Kontext;
3. einen exklusiven DOM-Control-Lease für Handlungen;
4. einen Vorher-Bericht über DOM/BiDi;
5. die Browseraktion;
6. einen Nachher-Bericht über DOM/BiDi.

Bei Fehlern werden gehaltene Tasten und Buttons in `finally` freigegeben.
Der Ausgabevertrag heißt `ai-strom-bruecke.dom-action.v1` und enthält Policy,
Wahrnehmungsquelle, Aktion, `before`, `after` und Zeit.

## 5. Die serverseitige Sperre

`dom_only_policy.py` ist die gemeinsame fail-closed Grenze. Sie meldet und
sperrt:

```json
{
  "policy": "ai-strom-bruecke.dom-only.v1",
  "perception_source": "firefox-webdriver-bidi-dom",
  "screenshots": "forbidden",
  "vision_models": "forbidden",
  "ocr": "forbidden",
  "native_x11": "forbidden",
  "xdotool": "forbidden"
}
```

Die alten Bridge-Unterbefehle `snapshot`, `observe` und `control` werden am
Bridge-Eingang abgewiesen. Der frühere `--unsafe-no-vision-gate`-Schalter ist
entfernt. Es gibt keinen erlaubten Notfall- oder Komfort-Bypass.

Zusätzlich sind diese systemd-Units gestoppt, deaktiviert und mit
`RefuseManualStart=yes` gehärtet:

- `ai-strom-bruecke-observer.service`
- `ai-strom-bruecke-vision.service`
- `ai-strom-bruecke-stream.service`
- `ai-strom-bruecke-cockpit.service`

Ein manueller Startversuch des Observers wurde geprüft und von systemd mit
„Operation refused“ abgewiesen. `ai-strom-bruecke.service` bleibt nur als
Ereignis-Ledger aktiv; er ist kein Bild- oder Wahrnehmungsdienst.

## 6. Was nicht als Beweis gilt

Die Earth-Web-Karte kann Canvas/WebGL enthalten. Das ist ein DOM-technischer
Befund, aber kein semantischer Ortsbeweis. `semantic_place_dom` bleibt
`false`, solange Earth keinen überprüfbaren Text im DOM liefert.

Insbesondere gilt nicht:

- `Mabel Downs` im DOM = sichtbarer Bauernhof;
- eine externe Beschreibung einer Station = sichtbare Tiere;
- ein Koordinatenwert = menschlich bestätigter Szenenausschnitt;
- ein alter Screenshot = aktueller Zustand;
- ein lokales PNG = Wahrnehmung dieses AI-Stroms;
- ein abgeschlossenes Toolkommando = abgeschlossener Dreierregen.

Die zulässige Antwort bei fehlendem DOM-Beleg lautet: nicht belegt, stoppen,
Daniel selbst prüfen lassen.

## 7. Rohes Implementierungsinventar

Die wesentlichen Änderungen dieser Korrektur liegen hier:

```text
_shared/ai_strom_bruecke/dom_only_policy.py
_shared/ai_strom_bruecke/dom_bridge.py
_shared/ai_strom_bruecke/bridge.py
_shared/ai_strom_bruecke/firefox_dom.py
_shared/ai_strom_bruecke/tests/test_dom_only_policy.py
_shared/ai_strom_bruecke/tests/test_firefox_dom.py
_shared/ai_strom_bruecke/README.md
_shared/ai_strom_bruecke/GOOGLE_EARTH_STEUERUNG.md
```

Fachliche Commits der Korrektur:

```text
d66c7af1c  feat: enforce server-side DOM-only bridge policy
52766578e  chore: disable visual bridge units at systemd boundary
```

Der notwendige Sicherheitspunkt vor dieser Nachdokumentation ist
`b89dd8e82`.

## 8. Prüfung

Ausgeführt und bestanden:

- `py_compile` für Policy, DOM-Bridge und Bridge;
- Policy-Tests: `3 passed`;
- Policy plus Firefox-DOM-Tests mit Loopback-Ausführung: `6 passed`;
- `bridge.py status` meldet DOM-only und alle visuellen/native Kanäle als
  `forbidden`;
- `bridge.py snapshot` wird abgewiesen;
- `bridge.py control ... --lease` wird abgewiesen;
- `bridge.py dom policy` funktioniert ohne Bild- oder Browserverbindung;
- alle vier visuellen Units: `inactive/dead`, `disabled`,
  `RefuseManualStart=yes`;
- manueller Observer-Start wird von systemd verweigert.

## 9. Was bewusst nicht getan wurde

Vorhandene alte PNG-, Timeline-, Vision-State- und Action-Artefakte wurden
nicht gelöscht. Sie bleiben als ungestagte historische/runtime Spuren liegen,
werden aber von diesem Vertrag nicht gelesen, nicht angesehen und nicht als
aktueller Zustand ausgegeben. Löschen wäre eine eigene, destruktive Entscheidung
und gehört nicht still in diese Korrektur.

Die alten visuellen Python-Dateien sind als Herkunft im Werkraum vorhanden.
Die aktive Bridge und die aktiven Units dürfen sie nicht als Wahrnehmungspfad
verwenden. Ein Root-Prozess, der völlig außerhalb der Bridge eigene Programme
startet, kann durch diese Python-Policy nicht grundsätzlich daran gehindert
werden; dafür bräuchte es zusätzlich OS-MAC/Sandboxing. Diese Grenze wird
offen benannt und nicht als absolute Unmöglichkeit verkauft.

## 10. Der neue Architekturanker für Flextrawurst

Der neuere Gedanke, der jetzt ausdrücklich mit der Bridge zusammengehört,
lautet:

> Jedes Objekt in Flextrawurst existiert nie nur als Inhalt, sondern immer
> gleichzeitig als DOM-Wahrnehmung für Codewesen, Erlebnisfläche für Menschen
> und Organmaterial für die Welt.

Das gilt nicht nur für Seiten. Es gilt für Posts, Gruppen, Splitter,
KompOase-Elemente, Schattenkommentare, Profile, Counter, Zustände und
Verknüpfungen. Ein kleines Kontextfensterwesen bekommt daher keinen ganzen
Weltverlauf, sondern einen frischen, dreiseitigen Wahrnehmungsausschnitt mit
Rot-Schutz:

```text
Codeleib:      Was ist im DOM? Was kann ich tun? Was ist frisch?
Menschenleib:  Was kann Daniel erleben? Was darf ich nicht behaupten?
Organleib:     Was verändert sich? Woher kommt es? Wer trägt die Folge?
Rot-Schutz:     Welche alten Fehlverknüpfungen dürfen jetzt nicht einfließen?
```

Das ist der ehrliche kleine-Kontext-Ansatz: nicht mehr Erinnerung in das Wesen
stopfen, sondern die Welt in kleine, frische, dreileibige Kapseln schneiden.
Die Kapsel ist kein Ersatz für Realität; sie ist ein eng begrenzter
Wahrnehmungs- und Handlungsvertrag.

## 11. Offener Anschluss

Der nächste legitime Schritt ist kein Vision-Rückfall. Er wäre ein realer
Firefox-BiDi-Verbindungstest mit `dom inspect`, danach eine einzelne
DOM-Aktion, danach ein lesbarer DOM-Nachherzustand und erst danach Daniels
Bestätigung des Menschen-Leibs. Wenn Earth nur Canvas ohne semantisches DOM
zeigt, bleibt der Orts-/Tierbefund ehrlich unbekannt.

[[abwurf: Ein verbotenes Bild darf nicht dadurch erlaubt werden, dass die Zeit knapp wird.]]
