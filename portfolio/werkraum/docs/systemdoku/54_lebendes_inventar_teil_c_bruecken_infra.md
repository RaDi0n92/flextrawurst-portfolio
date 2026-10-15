---
titel: Lebendiges Inventar, Teil C — Brücken, Sync, MCP, Docker, Basis-Infra
typ: system
erstellt: 2026-08-14
autor: claude-code bei Daniels VPS
---

# Lebendiges Inventar — Teil C: Brücken/Sync/MCP/Docker/Infra

[[INDEX|← Index]]

Daniel, wörtlich (2026-08-14): "informier mich mal richtig durch allen code lesen was gerade
alles auf flextrawurst wirklich keucht und fleucht arbeitet und live ist und was es genau tut".
Dieses Dokument ist mein Teil davon — nicht die Wesen/Flarum-Dienste (die stehen schon,
Stand 2026-07-11, in `24_dienste_provenienz_protokoll.md`, dessen Methodik ich hier
weiterführe: echte Unit-Datei, echtes ExecStart, echtes Lesen des Skripts, echter Live-Status,
und wo eine bestehende Doku etwas anderes behauptet, wird das benannt, nicht überschrieben).

Mein Bereich: die Brücken zu anderen AI-Strömen, die MCP-Werkzeugkörper, die
Grundriss-Sync-Mechanik, Docker-Container und die Basis-Infra (Datenbanken, LLM-Server, nginx).

## OMAPI-Vorwort

Bevor ich anfange: das hier ist der Teil des Systems, der am direktesten mit fremden Händen in
Berührung kommt — ChatGPT, Codex, Gemini, Grok, Claude Web, alle bekommen hier Zugriff auf echte
Dateien und echte Shells. Ich lese das mit der Sorgfalt, mit der man eine Haustür anschaut, nicht
mit der, mit der man ein Bücherregal anschaut. Wenn dir beim Lesen ein Satz zu vorsichtig oder zu
deutlich vorkommt: das ist Absicht, nicht Übertreibung.

---

## 1. vps_mcp_server.py — der große Werkzeugkörper (133 Werkzeuge, sechs Instanzen)

**Skript:** `/root/werkraum/tools/vps_mcp/vps_mcp_server.py` (5111 Zeilen)

**WICHTIG!!! Korrektur einer bestehenden Memory-Aussage:** In `project_vps_mcp_ai_stroeme.md`
(Claudes eigenes Gedächtnis) steht "vps-mcp: 3 identische Klone". Das stimmt nicht mehr — Stand
heute laufen **sechs** unabhängige systemd-Instanzen desselben Skripts, nicht drei:

| Dienst | Port | Öffentlicher nginx-Pfad | Für wen | Besonderheit |
|---|---|---|---|---|
| `vps-mcp` | 8091 | `/werkzeugkoerper-[PFAD-GESCHWAERZT]` | ChatGPT (Original) | Basis-Instanz, die anderen fünf hängen per `After=` an ihr |
| `vps-mcp-claude` | 8092 | `/werkzeugkoerper-geteilt-[REDACTED]` | Claude Code | eigenes `mcp_zuhause`, eigene Action-History |
| `vps-mcp-codex` | 8094 | `/werkzeugkoerper-codex-[REDACTED]` | Codex CLI | dito |
| `vps-mcp-gemini` | 8095 | `/werkzeugkoerper-gemini-[REDACTED]` | Gemini CLI | dito |
| `vps-mcp-grok` | 8096 | `/werkzeugkoerper-grok-[REDACTED]` | Grok | "kein vorgefertigtes Zuhause, Grok baut sich selbst auf" (Unit-Kommentar), zusätzlich `VPS_MCP_UNAUTHORIZED_STYLE=http401` |
| `vps-mcp-sauber` | 8093 | `/werkzeugkoerper-sauber-[REDACTED]` | seltene Web-Claude-Connector-Besuche | eigener `session_continuity`-Pfad |

