# PLAN-G02 Zyklus H: Gesamtverdrahtung (ErsterKoerper) — Evidence

Datum: 2026-09-30, Fortsetzung derselben Sitzung nach Zyklus G. Auslöser: Daniel fragte, ob schon eine exe fertig
sei; Antwort war ein klares Nein mit konkreter Lückenliste (kein Gesamtprogramm, kein Fensterscanner-Anschluss,
kein PyInstaller-Paket, kein echtes Windows). Daniel: „ja so meinte ich das. dann rann an die arbeit oder?“ — Auftrag,
genau diese Lücken anzugehen.

## Build-Schritt

### `scanner_anbindung.py` (neu)

Verbindet den Scanner-Knopf mit dem bereits vorhandenen, unveränderten `windows_scanner.py`/`windows_capture.py`
(G01/V3.4): scannen (Frame + gekoppeltes Fensterinventar), das Ergebnis als natives Popup-Menü an der Klickstelle
zeigen, bei Auswahl `terminal.setze_ziel()` aufrufen. Reine Funktionen (`snapshot_zu_eintraegen`, `eintrag_zu_ziel`)
für die Logik, `mache_scanner_callback()` für die Verdrahtung — alles mit injizierbarer Scanner-/Capture-/Menü-API,
genau wie schon bei `windows_scanner.py`/`windows_capture.py` selbst üblich.

`TerminalFenster.scanner_verbinden()` (neue, kleine öffentliche Methode) ergänzt: der echte Scanner-Callback
braucht das bereits gebaute Terminal selbst (`hwnd`, `setze_ziel`), ist zur Konstruktionszeit des Terminals also
noch nicht verfügbar — dieses Henne-Ei wird durch nachträgliches Verbinden gelöst.

### `erster_koerper.py` (neu)

`ErsterKoerper`: komponiert Raute, Terminal, Nachricht und Chat zu einem Ganzen pro gestartetem Agenten (R119).
Alle vier Fensterklassen sind als Konstruktorparameter injizierbar (`raute_klasse` usw.) — deshalb ist die gesamte
Verdrahtungslogik ohne Windows/Wine testbar, obwohl jede einzelne Fensterklasse selbst `require_windows()` verlangt.

Verdrahtung:

- `RauteFenster.sagen()` → neues `NachrichtFenster` (eine noch offene alte wird vorher geschlossen) **und**
  `ChatFenster.empfangen()`, falls der Chat schon offen ist.
- Klick auf die Raute → `ChatFenster` öffnen bzw. ein-/ausblenden.
- `ChatFenster.gesendet` → `TerminalFenster.tippe()` (der Weg zurück in die Sitzung existierte dort schon).
- `TerminalFenster`s Scanner-Knopf → `scanner_anbindung.mache_scanner_callback()`.

Was bewusst **nicht** drinsteckt: die echte Relay-/Sitzungsverbindung (`transport_client.py`/`bridge_runtime.py`
aus PLAN-G02-A). `terminal_senden` ist injizierbar, Standardwert ein No-Op — kein vorgetäuschtes Echo.

`tests/test_koerper_scanner_anbindung.py` (7 Tests), ein neuer Test für `scanner_verbinden` in
`test_koerper_terminal_fenster.py`, `tests/test_koerper_erster_koerper.py` (15 Tests) — 22 neue Tests insgesamt,
keiner braucht Windows.

## Echter Wine-Lauf: die komplette Kette, nicht nur einzelne Fenster

`probes/koerper_smoketest.py` um einen fünften Abschnitt erweitert: ein echtes `ErsterKoerper` (mit den echten
Fensterklassen, keine Fakes) unter Wine gebaut und die komplette Kette ausgelöst — zweimal ausgeführt, identisch
(Rohausgabe `PLAN_G02_H_GESAMTVERDRAHTUNG_WINE_OUTPUT.json`):

```json
{
  "nachricht_entstand_durch_sagen": true,
  "chat_entstand_durch_klick": true,
  "chat_verlauf": [["Daniel", "ok", "12:0x"]],
  "terminal_hat_getipptes_empfangen": true,
  "scanner_frame_breite_hoehe": [1280, 1024],
  "scanner_fand_eigene_fenster": true,
  "scanner_anzahl_ziele": 5
}
```

- `koerper.raute.sagen("Shader kompiliert!")` — der echte, öffentliche Weg, den ein sprechender Agent nutzen würde
  — hat wirklich ein neues `NachrichtFenster` erzeugt (`koerper.nachricht`, echtes `GetWindowRect` gelesen).
- `koerper.raute._klick()` — derselbe interne Callback, den ein echter Klick ohne Zug auslösen würde — hat wirklich
  ein `ChatFenster` geöffnet.
- Echtes Tippen von „ok“ + Enter im Chat landet im Chat-Verlauf **und** kommt über
  `ChatFenster.gesendet → TerminalFenster.tippe() → _eingabe() → terminal_senden` tatsächlich beim injizierten
  Test-Callback an (`terminal_hat_getipptes_empfangen: true`) — die volle Kette Raute-Klick → Chat → Terminal
  funktioniert real, nicht nur laut Verdrahtungscode.
- Der **echte** `WindowsWindowScanner`/`WindowsScreenCapture` (kein Fake!) hat unter Wine den echten virtuellen
  Bildschirm erfasst (1280×1024) und 5 reale Ziele gefunden — darunter die soeben selbst erzeugten Fenster
  (`scanner_fand_eigene_fenster: true`). Das native Popup-Menü (`TrackPopupMenuEx`) selbst wurde bewusst **nicht**
  automatisiert ausgelöst — das ist ein blockierender, auf echte Mausbedienung wartender Aufruf; ihn ohne echte
  Maus zu simulieren wäre keine ehrliche Prüfung. Geprüft wurde stattdessen die Scan-/Capture-Ebene direkt, die
  `mache_scanner_callback()` genauso aufruft.

## Was UNKNOWN bleibt

- Wine ist keine native Windows-Abnahme.
- Das native Popup-Menü selbst (Klick, Auswahl, `setze_ziel()`-Aufruf danach) — nur die Scan-/Capture-Ebene davor
  wurde real geprüft, nicht die Menü-Interaktion.
- Die echte Relay-/Sitzungsverbindung fehlt weiterhin; `terminal_senden` ist ein Test-Callback.
- Terminal-Geometrie-Delta und cv2/numpy-Wine-Kompatibilität aus Zyklus E/F unverändert offen.
- PyInstaller-Paket für den heutigen Code — noch nicht versucht.

## Testergebnis

```
PYTHONPATH=src:. python3 -m unittest discover -s tests -q
Ran 376 tests (Ausgangsstand 353 nach Zyklus G)
FAILED (failures=2, errors=1)
```

Dieselben drei vorbestehenden, umgebungsbedingten Fehlschläge in `test_terminal_adapter.py`, unverändert.
`python3 tests/pruefe_koerper.py` — PASS (0 von 4).

## Stand nach diesem Zyklus

Alle vier Körperteile sind nicht mehr nur einzeln vorhanden, sondern **echt zusammengeschaltet** und unter Wine
end-to-end durchgespielt. Es fehlt für die exe noch: das PyInstaller-Paket, die echte Relay-Anbindung, echtes
Windows statt Wine, und die zwei offenen technischen Fragen (Geometrie-Delta, cv2/numpy).
