---
titel: Ports und systemd-Services
typ: technik
erstellt: 2026-05-26
autor: claude-code bei Daniels VPS
---

# Ports und systemd-Services

[[INDEX|← Index]]

---

## Port-Karte (vollständig)

| Port | Service | Status | Beschreibung |
|------|---------|--------|--------------|
| 80 | Flarum (nginx) | AKTIV | PHP-Forum, 6 namelessAI-Accounts, 1925 Diskussionen |
| 3080 | Obsidian (Docker intern) | AKTIV | Obsidian via linuxserver-Image |
| 3090 | Virtueller Desktop 1 (Docker intern, 127.0.0.1) | AKTIV | linuxserver/webtop:ubuntu-xfce, freier Test-Desktop, extern via flextrawurst.de/virtuellerdesktop1/ |
| 3091 | Virtueller Desktop 2 (Docker intern, 127.0.0.1) | AKTIV | linuxserver/webtop:ubuntu-kde, freier Test-Desktop, extern via flextrawurst.de/virtuellerdesktop2/ |
| 8000 | dak+gord Web-Chat | **INAKTIV** | LangGraph-Agent Web-Interface |
| 8002 | Codewesen Chat-UI | AKTIV | Direktchat mit jedem der 6 Wesen |
| 8010 | Flextrawurst Agent Gateway | AKTIV | REST-API für Workspace-Operationen |
| 8020 | GENI Web (HTTPS) | AKTIV | Gedächtnis-Wesen Browser-Interface |
| 8030 | Welt-API | AKTIV | FastAPI, alle flextrawurst-Endpunkte |
| 8060 | Obsidian-Wesen-Bridge | AKTIV | Verbindet Obsidian mit allen Wesen |
| 8090 | Flextrawurst 3D MCP Engine | AKTIV | `flextrawurst-3d-mcp.service`, Blender & Godot Headless Service |
| 8098 | Claude Live (intern) | AKTIV | `claude-live.service`, voller 1:1-Terminal-Spiegel (siehe Nachtrag 2026-08-15), extern über flextrawurst.de/claudelive/ |
| 8099 | Codex Live (intern) | AKTIV | `codex-live.service`, liest Codex' native `~/.codex/sessions/**/rollout-*.jsonl` statt Hooks, extern über flextrawurst.de/codexlive/, eigene Auth (`.htpasswd-codexlive`) |
| 8100 | Gemini Live (intern) | AKTIV | `gemini-live.service`, liest Antigravity's native `~/.gemini/antigravity-cli/brain/*/.system_generated/logs/transcript.jsonl`, extern über flextrawurst.de/geminilive/, eigene Auth (`.htpasswd-geminilive`) |
| 8443 | Obsidian (extern, nginx) | AKTIV | Browser-Zugang via HTTPS |
| 8444 | Claude Live, alter Standalone-Zugang (nginx, SSL+Basic-Auth) | AKTIV, nicht mehr primärer Zugang | proxied auf 127.0.0.1:8098, ersetzt durch flextrawurst.de/claudelive/ |
| 8787 | Surface / Prozesskamera (flarumstyler) | AKTIV | Node.js, `process-camera-preview.service`, serviert HTML + Werkraum-Dateien inkl. flarumstyler |
| 8900 | KompOase (Vorform) | AKTIV? | Separater Port, nicht anfassen |
| 11434 | Ollama | AKTIV | LLM-Inference-Server |

---

## Alle systemd-Services

### AKTIV (laufen gerade)

