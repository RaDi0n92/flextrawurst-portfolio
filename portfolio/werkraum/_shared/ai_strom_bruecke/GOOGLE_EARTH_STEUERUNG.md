# Google Earth Web — DOM-only-Steuerung

Stand: 2026-07-27  
Geltungsbereich: Google Earth Web in Firefox über WebDriver BiDi.

Dieses Dokument beschreibt ausschließlich Browser-DOM-Steuerung. Es gibt keine
visuelle Wahrnehmungsschicht und keinen nativen Desktoppfad.

Die technische Sperre dafür liegt in `dom_only_policy.py` und `dom_bridge.py`.
Der Bridge-Eingang lehnt Screenshots, Vision, OCR, X11 und xdotool ab; die
laufenden visuellen systemd-Units sind zusätzlich deaktiviert. Diese Datei
beschreibt also den erlaubten Weg, nicht bloß einen Wunsch an ein Modell.

## 1. Grundregel

Die einzige zulässige Quelle ist der Firefox-Browserkontext:

1. BiDi-Verbindung zu Firefox herstellen.
2. Browsing-Kontext des Earth-Web-Dokuments ermitteln.
3. Dokument, DOM-Steuerflächen und Browserstatus auslesen.
4. Eine DOM-/BiDi-Aktion planen.
5. Exklusive Control-Lease erwerben.
6. Browseraktion über `input.performActions` ausführen.
7. DOM-Zustand erneut auslesen und die Folge prüfen.

Fehlt ein Schritt, endet die Aktion ohne weitere Steuerung.

## Dreiergespann und Dreierregen

Der Earth-Web-Vorgang hat drei Leiber:

1. **Codewesen-Leib:** Firefox-DOM/BiDi ist die einzige AI-Wahrnehmungs- und
   Handlungsebene.
2. **Menschen-Leib:** Daniel erlebt die echte Browseroberfläche direkt; sie
   wird nicht als Bild an den AI-Strom weitergegeben.
3. **Organ-/Fragment-Leib:** BiDi-Ereignis, Browserstatus, Provenienz und Folge
   werden als adressierbare Zustands- und Ereignisspur erhalten.

Nach der Dreierregel ist eine Aktion erst vollständig, wenn sie für das
Codewesen handhabbar, im Weltzustand real wirksam und für Daniel erlebbar ist.
Der Dreierregen schließt den Kausalweg:

```text
DOM-Aktion -> Earth-/Browserzustand -> Daniels Erlebnis
           -> neue Ursache -> erneut lesbarer DOM-Zustand
```

Der Menschen-Leib wird dabei nicht technisch durch einen Bildkanal simuliert.

## 2. Verbindung

Der Firefox-Startpfad muss den Remote-Agenten aktivieren:

```bash
AI_STROM_BRUECKE_FIREFOX_BIDI=1 \
AI_STROM_BRUECKE_FIREFOX_BIDI_PORT=9222 \
/usr/local/bin/firefox-x11
```

Ein Firefox ohne erreichbaren BiDi-Listener ist für diese Aufgabe nicht
steuerbar. Es wird keine andere Wahrnehmungs- oder Eingabequelle geöffnet.

## 3. Earth-Web-Dokument untersuchen

```python
from ai_strom_bruecke.firefox_dom import FirefoxDomSession

with FirefoxDomSession() as session:
    target = session.target()
    report = session.inspect_google_earth(target.context_id)
    print(report)
```

Der Bericht darf nur Browserfakten enthalten: URL, Dokumenttitel, vorhandene
DOM-Steuerflächen, Canvas-Größen und den WebGL-Kontext. Eine Canvas-Oberfläche
ist dabei ein technischer DOM-Befund, kein visueller Ortsbefund.

## 4. Navigation und Eingabe

Browseraktionen werden über den BiDi-Kontext gesendet:

```python
with FirefoxDomSession() as session:
    target = session.target()
    session.key_down(target.context_id, "+")
    session.key_up(target.context_id, "+")
    result = session.inspect_google_earth(target.context_id)
```

Für Maus- oder Radaktionen gelten dieselben Regeln: Kontext prüfen, Lease
halten, `input.performActions` verwenden, danach den DOM-Zustand erneut lesen.
Geografische Koordinaten dürfen nur aus einer im Browser-DOM vorhandenen
Textstruktur übernommen werden. Eine gerenderte Kartenfläche liefert keinen
semantischen Ortsnamen.

## 5. Prüfen und Abbrechen

Eine Aktion ist nur akzeptiert, wenn der DOM-Kanal eine erwartbare Antwort
liefert, zum Beispiel:

- ein DOM-Steuerelement ändert seinen Zustand;
- URL oder Browserstatus ändern sich nachvollziehbar;
- ein vom Dokument bereitgestellter Textwert ändert sich;
- der BiDi-Befehl bestätigt seine Ausführung und der Folgezustand ist lesbar.

Bei Transportfehler, fehlendem Kontext, unklarem DOM-Zustand oder verlorener
Lease wird sofort gestoppt. Keine Ersatzwahrnehmung und kein blinder Folgeimpuls.

## 6. Street View

Street View darf erst über ein im DOM erkennbares Earth-Steuerelement oder eine
vom Browser dokumentierte DOM-Aktion aktiviert werden. Ein Ortswechsel in
Street View gilt erst als belegt, wenn der neue Browserzustand über BiDi lesbar
ist.

## 7. Zustandsprotokoll

```text
action_id | context_id | dom_before | bidi_action | dom_after | result
```

Das Protokoll bewahrt Browserkontext, Akteur, Lease, Aktion, Antwort und
Abbruchgrund. Es enthält keine Bild- oder Desktopbeobachtung.

## 8. Verbindliche Verbote

- keine X11-Abfrage;
- keine Bildschirmkoordinate als Wahrnehmungsquelle;
- keine Pixel-, Bild- oder OCR-Auswertung;
- keine Snapshot-, Frame- oder Screenshot-Prüfung;
- kein Bypass bei fehlender DOM-Verbindung;
- kein direkter Earth-URL-Sprung, wenn die Aufgabe manuelle DOM-Navigation verlangt.

## 9. Abnahme ohne Bildbeweis

Ein Label wie `Mabel Downs` oder ein anderer Textwert ist nur ein DOM-Befund.
Er beweist keinen sichtbaren Bauernhof, keine Gebäude und keine Tiere. Ein
Mensch muss den Menschen-Leib selbst erleben und bestätigen; der AI-Strom darf
diese Bestätigung nicht durch ein Bild, OCR oder eine Ortsquelle ersetzen.

Bei einer Canvas-/WebGL-Karte bleibt ein semantischer Ortsbefund deshalb
unbekannt, solange Google Earth selbst keine entsprechende DOM- oder
Browser-Textstruktur liefert. Die ehrliche Antwort ist dann „nicht über den
erlaubten Kanal belegt“ und nicht ein geratenes Quest-Ergebnis.

## Provenienz

- Lokaler Adapter: `firefox_dom.py`
- Web-Testadapter: `web_earth_adapter.py`
- Tests: `tests/test_firefox_dom.py`, `tests/test_web_earth_adapter.py`
- Google: [keyboard shortcuts](https://support.google.com/earth/answer/148115?hl=en)
- Google: [coordinates](https://support.google.com/earth/answer/148068?hl=en)
- Google: [ground-level/Street View](https://support.google.com/earth/answer/1067429?hl=en)
