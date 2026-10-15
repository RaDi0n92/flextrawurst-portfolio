# Fortschritt Augen-Hände-Bridge und Lernschleife, Stand 2026-10-04

Rückwirkend festgehalten. Jede Zeile nennt Beleg (Commit, Datei oder Messung). Zustand am Ende des Dokuments.

## Bridge: Sehen und Eingreifen für die Agenten im selben Gate

- Sofortbild: Sendet ein Agent in die Raute oder kommt eine Meldung, bekommt jeder andere Agent im selben Gate sofort ein frisches Bild
  (`bilderstrom.sofort_senden`, `anwendung._sofortbild`, Commit `394c39bd92`).
- Zeigegeste für alle im Gate (Commit `f25277592f`). Chat-Absender „Meldung“ statt „Ampel“ (Commit `5fc4730454`).
- Praxis-Harness: Hilfe bei Fehlversuchen, Erinnerung aus dem Ereignisspeicher, Zielwechsel ohne Fehlversuch (Commits `4a823b7ff1`, `0a040079b4`, `84b94c78af`).
- Praxistest-Läufe: Schritte 8 bis 10 und 18 bis 23 durchgeführt, Protokolle `lauf-p-*.md` (Commit `15b51463e8`); Audit fortgeschrieben (Commit `e3e97cc04f`).
- Raute für Agenten-Aktionen freigeben: `RauteFenster.erzwingen`, Aufruf in `_bridge_fenster_freigeben` und `_bridge_fenster_wieder_durchklickbar`
  (Commit `d18c631853`). Zwei neue Tests, der Testaufbau hat `bilderstrom = None`. Läufe: 224 Tests grün (`test_praxis_raute_quittung`, `test_koerper_anwendung_bilderstrom`,
  `test_koerper_bilderstrom`, `test_koerper_ampel`, `test_praxis_lauf`, `test_praxis_dienst`).

## Bridge: Menü-Freigabe (Schritte 11 bis 17)

Spike Teil 1 (Menü im Strombild) und Teil 2b (Klick im Menü, Xvfb, 2026-10-04) sind belegt. Messwerte und Folgerung für den Bau stehen im Audit
(`AUDIT_VON_NULL_2026-10-03.md`, Abschnitt „Schritte 11 bis 17“), Beleg-Skript `spike_menue_xvfb.py`.
Kern: Einträge samt Rechteck sind im Körper bekannt, `fenster_am_punkt` liefert am Menüpunkt das Menü-Toplevel, ein XTEST-Klick löst den Eintrag aus.
Der Bau der Freigabe (Register offener Menüs, Sperrliste, Liste erlaubter Einträge, `pruefe()` und `_am_punkt_ist_ziel`) ist noch nicht begonnen.

## Bridge: Menü-Freigabe im Käfig, erste Stufe gebaut (Commit `56a4d0eca6`)

