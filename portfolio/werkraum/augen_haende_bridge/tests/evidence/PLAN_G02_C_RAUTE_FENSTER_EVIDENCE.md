# PLAN-G02 Zyklus C: Raute-Fenster — Evidence

Datum: 2026-09-24, direkte Fortsetzung von Zyklus B in derselben Sitzung (Backup-Commit vor diesem Zyklus:
`a8c892688d`, der Abschluss von Zyklus B).

## Warum nur die Raute, nicht Banner/Ticker/Chat

`PLAN.md` zählt für G02 „die Raute mit Banner, Ticker und Chat“ zum ersten Körper. `ANFORDERUNGEN.md` führt die
zugehörigen Register-Zeilen aber ausdrücklich als **offen**: R023 (Raute ist Sprechort), R024 (Name/Farbe/Hotkey/
Position einstellbar), R026 (ein Ereignis als Ticker/Banner/Chat gleichzeitig) und R027 (Banner räumlich zur Raute
orientiert) — keine davon legt fest, ob Banner, Ticker und Chat eigene Fenster sind oder Teile eines gemeinsamen.
Das ist eine Architekturentscheidung (wie viele Fenster, welche Beziehung zueinander), die laut den eigenen Regeln
dieses Systems nicht allein getroffen wird. Dieser Zyklus baut deshalb bewusst nur die Raute selbst — Form, Farbe,
Kürzel, Ziehen, Klick, `sagen()` als Anschlussstelle — und benennt Banner/Ticker/Chat als offenen nächsten Schritt
statt sie implizit mitzuentscheiden.

## Build-Schritt

`src/augen_haende_bridge/koerper/raute_fenster.py` (neu): `RauteFenster(Fenster)`.

- Form: Raute aus vier Eckpunkten (`umriss()`), über `setze_form()` als Fensterregion gesetzt — kein Rechteck,
  kein flächiges Overlay (R118).
- Farbe und Kürzel: `farbe_hex`/`kuerzel` optional; ohne Angabe deterministisch aus `stil.AGENTENFARBEN` bzw.
  `stil.kuerzel_aus_name()` abgeleitet (diese eine Zeile in `__init__` läuft nach `require_windows()` und ist damit
  unter Linux nicht direkt aufrufbar — siehe „Was UNKNOWN bleibt“).
- Ziehen gegen Klick: Anker und laufende Position werden über `maus_position()` (Bildschirmkoordinaten via
  `GetCursorPos`) verglichen, nicht über das client-relative `lParam` von `WM_MOUSEMOVE` — weil sich das
  Bezugssystem sonst mit jedem `SetWindowPos`-Aufruf mitverschiebt und die Deltaberechnung sofort falsch würde.
  Eine Bewegung unter 4 Pixeln zählt als Klick, darüber als Zug; ein Zug löst keinen Klick aus, ein verlorener
  Maus-Capture (`WM_CAPTURECHANGED`) setzt den Zustand sauber zurück.
- `sagen(text)`: merkt sich die letzte Nachricht und ruft einen Callback. Zeichnet selbst noch kein Banner und
  keinen Ticker — das ist die Anschlussstelle für den jeweiligen Baustein, sobald die Fensterfrage entschieden ist.
- `tests/test_koerper_raute_fenster.py` (neu, 12 Tests): Windows-Gating des Konstruktors, `umriss()`-Geometrie,
  `treffer()` immer `HTCLIENT` (Zug wird selbst gehandhabt, kein System-Fensterzug), die Zieh-gegen-Klick-
  Zustandsmaschine (mit und ohne gedrückte Maustaste, unterhalb/oberhalb der Schwelle, nach Verlust der
  Mauserfassung), `sagen()`, Schriftfreigabe bei Zerstörung. Gebaut per `object.__new__`-Fixture ohne echten
  Konstruktor, wie schon bei `terminal_fenster.py`.

## Testergebnis

```
PYTHONPATH=src:. python3 -m unittest discover -s tests -q
Ran 299 tests (Ausgangsstand 287 nach Zyklus B)
FAILED (failures=2, errors=1)
```

Dieselben drei vorbestehenden, umgebungsbedingten Fehlschläge in `test_terminal_adapter.py` wie in Zyklus B,
unverändert, kein Bezug zu `raute_fenster.py`.

`python3 tests/pruefe_koerper.py` — PASS (0 von 4 beanstandeten Dingen), weiterhin gegen den alten
`client_windows/overlay_app.py`, nicht gegen `koerper/`.

## Was UNKNOWN bleibt

- Echtes Fensterverhalten (Rautenform auf dem Bildschirm, tatsächliches Ziehen mit der Maus, Deckkraft) — braucht
  Windows oder Wine, wie bei `fenster.py`/`terminal_fenster.py` bereits vermerkt.
- Die eine Zeile der deterministischen Standardfarbwahl (`farbe_hex or stil.AGENTENFARBEN[...]`) läuft im
  Konstruktor nach `require_windows()` und wurde deshalb nicht gegen den echten Konstruktor geprüft, nur gelesen.
- Ob mehrere Rauten gleichzeitig (mehrere Agenten) korrekt getrennt bleiben, ist noch ungeprüft — hier wurde nur
  eine einzelne Raute betrachtet.

## Was als Nächstes offen ist (bewusst nicht in diesem Zyklus entschieden)

Banner (3,3 s, fenstergebunden, Zugkraft zur Raute), Ticker (6,6 s, direkt neben der Raute) und Chat (dauerhaft,
R026) brauchen eine gemeinsame Fensterentscheidung, bevor gebaut wird: eigene Fenster je Bauteil, oder eine
erweiterte Zeichenfläche der Raute selbst. Das ist eine Architekturfrage im Sinne der eigenen Drei-Stopp-Fragen
dieses Systems und wird benannt statt allein entschieden.
