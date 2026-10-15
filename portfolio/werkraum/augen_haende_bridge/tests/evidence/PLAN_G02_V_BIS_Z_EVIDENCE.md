# PLAN-G02 Zyklen V bis Z: Agenten-Startnachricht, Hände, Bilderstrom, Sprache, Selbsttest — Evidence

Datum: 2026-09-30. Sicherheitspunkt: `7bf407eadc`. Anlass: Daniel: „alle 4 bzw. 5 der Reihe nach und ohne stoppen“ (Agenten beibringen, Eingabe-Hände, Bilderstrom, Mikrofon-Audio, nativ prüfen).
Ergebnis: 784 Tests (nur die drei bekannten, umgebungsbedingten Fehlschläge in `test_terminal_adapter.py`), ZIP 0.5.0-g02.

## 1. Agenten beibringen (Startnachricht, `hilfe`)

`client_vps/starts.json` kennt je Eintrag das optionale Feld `startnachricht` (`"standard"` = Hinweis auf `say`, `hoere`, `hilfe`; leer = aus; eigener Text mit `{cli}`).
Der Starter tippt sie in die Sitzung, sobald deren Ausgabe 2,5 s still war (höchstens nach 45 s gar nichts). Eingeschaltet nur für `claude-vd1`, `codex-vd1`, `gemgem-vd1` und die drei neuen
Host-Einträge; die übrigen unverändert. `bridge_cli.py hilfe` listet alle Werkzeuge. Tests: `test_terminal_launcher_startnachricht.py` (13, auch mit echter PTY).

## 2. Eingabe-Hände (`schreibe`, `raute_tippen`)

Ein Agent ruft `bridge_cli.py schreibe "Text"`; der Starter sendet `raute_tippen` (höchstens 500 Zeichen); die Bridge drückt per **SendInput** die Tastenkombination der Raute des Agenten (öffnet sein Feld),
wartet, bis das Feld vorn steht **und** die Tastatur hat, tippt den Text (Unicode) nur dorthin und bestätigt mit Enter. Bei jedem Schritt wird der Fokus geprüft; verliert das Feld ihn, wird nichts mehr gedrückt und
das Feld geschlossen. Gesperrt bei Not-Aus, ausgeschaltetem Schalter (Raute-Menü „Hände“, je Agent, gespeichert, Standard an) und ohne Hotkey. Eine Rückmeldung an der Raute nennt den Grund.
`Fenster.fokus_erzwingen` (Anhängen an den Eingabefaden des Vordergrundfensters) gegen die Vordergrundsperre von Windows. Wine (`PLAN_G02_W_HAENDE_WINE_OUTPUT.json`, echtes SendInput, Umlaute): der Text steht als
„Simi“ im Chat, Feld danach zu; Hände aus und Not-Aus tippen nichts. Tests: 17 (`tasten_senden`) + 14 (Anwendung) + Transport/Starter.

## 3. Laufender Bilderstrom

Nach der Bindung eines Ziels sendet die Bridge alle 2 s ein Bild genau dieses Ziels (Fenster: Ausschnitt folgt dem Fenster; Desktop: ganz), nur bei Änderung, alle 15 s ein Lebenszeichen, ein Frame je Takt für alle Agenten,
Not-Aus sperrt, je Agent abschaltbar (Raute-Menü). `windows_capture.py` nimmt jetzt mit `CAPTUREBLT` auf (ohne das Bit fehlen Layered Windows wie Raute, Ticker und Chat im Bild). Wine
(`PLAN_G02_X_BILDERSTROM_WINE_OUTPUT.json`, echte Aufnahme): die Raute steht im JPEG, unveränderte Bilder werden übersprungen, der Ausschnitt folgt einem fremden Fenster (notepad) exakt, ein geschlossenes Fenster
beendet den Strom. **Unter Wine ist die Raute mit und ohne Flag im Bild; ob das Flag nativ nötig ist, prüft der Selbsttest.** Tests: 19 + 13.

## 4. Sprache (Mikrofon → VPS → Whisper → Text)

Desktop: `sprachaufnahme.py` schneidet Äußerungen (Standard **Sprechtaste** F8 gehalten; Modus „offen“ mit Energieerkennung, nur auf ausdrückliche Wahl), `Medien` reicht sie als WAV weiter, `terminal_audio` (Live-Strom,
höchstens etwa 30 s, nur Desktop → Starter). VPS: `client_vps/sprache.py` (faster-whisper, int8, CPU, Silero-VAD, Wortliste „Claude, Codex, Gemgem, Flextrawurst, Strg, Alt …“, Phantomsatz-Filter), Warteschlange mit
Verwerfen, `sprache_text` zurück; der Agent liest mit `bridge_cli.py hoere`. Das Audio wird nicht gespeichert. Not-Aus sperrt Aufnahme und Senden.