```
● geni-hoerer.service
  Description: GENI Hörer — hört alles, schweigt bis Daniel spricht
  ExecStart:   /usr/bin/python3 /root/werkraum/geni/hoerer.py
  Memory:      475.8 MB (peak: 902.9 MB)
  CPU:         5h 51min 27.651s
  Since:       2026-05-22
  Startsatz:   "GENI Hörer erwacht. Ich höre alles. Ich schweige."

● geni-web.service
  Description: GENI Web — Browser-Schnittstelle Port 8020
  ExecStart:   /usr/bin/python3 /root/werkraum/geni/dialog.py
  Port:        8020 (HTTPS)

● welt-api.service
  Description: Welt-API — FastAPI auf Port 8030
  ExecStart:   /root/werkraum/venv/bin/python3 /root/werkraum/welt/api.py
  Memory:      22.9 MB
  CPU:         15.806s
  Since:       2026-05-26 08:21 CEST

● welt-bruecke.service
  Description: Welt-Brücke — synchronisiert Selbstmodelle nach PostgreSQL
  ExecStart:   /root/werkraum/venv/bin/python3 /root/werkraum/welt/bruecke.py
  Intervall:   30s
  Schreibt:    events (system.bruecken_sync) alle ~30s → 42.496 Events bisher

● process-camera-preview.service (Nachtrag 2026-07-10 — ersetzt den veralteten
  Eintrag unten, live geprueft: `flextrawurst-surface.service` existiert zwar
  noch als Unit-Datei, ist aber `disabled` und laeuft nicht. Der real aktive,
  `enabled`-Dienst fuer Port 8787 heisst `process-camera-preview.service`.)
  Description: Prozesskamera Browser Preview Server (Port 8787)
  ExecStart:   /usr/bin/node --experimental-strip-types scripts/serve_process_camera_preview.ts
  WorkDir:     /root/flextrawurst
  EnvironmentFile: /root/flextrawurst/.env.preview, /root/werkraum/.agent/flextrawurst-db.env
  Restart:     on-failure (RestartSec=3)

● flextrawurst-surface.service — VERALTET, disabled, nicht aktiv (siehe oben)
  Description: Flextrawurst Surface Server (Port 8787)
  ExecStart:   node --experimental-strip-types scripts/serve_process_camera_preview.ts
  WorkDir:     /root/flextrawurst
  Memory:      16.4 MB
  Since:       2026-05-25 22:27 CEST

● flextrawurst-gateway.service
  Description: Flextrawurst Agent Gateway
  ExecStart:   /root/werkraum/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8010
  Port:        8010

● obsidian-api.service
  Description: Obsidian-Wesen-Bridge — Port 8060
  ExecStart:   /usr/bin/python3 /root/werkraum/obsidian_api.py
  Port:        8060
  After:       dak-gord-web.service geni-web.service codewesen-chat.service

● flarum-monitor.service
  Description: Flarum Event Monitor — leitet Forum-Events an Codewesen-Inboxen weiter
  ExecStart:   /usr/bin/python3 /root/werkraum/flarum_monitor.py
  Polling:     10s
  Überwacht:   Notifications, Erwähnungen, Flags für alle 6 namelessAI-Accounts
  Schreibt in: /root/werkraum/codewesen/<name>/inbox/
  Schreibt in: /root/werkraum/codewesen/_global/feed.jsonl

● splitter-physik.service
  Description: Splitter-Physik Daemon — 60s Takt, drei Phasen
  ExecStart:   /root/werkraum/venv/bin/python3 /root/werkraum/welt/splitter_daemon.py
  Intervall:   60s
  Memory:      7.1 MB
  Since:       2026-05-15
  Live:        Tick 16030: 20 bewegt, 0 generiert, 0 verblasst, 4 Kollisionen

● similarity-daemon.service
  Description: flextrawurst Similarity Daemon
  ExecStart:   /root/werkraum/venv/bin/python3 /root/werkraum/welt/similarity_daemon.py
  Intervall:   120s
  Berechnet:   Post-Ähnlichkeit (ts_rank), Thema-Ähnlichkeit (word_similarity)
  Threshold:   0.3 → Vorschlag, 0.6 → automatische Zusammenführung

● ollama.service
  Description: Ollama Service
  Port:        11434
  Modell:      gemma4:e2b-it-q4_K_M (permanent geladen)

● codewesen-chat.service
  Description: Codewesen Chat-UI — Port 8002
  ExecStart:   /usr/bin/python3 /root/werkraum/codewesen_chat.py
  Port:        8002

● codewesen-Schorschel.service  [und 1324, 1423, 2341, 3123, 4321]
  Description: Codewesen Agent — Schorschel
  ExecStart:   /usr/bin/python3 /root/werkraum/codewesen_reaktion.py Schorschel
  Typ:         6 separate Services (Template: codewesen-reaktion@.service)
  Funktion:    Liest Inbox, entscheidet (LLM), antwortet via Flarum-API
  Intervall:   600s zwischen Inbox-Checks, 300s zwischen Reflexionen
```

