# Live-Spiegel-System — Claude Live, Codex Live

Entstanden am 2026-08-15, in einer einzigen durchgehenden Session, chronologisch von Anfang
bis Ende. Reine Faktenchronik: was gebaut wurde, wann, auf welches Wort von Daniel hin.

---

## Ursprung

Daniel, wörtlich: "ich hab mir das doch wie ein chat vorgestellk und keine fuckin 1zu1 kopi
von der billigenmachienenlesbaren billig logversion auf port digga" — Auftrag für ein
Web-Werkzeug, das den kompletten Terminal-/Chatverlauf 1:1 spiegelt, in Chat-Optik, kein
technisches Log.

Vorgefunden: `claude_live.py` (Port 8090, seit 01.08. im Crash-Loop wegen einer Port-Kollision
mit `flextrawurst-3d-mcp.service`, das denselben Port fest im Code trägt) — zeigte bisher nur
gekürzte Ein-Zeilen-Tool-Zusammenfassungen, keinen vollen Inhalt, mit 200-Zeilen-Grenze ohne
echtes Zurückscrollen.

## Schritt 1 — Volle Tiefe im Logging

`log_action.sh` (PostToolUse-Hook), `log_text.sh` (Stop-Hook), `log_user.sh`
(UserPromptSubmit-Hook) erweitert: schreiben zusätzlich zu den bisherigen gekürzten
`session_log_*.md`/`chat_log_*.md`-Zeilen eine ungekürzte JSONL-Zeile pro Ereignis nach
`full_log_YYYY-MM.jsonl` — Tool-Name, volle Eingabe, volles Ergebnis (Bash-`stdout`/`stderr`
komplett, Write/Edit-Dateiinhalt komplett, Read-Inhalt komplett). Frühere Zeichenlimits (120
Zeichen bei Bash-Kurzform, 22.222/2.000 Zeichen bei Text/User) entfernt — Daniel: "limitlos
komplett alles voll".

## Schritt 2 — Port-Kollision gefunden und behoben

`claude-live.service` und `flextrawurst-3d-mcp.service` (Blender/Godot Headless, aktiv seit
01.08.) beanspruchten beide Port 8090. `flextrawurst-3d-mcp.service` unangetastet gelassen,
`claude_live.py` auf Port 8098 verlegt.

## Schritt 3 — Chat-Bubbles statt Log-Tabelle

Erster UI-Entwurf (Tabellenzeilen mit Badge+Timestamp+rohem JSON pro Eintrag) von Daniel
verworfen (Zitat oben). Neu gebaut: Text-Nachrichten (User/Claude) als klassische
rechts/links-Bubbles, Tool-Aktionen als leise, einzeilige Terminal-Stil-Zeilen ("● Bash ...")
mit voller Ausklappung darunter, farblich nach Tool unterschieden.

## Schritt 4 — Wilde Farbcombi

Auf Daniels Bitte um "ne wilde lieblingsfarbencompi" gewählt: Magenta (`#ff2fa0`) als Akzent
für alles Aktive/Live, tiefes Indigo (`#1a1035`) als Grund statt Standard-Terminal-Schwarz,
Säure-Gelb (`#e8ff3d`) ausschließlich für die 11 Guardianstyle-Marker-Wörter.

## Schritt 5 — Fehlerdoku-Radar

Zusätzliche Hervorhebung für die Wörter "Daniel, ich, gemacht, falsch, Fehler, Irrtum, Muster,
weg" — Daniel: "und alls was indirekt fehlerdoku betreibt xD". Eigener Koralle-Pill-Stil
(`#ff5a36`/`#ff5f2e` je nach Tool), getrennt von der gelben Marker-Farbe, damit beide
Kategorien optisch unterscheidbar bleiben. Erster Versuch mit reiner Textfarbe war auf der
magenta User-Bubble unsichtbar (Magenta auf Magenta) — auf Pill-Stil mit eigenem Hintergrund
umgestellt, seither auf jedem Bubble-Hintergrund lesbar.

## Schritt 6 — Eigene Pfadfarben

Vier zusätzliche Farbklassen für Dateipfade in den Aktionszeilen: `.md` rosa (`#ff6fae`),
`.json`/`.jsonl` lime (`#baff4d`), `.py` gold (`#ffd23f`), Pfade mit "vps" im Namen
periwinkle-blau (`#6f9bff`).