**Whisper-Qualität gemessen** (drei deutsche Sätze, synthetische Stimmen, 16 kHz; `PLAN_G02_Y_WHISPER_BENCHMARK_MEDIUM_LARGE.jsonl`, `…_LARGE_V3_E2E.txt`): Wortfehlerrate tiny 0,15–0,32, small 0,11–0,27, medium 0,11–0,27, large-v3 0,07–0,18
(Zahlwörter als Ziffern zählen als Fehler). large-v3 erkannte „Claude“, „Flextrawurst“, „Gemgem“, „Bauprotokoll“ und „Strg Alt F5“ richtig, bei etwa gleicher Laufzeit wie medium (8 Threads, 16-Kern-VPS): Erkennung etwa so lang wie die Äußerung.
Standard deshalb `large-v3` (Laden einmalig ~45 s beim Dienststart, ~3 GB RAM); wählbar über `BRIDGE_WHISPER_MODELL`. Die Modelle medium und large-v3 liegen jetzt im Cache des Hosts (`/root/.cache/huggingface`).
Gesamtkette unter Wine (`PLAN_G02_Y_SPRACHE_E2E_WINE_OUTPUT.json`): eine WAV-Äußerung wird statt des Mikrofons eingespeist → echtes Relay → echter Starter mit Whisper → „Daniel → Simi: (Sprache) Schieb die Raute nach rechts oben, …“ im Chat.
Die Wine-Umgebung hat kein Mikrofon: echte Aufnahme und die Sprechtaste nativ **UNKNOWN** (der Selbsttest prüft die Geräte). Tests: Segmentierer 13, Medien 7, Starter/Transkriber 17, Anwendung 12, Transport 3.

## 5. Nativ prüfen: `--selbsttest` / `selbsttest.bat`

Ein Prüfmodus der exe schreibt `%LOCALAPPDATA%\AugenUndHaendeBridge\selbsttest.txt/.json`: Bildschirm/DPI, Testfenster, **Durchklicken mit echten Strg+Alt-Tasten**, **Hotkeys per echtem Tastendruck**, Bildaufnahme mit und ohne `CAPTUREBLT`
(sind die Layered Windows im Bild?), ein Bilderstrom-Takt, Programmliste/Vordergrund, Einstellungen, Relay-Erreichbarkeit, **Eingabefeld und Hände bei vorn stehendem Notepad**, Kamera und Mikrofon **in eigenen Kindprozessen**
(ein Absturz der Bibliotheken ist selbst der Befund). Er sendet nichts ins Netz und tippt nur in ein eigenes Testfeld. Wine-Lauf (`PLAN_G02_Z_SELBSTTEST_WINE_OUTPUT.txt`): 8 ok, 1 Warnung (keine fremden Programme in der Wine-Sitzung),
1 unbekannt (kein Relay), 3 Fehler — sie sind Umgebungsbefunde, keine Testfehler: die Hände scheitern bei vorn stehendem Notepad (Wine ohne Fenstermanager nimmt `SetForegroundWindow` nicht an), Kamera und Mikrofon fehlen (Quell-Prefix ohne numpy/opencv).
Aus der gebauten exe: die Geräte-Kindprozesse stürzen unter Wine wegen `ucrtbase.crealf` ab und werden als „Prozess ohne Ergebnis beendet (Exitcode …)“ gemeldet, der Test läuft weiter. `--nur=…`/`--ohne=…` wählen Prüfungen, `--still` unterdrückt das Meldungsfenster.

## UNKNOWN / offen

- Alles nativ außer dem ersten Start: Daniel soll `selbsttest.bat` laufen lassen und den Bericht zeigen (besonders: Layered Windows im Bild, Hände bei vorn stehendem Fremdprogramm, Kamera/Mikrofon, opencv/numpy aus dem Bundle).
- Der Dienst `bridge-relay` muss neu gestartet werden, damit Starter, Transport, Whisper und die neue Startliste wirksam werden (Daniel, auf dem Host).
- Agenten müssen die Werkzeuge wirklich nutzen; die Startnachricht ist der Anstoß, kein Zwang. Gemgem-Host/Codex-Host/Claude-Host mit `/root` als Ordner sind angenommen.
- Bilderstrom: Aufnahme begrenzt auf 16 Mio. Pixel; bei größeren virtuellen Bildschirmen scheitert jeder Takt (wird protokolliert, der Selbsttest nennt es).
- Offene Audio-Fragen: Datenschutz im Modus „offen“ (alles geht zum VPS); Sprechtaste als Einzeltaste (F8) kann mit Programmen kollidieren, die F8 selbst nutzen (polled, nicht global angemeldet).
