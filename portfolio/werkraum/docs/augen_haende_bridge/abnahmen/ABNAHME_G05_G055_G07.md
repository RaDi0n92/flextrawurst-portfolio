---
autor: claude bei Daniels VPS
datum: 2026-10-01
status: Entwurf zur Abnahme durch Daniel; alles nur auf dem VPS und unter Wine geprüft, nativ bei Daniel noch nicht
herkunft: `PLAN.md` (G05, G05.5, G07), `ANFORDERUNGEN.md` (R006, R015–R016, R020, R023–R029, R031–R032, R036, R038–R042, R113–R115, R119, R121, R122, UQ01–UQ10), Tests und Proben der Version 0.8.0-g02
---

# Abnahmeprotokoll G05, G05.5 und G07 (Version 0.8.0-g02)

Zeichen: **belegt** (Test oder Wine-Probe), **nativ offen** (braucht Daniels Windows, steht in `PRUEFLISTE_0.8.0.md`), **Lücke** (nicht gebaut), **Entscheidung** (Daniel muss sagen).

## G05 — Das Overlay nach Daniels Referenz richtig bedienbar machen

| Forderung | Stand | Beleg oder Lücke |
|---|---|---|
| Regie und Medien unten links, Scanner unten rechts je Terminal | belegt (G02), nativ bestätigt | Daniel bedient sie seit Version 0.2. |
| Verschiebbare, größenänderbare Ansichten; wählbare Bindungen | belegt | Terminal, Chat, Selbstbild: verschieben und vergrößern; Scanner-Dropdown bindet; **neu:** „Bindung lösen“ im Scanner (R015 „auswählen, binden, wechseln, lösen“); das Zielrechteck folgt dem gebundenen Fenster (vorher festes Rechteck vom Moment der Bindung). |
| Individuelle Name, Farbe, Transparenz | belegt | **Neu:** Name ändern (Raute-Menü, Eingabefeld, höchstens 24 Zeichen, keine Duplikate) und Farbe wählen (acht benannte Farben und Standardfarbe), bleiben nach dem Neustart; Transparenz je Fenster seit G02. Wine-Probe `probes/identitaet_smoketest.py`. |
| Kürzel | Entscheidung | Ein eigenes Kürzel gibt es nicht mehr: die Raute zeigt nach Daniels Wunsch Name und Tastenkombination (ERLEBEN). Das Wort „Kürzel“ im Plan ist damit durch den Namen ersetzt, falls Daniel nichts anderes will. |
| Zwei Sitzungen gleichen Namens unterscheidbar (R024, UQ02) | belegt | „Codex“, „Codex 2“, … mit eigenem Speicherplatz für Ort und Größe; Nummer wird wieder frei. |
| Agenten senden von ihrer Raute; Banner, Box, Chat gehören zur selben Nachricht (R026) | belegt | Seit G02; Zeiten seit 2026-10-01: Banner 6,6 s, Box 9,9 s, Daniel bestätigte das Aussehen. |
| Alle Sprüche adressierbar, Empfänger vor dem Versand erkennbar (R028, UQ02) | belegt | Das Regie-Menü sagt oben „Sprüche gehen an: …“; Empfänger wählbar im Chat. |
| Wartezustand, Zustellung und Fehler erkennbar (UQ03) | teilweise | Mik und Cam zeigen den Zustand jetzt auch als Wort (aus, …, an, Fehler), nicht nur als Farbe (UQ08). Eine Zustellmeldung für Regiesprüche gibt es nicht: Daniels Worte gehen nicht über das Relay, sondern werden als Banner und im Chat gezeigt; ob der Agent sie im Bild gesehen hat, wird nicht gemeldet. **Lücke.** |
| Freie Bereiche klickdurchlässig, Texteingabe bleibt möglich | belegt, nativ bestätigt | Selbsttest und Alltag. |
| Offline-Einstellungen, Layout hält den Neustart aus (R006, UQ06) | belegt | Einstellungsdatei; **neu:** Zurücksetzen aller Fenster, Namen und Farben mit Rückfrage (UQ06 „Konflikte und Zurücksetzen“). |
| Hotkeykonflikte sichtbar | belegt (G02) | Meldungen an der Raute. |
| R020 Terminalansichten austauschen | Entscheidung | Jeder Agent hat genau sein Terminal; „zwei Ansichten umbelegen“ gibt es nicht. Vorschlag: streichen oder als „Plätze tauschen“ nachholen, wenn Daniel es braucht. |
| R114 Terminal ausblenden, minimieren, wieder einblenden | belegt | X blendet nur aus, Raute-Menü bringt es zurück; die Sitzung läuft weiter. |
| UQ07 Mehrere DPI-Werte, kleine Fenster | nativ offen | Der Selbsttest zeigte „Prozess: None“ (DPI-Bewusstsein unklar); die Fenster wirken scharf, das ist aber nicht gemessen. |
| UQ08 Tastaturwege, Fokusmarkierung | Lücke | Hotkeys und Esc gibt es; eine durchgängige Tastaturbedienung der Menüs außer den Windows-Standardmenüs nicht. |

## G05.5 — Ort der Elemente und „nur Terminal“

