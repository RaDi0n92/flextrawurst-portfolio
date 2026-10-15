# PLAN-G02 Zyklus F: Nachricht-Fenster (Banner/Ticker) — Evidence

Datum: 2026-09-25, direkte Fortsetzung von Zyklus E in derselben Sitzung (Backup-Commit vor diesem Zyklus:
`7502aed729`).

## Architekturfrage geklärt

Vor diesem Zyklus stand offen, ob Banner, Ticker und Chat drei eigene Fenster sind oder eine erweiterte
Zeichenfläche der Raute. Frage an Daniel gestellt; Antwort: „so wie es geschrieben steht“ — gemeint ist der
historische Rauten-Anker-Entwurf im Bridge-Skill (Abschnitt 2, dort ausdrücklich als Orientierung markiert, nicht
als unverändert auszuführender Vertrag): „Stufe 1 (Raum-Banner): 3,3 Sekunden … Stufe 2 (Rauten-Ticker): 6,6
Sekunden (doppelte Zeit)“. Zusammen mit R026 („Gleiches Ereignis als 6,6-s-Ticker, 3,3-s-Fade-Banner und
Chatnachricht … eine Nachrichten-ID in drei Darstellungen“) gelesen als: **ein** Fenster mit zwei zeitlichen
Phasen für Banner/Ticker, nicht zwei unabhängige Fenster. Der Chat bleibt ein eigener, noch nicht gebauter
Baustein mit eigener Lebensdauer (dauerhaft statt ephemer).

## Build-Schritt

`src/augen_haende_bridge/koerper/nachricht_fenster.py` (neu): `NachrichtFenster(Fenster)`.

- Reine Geometriefunktionen (`banner_groesse`, `banner_position`, `ticker_groesse`, `ticker_position`), unabhängig
  von jedem Fenster testbar: Banner zentriert über der Raute mit Abstand (die „Zugkraft zur Raute“ als räumliche
  Nähe nach oben), Ticker direkt rechts neben der Raute, vertikal auf ihrer Mitte.
- Phasenwechsel über zwei Timer: `TIMER_PHASE` nach 3,3 s wechselt Optik und Position/Größe von Banner zu Ticker;
  `TIMER_SCHLIESSEN` nach 6,6 s Gesamtdauer schließt das Fenster selbst.
- `tests/test_koerper_nachricht_fenster.py` (neu, 9 Tests): Geometrie direkt, Phasenwechsel per
  `object.__new__`-Fixture wie bei `terminal_fenster.py`/`raute_fenster.py`.

## Echter Wine-Lauf

`probes/koerper_smoketest.py` um einen dritten Abschnitt erweitert: ein echtes `NachrichtFenster`, anchored an
eine echte, zuvor erzeugte `RauteFenster`-Position, unter Wine gebaut. Der Phasenwechsel wurde direkt ausgelöst
(`nachricht._zu_ticker_wechseln()`), statt die echten 3,3 Sekunden abzuwarten — das prüft dieselbe Methode, die der
Timer im echten Betrieb aufruft, nur ohne die Wartezeit. Zweimal ausgeführt, identisch
(Rohausgabe: `PLAN_G02_F_NACHRICHT_FENSTER_WINE_OUTPUT.json`):

```
banner_rect: [152, 155, 297, 188]   ticker_rect: [254, 215, 361, 233]
banner_ueber_der_raute: true        ticker_rechts_neben_der_raute: true
ticker_kleiner_als_banner: true     schriften_aufgebaut: true
```

Die Raute stand bei diesem Lauf bei `[200, 200, 248, 248]`. Der Banner sitzt echt oberhalb (`188 < 200`... genauer:
Banner-Unterkante 188 liegt oberhalb der Raute-Oberkante 200, mit dem konfigurierten Abstand), der Ticker echt
rechts daneben (Ticker-Linke 254 ≥ Raute-Rechts 248) und ist flächenmäßig kleiner als der Banner. Beide Phasen
haben real über GDI aufgebaute Schriften.

## Was UNKNOWN bleibt

- Wine ist keine native Windows-Abnahme (wie in Zyklus E).
- Der Chat-Baustein selbst ist noch nicht gebaut.
- Die Verdrahtung von `RauteFenster.sagen()` zu einem echten `NachrichtFenster` (wer besitzt/konstruiert es, mit
  welcher aktuellen Raute-Position) ist als Callback-Anschlussstelle vorbereitet, aber noch nicht verdrahtet —
  das ist Teil der späteren Gesamtverdrahtung (Stein „Verdrahtung/Einstellungen“ aus der vorherigen Planung).
- Das Fade-Out am Ende der Bannerphase (per Deckkraft-Rampe statt hartem Schnitt) ist noch nicht gebaut; aktuell
  wechselt die Optik hart bei 3,3 s.

## Testergebnis

```
PYTHONPATH=src:. python3 -m unittest discover -s tests -q
Ran 330 tests (Ausgangsstand 321 nach Zyklus E)
FAILED (failures=2, errors=1)
```

Dieselben drei vorbestehenden, umgebungsbedingten Fehlschläge in `test_terminal_adapter.py` wie in den vorherigen
Zyklen, unverändert. `python3 tests/pruefe_koerper.py` — PASS (0 von 4).

## Was als Nächstes offen ist

Chat-Baustein bauen; `RauteFenster.sagen()` mit einem echten `NachrichtFenster` verdrahten; Terminal-Geometrie-Delta
und cv2/numpy-Wine-Kompatibilität aus Zyklus E klären; Fensterscanner-Anbindung; PyInstaller-Paket.