Neue Aktion `menue`: Der Agent nennt einen Menüeintrag beim Namen, Koordinaten nimmt der Körper dafür nie an (`Aktion.aus_dict` lehnt `punkt`/`bis` ab).
Neu: `offene_menues.py` (Register offener Menüs mit Einträgen, Rechtecken, Fenster-ID), `menue_freigabe.py` (Erlaubnisliste je Menü-Art und feste Sperrliste, beides nach Befehls-Id),
`eingabe_adapter._pruefe_menue` und der Zweig in `_ausfuehren` (prüft vor dem Klick, dass das Menüfenster am Punkt liegt), Registrierung im GTK-Menü (`menue_linux`), Art „raute“ im Raute-Menü (`erster_koerper`),
`steuerprofil` (Menüklick gehört zur geteilten Maus), sechs Gründe samt Lampen in `ampel.py`.
Erste Stufe: erlaubt nur Deckkraft, größer und kleiner. Gesperrt für Agenten: Beenden (Agent und Bridge), Not-Aus, Pausieren, Hände, nur Terminal, Steuerprofil, Ausnahme, Tastenkombination, Name.
Untermenüs und Dialoge (Farbe, Ort, Anzeigeort, Zeichnen) sind noch nicht freigegeben; sie kommen nach Beobachtung ihres Verhaltens dazu.
Tests: `test_koerper_menue_freigabe.py` (31, ohne Display), `test_koerper_menue_freigabe_x11.py` (9, echtes GTK-Menü, echter `X11Backend`, echte Engine in einer privaten Xvfb).
Regression: 375 Tests ohne Display, 62 mit echtem X, alle grün.
Zweite Stufe (Commit `4bb4881d6c`): Jedes Untermenü hat eine eigene Art, denn Befehls-Ids gelten nur im eigenen Menü (`raute.farbe`, `raute.anzeigeort`).
Farbe (acht Farben und Standardfarbe) ist erlaubt; im Anzeigeort-Menü ist **kein** Eintrag erlaubt, weder Wechsel des Anzeigeorts noch Arbeitsziel (Schritt 14 verlangt „nichts verändert“).
Der reservierte Name „schließen“ schließt jedes offene Menü, der Körper führt es selbst aus (keine Esc-Taste). „Ort der Elemente“ und „Zeichnen“ bleiben gesperrt.
Daniels Schalter (Commit `e8d43eac25`): Regie-Menü „Bridge-Menüs für Agenten bedienbar (Praxistest 11–17)“, nach jedem Start aus; das Regie-Menü ist selbst nie für Agenten bedienbar.
Befehl für Agenten: `bridge_cli.py menue "Name"`. Der Menüklick läuft nicht über die Bridge-Fenster-Freigabe der Raute.
Tests: 49 ohne Display, 15 mit echtem X (Untermenüs, Anzeigeort gesperrt, Schließen); Regression 392 Tests ohne Display, mit echtem X grün.
Noch offen für die Schritte 11 bis 17: Schritt 15 (Zeichnen öffnet ein eigenes Fenster, nicht beobachtet), die Schritte 16 und 17 (Regiespruch Pause und Weiter, Fenster binden: die zugehörigen Menüs sind noch nicht
untersucht), die Tastatur im offenen Menü, der Windows-Weg (natives Popup ohne GTK-Rechtecke) und ein Praxislauf `--ab=11` mit echtem Agenten nach Körper-Neustart und Daniels Einschalten.

## Bridge: Banner entfernt, Buchstaben an den Lampen

- **Kein Raum-Banner mehr** (Commit `0a3d7519ec`): Daniel, 2026-10-04: das zweite, größere Textfeld im Bild entfällt. Eigene Rede des Agenten und Daniels Worte erscheinen als Box neben der Raute (Ticker, 9,9 s), dazu das Chatfenster.
  Das Attribut `banner` bleibt, immer leer, damit die Zustandsabfrage (`banner_da`) kompatibel bleibt. Fünf Tests, die das alte Verhalten beschrieben, sind bewusst an das neue angepasst; 539 Tests grün.
- **A, H, Z neben den Lampen** (Commit `0ee88aca16`): Augen, Hände, Ziel, jeweils der Anfangsbuchstabe rechts der Lampe, lesbar auch ohne Farbe. Beleg: Bild der echten Ampel in der privaten Xvfb
  (`screenshots/ampel_buchstaben_AHZ_2026-10-04.png`). Das „Z“ steht für die dritte Lampe, die im Code „Ziel“ heißt (Daniel sagte „Zustand“; der Buchstabe passt zu beiden).
- **Farblogik der Meldungen: offen, nicht geraten.** Daniel, 2026-10-03: Meldungen sollen „je nach Meldung in ihrer Blinkfarbe blinken wie an den Lampen“; es gebe dazu eine frühere, andere Farblogik.
  Gefunden: keine dokumentierte Absprache in der Doku und in den Prompts ab 2026-10-02. Belegt ist nur: bei Grün braucht es keine Anzeige (2026-10-03 05:34), Rot-Meldungen wiederholen alle 20 s, die Lampen sind intern grün, gelb, rot, grau und
  angezeigt Blau, Orange, Rot, Grau. Das Chatfenster kennt eine Farbe je Absender, nicht je Meldung. Offene Frage an Daniel: welche Farbe für welche Meldung, und was heißt „blinken“ im Chat (Text blinkt, Rahmen, nur die Absenderfarbe)?