| Forderung | Stand | Beleg |
|---|---|---|
| Ort je Element (Raute, Terminal, Selbstbild) einzeln: Desktop oder Zielfenster (R121) | belegt (Logik, Wine) | `test_koerper_ziel_halter` (20 Tests), `test_koerper_anwendung_nur_terminal_ort`; Wine-Probe `ziel_halter_smoketest`: mitgewandert, eingerahmt, beim Schließen verschwunden. Native Prüfung offen. |
| Eingerahmt, wandert mit, minimiert mit, verschwindet beim Schließen | belegt (Logik) | Minimieren nur als Logiktest (Wine kennt hier kein echtes Minimieren). |
| Zurück auf den Desktop bei Bindung auf ganzen Desktop oder gelöster Bindung | belegt | Test. |
| Schalter neben dem Scanner-Knopf | belegt | Knöpfe „Ort“ und „A+H“ links neben dem Scanner, Wine-Probe. |
| „Nur Terminal“ je Agent und für alle (R122) | belegt (Test) | Bilder (Strom und erstes Bild), Kamera (Frames und Einschalten), Hände, Rautenchat samt Banner und Box aus; Mikrofon und Terminal unberührt; Einzelschalter behalten ihre Werte; je Agent einzeln; für alle gleichzeitig; Neustart merkt es. Native Prüfung offen. |
| Zugänge: Knopf im Terminalbereich und Raute-Rechtsklick | belegt | Beide vorhanden; zusätzlich Regie-Menü für „alle“. |

**Offene Punkte G05.5:** Chat und Regieleiste (für alle Agenten gemeinsam) haben keinen Ort „im Zielfenster“ (nicht eindeutig, welches Ziel gemeint wäre); „im Zielfenster“ gilt für Raute, Terminal und Selbstbild.

## G07 — Bilderzufuhr, Kamera und Mikrofon individuell steuern

| Forderung | Stand | Beleg oder Lücke |
|---|---|---|
| Liveframe | belegt (G02/G03) | Bilderstrom, nativ im Selbsttest. |
| Bilddatei als Quelle (R038) | belegt (Test), nativ offen | **Neu:** Raute-Menü „Bilddatei an den Agenten senden …“ (Windows-Dialog, JPEG, höchstens 1920×1080, Quelle `file`). |
| Bildsequenz, Replay | Lücke | Nicht gebaut; Replay hängt an G13. |
| Beobachtung und sichtbare Einblendung unabhängig schaltbar (R039) | belegt (Test), nativ offen | **Neu:** „Bridge-Fenster im Bild der Agenten: an/aus“ (Windows-Funktion „aus der Aufnahme ausnehmen“, Windows 10 ab 2004). Der Selbsttest prüft nativ, ob sie wirkt; unter Wine nimmt Windows die Einstellung nicht an (gemeldet, nichts kaputt). Nebenwirkung: ohne Bridge im Bild sehen die Agenten Daniels Banner nicht (steht im Menü). |
| Kamera pro Agent, PiP frei platzierbar (R040) | belegt, nativ bestätigt | Selbstbild je Agent (0.5.x–0.6.x). „Optional im Gesamtbild“: das Selbstbild ist ein Fenster und damit im Desktopbild, solange „Bridge im Bild“ an ist. |
| Mikrofon individuell, Sprechtaste (R041) | belegt (Wine/VPS), nativ offen | Von Daniel bis zum Schluss zurückgestellt (alle Geräte nativ stumm). |
| Start, Pause, Fortsetzen, Stop sichtbar mit Auslieferungszähler (R036) | belegt | Menü „Bilder an den Agenten“ zeigt an/aus und die Zahl der gesendeten Bilder; „nur Terminal“ stoppt sie. Ein eigener sichtbarer Zustandswechsel an der Raute fehlt. |
| Frische, begrenzte Pufferung, Quelle unterscheidbar (R042) | teilweise | Frames tragen Quelle (`capture`, `file`), Aufnahmezeit, Größe; der Starter berechnet das Alter. Anzeige von Überlast und Samplinglücken im Bridge-Fenster: Lücke. |

## Nicht in diesem Stand

- **G06 (KDE 1 und 2):** Die Anzeige der Bridge auf KDE und das Binden eines KDE-Desktops brauchen einen Linux-Adapter (Aufnahme und Eingabe im Container `virtuellerdesktop1`/`2`) und eine Linux-Oberfläche. Das ist neue Infrastruktur und braucht Daniels Entscheidung. Der Windows-Teil (ganzer Desktop, Fenster, Spiel binden; Binden verschiebt das Fenster nicht) ist seit G02 da.
- **G08 (Bilder, Texte, Zeichnen als gemeinsame Arbeitsfläche):** Nicht gebaut; es braucht einen Objektspeicher, einen Editor und die Komposition je Empfänger. Entwurf und Rückfragen siehe Gespräch.

## Entscheidung (Daniel)

- G05: ☐ abgenommen ☐ abgenommen mit Ausnahme (siehe Lücken) ☐ erst nach der Prüfliste
- G05.5: ☐ abgenommen ☐ erst nach der Prüfliste
- G07: ☐ abgenommen mit Ausnahme (Mikrofon, Bildfolge/Replay, Überlastanzeige) ☐ erst nach der Prüfliste