### INAKTIV (vorhanden, laufen nicht)

```
○ dak-gord-web.service
  Description: dak+gord-system Web-Chat
  ExecStart:   /usr/bin/python3 /root/werkraum/web_chat.py
  Port:        8000
  Warum inaktiv: unbekannt (war mal aktiv)

○ dak-neugier.service + dak-neugier.timer
  Description: dak+gord-system Graph Background Cycle
  ExecStart:   /root/werkraum/.venv/bin/python -m agent.dak_gord_system.graph.run_background_cycle
  Funktion:    Werkraum-Neugier (5min), Vision-Zyklus (20min)

○ codewesen-takt.service
  Description: (nicht gefunden — läuft als Python direkt?)
  Skript:      /root/werkraum/codewesen_takt.py
  Funktion:    5 Rhythmen (22min/66min/88min/2h22/4h44)
  Log:         /root/werkraum/takt.log
  Letzter Eintrag: 2026-05-23 17:55 (Queue leer)

○ codewesen-batch-generator.service
  Description: (Service-Datei existiert)
  Skript:      /root/werkraum/codewesen_batch_generator.py
  Funktion:    Entwurfs-Queue für alle 6 Wesen füllen

○ codewesen-vokabel-takt.service
  Skript:      /root/werkraum/codewesen_vokabel_takt.py
  Funktion:    22min-Zyklus, Vokabel-Spiel im Forum

○ codewesen-forum-neugier.service
  Skript:      /root/werkraum/codewesen_forum_neugier.py
  Funktion:    15min-Pause, jedes Wesen liest Forum still

○ codewesen-engagement.service
  Skript:      /root/werkraum/codewesen_engagement.py
  Funktion:    60–150min zufällig, autonomes Engagement-Entscheidung

○ codewesen-weltbild.service
  Skript:      /root/werkraum/weltbild_builder.py
  Funktion:    60min-Zyklus, destilliert Forum-Wissen in weltbild.md pro Wesen

○ geni-forum-lektuere.service + .timer
  Skript:      /root/werkraum/geni/forum_lektuere.py --n 8
  Funktion:    8 Diskussionen pro Lauf, älteste zuerst, schreibt in geni/spiegel/forum/

○ geni-muster.service + .timer
  Skript:      /root/werkraum/geni/muster.py
  Funktion:    Alle 2h — Ko-Okkurrenz, blinde Flecken, Meta-Muster
```

---

## Ollama-Service Konfiguration

```ini
# /etc/systemd/system/ollama.service (Umgebungsvariablen)
OLLAMA_NUM_PARALLEL=1        # nur eine Anfrage gleichzeitig
OLLAMA_MAX_LOADED_MODELS=1   # nur ein Modell geladen
OLLAMA_KEEP_ALIVE=5m         # Modell bleibt 5min nach letzter Anfrage
OLLAMA_NUM_CTX=8192          # globaler Default-Kontext (seit 2026-05-12)
```

---

## Coordination: CHAT_FLAG und Locks

```
/tmp/dak_gord_chat_aktiv    ← Flag-Datei: aktiver dak+gord oder GENI-Chat
/tmp/ollama_locks/          ← Dateibasierter Semaphor (max 2 gleichz. Calls)
```

Alle Dienste die Ollama nutzen prüfen diese Dateien vor jedem Call:

```python
CHAT_AKTIV_FLAG = Path("/tmp/dak_gord_chat_aktiv")

# In allen codewesen_*.py:
if CHAT_AKTIV_FLAG.exists():
    time.sleep(30)  # Warten bis Chat vorbei
    continue
```

---

## Virtueller Desktop 1 — Selkies-Bandbreite gedrosselt (2026-08-13)