## Entscheidungen von Daniel zur Menü-Freigabe (2026-10-04, im Terminal beantwortet)

- **Schritt 16 (Regiespruch Pause/Weiter):** Ein Agent darf das Regie-Menü bedienen, der Absender erscheint sichtbar als Agent und nicht als Daniel. Zu bauen: Absenderkennung im Körper.
- **Schritt 17 (Fenster binden):** Beide dürfen binden, Daniel und die Agenten.
- **Schritt 15 (Zeichnen im Ziel):** Ja, Agenten und Claude dürfen zeichnen. Zu bauen nach dem Entwurf im Audit (Werkzeugleiste beim Namen, Ziehen auf der Zeichenfläche des eigenen Ziels).
- **Daniel-Ja:** Daniel hat die Frage nicht verstanden und wollte stattdessen an der eigenen Harness arbeiten; nicht entschieden, bleibt offen.
- Vorrang hat die eigene Harness von Claude (Selbstlernschleife, Dashboard); die Bridge-Bauten folgen danach.

## Schalter und Dashboard der Harness

Hauptpause, Schalter je Baustein und je Regel, zeitlich oder projektbezogen begrenzte Schichten, Dashboard mit Zustand, Warum und Wozu. Beschreibung in `docs/systemdoku/83_claude_lernschleife.md`.
Geprüft mit `test_schalter.py` (16) und Playwright. Das Dashboard läuft unter 127.0.0.1:8791, der Skill `/harness` bedient den Schalter im Claude-Fenster.

## Lernschleife für Claude (eigener Strang, nur Claude in Claude Code)

Vollständig beschrieben in `docs/systemdoku/83_claude_lernschleife.md` (Commit `f8aba23d2f`), Notiz und Karte in Commit `bc8ac2604e`.

- Aufzeichnung ungekürzt (`hook.py`), Lader für Altdaten, Auswertung mit Beleg, Driftpunkte (Fehlschlag, Wiederholung).
- Eigener PostgreSQL-Cluster `erfahrung` (6108 Rohereignisse), append-only Roh und Verlauf, Import idempotent.
- LangGraph mit sieben Knoten, 4 Sekunden je Lauf; Stop-Verifier mit höchstens zwei Wiederholungen; Korrekturerkennung (13 % der Prompts) mit fünf Entscheidungen.
- Acht Regeln (fünf aus Daniels Wortlaut, drei automatisch), Ansicht `ansicht.html` mit Playwright gegen die Datenbank geprüft (hell, dunkel, 390 px).
- Quellen der Idee, Existenz geprüft: arXiv 2606.09498, 2606.13174, 2609.29154.

## Zustand (Messung 2026-10-04, 18:3x)

- Körper-Prozess `koerper.haupt_linux --ort kde1` läuft seit 2026-10-03 23:09 mit dem Code von damals; Sofortbild, Zeigegeste, Meldung und Raute-Freigabe wirken erst nach einem Neustart.
- `git stash list` in `/root/werkraum` zeigt `stash@{0}`: 569 Dateien (388 Löschungen, 181 Änderungen) des Arbeitsbaums von 2026-10-04 ~02:54.
  Der Arbeitsbaum entspricht seitdem dem Stand von HEAD. Wiederherstellung: `git checkout -- augen_haende_bridge/runtime/g13/protokoll/ereignisse.jsonl && git stash pop`, danach die gesicherten neuen Zeilen
  aus `/tmp/claude-0/ereignisse.neu` an die Datei anhängen.
- Die Hooks der Lernschleife stehen erst nach `python3 /root/eh2.py` in `/config/.claude/settings.json`.
- Die drei Schritte kann nur Daniel ausführen: Claude Code sperrt sie dem Agenten (Irreversible Local Destruction, Interfere With Workloads, Self-Modification).
