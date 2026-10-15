# PLAN-G02 Zyklus J: Banner und Ticker als zwei gleichzeitige Fenster — Evidence

Datum: 2026-09-30. Sicherheitspunkt: `61591f367f`.

## Anlass

`ERLEBEN.md`, „Was ein Agent sagt, kommt auf zwei Zeitebenen an“: das Raum-Banner (3,3 s, breit und fast mittig im
aktiven Programm, mit Zug zur Raute, kontinuierlich durchsichtiger) und der Rauten-Ticker (6,6 s, klein, direkt an
der Raute). `nachricht_fenster.py` war bis Zyklus F ein einzelnes Fenster mit hartem Wechsel zwischen zwei Phasen.

## Build-Schritt

- `src/augen_haende_bridge/koerper/nachricht_fenster.py` neu: `BannerFenster` und `TickerFenster`, beide
  klickdurchlässig und ohne Fokus. Reine Funktionen: `banner_breite` (höchstens 80 % des Ziels),
  `banner_position` (Zielmitte, 35 % des Wegs zur Raute, in den Zielbereich geklemmt), `banner_alpha` (linear von
  255 auf 0 über 3,3 s), `ticker_position` (rechts an der Raute, auf ihrer Mitte).
- `src/augen_haende_bridge/koerper/erster_koerper.py`: `sagen()` erzeugt beide gleichzeitig; Zielbereich über einen
  Geber, Standard die Arbeitsfläche des Desktops (R120); der Ticker folgt der verschobenen Raute.
- Tests: `tests/test_koerper_nachricht_fenster.py` neu, `tests/test_koerper_erster_koerper.py` angepasst.

## Ergebnis

Core: 395 Tests, grün bis auf die drei bekannten, umgebungsbedingten Fehlschläge in `test_terminal_adapter.py`.

Wine, echte Zeit (Rohausgabe `PLAN_G02_J_BANNER_TICKER_WINE_OUTPUT.json`):

- Banner-Deckkraft zurückgelesen bei 259 / 511 / 764 / 1016 / 1269 / 1523 / 1778 / 2030 / 2284 / 2538 / 2788 /
  3043 ms: 237 / 217 / 196 / 178 / 158 / 137 / 119 / 99 / 79 / 61 / 41 / 20 — kontinuierlich fallend.
- Banner schließt sich nach **3304 ms**, der Ticker ist bei 4 s noch da und schließt sich nach **6607 ms**.
- Beide klickdurchlässig (`WindowFromPoint` an ihrer Mitte trifft keins von beiden).
- Banner im Zielbereich (Arbeitsfläche `[0, 0, 1280, 1024]`) und zur Raute (oben links) gezogen; Ticker direkt
  rechts an der Raute.
- Über `ErsterKoerper`: `raute.sagen()` erzeugt Banner und Ticker gleichzeitig.

Playwright: nicht anwendbar. Native Windows: **UNKNOWN**.

## Offen

- Zielbereich ist bis zum nächsten Stein immer die Arbeitsfläche; das gebundene Fenster als Zielbereich folgt mit
  dem Scanner-Umbau.
- Banner, das einem sich bewegenden Zielfenster folgt (R027 „Fenster bewegen/skalieren … ohne Abdriften“), ist G05.