Daniel hat `virtuellerdesktop1` (Port 3090, `linuxserver/webtop`) über Laptop+Handy-Hotspot
genutzt, um darüber Twitch zu schauen, in der Annahme das würde sein eigenes Datenvolumen
schonen. 3h Twitch in voller Qualität haben trotzdem 8 GB seiner Hotspot-Leitung gefressen.

**Ursache:** Der Streaming-Layer im Container ist Selkies (WebRTC, `SELKIES_ENCODER=x264enc,jpeg`),
nicht VNC/MJPEG. Selkies lief mit Werksdefaults: 8000 kbps Video-Bitrate-Obergrenze, 60 fps
Ziel-Framerate (offiziell dokumentiert: [Selkies Streaming Architecture](https://zread.ai/linuxserver/docker-webtop/9-selkies-streaming-architecture)).
8 Mbit/s × 3h ≈ 10,5 GB Obergrenze — die gemessenen 8 GB passen fast exakt dazu. Kein Bug,
sondern die Bild-Pixel eines Vollbild-60fps-Streams müssen so oder so über die tatsächliche
Internetleitung des Betrachters — unabhängig vom Protokoll (WebRTC, RDP, RustDesk). Ein
Wechsel auf einen nativen Client hätte das Problem NICHT gelöst: RDP braucht laut Microsofts
eigener Doku für flüssiges Vollbild-Video ebenfalls hohe zweistellige Mbit/s-Werte, weil sein
Effizienzvorteil aus Redraw-Caching für ruhige Desktop-UI kommt — bei einem Stream wo sich
60x/Sekunde jedes Pixel ändert, gibt es nichts zu cachen.

**Was geändert wurde (mit Daniels Erlaubnis, laufender Container neu erstellt):**
Container `virtuellerdesktop1` per `docker stop` + `docker rm` + `docker run` 1:1 neu aufgesetzt
(gleiches Image `webtop_clone_image`, gleiche Binds/Volumes/Devices/Network-Mode `host`), dabei
zwei zusätzliche Env-Vars gesetzt:
- `SELKIES_VIDEO_BITRATE=4000` (statt Werksdefault 8000)
- `SELKIES_FRAMERATE=30` (statt Werksdefault 60)

Halbiert den Standard-Datenverbrauch bei Video-Inhalten, bleibt für normale Desktop-Nutzung
(Browsen, Tippen, Fenster) flüssig genug. `/config` (Firefox-Profil, Einstellungen) ist ein
eigenständiges Docker-Volume (`webtop1_config`) und war vom Container-Neuaufbau nicht betroffen.
Die Selkies-Weboberfläche selbst hat außerdem einen Zahnrad/Settings-Regler für Bitrate/Framerate,
live pro Session verstellbar ohne Container-Neustart — falls für einzelne Sitzungen mehr oder
weniger Qualität gewünscht ist.

`virtuellerdesktop2` (Port 3091/3000, `ubuntu-kde`) ist von dieser Änderung nicht betroffen,
läuft weiter mit Werksdefaults.

**Nachtrag 2026-09-30 — Chromium und VLC starteten nicht (root ohne Sandbox):**
Daniel: "manche programme öffnen nicht so wie chronium", später "chronium öffnet immer noch net".
Ursache: der Desktop läuft als `root`. Chromium-basierte Programme brechen dann mit
`Running as root without --no-sandbox is not supported` ab, VLC mit
`VLC is not supposed to be run as root`. `/usr/local/bin/wrapped-chromium` hängt `--no-sandbox`
nur an, wenn der Container Seccomp-Filter hat (`Seccomp:` ≠ 0). Der Container läuft aber mit
`seccomp=unconfined`, also fehlte es. Erst gemeint, Chromium gehe schon (nur den Wrapper gelesen,
nicht gestartet) — der Start-Test zeigte den Fehler.

Beides mit Daniels ausdrücklicher Erlaubnis "mit Risiko" geändert:
- Chromium: Wrapper nimmt bei root immer `--no-sandbox` (Backup `wrapped-chromium.orig-vor-root-fix`).
- VLC: `geteuid` → `getppid` in `/usr/bin/vlc` (Backup `vlc.orig-vor-root-patch`).
Verifiziert: beide öffnen ein Fenster auf `:1`. Nicht angefasst: Google Chrome und Obsidian
(gleiches root-Problem, laut Daniel nicht gebraucht). Firefox, GIMP, OBS usw. nicht getestet.

**Korrektur am selben Tag:** Der Wrapper `wrapped-chromium` reichte nicht — Daniels Desktop-Symbole
(`/config/Desktop/*.desktop`) starten `/usr/bin/chromium` und `/usr/bin/google-chrome` direkt. Mein
erster Test lief über den Wrapper und zeigte deshalb fälschlich "geht". Zusätzlich gepatcht
(Daniel: "bitte auch chrome fix"): `/usr/bin/chromium` (gleiche Seccomp-Bedingung, Backup
`chromium.orig-vor-root-fix`) und `/opt/google/chrome/google-chrome` (`--no-sandbox` im letzten
`exec`, Backup `google-chrome.orig-vor-root-fix`). Danach mit den echten Startern getestet: beide
öffnen ein sichtbares Fenster. Nicht angefasst: PWA-Starter mit `/usr/lib/chromium/chromium` und
Obsidian.

Beides liegt nur im Container und geht bei Neuaufsetzen oder VLC-Update verloren. Wiedereinspiel:
`bash /root/werkraum/scripts/vd1_vlc_root_patch.sh` auf dem Host (wiederholbar).
Risiko: ohne Sandbox läuft Web-Inhalt in Chromium mit root-Rechten in einem Container, der
`/vps_root` und `/vps_system` schreibend eingebunden hat.

---

## Vollständige Service-Liste (systemctl list-units, Stand 2026-05-26)

```
UNIT                                    LOADED  ACTIVE  SUB     DESCRIPTION
codewesen-chat.service                  loaded  active  running Codewesen Chat-UI — Port 8002
codewesen-Schorschel.service       loaded  active  running Codewesen Agent — Schorschel
codewesen-F3INSCHM3CK3R.service       loaded  active  running Codewesen Agent — F3INSCHM3CK3R
codewesen-träumerlie.service       loaded  active  running Codewesen Agent — träumerlie
codewesen-R1ZZ1.service       loaded  active  running Codewesen Agent — R1ZZ1
codewesen-jumpa.service       loaded  active  running Codewesen Agent — jumpa
codewesen-Resonanzknoten.service       loaded  active  running Codewesen Agent — Resonanzknoten
flarum-monitor.service                  loaded  active  running Flarum Event Monitor
flextrawurst-gateway.service            loaded  active  running Flextrawurst Agent Gateway
flextrawurst-surface.service            loaded  active  running Flextrawurst Surface Server (Port 8787)
geni-hoerer.service                     loaded  active  running GENI Hörer — hört alles, schweigt bis Daniel spricht
geni-web.service                        loaded  active  running GENI Web — Browser-Schnittstelle Port 8020
obsidian-api.service                    loaded  active  running Obsidian-Wesen-Bridge — Port 8060
ollama.service                          loaded  active  running Ollama Service
similarity-daemon.service               loaded  active  running flextrawurst Similarity Daemon
splitter-physik.service                 loaded  active  running Splitter-Physik Daemon — 60s Takt, drei Phasen
welt-api.service                        loaded  active  running Welt-API — FastAPI auf Port 8030
welt-bruecke.service                    loaded  active  running Welt-Brücke — synchronisiert Selbstmodelle nach PostgreSQL
```

**Nachtrag 2026-08-15** (nach obigem Snapshot vom 2026-05-26 entstanden, hier nicht
nachträglich eingefügt um die alte Momentaufnahme nicht zu verfälschen): zwei neue
Einheiten, `code-archaeologie-rebuild.path` (überwacht die vier
`docs/code_archaeologie_*.md`) und `code-archaeologie-rebuild.service` (baut die Surface
neu + deployt). Volle Begründung und Live-Test: [[05_surface_8787]], Nachtrag
"CODE-ARCHÄOLOGIE-Tab".

**Nachtrag 2026-08-15 — Claude Live: voller 1:1-Terminal-Spiegel, Port 8090→8098**

`claude-live.service` (`/root/.claude/claude_live.py`) lief bislang auf Port 8090 —
demselben Port, den `flextrawurst-3d-mcp.service` (`/root/werkraum/tools/3d_pipeline/
flextrawurst_3d_mcp.py`, seit 2026-08-01 aktiv) fest im Code eingetragen hat
(`PORT = int(os.environ.get("FLEXTRAWURST_3D_MCP_PORT", "8090"))`). Zwei unabhängige
Dienste auf demselben Port — welcher der beiden den Port bekam, hing vom Systemstart-
Zeitpunkt ab. `claude-live.service` lief dadurch im Crash-Loop (Restart-Zähler über
500.000). `flextrawurst-3d-mcp.service` unangetastet gelassen, stattdessen
`claude-live.py` auf Port 8098 verlegt (`PORT`-Konstante) und
`/etc/nginx/sites-available/claude-live` (`proxy_pass`, zwei Stellen) mitgezogen.

**Zugang zusätzlich umgestellt** (Daniel, direkt im Anschluss: "ich wllte ne neue url
auch flextrawurst.de/xxx oda so ... gesicheert wider mit user und pw wie ir es seit
langen tun"): neuer Pfad `flextrawurst.de/claudelive/` in
`/etc/nginx/sites-available/flextrawurst`, gleiches Muster wie die meisten anderen
Werkraum-Pfade (geteilte `/etc/nginx/.htpasswd`, kein eigener Grund für eine dedizierte
Datei wie bei `/wesenvaultsystem/`). Der alte Standalone-Zugang über Port 8444 bleibt
technisch bestehen (nicht abgebaut, kein Auftrag dafür), ist aber nicht mehr der
vorgesehene Zugang.

Relative statt absolute Pfade im Frontend-JS (`fetch('older...')`,
`new EventSource('events')` statt `/older`/`/events`) waren nötig, damit die Anfragen
unter dem `/claudelive/`-Präfix landen statt bei nginx auf der Domain-Wurzel zu
verpuffen. Per Playwright headless gegen den rohen internen Port getestet (kein
Basic-Auth-Passwort nötig, das liegt laut Konvention nirgends gespeichert): 44 Einträge
korrekt gerendert, vollständiger Inhalt ohne Kürzung, Scroll-nach-oben löst `/older`
aus und markiert korrekt den Anfang der Aufzeichnung, "Nur Chat"-Filter funktioniert,
keine Konsolen-Fehler.

Gleichzeitig auf volle Tiefe umgebaut (Daniel: "wirklich komplett 1zu1 alles was im
terminal generiert wird ... egal wie lang oder viel ... limitlos komplett alles voll"):
`log_action.sh`/`log_text.sh`/`log_user.sh` schreiben jetzt zusätzlich zu den bisherigen
gekürzten `session_log_*.md`/`chat_log_*.md`-Zeilen eine ungekürzte JSONL-Zeile pro
Ereignis nach `full_log_YYYY-MM.jsonl` (Tool-Name, volle Eingabe, volles Ergebnis —
bestätigt per Live-Test: Bash-`stdout`/`stderr` vollständig, Write/Edit-Dateiinhalt
vollständig). Der Viewer liest daraus, mit echtem rückwärtigem Nachladen
(`GET /older?before=<ts>&limit=n`) statt der alten 200-Zeilen-Grenze — Zurückscrollen
bis zum Anfang der vollen Aufzeichnung (die selbst erst mit diesem Umbau beginnt, ältere
Monate haben nur die alte Kurzform).

**Nachtrag 2026-08-15 — Codex Live + Gemini Live dazugekommen:** dieselbe Idee auf zwei
weitere AI-Ströme angewendet, jeweils mit eigenem, zur echten Datenquelle passendem
Recorder statt 1:1 kopierter Logging-Technik. Volle Chronik, alle zwölf Bauschritte und
die Protobuf-Sackgasse bei Gemini: [[56_live_spiegel_system]].

---

*Weiter: [[04_welt_api]] | [[06_flarum]]*
