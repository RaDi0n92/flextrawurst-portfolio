# PLAN-G02 Zyklus U: Bedientaste wählbar, Tastenkombination je Agent, Raute mit Name und Kombination — Evidence

Datum: 2026-09-30. Sicherheitspunkt: `d70a6291e9`. Anlass: Daniels Hinweise („Strg+Alt wäre besser“; „in der Doku steht, dass ich die Tastenkombi festlege und sie in der
Raute steht — Name und Tastenkombi immer sichtbar“; „die Raute nicht so alle Seiten gleich lang“).

## Doku-Stand (gelesen, ERLEBEN.md „Die Rauten und ihre Sprache“, ANFORDERUNGEN R024/R025)

„Daniel weist jedem Strom eine Akzentfarbe und einen Hotkey zu. Ändert er die Belegung, ändert sich die Beschriftung der Raute sofort“ (Beispiel `◆ Codex [F14]`);
Hotkeys F13 bis F24 oder Klick mit gehaltener Modifikatortaste öffnen ein schlankes Eingabefeld; R024: Name, Farbe, Hotkey und Position pro Raute einstellbar, Einstellungen nach Neustart.

## Build

- `koerper/tastenkombi.py`: `Bedientaste` (Strg, Strg+Alt, Alt, Strg+Umschalt, Alt+Umschalt; Standard Strg+Alt), `Kombination` (Text wie „Strg+Alt+F5“, Zulässigkeit:
  Buchstaben/Ziffern nur mit Modifikator), `Erfasser` (nächster Tastendruck, Esc bricht ab).
- `koerper/raute_fenster.py`: die Raute ist **nicht mehr gleichseitig**: Höhe = Einstellung, Breite aus der Beschriftung (Text passt mathematisch in die Raute); in ihr stehen der
  Name und die Tastenkombination (`Claude-Host [F13]`), Namen über 14 Zeichen werden gekürzt; `setze_hotkey` ändert die Beschriftung sofort.
- `koerper/fenster.py`: `hotkey_setzen` (Hotkey unter Namen, ersetzen ohne die alte zu verlieren, wenn die neue belegt ist), `hotkey_loeschen`.
- `koerper/anwendung.py`: Hotkey je Agent (gespeichert, sonst erste freie F13–F24), Raute-Menü „Tastenkombination festlegen …“ (Ticker an der Raute: „Tastenkombination drücken …“),
  Ablehnung von Unzulässigem / schon Vergebenem / von Windows Belegtem, Regie-Menü „Bedientaste für alle Fenster: … …“; alles in `einstellungen.json`.

## Ergebnis

Core: 614 Tests, drei bekannte Fehlschläge in `test_terminal_adapter.py`.
Wine (`PLAN_G02_U_HOTKEY_RAUTE_WINE_OUTPUT.json`, echte Fenster und Tastendrücke): Raute mit „Claude-Host [F13]“ 204×52 px, mit „… [Strg+Alt+F5]“ 293×52 (Position bleibt, Beschriftung
gezeichnet); Erfassen einer echten Strg+Alt+F5-Eingabe liefert „Strg+Alt+F5“; Bedientaste Strg+Alt ist nur mit beiden Tasten wahr; Hotkey F13 → Strg+Alt+F5 ersetzt, die alte löst nicht mehr aus,
eine doppelte Kombination wird abgelehnt, die neue löst aus. Zeichnung der größeren Raute pixelgeprüft (`PLAN_G02_Q_CHAT_RAUTE_WINE_OUTPUT.json`).

## UNKNOWN / offen

- Native Windows: RegisterHotKey-Belegung durch Windows/Programme, Strg+Alt als AltGr auf deutschen Tastaturen (harmlos erwartet, nicht gesehen), Schriftdarstellung.
- **Nicht gebaut:** das „schlanke Eingabefeld“ an der Raute aus der Doku. Die Tastenkombination wählt den Agenten als Empfänger und zeigt/fokussiert den Chat (dort tippt Daniel).
- Agenten schreiben nur, wenn sie das Werkzeug `bridge_cli.py say` aufrufen; ihnen das beizubringen (Anweisung/Startnachricht) ist nicht gebaut. Agenten sehen einander nur über den Bildschirm.
- Hotkey-Zuordnung ist pro Agentenname gespeichert (zwei gleichnamige Agenten teilen sie).
ZIP 0.4.0-g02, SHA256 `863e60d0a9b3c894de7bb0620677b941a3af25fb453fd961d6a9b5ddb2debf59`.

## Korrektur (Version 0.4.1-g02): die Tastenkombination gehört dem **Agenten**

In der ersten Fassung wählte die Kombination den Agenten als Chat-Empfänger und zeigte den Chat (für Daniel). Daniel stellte klar: **der Agent** nutzt die Kombination. Er sieht sie in seiner Raute
(„Name [F13]“), drückt sie mit seinen Händen, dann öffnet sich an **seiner** Raute ein schlankes Eingabefeld (so auch in ERLEBEN.md); er tippt, Enter bestätigt, der Text ist **seine Rede**
(Raute, Banner, Ticker, Chat). Der Chat bleibt Daniels Weg zu den Agenten.

Umsetzung: `koerper/eingabe_fenster.py` (`RauteEingabe`: Fokus bei Öffnung, Enter sendet und schließt, Esc bricht ab, Fokusverlust und 30 s Leerlauf schließen, rechts neben der Raute bzw. am Rand
links, nur einmal schließen/melden), `ErsterKoerper.eingabe_oeffnen` (der Text geht an `raute.sagen`), `KoerperAnwendung.eingabe_oeffnen` als Hotkey-Aktion; `agent_waehlen` entfernt.
Core: 637 Tests (drei bekannte Fehlschläge). Wine (`PLAN_G02_V_EINGABEFELD_WINE_OUTPUT.json`, echte Fenster, echter Hotkey und Tastendruck Strg+Alt+F5): die Raute zeigt „Simi [Strg+Alt+F5]“, die
Kombination öffnet das Feld neben der Raute (überlappt nicht, Mitte passt), „Hallo Welt“ + Enter erscheint im Chat als „Simi“ und in der Raute, Banner und Ticker entstehen, das Feld ist danach zu; Esc bricht ab
und lässt den Chat unverändert. ZIP 0.4.1-g02, SHA256 `7fe1916e24b8da46958b4186d711d3d9dd1089f7fc714f513e8ea7c1ac1986cf`.

Offen: Der Agent muss die Tasten wirklich drücken können (Eingabe-Hände, späteres Goal); heute löst nur ein echter Tastendruck das Feld aus. Das Feld nimmt den Fokus (auch von einem Spiel).