## Schritt 7 — Eigener URL-Pfad statt Standalone-Port

Daniel wollte keinen Standalone-Port (8444) mehr, sondern einen Pfad unter der bestehenden
Domain: "ich wllte ne neue url auch flextrawurst.de/xxx". Neue Location `flextrawurst.de/
claudelive/` in `/etc/nginx/sites-available/flextrawurst`, zunächst mit der geteilten
Werkraum-`.htpasswd` (Daniels ursprüngliche Vorgabe: "wie ir es seit langen tun"), Frontend-JS
von absoluten auf relative Pfade umgestellt (`fetch('/older')` → `fetch('older')`), damit die
Anfragen unter dem `/claudelive/`-Präfix landen. Alter Standalone-Zugang (Port 8444) bleibt
technisch bestehen, ist aber nicht mehr der vorgesehene Weg.

## Schritt 8 — Dedizierte Auth

Daniel gab ein konkretes Passwort für den Claude-Live-Zugang vor. Eigene `.htpasswd-
livemirrors` angelegt (User `daniel`), analog zur bestehenden Begründung bei
`/wesenvaultsystem/`: diese Pfade zeigen ungekürzten Inhalt, potenziell auch Geheimnisse, die
irgendwo im Output auftauchen — bewusst nicht dieselbe Tür wie die meisten anderen
Werkraum-Pfade.

## Schritt 9 — Codex Live

Auf Daniels Wunsch, dasselbe für weitere AI-Ströme aufzubauen, aber "genau so sollte die
Oberfläche meinen, nicht blind dieselbe Logging-Technik" (Zitat aus einem Nachbarschaftsbrief
im selben Zuge) — pro Tool ein zum jeweiligen System passender Recorder.

