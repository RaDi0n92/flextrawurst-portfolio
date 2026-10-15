# PLAN-G02 Zyklus Q: gemeinsamer Chat, agentengesteuerte Raute — Evidence

Datum: 2026-09-30. Sicherheitspunkt: `3e7b69efd1`. Anlass: Daniels Korrektur nach dem ersten echten Start.

## Vorgabe (Daniel, wörtlich sinngemäß)

Terminal genau wie ein normales Terminal, nichts hinein getippt. Die Raute steuert der **Agent**, nicht Daniel; mehrere
Agenten dürfen dort schreiben. Dazu ein kleines Chatfenster, das das anzeigt (dauerhaft) — die Nachricht zusätzlich als
Banner (3,3 s) auf dem Bildschirm und als Ticker (6,6 s) an der Raute. Daniels Regiebefehle stehen im selben Chat und
6,6 s auf dem Bildschirm, **nicht** im Terminal. Der Agent soll sie am besten auf dem Bildschirm sehen und selbst
reagieren. Daniel will im Chat auch selbst schreiben. Klick auf die Raute entfällt; sie bleibt nur zum Verschieben,
Transparenzeinstellen und Vergrößern.

## Build

- `chat_fenster.py`: ein gemeinsames Fenster für alle; Verlauf mit Agentenfarbe, „An: Name“ im Kopf (Klick wechselt),
  Eingabezeile, Kopf zum Verschieben, Kanten zum Vergrößern, Prozent-Knopf für die Deckkraft.
- `erster_koerper.py`: kein Chat mehr im Körper, kein Klick-Zweck der Raute; `gesprochen`-Rückruf; `zeige_ticker()` für Daniels
  Worte; Raute-Menü: Deckkraft, größer, kleiner, Terminal, Not-Aus, Beenden.
- `raute_fenster.py`: `groesse_setzen()`, `deckkraft_weiter()`, Klick entfällt.
- `anwendung.py`: hält den einen Chat; `daniel_sagt()` (Chat-Eingabe und Regiesprüche) → Chat + Ticker an der Raute des
  Angesprochenen; nichts geht ins Terminal oder ans Relay; F13–F24 wählen den Agenten und zeigen den Chat;
  Regie-Menü: „Chat ein-/ausblenden“. Der frühere Weg „Regiespruch tippt ins Terminal“ ist entfernt.

## Ergebnis

Core: 487 Tests, drei bekannte, umgebungsbedingte Fehlschläge in `test_terminal_adapter.py`; Körper-Tor 0 von 4.
Wine (Fenster): Chat-Kopf verschiebt, Kanten und Ecke vergrößern, Knöpfe sind Client, Deckkraft-Knopf 255 → 87, Klick auf „An:“
wechselt, Enter gibt den Text an den Besitzer; Raute 48 → 72 px (Form folgt), Deckkraft 87 → 128, geklemmt 24…144
(`PLAN_G02_Q_CHAT_RAUTE_WINE_OUTPUT.json`).
Wine (Gesamtweg, gebaute exe und exe aus dem entpackten ZIP, echtes Relay, simulierter Agent auf der PTY): der Agent spricht
über sein Werkzeug → Raute, Banner, Ticker und Chat; Daniels „Go!“ steht im Chat als „Daniel → Simi“, ein Ticker erscheint,
und im Terminal steht nur die Antwort des Werkzeugs, **kein** „Go!“ (`PLAN_G02_Q_EXE_WINE_OUTPUT.json`,
`PLAN_G02_Q_ZIP_WINE_OUTPUT.json`).

## Neues Paket

`dist/AugenUndHaendeBridge-G02-win64.zip`, Version 0.2.1-g02, SHA256
`709bb81899d0011bce74116bd962893a66ae4d9018e4e896537d1ba85835bd1b`; exe-SHA256
`51f7efc364fca3f72abd4b42c7d1f9720b099eb60b6999c9030d5bda5cd19497`; Manifest 1449 Dateien, nach dem Entpacken bestätigt. Enthält das
korrigierte `start_with_ssh_tunnel.ps1` (wartet auf die GUI-exe) und eine neue Startanleitung. Einzeln:
`dist/start_with_ssh_tunnel_G02.ps1`.

## UNKNOWN / offen

- Native Windows: nur der erste Start (Verbindung, Startliste, Claude-Sitzung) ist von Daniel gesehen; Chat, Ticker-Sichtbarkeit,
  Ziehen/Vergrößern, Strg-Bedienung der Raute dort ungetestet.
- Ob der Agent Daniels Worte sieht, hängt am Bild: bisher entsteht ein Bild nur bei der Bindung; ein laufender Bilderstrom
  gehört zu G03 und ist nicht gebaut. Der Ticker steht also gut sichtbar auf dem Schirm, ob er im Bild landet, ist offen.
