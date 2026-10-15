# PLAN-G02 Zyklus T: Durchklick-Modus (Variante A) und Host-Starteinträge — Evidence

Datum: 2026-09-30. Sicherheitspunkt: `80e4424224`. Anlass: Daniels Vorgaben („Variante A“; Claude, Codex, Gemini auch als Host).

## Durchklick-Modus (Variante A)

Chat, Regieleiste und Terminal sind standardmäßig **durchklickbar wie die Raute**: Klicks gehen an das Programm darunter, solange Strg nicht gehalten wird; mit Strg
nehmen sie Klicks an. Je Fenster abschaltbar (Regie-Menü: „Chat: durchklickbar …“, „Leiste: durchklickbar …“; Terminal im Raute-Menü), gespeichert in
`einstellungen.json`. Umsetzung: `koerper/durchklick.py` (`DurchklickVerwalter`, Takt 80 ms, Fensterstil WS_EX_TRANSPARENT), `Fenster.durchklick_setzen`.
Die Tastatur bleibt beim angeklickten Fenster. Bewusste Folge: auch der STOP-Knopf der Leiste braucht im Durchklick-Modus Strg (F12 bleibt davon unberührt).

Wine (`PLAN_G02_T_DURCHKLICK_WINE_OUTPUT.json`, echte Fenster, echter Strg-Druck): ohne Strg trifft `WindowFromPoint` keines der drei Fenster, mit Strg alle drei, nach dem
Loslassen wieder keines; Chat einzeln auf „aus“ → nur der Chat nimmt Klicks an. Die gebaute exe speichert `durchklick` je Fenster.

## Startliste

`client_vps/starts.json`: neu `claude-host` („Claude-Host“), `codex-host` („Codex-Host“), `gemgem-host` („Gemgem-Host“, Programm `agy`), alle Ort „Host“,
Ordner `/root`, `bestaetigt: false` (Ordner von mir angenommen, wie bei GLM/Kimi). Die Programme `claude`, `codex`, `agy` liegen auf dem Host (Dateisystem geprüft).
`load_starts` akzeptiert die 11 Einträge. Der laufende Dienst `bridge-relay` liest die Liste erst nach einem Neustart.
Daniels Beobachtung „bei Claude (vd1) erscheint kein Terminal auf vd1“ ist Absicht (BE01): die Sitzung läuft im Container vd1, erscheint aber nur im Bridge-Terminal auf Windows.

## Nebenbei

Agentenfarben sind jetzt stabil über Neustarts (`stil.agentenfarbe`, crc32) statt vom zufälligen `hash()` abhängig.

## Ergebnis / offen

Core: 579 Tests, drei bekannte Fehlschläge. ZIP 0.3.1-g02, SHA256 `559547e56886e8eb56f3a63ad4e6b676f88882c5cd53e934eb6eb3ab18581724`.
Offen: native Windows (Durchklick über Spielen, Zusammenspiel mit Vollbild), ob die Host-Ordner `/root` gewollt sind, und der Dienst-Neustart durch Daniel.