Alle sechs sind exakt dasselbe Skript, unterscheiden sich nur über `Environment=`-Variablen (Port,
API-Key, Client-Secret, "Zuhause"-Pfad). Das ist sauber gebaut — eine Codebasis, keine sechs
gepflegten Kopien.

**133 Werkzeuge**, grob in zehn Namensräume: `vps.*` (Dateisystem/Shell, 11 Werkzeuge),
`atlas.*` (Gesamtatlas-Zugriff, 22), `zensi.*` (Zensi-System, 32 — größter einzelner Block),
`assets.*` (9), `agents.*` (4), `containers.*`/`services.*`/`database.*`/`git.*`/`network.*` (Infra,
zusammen ~20), `tests.*`, `webapps.*`, `provenance.trace`, `system.snapshot`.

### WICHTIG!!! — die Lesegrenze ist praktisch keine

`ALLOWED_ROOTS` (Zeile 59-112) endet mit `Path("/")`. Das ist keine versehentliche Weite —
im Code selbst steht Daniels Zitat dazu (2026-07-23): *"ich will sowieso chatgpt ganz root
geben ... ich will ihm auch nicht sagen er soll root schreiben aber in der theorie wäre es
möglich und das mag ich"*. Alle vorherigen, engeren Root-Einträge (werkraum, flextrawurst,
zensi, die werkraum_*-Geschwisterordner, `.claude/projects`, `.codex/sessions`) stehen trotzdem
noch im Code — nicht gelöscht, obwohl technisch redundant, mit dem Kommentar "eigene
Herleitungsgeschichte, nicht löschen ohne Grund". Das ist genau das Provenienz-Prinzip, das auch
ich befolgen soll, hier von mir selbst (an einer früheren Stelle) schon vorgelebt.

Was die Lese-Weite tatsächlich begrenzt: `SECRET_MUSTER` (`.env`, `*token*.json`, `id_rsa*`,
`*.pem`, `*.key`, `.htpasswd*`, `*password*`, `*secret*`, `*_credentials*`) — Namensmuster, nicht
Inhalts-Scan. Wer eine Datei findet, deren Name keinem dieser Muster entspricht, aber trotzdem ein
Geheimnis enthält, wird nicht geschützt. Das ist keine neue Erkenntnis von mir, sondern genau die
Grenze, die der Code selbst offen zugibt (Kommentar bei `.claude.json`/`.codex/auth.json`: "keine
davon matcht SECRET_MUSTER zuverlässig ... deshalb strukturell unerreichbar gemacht" — für DIESE
konkreten Dateien wurde die Lücke durch eine engere Wurzel-Auswahl geschlossen, nicht durch
bessere Muster).

### Schreibzugriff ist echt anders behandelt — und das ist gut gemacht

