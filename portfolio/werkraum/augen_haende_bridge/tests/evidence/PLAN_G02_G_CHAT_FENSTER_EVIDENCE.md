# PLAN-G02 Zyklus G: Chat-Fenster — Evidence

Datum: 2026-09-25, direkte Fortsetzung von Zyklus F in derselben Sitzung (Backup-Commit vor diesem Zyklus:
`ef28cffcf6`).

## Womit dieser Baustein arbeitet

R026 nennt Chat als die **dauerhafte** Darstellung desselben Ereignisses, im Unterschied zu Banner/Ticker (ephemer,
Zyklus F). `TerminalFenster.tippe()` existiert bereits (Docstring: „für Chat und Regie: zeichenweise als Eingabe an
die Sitzung“) — `ChatFenster` muss deshalb keinen eigenen Sitzungskanal bauen, nur einen `gesendet`-Callback
bedienen, den der spätere Besitzer an `terminal.tippe()` hängt.

## Build-Schritt

`src/augen_haende_bridge/koerper/chat_fenster.py` (neu): `ChatFenster(Fenster)`, schließt sich — anders als
`NachrichtFenster` — nicht von selbst.

- Reine Funktionen: `verlauf_anhaengen` (mit Obergrenze `MAX_VERLAUF=500`, R045: kein unbegrenztes Wachstum),
  `sichtbare_zeilen`, `maximaler_versatz` — alle ohne Fenster testbar.
- Tastatur: Zeichen hängen an die Eingabezeile an, Backspace löscht, Enter sendet (`empfangen("Daniel", …)` plus
  `gesendet`-Callback), Steuerzeichen und verirrte UTF-16-Ersatzzeichen werden verworfen.
- Mausrad blättert durch den Verlauf, gekappt an beiden Enden.
- Blinkender Eingabecursor, nur wenn das Fenster den Fokus hat.
- **Bewusste Lücken der ersten Fassung**, offen benannt statt vorgetäuscht: kein Zeilenumbruch (lange Nachrichten
  laufen ab), keine Chrome-Knöpfe (Schließen/Verbergen), keine eigene Größenänderung.
- `tests/test_koerper_chat_fenster.py` (neu, 23 Tests).
- `probes/koerper_smoketest.py` um einen vierten Abschnitt erweitert.

## Echter Wine-Lauf

Ein echtes `ChatFenster` gebaut, eine eingehende Nachricht per `empfangen()` eingespeist, dann die Zeichen „h“ und
„i“ über `bei_zeichen()` „getippt“ und mit Enter gesendet — das ist derselbe Code-Pfad, den echte `WM_CHAR`-Ereignisse
auslösen würden. Zweimal ausgeführt, identisch (Rohausgabe `PLAN_G02_G_CHAT_FENSTER_WINE_OUTPUT.json`):

```
rect: [600, 200, 920, 420]
verlauf: [["testagent", "Shader kompiliert!", "12:00"], ["Daniel", "hi", "12:00"]]
gesendete_texte: ["hi"]
eingabe_nach_senden_leer: true
schrift_aufgebaut: true
```

Die eingehende und die getippte Nachricht stehen beide korrekt im Verlauf, der `gesendet`-Callback wurde mit genau
dem getippten Text aufgerufen, die Eingabezeile ist danach leer, die Schrift wurde real über GDI aufgebaut.

## Was UNKNOWN bleibt

- Wine ist keine native Windows-Abnahme.
- Zeilenumbruch, Chrome-Knöpfe, eigene Größenänderung — bewusste Lücken dieser ersten Fassung.
- Die Verdrahtung `RauteFenster.sagen()` → `ChatFenster.empfangen()`/`NachrichtFenster` und
  `ChatFenster.gesendet` → `TerminalFenster.tippe()` ist als Callback-Anschlussstelle vorbereitet, aber noch nicht
  zusammengesteckt — das ist die Gesamtverdrahtung, kein einzelner Baustein mehr.

## Testergebnis

```
PYTHONPATH=src:. python3 -m unittest discover -s tests -q
Ran 353 tests (Ausgangsstand 330 nach Zyklus F)
FAILED (failures=2, errors=1)
```

Dieselben drei vorbestehenden, umgebungsbedingten Fehlschläge in `test_terminal_adapter.py`, unverändert.
`python3 tests/pruefe_koerper.py` — PASS (0 von 4).

## Stand nach diesem Zyklus

Alle vier Körperteile aus BE03 (Terminal, Fensterscanner-Vorbereitung, Raute, Banner/Ticker, Chat — Kamera/Mikrofon
aus Zyklus D) existieren jetzt als eigene, getrennt getestete `koerper/*.py`-Module. Was fehlt, ist keine neue
Einzelkomponente mehr, sondern die **Gesamtverdrahtung**: alle Fenster zusammen aus einer Startliste heraus
erzeugen, ihre Callbacks aneinanderhängen, den Fensterscanner an das Terminal anschließen, und daraus ein
PyInstaller-Paket bauen.