- Chat-Zeilen brechen nicht um. Daniels Farbe (#F2F2F2) und die Ticker-Zuordnung „an die Raute des Angesprochenen“ sind meine
  Annahme, von Daniel nicht bestätigt. Die F13–F24-Belegung (Agent ansprechen und Chat zeigen) ebenso.
- Harness: bewusst `running` vor `skill_prebuild_read`.

## Nachtrag: „Bridge beenden“ (Version 0.2.2-g02)

Daniel meldete, die Regieleiste blieb nach „Bridge beenden“ offen. Ursache **nicht gefunden**: die Wine-Probe
`probes/beenden_smoketest.py` (echter Klick auf den Regie-Knopf, laufender Agent, feste Menüwahl) beendet die Schleife und
zerstört alle Fenster schon mit dem alten Code. Unterschiede zu Daniels Windows (echtes Popup-Menü, echte Sitzung über den
Tunnel) sind nicht nachgestellt. Deshalb gehärtet, nicht behoben: Beenden läuft über den GUI-Thread und erst nach dem Klick,
Fenster werden zuerst geschlossen, danach Medien, Sender, Runtime; jeder Schritt einzeln geschützt und im Log
(`beenden: …`); eine Notbremse beendet den Prozess nach 8 s, falls etwas hängt. ZIP 0.2.2-g02, SHA256
`2216a63e4449ff2cf8ad1f269804f68e538adf182ab40e9079cffb6c78f4cd5f`. Ob es bei Daniel wirkt, zeigt erst sein Lauf; das Log nennt dann den Schritt.

## Nachtrag: Chat „an alle“ (Version 0.2.3-g02)

Daniel: der Chat soll nicht nur an einen Agenten gehen, sondern an alle, die ihn sehen, egal ob deren Ziel der ganze Desktop, ein
Fenster oder ein Spiel ist. Umsetzung nach meiner Lesart (von Daniel nicht bestätigt): Standard „An: alle“; Daniels Worte und
Regiesprüche stehen im Chat als „Daniel → alle“ und als 6,6-s-Ticker an der Raute **jedes** Agenten — jede Raute steht im Ziel
ihres Agenten, also im Bild jedes Agenten. Klick auf „An:“ schaltet alle → Agent → … → alle; F13–F24 sprechen einen Agenten
allein an. Der Chat selbst ist ein Fenster und erscheint nur im Bild eines Agenten, wenn sein Ziel diese Stelle enthält.
Tests 496 (drei bekannte Fehlschläge); Wine, gebaute exe: „Daniel → alle“ im Chat, Ticker da
(`PLAN_G02_Q_EXE_023_AN_ALLE_WINE_OUTPUT.json`). Ein Wine-Lauf mit zwei gleichzeitigen Agenten fehlt (die Prüfhaken starten nur einen);
die Verteilung an mehrere ist nur per Test belegt. ZIP 0.2.3-g02, SHA256
`ab1f6fc6b2d3862235cf539844ef08575513bbc0e8c2b65cc53ee3d093580806`.

## Nachtrag: Raute beim Vergrößern und Beenden (Version 0.2.4-g02)

Zwei Fehler nach Daniels erstem Test von Größe und Beenden:

1. **Raute buggt beim Vergrößern.** Ursache gefunden: `zeichnen()` malte die Raute immer in der Startgröße (48 px), nur das Fenster wuchs.
   Beleg unter Wine: bei 96 px war im alten Stand Pixel (72,48) und die Mitte schwarz, im neuen Stand gefüllt
   (`PLAN_G02_Q_CHAT_RAUTE_WINE_OUTPUT.json`, Feld `gezeichnet_bei_96`). Die frühere Probe prüfte nur Fenstergröße und Form, nicht das Gezeichnete —
   deshalb blieb es unentdeckt.
2. **Raute blieb nach „… beenden“ stehen.** Jetzt verschwindet der ganze Körper (Raute, Terminal, Banner, Ticker), sobald die
   Sitzung nach einem gewünschten Beenden endet. Endet ein Agent von selbst, bleibt er als „beendet“ sichtbar (Menü → beenden schließt ihn).

Tests 500 (drei bekannte Fehlschläge). Neu im ZIP: `client_windows/start_bridge.bat` (Doppelklick-Starter) und ein Abschnitt in der Anleitung.
ZIP 0.2.4-g02, SHA256 `1b45bc1794e8e195455c6e02488d57c3ec976681fc18048ca7a7d9f7a7bed278`.

## Nachtrag: Regieleiste verschiebbar und transparent (Version 0.2.5-g02)

Daniel: Stop, Regie, Cam und Mik sollen sich verschieben und transparenter machen lassen. Umgesetzt: ein Griff (drei Punkte) ganz oben verschiebt die
Leiste, ein Prozent-Knopf unten schaltet die Deckkraft weiter (34/50/75/100 %). Unter Wine (Fensternachrichten): Griff liefert HTCAPTION, der Rest
HTCLIENT, jeder Knopf wird getroffen, Deckkraft 230 → 255 (`PLAN_G02_R_REGIE_VERSCHIEBBAR_WINE_OUTPUT.json`); 504 Tests (drei bekannte Fehlschläge).
Nicht getestet: das echte Ziehen mit der Maus auf Windows und dass das Verschieben ohne Aktivierung sauber läuft (Fenster hat WS_EX_NOACTIVATE).
Positionen und Deckkraft werden **nicht** gespeichert; nach einem Neustart stehen die Fenster wieder an ihren Standardplätzen.
Daniels Raute-Definition (Präsenzort einer Session, Ticker/Banner, verschiebbar, transparent, weder Chat noch Terminal) entspricht dem gebauten Stand;
offen ist seine Forderung, Terminal und Chat pro Ziel (Desktop, Fenster, Programm, Spiel) einstellbar zu machen — Rückfrage an Daniel.
ZIP 0.2.5-g02, SHA256 siehe `dist/AugenUndHaendeBridge-G02-win64.zip.sha256`.