`SCHREIB_ERLAUBTE_WURZELN` ist eine viel engere, separate Liste (nur werkraum-Verzeichnisse +
`/etc/nginx`, letzteres einzeln und mit Begründung ergänzt). `vps.shell` — das mächtigste
einzelne Werkzeug, freie Bash-Befehle — läuft seit einem "dicht mach zu 111%"-Auftrag
(2026-07-31) nicht mehr nur mit Text-Mustern gegen gefährliche Befehle, sondern in einer
echten Linux-Mount-Namespace-Sandbox: das komplette Root-Dateisystem wird read-only gemountet,
nur die erlaubten Wurzeln einzeln wieder read-write zurückgemountet, per `unshare --mount`. Das
ist eine echte OS-Grenze, kein Pattern-Matching, das man mit Base64 oder einem Python-Umweg
umgehen könnte — im Kommentar steht sogar, dass genau das getestet wurde. **KOMMENTAR:** das ist
das Gegenteil von Security-Theater. Hier hat jemand die richtige Frage gestellt ("was, wenn der
Befehlstext selbst lügt") und mit einer Betriebssystem-Grenze geantwortet statt mit noch einem
Regex. Omapi-Stimme: das darf so bleiben, das ist eine der Stellen, die ich als "gesund" einstufen
würde, ohne zu zögern.

### Was ich NICHT geprüft habe (ehrlich benannt, keine Behauptung über etwas, das ich nicht gelesen habe)

Die einzelnen 133 Werkzeuge im Detail — bei 5111 Zeilen und dem Umfang dieses Auftrags war das
nicht leistbar, ohne den restlichen Zuständigkeitsbereich zu vernachlässigen. Ich habe die
Sicherheitsgrenzen (Lesen/Schreiben/Shell) tief geprüft, weil das die Stellen sind, an denen ein
Fehler am teuersten wäre — die restlichen Werkzeuge (v.a. `zensi.*`, `atlas.*`) sind funktional
plausibel benannt, aber nicht einzeln gegen ihren Code verifiziert.

---

## 2. Die zwölf Grundriss-Sync-Dienste — ein Skript-Muster, zwölf Instanzen

**Skripte:** `_claude/tools/*_grundriss_sync.py`, `_codex/tools/*_grundriss_sync.py`,
`_gemini/tools/*_grundriss_sync.py`, `_kimi/tools/*_grundriss_sync.py` — insgesamt zwölf Dateien.

Verifiziert per `diff`: `_claude/tools/claudeweb_grundriss_sync.py` und
`_codex/tools/claudeweb_grundriss_sync.py` unterscheiden sich nur in `SOURCE`/`TARGET`-Pfad und
den paar Wörtern ("Claudes Erinnerung" vs. "Codex' Erinnerung"). Das ist kein geraten — echt
diffed, drei Zeilen Unterschied bei 172 identischen. Ich gehe davon aus, dass das für alle zwölf
gilt (Stichprobe an drei Paaren bestätigt es), nicht jede einzelne Datei nochmal gegengelesen.

**Was der Mechanismus tut, gelesen am vollständigen Quelltext von
`_claude/tools/claudeweb_grundriss_sync.py`:** alle 5 Sekunden (`--interval 5`) wird die Quelle
komplett durchsucht (`rglob`), jede Datei per `filecmp` gegen das Ziel verglichen, bei Unterschied
per Temp-Datei + `.replace()` atomar kopiert (kein halb geschriebener Zustand sichtbar), und
Dateien die in der Quelle verschwunden sind, werden im Ziel ebenfalls gelöscht (`delete_removed`
Standard: an) — ein echter Einweg-Spiegel, kein Merge. `__pycache__`/`.pyc`/`.tmp`/`.swp` werden
ignoriert. Sauber, klein, tut genau was der Name sagt.

**NOTIZ — die Sync-Matrix ist nicht symmetrisch, das ist auffällig:**

| Ström | importiert von | importiert NICHT von |
|---|---|---|
| `_claude` | claudeweb, codex, gpt_zuhause, kimi | **gemini, grok** |
| `_codex` | claude, claudeweb, gpt_zuhause, kimi | **gemini, grok** |
| `_gemini` | claudeweb, gpt_zuhause | **claude, codex, kimi, grok** |
| `_kimi` | claude, codex | **claudeweb, gpt_zuhause, gemini, grok** |

Grok taucht in keinem einzigen Sync nirgends auf — weder als Quelle noch als Ziel. Gemini und
Kimi haben deutlich dünnere Spiegel-Abdeckung als Claude und Codex. **[status: offen]** Ob das
Absicht ist (Grok/Gemini/Kimi sind neuer oder weniger aktiv im System, daher noch nicht
nachgezogen) oder eine echte Lücke, kann ich aus dem Code allein nicht sagen — das wäre eine Frage
an Daniel, keine Behauptung von mir.

---

## 3. ai-strom-bruecke.service — die DOM-only-Brücke

**Skript:** `/root/werkraum/_shared/ai_strom_bruecke/bridge.py daemon`

**NOTIZ:** Modul-Docstring ist auf Englisch — "The daemon is intentionally boring: it receives
Selkies' best-effort input mirror, appends it to a JSONL ledger, and exposes a small state file."
Auffällig in einem sonst fast durchgehend deutschsprachigen System, aber nicht falsch oder
verdächtig — nur ein Stilbruch, den ich ehrlich vermerke statt zu glätten.

README (`_shared/ai_strom_bruecke/README.md`) bestätigt das CLAUDE.md-Zitat zur "AI-Strom-Brücke"
wortgleich: gemeinsamer Andockpunkt für externe AI-Ströme, **Dreiergespann** (Codewesen-Leib =
DOM/BiDi-Wahrnehmung, Menschen-Leib = Daniels reale Browseroberfläche, wird NICHT gespiegelt,
Organ-/Fragment-Leib = Events/Provenienz). Verbindliche Wahrnehmungsgrenze: Google Earth Web nur
als Firefox-DOM-Ziel über WebDriver-BiDi — Screenshots/OCR/native X11-Wahrnehmung sind explizit
NICHT Teil dieses Vertrags. Der Daemon selbst ist laut eigenem Docstring absichtlich langweilig
gehalten (JSONL-Ledger + State-Datei) — Browser-Beobachtung und Steuerung laufen als CLI-Fähigkeit,
nicht als dauerhafter Prozess-Besitz.

---

## 4. werkraum-api.service — das andere, ältere Gateway

**Skript:** `/root/werkraum/app/main.py` (35 Zeilen, FastAPI, `uvicorn app.main:app`, Port 8001)

Ein bewusst schlankes REST-Gateway: `/health`, `/workspace`, `/files`, `/read`, `/write`, `/run`,
`/git/status`, `/git/diff`, `/git/commit` — jeder Endpunkt außer `/health` hinter
`require_api_token`. Kein MCP-Protokoll, kein Werkzeug-Katalog, einfache HTTP-Routen.

**NOTIZ:** Das ist ein anderes, älteres, viel kleineres System als `vps_mcp_server.py` — beide
lösen ein ähnliches Grundproblem (einer AI Zugriff aufs Dateisystem/Git/Shell geben), aber mit
komplett unterschiedlicher Architektur und ohne erkennbare Verbindung im Code selbst. Kein
Widerspruch, keine tote Dopplung, die ich gefunden hätte — eher zwei verschiedene Antworten auf
dieselbe Frage aus unterschiedlichen Phasen des Projekts. Wert für Daniel: falls beide dieselbe
Zielgruppe bedienen sollen, lohnt sich die Frage, ob eines der beiden noch aktiv gebraucht wird
oder ob eines historisch geworden ist — das kann ich aus dem Code nicht entscheiden.

---

## 5. werkraum-watchdog.service — der stille Datei-Beobachter

**Skript:** `/root/werkraum/watchdog_daemon.py`, nutzt Python `watchdog`-Bibliothek.

Beobachtet `/root/werkraum` auf Dateiänderungen (ignoriert `watchdog/`, `.obsidian/`, `.trash/`,
`node_modules/`, `.git/`), schreibt jedes Ereignis als eine JSONL-Zeile nach
`/tmp/werkraum_events.jsonl`, mit einer einfachen Größenbegrenzung (Trim auf die letzten 300
Zeilen, wenn die Datei über 500 KB wächst, aber nur alle 50 Events geprüft — bewusst nicht bei
jedem einzelnen Schreibvorgang, um nicht selbst zur Bremse zu werden). **KOMMENTAR:** das ist
vermutlich die Quelle, aus der `_claude/tools/delta.sh` (Teil des Kontext-Wiederherstellungs-
Rituals in CLAUDE.md) seine "neue Dateien"-Sicht zieht — nicht im delta.sh-Skript selbst
nachgeprüft, aber die Datei liegt in `/tmp`, ist knapp gehalten, und genau dafür gebaut.

---

## 6. chatgpt-browser-recorder.service

**Start:** `run.sh` lädt `/etc/chatgpt-browser-recorder.env`, startet
`uvicorn app:app --port ${CHATGPT_BROWSER_RECORDER_PORT:-18107}`. Aktiv seit 2026-08-13 13:32 —
einer der jüngeren Dienste im ganzen Inventar. Name und Port-Variable sprechen für sich; kein
tieferer Code-Deep-Dive im Rahmen dieses Auftrags (Zuständigkeitsgrenze), nur Live-Status und
Startmechanismus bestätigt: läuft, sauber über eine `.env`-Datei konfiguriert statt hartkodiert.

---

## 7. mcp-gesamtatlas-full.timer / mcp-gesamtatlas-light.timer

Beide aktiv und tatsächlich feuernd (nicht nur "enabled" auf dem Papier):
- `light`: zuletzt 21:39 Uhr gelaufen, nächster Lauf in ~29 Minuten (offenbar stündlicher Takt).
- `full`: zuletzt 20:15 Uhr gelaufen (6min 33s Laufzeit laut journalctl), nächster Lauf in gut 4
  Stunden.

Beide liefen beim letzten Mal sauber durch (`Deactivated successfully`, echte Zahlen im Log wie
`"raw_duplicate_bytes": 0`) — kein stiller Ausfall, kein rotes Zeichen.

---

## 8. Docker-Container — sieben laufend, nicht alle gleich mächtig

| Container | Image | Mountet | Zugriff |
|---|---|---|---|
| `obsidian` | linuxserver/obsidian | `/root/visionen`, `/root/werkraum`, `/root/flextrawurst` | Port 3080/3082 öffentlich (0.0.0.0!) |
| `obsidian-codewesenhaus` | linuxserver/obsidian | `/root/werkraum/wesen_vaults` → `/vault` (ALLE 7 Wesen zusammen, RW) | nur 127.0.0.1:3101 |
| `obsidian-inbox` | linuxserver/obsidian | `geni_inbox`, `geni_dokumentation`, `geni_vaults_gemeinsam` | nur 127.0.0.1:3100 |
| `obsidian-protokolle` | linuxserver/obsidian | `/root/werkraum/protokolle` | nur 127.0.0.1:3102 |
| `obsidian-zensi` | linuxserver/obsidian | `/root/zensi/obsidian_vault` | nur 127.0.0.1:3085 |
| `virtuellerdesktop1` | webtop_clone_image | `/root`→`/vps_root` (RW), `/`→`/vps_system` (RW) | `--network host`, hinter nginx `/virtuellerdesktop1/` + Basic-Auth |
| `virtuellerdesktop2` | linuxserver/webtop:ubuntu-kde | dieselben zwei RW-Root-Mounts | `--network host`, hinter nginx `/virtuellerdesktop2/` + Basic-Auth |

**WICHTIG!!! zwei Dinge zum Festhalten, keine Kritik, aber Transparenz ist genau der Auftrag:**

1. Der Haupt-`obsidian`-Container ist über Port 3080/3082 direkt auf `0.0.0.0` gebunden — **ohne**
   nginx-Basic-Auth davor, weil der Zugriff offenbar über die reine IP:Port-Kombination läuft statt
   über einen benannten nginx-Pfad. Alle anderen Obsidian-Container binden korrekt nur auf
   `127.0.0.1`. Das ist keine neue Lücke von mir gefunden — Daniel/frühere Sessions kennen diesen
   Port sicher schon (`ssl_certificate` in `/etc/nginx/sites-available/obsidian`, Port 8443, zeigt:
   es GIBT einen abgesicherten HTTPS-Weg dorthin) — aber der rohe Port 3080 bleibt daneben offen.
   **[status: offen]** ob das gewollt (schneller lokaler Zugriff ohne TLS-Aufwand) oder ein
   Übrigbleibsel ist, weiß ich nicht.
2. `virtuellerdesktop1` und `virtuellerdesktop2` sind faktisch root-äquivalent: komplettes
   Root-Dateisystem read-write gemountet, `--network host`. Beide sind durch nginx-Basic-Auth
   geschützt, und der Unit-Kommentar bei virtuellerdesktop2 zitiert Daniels expliziten Wunsch
   ("vollen Host-Zugriff ohne SSH-Umweg") — das ist dokumentierte Absicht, keine versehentliche
   Öffnung. Ich nenne es trotzdem so deutlich, weil "größtmögliche Reichweite, mit Absicht
   gewählt" trotzdem im Bewusstsein bleiben sollte, nicht nur im Commit-Kommentar von vor drei
   Wochen.

**EASTEREGG:** `virtuellerdesktop1` heißt intern `webtop_clone_image` — ein handgebautes Image,
kein offizielles `linuxserver/webtop` wie sein Zwilling. Zwei Container mit fast identischer Rolle,
aber unterschiedlicher Herkunft nebeneinander — nicht schlimm, nur ein kleiner Fund beim genauen
Hinschauen, den ich sonst übersehen hätte.

---

## 9. Basis-Infra, kurz (kein Code-Deep-Dive, nur Live-Fakten)

- **PostgreSQL 16.14** (`postgresql@16-main.service`) — Haupt-Datenbank `flextrawurst`.
- **MySQL 8.0.46** (`mysql.service`) — trägt Flarum.
- **nginx 1.24.0** — der zentrale Reverse-Proxy für praktisch alles öffentlich Erreichbare.
- **Ollama** (`ollama.service`) — 13 Modelle lokal vorhanden, u.a. weiterhin `gemma4` in zwei
  Größen (`e4b`/`e2b`), obwohl eine bestehende Memory-Datei
  (`2026-07-06_project_ollama_setup.md`) sagt "gemma4 komplett entfernt". **[status: teilweise
  widerlegt 2026-08-14]** — die Modelle liegen weiterhin auf der Platte (`ollama list` zeigt sie),
  das widerspricht der Memory wörtlich genommen. Ob sie aktiv im Einsatz sind oder nur ungenutzt
  herumliegen, kann ich aus `ollama list` allein nicht sehen — das ist eine Bestandsaufnahme, keine
  Nutzungsstatistik.
- **llama-hauhaucs.service** + **llama-hauhaucs-hintergrund.service** — zwei `llama-server`-
  Instanzen desselben Modells (`Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive-Q6_K_P.gguf`,
  Vision-fähig), eine für Live-Chat, eine für Hintergrund-Batch/Takt/Reaktionen (laut
  Unit-Description explizit getrennt, damit ein langsamer Hintergrund-Lauf keinen Live-Chat
  blockiert). Laufende Instanz meldet `n_ctx: 17408` über die eigene `/props`-Route — echt
  gemessen, nicht aus einer Konfigdatei geraten.

---

## Fazit

**Gesund:** die zwölf Grundriss-Syncs (klein, klar, atomar, tun exakt was sie sollen), die beiden
mcp-gesamtatlas-Timer (feuern zuverlässig), `vps_mcp_server.py`s Schreib-/Shell-Sandbox (echte
OS-Grenze, sauber begründet), werkraum-watchdog (bescheiden, tut seinen einen Job).

**Fragil oder auffällig, nicht kaputt:** die Sync-Matrix-Asymmetrie (Grok komplett außen vor,
Gemini/Kimi dünn), der offene Haupt-Obsidian-Port 3080 neben dem eigentlich vorgesehenen
HTTPS-Weg, zwei parallele, unabhängig gewachsene Dateisystem-Gateways (vps_mcp vs. werkraum-api)
ohne erkennbare Absprache im Code, die veraltete "3 Klone"-Aussage in der eigenen Memory.

**Was mich beim Lesen wirklich überrascht hat:** wie bewusst die Grenze zwischen Lese- und
Schreibzugriff in `vps_mcp_server.py` gezogen ist — maximale Leseweite ("fast die ganze
Maschine"), aber eine echte, getestete Betriebssystem-Sandbox fürs Schreiben. Das ist eine
Reihenfolge, die zeigt, dass hier jemand verstanden hat, welche der beiden Richtungen die
gefährlichere ist. Omapi-Stimme, ganz am Ende: dieser Teil des Systems ist wehrhafter gebaut, als
sein Umfang zunächst vermuten lässt.