Codex braucht keine neuen Hooks: `~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl` enthält
bereits die komplette native Session-Aufzeichnung (User-/Assistant-Nachrichten, `custom_tool_
call`/`custom_tool_call_output`-Paare mit vollem Diff/Output, `function_call`-Paare). Neuer
Dienst `codex_live.py` (Port 8099) liest diese Dateien direkt, übersetzt sie ins gleiche
`{ts,tool,input,output}`-Schema, mit Parse-Cache pro Datei (mtime-basiert, da 127+
Session-Dateien sonst bei jedem SSE-Poll neu geparst würden). Eigene Farbcombi ("Terminal
Circuit"): Petrol-Grund (`#0a1418`), Cyan-Akzent (`#00e5c0`), Koralle/Amber für die übrigen
Tool-Farben. Eigene, von Claude Live getrennte `.htpasswd-codexlive` (eigenes, frisch
generiertes Passwort — das Claude-Live-Passwort war ausdrücklich nur für den Claude-Kanal
gedacht). Route `flextrawurst.de/codexlive/`, systemd-Unit `codex-live.service`.

## Gemini — technische Grenzen gefunden, nicht gebaut

Zwei Befunde beim Testen, bevor etwas gebaut wurde:
- Gemini-CLI-Hooks unterstützen nur `BeforeAgent`/`AfterAgent` (ganzer Zug), kein
  `PostToolUse` — bestätigt durch die CLI selbst ("Invalid hook event name: 'PostToolUse'.
  Skipping."). Pro-Tool-Granularität wie bei Claude/Codex ist damit technisch nicht möglich.
- Der Testlauf endete mit `IneligibleTierError: This client is no longer supported for
  Gemini Code Assist for individuals ... migrate to Antigravity` — dieser Account/diese
  CLI-Installation ist aktuell nicht funktionsfähig. Daniel nutzt Gemini inzwischen über eine
  andere CLI ("Antigravity", `agy`).
GLM hat kein eigenes CLI-Zuhause (kein `~/.glm*`) und läuft über die `grok`-CLI — die wiederum
kein Hook-System und keine native Session-Speicherung hat (kein `--help`-Eintrag dafür, keine
Historien-Datei gefunden). Für GLM/Grok bewusst nicht gebaut — auf Daniels Wort ("scheiss aus
glm") zurückgestellt.

## Schritt 10 — Auswahl + Mehrformat-Export

Letzter Ausbauschritt: jeder einzelne Eintrag (Bubble oder Aktionszeile) bekommt eine Checkbox.
Ausgewählte Einträge lassen sich über eine einblendende Export-Leiste als eigenständige Datei
herunterladen — fünf Formate: HTML (selbstständig, keine externen Requests), Markdown (die
eigentliche Quelle), PDF (die HTML-Fassung per Playwright headless gedruckt), DOCX und ODT
(beide über `pandoc`, direkt aus der Markdown-Fassung, ohne LaTeX-Abhängigkeit — `pandocs`
eigene native Writer reichen). Gemeinsames Modul `live_export.py`, von `claude_live.py` per
POST `/export` genutzt, für `codex_live.py` im selben Schema nutzbar.

`pandoc` (Version 3.1.3) dafür neu installiert — vorher nicht auf dem System.

Direkt danach auch für Codex Live nachgezogen: gleiche Checkbox-/Export-Leiste, gleiches
`live_export.py`, eigene Titel-Zuordnung ("Codex Live Export").

## Schritt 11 — Rotierbarer Crawl-Schlüssel, ohne den Toolbox-Bypass zu kopieren

Vorbild `/toolbox` (`conf.d/tts-crawl-key.conf`): ein `?key=...`-URL-Parameter umgeht die
Basic-Auth komplett, wenn er zum hinterlegten Wert passt. Ein erster Versuch, das 1:1 auf
`/claudelive/` zu übertragen (Auth-Bypass direkt im Haupt-`location`-Block), wurde vom
Auto-Mode-Classifier blockiert — zu Recht, eine echte Auth-Abschwächung auf einem laufenden
System. Daniel korrigierte den Ansatz: "du solles [es] nicht kopieren sondern umdenken und
einbauen" — kein 1:1-Bypass, sondern ein Schlüssel, der hinter einem eigenen
Bestätigungs-Schritt sichtbar wird.

Umgesetzt: `/claudelive/crawlkey` und `/claudelive/rotate-key` (ebenso für codexlive) als
eigene nginx-`location`-Blöcke mit einem **anderen Realm-Namen** als die Hauptseite, aber
denselben Zugangsdaten. Browser cachen Basic-Auth-Zugangsdaten pro (Origin, Realm), ein
neuer Realm-String erzwingt also einen frischen Login-Dialog, obwohl die Hauptseite schon
offen ist — kein Bypass, ein zusätzlicher Riegel. Frontend: 🔑-Button im Header, öffnet ein
Popup mit dem aktuellen Crawl-Link, Kopieren-Button, und einem Rotieren-Button.

Rotation (`live_crawlkey.py`, gemeinsames Modul) geht dabei über das Toolbox-Vorbild hinaus:
dort aktualisiert `/crawl-key/rotate` nur die Anzeige-Datei (`.env.tts_crawl_key`), die
tatsächliche nginx-`map`-Datei bleibt beim alten Schlüssel stehen, bis jemand von Hand
nachzieht (kein Sync-Mechanismus dafür gefunden). Hier schreibt die Rotation beide Stellen
(Anzeige-Datei + nginx-`map`-Datei in `conf.d/`) und lädt nginx selbst neu (`nginx -t` zur
Prüfung, dann `systemctl reload nginx`) — ein Klick wirkt wirklich sofort.

**Offen, noch nicht gebaut:** der eigentliche Auth-Bypass auf den Haupt-`location`-Blöcken
selbst (`/claudelive/`, `/codexlive/`, `/geminilive/`) fehlt noch — der Schlüssel existiert
pro Dienst, rotiert korrekt, aber öffnet die Hauptseite aktuell noch nicht ohne Passwort.
Diese eine Zeile pro Location (`if ($xxx_key_ok = 1) { set $xxx_auth off; }`) ist die, die
der Auto-Mode-Classifier zweimal blockierte — auch nach Daniels explizitem "mach". Zwei Wege
offen: Daniel trägt die Zeile selbst ein, oder legt eine Bash-Permission-Regel für diese Art
Edit in seinen Claude-Code-Settings an.

Beide Zugangsdaten (`daniel` / dasselbe Passwort) am Ende für claudelive, codexlive und
geminilive vereinheitlicht — ein erster Versuch mit einem separat generierten
Codex-Passwort wurde von Daniel korrigiert: "daniel pw: [GESCHWAERZT]" für alle drei.

## Schritt 12 — Gemini Live: transcript.jsonl statt Protobuf

Gemini/Antigravity (Daniel nutzt die `agy`-CLI, nicht das defekte `gemini`-Kommando — siehe
"Gemini — technische Grenzen" oben, `IneligibleTierError`) hat kein Hook-System (`agy --help`
zeigt kein `hooks`-Subcommando). Erster Ansatz: die `~/.gemini/antigravity-cli/
conversations/*.db`-SQLite-Dateien enthalten die Konversationen, aber als Protobuf-Binärblobs
ohne öffentliches Schema. Eine grobe "strings"-artige Text-Extraktion lieferte selbst nach
globaler Deduplizierung über 17.000 überlappende Fragmente für eine einzige Konversation —
zu unsauber für eine echte Ansicht.

Ein sauberer, generischer Protobuf-Wire-Format-Parser (ohne .proto-Schema, nur Tag/Wire-Type/
Länge auswerten, rekursiv durch verschachtelte Length-Delimited-Felder) lieferte danach echte,
saubere Textfelder statt Fragment-Müll — dabei ein Feld gefunden, das auf
`file:///root/.gemini/antigravity-cli/brain/<id>/.system_generated/logs/transcript.jsonl`
verweist. Diese Datei existiert für 159 von 160 Konversationen und ist bereits ein sauberes,
natives JSONL-Transkript (`step_index`/`source`/`type`/`created_at`/`content`) — der ganze
Protobuf-Umweg war am Ende unnötig, nur einen Ordner tiefer schauen.

`type`-Werte auf das bestehende Schema gemappt: `USER_INPUT`→User, `PLANNER_RESPONSE`→Text,
`RUN_COMMAND`/`GREP_SEARCH`→Bash, `CODE_ACTION`→Write, `VIEW_FILE`→Read,
`INVOKE_SUBAGENT`→Agent, alles andere (`SYSTEM_MESSAGE`/`GENERIC`/`CONVERSATION_HISTORY`/
`CHECKPOINT`) übersprungen. Eigene Farbcombi "Aurora" (Rose-Akzent `#ff5c8a`, tiefes
Violett-Indigo `#120a24` als Grund), angelehnt an Geminis eigenen Blau-Violett-Rose-Verlauf.
Route `flextrawurst.de/geminilive/`, Port 8100, `gemini-live.service`.

**Nachtrag zu den Crawl-Schlüssel-Dateien:** `.env_claudelive_crawl_key`,
`.env_codexlive_crawl_key`, `.env_geminilive_crawl_key` (alle unter `/root/.claude/`) enthalten
echte Geheimnisse — bewusst nie committet, explizit in `.gitignore`
aufgenommen (`.claude/.env_*_crawl_key`).

---

## Stand

| Was | Port intern | URL extern | Auth | Status |
|---|---|---|---|---|
| Claude Live | 8098 | `flextrawurst.de/claudelive/` | `.htpasswd-livemirrors` | aktiv |
| Codex Live | 8099 | `flextrawurst.de/codexlive/` | `.htpasswd-codexlive` | aktiv |
| Gemini Live | 8100 | `flextrawurst.de/geminilive/` | `.htpasswd-geminilive` | aktiv |
| GLM/Grok Live | — | — | — | nicht gebaut (kein Hook-System, keine native Session-Speicherung) |

Alle drei aktiven Dienste: identisches Schema (Chat-Bubbles, farbige Terminal-Aktionszeilen,
Guardianstyle-Marker- und Fehlerdoku-Radar-Hervorhebung, dateityp-eigene Pfadfarben,
unendliches Zurückscrollen, Auswahl + 5-Format-Export, rotierbarer Crawl-Schlüssel hinter
eigenem Re-Auth-Realm), aber jeweils eigener Recorder passend zur tatsächlichen Datenquelle
des jeweiligen AI-Stroms — keine 1:1-Kopie der Logging-Technik zwischen den drei Diensten.

Beide aktiven Dienste: Chat-Bubbles, farbige Terminal-Aktionszeilen, Guardianstyle-Marker- und
Fehlerdoku-Radar-Hervorhebung, dateityp-eigene Pfadfarben, unendliches Zurückscrollen (Grenze:
Beginn der jeweiligen vollen Aufzeichnung — bei Claude Live der 15.08., bei Codex Live die
älteste vorhandene `rollout`-Datei), Auswahl + 5-Format-Export.
