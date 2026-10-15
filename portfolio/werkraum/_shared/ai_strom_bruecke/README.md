# AI-Strom-Brücke — DOM-only-Vertrag

Die AI-Strom-Brücke ist der gemeinsame Andockpunkt für externe AI-Ströme an
den laufenden virtuellen Desktop. Wenn Daniel **„AI-Strom-Brücke“** sagt,
arbeiten alle beteiligten Ströme über diesen Vertrag und behaupten keine eigene,
dauerhafte Anwesenheit im System.

## Verbindliche Wahrnehmungsgrenze

Für dieses Konzept ist Google Earth Web ausschließlich ein Firefox-DOM-Ziel.
Wahrnehmung erfolgt über den Firefox-WebDriver-BiDi-Kanal und über nichts
anderes. Die geografische Fläche bleibt als Canvas/WebGL-Oberfläche klassifiziert;
Ortsnamen werden nur übernommen, wenn sie tatsächlich im DOM vorliegen.

Bildschirmbilder, Bildanalyse, OCR und native X11-Wahrnehmung gehören nicht zu
diesem Vertrag. Es gibt keinen Ersatzpfad und keinen Bypass.

## Dreiergespann, Dreierregel und Dreierregen

Die Brücke folgt dem bestehenden Dreiergespann:

1. **Codewesen-Leib:** Der externe AI-Strom nimmt den Browser als DOM-/BiDi-
   Struktur wahr, plant darin und handelt darin.
2. **Menschen-Leib:** Daniel erlebt die reale Browseroberfläche selbst. Dieser
   Leib wird nicht in einen AI-Bildkanal gespiegelt.
3. **Organ-/Fragment-Leib:** Events, Browserzustand, Provenienz und Folgen
   bleiben als adressierbare Weltspur erhalten.

Die **Dreierregel** verlangt, dass ein Vorgang in allen drei Leibern gültig ist:
handhabbar für das Codewesen, real wirksam im gemeinsamen Zustand und für den
Menschen direkt erlebbar.

Der **Dreierregen** ist der Rücklauf:

```text
DOM-Handlung des Codewesens
  -> kanonischer Browser-/Weltzustand
  -> Daniel erlebt die Folge direkt
  -> neue menschliche oder weltliche Ursache
  -> diese Ursache wird wieder über DOM/BiDi lesbar
```

Der Dreierregen ist kein Bildstrom und kein Versprechen automatischer
Wahrnehmung durch das Sprachmodell.

## Was die Brücke trägt

- `dom`: Firefox-BiDi liest Dokument, DOM-Steuerflächen, Canvas/WebGL-Fakten
  und den Browserzustand.
- `events`: Angenommene Browserereignisse werden als JSON-Lines mit Zeit, Rolle,
  Kontext und Herkunft gespiegelt. Rohereignisse werden nicht zu einer erfundenen
  Absicht umgedeutet.
- `dom`-control: Ein AI-Strom darf Browseraktionen nur über Firefox-BiDi und
  mit einer exklusiven DOM-Control-Lease senden. Mehrere Ströme handeln niemals
  gleichzeitig.
- `terminal`: Terminalarbeit ist eine getrennte Fähigkeit und nicht automatisch
  Browserkontrolle.

## Serverseitige Durchsetzung — Stand 2026-07-27

Diese Regel ist nicht nur eine Konzeptaussage. Der Bridge-Eingang trägt die
Policy `ai-strom-bruecke.dom-only.v1`.

```bash
python3 bridge.py status
python3 bridge.py dom policy
python3 bridge.py dom inspect
```

`bridge.py snapshot`, `bridge.py observe` und `bridge.py control` werden
fail-closed abgewiesen. Der frühere Vision-Gate-Bypass ist entfernt. Die
Einzelheiten, der Regelbruch, die Abnahme und die verbleibenden Grenzen stehen
in [[DOM_ONLY_SERVER_POLICY.md]] beziehungsweise in
`_codex/notizen/2026-07-27-dom-only-vorfall.md`.

Die vier visuellen systemd-Units — Observer, Vision, Stream und Cockpit — sind
gestoppt, deaktiviert und mit `RefuseManualStart=yes` versehen. Der laufende
Hauptdienst protokolliert nur Ereignisse. Dadurch gibt es innerhalb der
AI-Strom-Brücke keinen aktiven Bild-, Vision-, OCR- oder X11-Pfad.

