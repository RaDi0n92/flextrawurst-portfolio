# PLAN-G02 Zyklus S: Sichtbarkeit je Fenster und gespeicherte Einstellungen — Evidence

Datum: 2026-09-30. Sicherheitspunkt: `c4980538dc`. Anlass: Daniels Vorgabe „es soll nur bei dem jeweiligen Ziel (Programm, Fenster, Spiel) zu sehen
sein — aber ganz individuell gestaltbar“.

## Auslegung (von Daniel bestätigt: „das erste ist gemeint“, „ganz individuell“)

Jedes Fenster des Körpers hat seine **eigene** Regel: `immer sichtbar` (Standard) oder `nur bei <Programm>`. Betroffen: Raute und Terminal je Agent,
der gemeinsame Chat, die Regieleiste. Gemeint ist mit „Ziel“ das **Programm** (die exe des Vordergrundfensters, also auch Spiele); ein einzelnes
Fenster desselben Programms wird nicht von einem anderen unterschieden — das ist eine bewusste Vereinfachung, von Daniel nicht bestätigt.

## Build

- `koerper/sichtbarkeit.py`: Regel, Kanten-Logik (nur beim Wechsel des Vordergrunds; eigene Fenster vorn ändern nichts; vom Nutzer ausgeblendetes Terminal
  kommt nicht von selbst zurück), Vordergrund und offene Programme über die Fensteraufzählung des Scanners, Taktfaden (0,3 s) der `tick` im GUI-Thread anstößt.
- `koerper/einstellungen.py`: JSON-Datei `%LOCALAPPDATA%\AugenUndHaendeBridge\einstellungen.json` (Ort, Größe, Deckkraft, Regel je Fenster); tolerant gegenüber
  fehlender/kaputter Datei; Orte werden auf den sichtbaren Bildschirm geklemmt.
- `koerper/anwendung.py`: meldet alle Fenster an, wendet Gespeichertes an, Auswahlmenü (Immer / offene Programme, aktuelle Regel mit Haken), speichert beim Beenden
  (vor dem Schließen), bei jeder Regel-Änderung, alle 30 s und wenn ein Agent entfernt wird.
- `koerper/erster_koerper.py`: Raute-Menü „Raute: … …“ und „Terminal: … …“; ohne Erlaubnis der Regel kein Banner und kein Ticker (der Chat bekommt die Nachricht trotzdem).
- Regie-Menü: „Chat: … …“ und „Leiste: … …“. `haupt.py` verdrahtet alles.

## Ergebnis

Core: 561 Tests, drei bekannte, umgebungsbedingte Fehlschläge in `test_terminal_adapter.py`.
Wine mit **echten fremden Programmen** (notepad, regedit; `PLAN_G02_S_SICHTBARKEIT_WINE_OUTPUT.json`): Programmliste enthält beide, der Vordergrund wird als
`notepad.exe`/`regedit.exe` erkannt, eine Raute mit Regel „nur bei notepad.exe“ ist bei Notepad sichtbar, bei Regedit unsichtbar, wieder sichtbar bei Notepad; Ort (321,222),
Größe 72 und Deckkraft 128 werden nach dem Speichern wiederhergestellt. Die gebaute exe schreibt beim Beenden die Einstellungen
(`PLAN_G02_S_EXE_EINSTELLUNGEN_WINE_OUTPUT.json`).

## UNKNOWN / offen

- Native Windows: Vordergrund-Erkennung mit echten Spielen (Vollbild-exklusiv verdeckt schwebende Fenster unter Umständen; Fenster/Randlos ist der Normalfall),
  Programme mit erhöhten Rechten (deren exe-Name lässt sich ohne Adminrechte eventuell nicht lesen → sie erscheinen nicht in der Liste und werden nicht erkannt).
- Programm statt einzelnes Fenster als Ziel (siehe oben). Zwei Agenten mit gleichem Namen teilen sich die gespeicherten Einstellungen.
- Eine Regel „nur bei X“ für die Regieleiste kann sie unsichtbar machen; Rückweg in der Anleitung (Programm nach vorn oder `einstellungen.json` löschen).
- Nicht geprüft: das Verhalten beim Umstecken von Monitoren (nur das Klemmen auf den virtuellen Bildschirm ist getestet).
