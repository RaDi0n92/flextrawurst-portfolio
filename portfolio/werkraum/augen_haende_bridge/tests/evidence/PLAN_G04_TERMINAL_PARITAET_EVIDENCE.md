# PLAN G04 — Original-Terminal spiegeln und bedienen: Belege (2026-10-01, Version 0.7.0-g02)

Alle Läufe auf dem VPS (Linux, Python 3.14). Was nativ bei Daniel noch nicht gelaufen ist, steht unten.

## Was geprüft wurde und womit

| Forderung aus `PLAN.md` G04 | Prüfung | Datei |
|---|---|---|
| Sessionidentität geprüft (R017) | Die Terminalliste trägt `pid` und `gestartet` (Startzeit); die Bridge merkt sie und meldet einen anderen Prozess unter derselben ID; ein echter Server-Prozess liefert vor und nach dem Wiederverbinden dieselbe Identität | `test_terminal_launcher.WiederaufnahmeTests`, `test_koerper_anwendung.WiederaufnahmeClientTests`, `test_bridge_server_wiederverbinden` |
| Original- und Anzeigeausgabe verglichen (R018) | 18 Referenzfälle nach VT100/xterm (Cursor, Löschen, Umbruch, Scrollbereich, Zeile einfügen/löschen, Tabulatoren, Cursor sichern, OSC-Titel, Rückschritt, umgekehrter Vorschub, DEC-Linienzeichen, Unicode breit und kombinierend, Inverse, Verlauf, Größenänderung); die erwartete Anzeige ist von Hand geschrieben, nicht aus dem Modell abgeleitet | `test_koerper_terminal_referenz` |
| Gleicher Bildschirm nach Wiederaufnahme | Ein Strom (Farben, Truecolor, Umlaute, breite Zeichen, 40 Zeilen Verlauf, Alternate Screen hinein und hinaus, Zeilenüberschreiben) erzeugt im „Original“-Modell und im Modell, das zurückgesetzt und in 7-Byte-Stücken mit demselben Strom gefüttert wurde, dieselben Zellen, denselben Cursor, denselben Verlauf, ganz oben im Verlauf ebenfalls | `test_koerper_terminal_modell.test_wiederaufnahme_baut_bildschirm_und_rueckblaettern_identisch_wieder_auf` |
| ANSI, Unicode, Cursor, Scrollback, Alternate Screen, Resize | siehe die Referenzfälle und die bestehenden Modelltests (Farben, 256 und Truecolor, Alternate Screen hält den Hauptschirm, kein Verlauf im Alternate Screen, Blättern, Größe ändern) | `test_koerper_terminal_modell`, `test_koerper_terminal_referenz` |
| Eingaben und Sondertasten genau einmal im richtigen Ziel (R019) | Echtes PTY des Starters; der Empfänger ist ein Rohmodus-Programm, keine Shell (so trifft keine Probe einen Agenten oder Befehl); 20 Sondertasten, Zeichen, Enter, Rücktaste, Strg+C, Esc, Tab, Alt+x, Umlaute, Einfügen (eingeklammert), 50 KB Einfügen in 8-KB-Stücken: genau die erwarteten xterm-Bytes, genau einmal, in Reihenfolge, keine Nachlieferung nach 0,5 s; Eingabe für eine fremde Sitzungs-ID trifft die Sitzung nicht | `test_terminal_eingabe_paritaet` |
| Größenänderung rückgelesen | `terminal_resize` löst im Empfänger SIGWINCH aus; er meldet die Größe, der Starter hält sie | `test_terminal_eingabe_paritaet.test_groessenaenderung_kommt_an_und_wird_zurueckgelesen` |
| Reconnect: keine neue Shell, keine doppelten Eingaben | Echter Server-Prozess (Relay + Starter) und echter Desktop-Client: Sitzung starten, Eingabe `AAA`, Client trennen, neuer Client: gleiche ID, gleicher Prozess, gleiche Startzeit, genau eine Sitzung; `terminal_attach` liefert das erste Stück mit `replay` und die gesamte Ausgabe seit dem Start; die alte Eingabe erscheint einmal als Ausgabe, kommt aber nicht noch einmal beim Programm an; neue Eingabe `B` kommt genau einmal an | `test_bridge_server_wiederverbinden` |
| Stream bleibt live, kein Journal | `terminal_attach` und `terminal_output` mit `replay` sind Stream-Arten ohne Journal und Quittung, ein Wiederverbinden spielt sie nicht alt ab | `test_transport_terminal` |

## Neu gebaut für G04

- **Wiederaufnahme:** Der Starter merkt sich je Sitzung die letzte Ausgabe (höchstens 512 KB, am Anfang auf eine Zeilengrenze gekürzt). Die Bridge fragt nach jedem Verbinden mit `terminal_attach`; der Starter spielt die Ausgabe ein, das erste Stück trägt `"replay": true`,
  die Bridge setzt den Bildschirm zurück und baut Bildschirm und Rückblättern daraus auf. Ausgabe und Wiedereinspielung sind gegeneinander gesperrt (keine vermischten Stücke).
- **Identität:** `terminal_list` trägt `pid` und `gestartet`; die Bridge erkennt einen anderen Prozess unter derselben ID.
- **DEC-Linienzeichensatz:** Behoben, ein echter Fehler, den die Referenzfälle gezeigt haben: Programme mit Rahmenzeichen über `ESC ( 0` (mc, dialog, ncurses-Oberflächen) zeigten Buchstaben statt Linien, weil pyte Zeichensatzwechsel im UTF-8-Modus ignoriert. Jetzt eigener Strom (`terminal_modell.Strom`),
  UTF-8 bleibt erhalten.

## Grenzen und nicht Belegtes

- **Nativ bei Daniel noch nicht gelaufen:** die Wiederaufnahme in der echten Oberfläche (Bridge beenden, neu starten, Terminal ist wieder gefüllt). Sie braucht den neuen Relay-Dienst (`systemctl restart bridge-relay`) und das Paket 0.7.0.
- **Wiederaufnahme zeigt nur die letzten 512 KB**; ältere Ausgabe und damit das Rückblättern davor fehlen. Beginnt der Puffer mitten in einer Escape-Folge (nur nach Überlauf), ist die Anzeige bis zur nächsten Zeichnung leicht verstört.
- **Die Darstellung selbst** (GDI-Zeichnen unter Windows) ist nicht gegen ein Referenzbild geprüft, nur das Modell dahinter; die Oberfläche hat Daniel mit Claude Code, Markieren, Scrollen und Rad bestätigt.
- **Kein Textspiegel, keine Ersatzsitzung:** Die Sitzung gehört dem Starter; ihr Prozess wurde für die Tests nicht beendet oder ersetzt (jeder Test startet eigene Testprozesse).
- Die bekannten drei Fehlschläge in `test_terminal_adapter.py` gehören zum alten Prototypen und sind unverändert.

Lauf: `PYTHONPATH=src:.:tests python3 -m unittest discover -s tests` → 945 Tests, drei bekannte Fehlschläge.