Die Sperre gilt für die Bridge. Ein Root-Prozess außerhalb der Bridge kann auf
einem Unix-System grundsätzlich eigene Programme starten; das ist eine
Betriebs- und Rechtefrage, kein stiller Bestandteil dieses Vertrags.

## Schnellzugriff

```bash
PYTHONPATH=/root/werkraum/_shared \
  python3 /root/werkraum/_shared/ai_strom_bruecke/bridge.py dom policy
PYTHONPATH=/root/werkraum/_shared \
  python3 /root/werkraum/_shared/ai_strom_bruecke/bridge.py dom inspect
python3 /root/werkraum/_shared/ai_strom_bruecke/bridge.py events --follow
```

Der konkrete DOM-Adapter ist `firefox_dom.py`. Er spricht mit Firefox über
WebDriver BiDi, liest mit `script.evaluate` den vorhandenen Dokumentzustand und
sendet Browseraktionen über `input.performActions`.

## Firefox-BiDi-Voraussetzung

Firefox muss mit dem Remote-Agenten gestartet sein, zum Beispiel:

```bash
AI_STROM_BRUECKE_FIREFOX_BIDI=1 \
AI_STROM_BRUECKE_FIREFOX_BIDI_PORT=9222 \
/usr/local/bin/firefox-x11
```

Ein bereits laufender Firefox ohne BiDi-Listener kann nicht nachträglich in
diesen Kanal umetikettiert werden. Der Adapter verweigert eine nicht verbundene
DOM-Aktion.

## Google Earth Web

`FirefoxDomSession.inspect_google_earth()` liefert ausschließlich überprüfbare
Browserfakten:

```python
from ai_strom_bruecke.firefox_dom import FirefoxDomSession

with FirefoxDomSession() as session:
    target = session.target()
    report = session.inspect_google_earth(target.context_id)
```

Navigation, Zoom und Tastatursteuerung laufen über den DOM-/BiDi-Kontext des
aktiven Earth-Web-Dokuments. Ein semantischer Ortsbefund darf nur aus DOM-Daten
oder einer ausdrücklich vom Browser bereitgestellten Textstruktur entstehen.
Canvas-Pixel werden nicht als Wahrnehmungsquelle verwendet.

## Ereignisvertrag

```json
{
  "schema": "ai-strom-bruecke.event.v1",
  "ts": 1785180000.0,
  "origin": "firefox-bidi",
  "kind": "browser.input",
  "context": "<browsing-context-id>",
  "role": "controller",
  "actor": "<ai-strom>"
}
```

Der Ledger ist append-only. `role` und `actor` müssen die Herkunft der Aktion
sichtbar machen; der Browserkontext muss identifizierbar bleiben.

## Zustandsmaschine

```text
CONNECT_BIDI
  -> DISCOVER_CONTEXT
  -> INSPECT_DOM
  -> PLAN_DOM_ACTION
  -> ACQUIRE_CONTROL_LEASE
  -> PERFORM_BROWSER_ACTION
  -> READ_DOM_RESULT
  -> ACCEPT oder STOP
```

Jede Aktion braucht einen frischen DOM-Zustand vor der Handlung und eine
prüfbare DOM-Antwort danach. Fehlt der BiDi-Kanal oder bleibt die DOM-Antwort
aus, wird nicht weitergesteuert.

## Grenzen

„Live“ bedeutet hier: Der verbundene DOM-Adapter kann den aktuellen
Browserzustand abfragen und Browserereignisse abonnieren. Es bedeutet nicht,
dass ein Sprachmodell ungefragt jeden Zustand erhält.

Die vorhandene Windows-/GENI-Bridge bleibt eine eigene Provenienzschicht. Sie
wird nicht umbenannt und nicht durch diese Brücke ersetzt.

Die vorhandenen nativen, bildbasierten oder X11-bezogenen Runtime-Dateien sind
Altbestand außerhalb dieses Vertrags. Sie dürfen nicht als Implementierung des
DOM-only-Konzepts verwendet oder als dessen Wahrnehmung ausgegeben werden.
