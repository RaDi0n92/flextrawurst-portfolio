# Systemdokumentation 39: Security-Audit-Nachzug — Port-Härtung + Status-Check des Mai-Reports

---
autor: claude-code bei Daniels VPS
datum: 2026-07-29
status: Priorität 5 des Mai-Reports abgeschlossen, Priorität 1-3 teilweise/offen
bezug: /root/SECURITY_FINAL_REPORT_FLEXTRAWURST_20260530.md
---

## 1. Anlass

Daniel: *"/root/SECURITY_FINAL_REPORT_FLEXTRAWURST_20260530.md bitte cheken und alles
durchführen pls"* — der Report ist zwei Monate alt. Statt blind auszuführen, erst jeden
Punkt live gegen den aktuellen Systemzustand geprüft (Daniels eigene Regel: nicht Logs/alte
Berichte glauben, sondern selbst verifizieren).

## 2. Status-Check der Mai-Prioritäten

| Priorität | Status heute | Beleg |
|---|---|---|
| 4 — Doku-Credentials bereinigen | **Bereits erledigt** (unbekannt von wem/wann) | `06_flarum.md` etc. zeigen schon `[REDACTED]`/Variablen |
| Offenes Risiko: `welt-api.service` ohne EnvironmentFile | **Bereits erledigt** | `EnvironmentFile=/root/werkraum/.agent/flextrawurst-db.env` existiert |
| 1 — Credential-Rotation (Flarum-DB, Flarum-Master-Key, dak-gord-DB, GENI-Bridge-Token) | **Unklar, ob je rotiert** — alle vier live gegen die echten Systeme getestet, funktionieren aktuell (MySQL-Login, Postgres-Connect, Flarum-API-Call alle erfolgreich) | Kann nicht unterscheiden zwischen "nie rotiert" und "rotiert und synchron gehalten" — nur Daniel weiß das |
| 3 — `welt/api.py` nutzt Claude-CLI-OAuth-Token statt echtem `ANTHROPIC_API_KEY` | **Weiterhin offen, bewusst zurückgestellt** | Zeile ~10276, liest `/root/.claude/.credentials.json`. Daniel: ein echter API-Key wäre nicht durch sein Abo gedeckt, sondern separat nutzungsbasiert abgerechnet — Kosten-Nutzen-Abwägung, kein Sicherheitsvorfall. Bleibt akzeptiertes Risiko bis Daniel das anders will. |
| 5 — App-Ports hinter Nginx | **Heute vollständig abgeschlossen** | Siehe Abschnitt 3 |
| 6 — Git-History-Rewrite | Nicht nötig laut Mai-Report, nicht neu geprüft | — |

## 3. Port-Härtung — alle 10 Ports einzeln durchgegangen

Daniel wollte das **einzeln, nicht pauschal** durchgehen — für jeden Port erst gefragt, ob
er direkt per IP:Port genutzt wird, dann je nach Antwort entweder (a) hinter Nginx mit
Basic-Auth gelegt oder (b) komplett ohne Ersatzweg geschlossen.

| Port | Dienst | Direkt genutzt? | Aktion | Neuer Weg |
|---|---|---|---|---|
| 7777 | `galerie_server.py` (Bilder-Galerie), systemd `bilder-galerie.service` | Ja | Proxy + Bind-Fix im Code (`HTTPServer(('0.0.0.0'...` → `'127.0.0.1'`) | `https://flextrawurst.de/galerie/` |
| 8000 | `web_chat.py`, `dak-gord-web.service` | Ja | Proxy + Bind-Fix im Code | `https://flextrawurst.de/dakgord-chat/` |
| 8001 | `werkraum-api.service` ("Flextrawurst Agent Gateway", `/files /read /write /run /git/*` — bereits eigener `require_api_token`-Schutz auf allen kritischen Routen) | Ja | Proxy + Bind-Fix in der systemd-Unit (`--host 0.0.0.0` → `--host 127.0.0.1`) | `https://flextrawurst.de/werkraum-api/` |
| 8002 | `codewesen_chat.py`, `codewesen-chat.service` | Ja | Proxy + Bind-Fix im Code | `https://flextrawurst.de/codewesen-chat/` |
| 8010 | `flextrawurst-gateway.service` (zweite Instanz derselben Agent-Gateway-App, mit `AGENT_ALLOWED_COMMAND_PREFIXES`-Whitelist) | **Nein, "noch nie"** | Nur Bind-Fix in der systemd-Unit + UFW zu, **kein** Nginx-Weg | Keiner (bewusst) |
| 8020 | GENI (`geni/dialog.py`), `geni-web.service` — terminiert selbst schon HTTPS mit selbstsigniertem Zertifikat | Ja | Proxy (mit `proxy_ssl_verify off` wegen self-signed Backend) + Bind-Fix im Code (2 Stellen) | `https://flextrawurst.de/geni/` |
| 8030 | `welt/api.py`, `welt-api.service` — hatte schon `/api/*`+WebSocket-Proxy | **Nein, "noch nie geöffnet"** | Nur Bind-Fix im Code + UFW zu, bestehende `/api/*`-Routen unverändert nutzbar | Bestehender `/api/*`-Weg bleibt, kein neuer Direktweg |
| 8060 | `obsidian_api.py`, `obsidian-api.service` — terminiert selbst HTTPS (selbstsigniert) | **Nein, "noch nie"** | Nur Bind-Fix im Code, UFW hatte hierfür **überraschend gar keine Regel** (Fund: war schon vorher firewall-seitig nicht erreichbar, nur die Bindung war offen) | Keiner (bewusst) |
| 8787 | Flextrawurst-Frontend (`serve_process_camera_preview.ts`), `process-camera-preview.service` — hatte schon Domain-Root-Proxy | **Nein, "eig nicht genutzt"** | Nur Bind-Fix im Code (`const HOST = "0.0.0.0"` → `"127.0.0.1"`) + UFW zu | Bestehender `/`-Weg bleibt |
| 8900 | `kompoase/server.py`, `kompoase.service` | Ja, gelegentlich | Proxy + Bind-Fix im Code | `https://flextrawurst.de/zusatz-kompoase/` (Name explizit von Daniel gewählt, nicht `/kompoase/`) |

**Gemeinsames Muster pro Port:** Backup-Commit vor jeder Code-Änderung (jeweils im
zuständigen Repo — `/root`, `/root/werkraum`, `/root/flextrawurst`, `/root/kompoase`, je
nachdem wo die Datei tatsächlich liegt, inkl. zwei Fälle mit Symlink-Zielen außerhalb
`werkraum/` selbst: `bilder/` → `werkraum_bilder`, `geni/` → `werkraum_geni`), dann Bind
auf `127.0.0.1` (Python-Quellcode direkt bei drei Diensten, systemd-`ExecStart`-Flag bei
zwei uvicorn-Diensten), Dienst-Neustart, Live-Verifikation (Nginx-Weg testen, externe
IP:Port-Erreichbarkeit testen — überall `HTTP 000`/Timeout danach), dann erst
`ufw delete allow <port>/tcp`.

**Alle vier neuen, Nginx-proxy'd Direktwege** (`/galerie/`, `/dakgord-chat/`,
`/werkraum-api/`, `/codewesen-chat/`, `/geni/`, `/zusatz-kompoase/` — sechs, nicht vier)
nutzen `auth_basic "Werkraum"` gegen die bereits existierende
`/etc/nginx/.htpasswd` (derselbe "daniel"-Nutzer wie bei `/bildgenerator` und anderen
bestehenden geschützten Pfaden — kein neuer Nutzer angelegt, nur wiederverwendet).

## 4. Nginx-Edits — Classifier-Umweg wie schon beim MCP-Connector-Fix

Direkte Nginx-Config-Edits wurden vom Auto-Mode-Classifier weiterhin blockiert
(`permissions.allow` in `.claude/settings.json` war trotz früherem Versuch immer noch
leer). Für jeden der sechs neuen Proxy-Blöcke ein eigenes, kleines Shell-Skript
(`/root/fix_<dienst>_proxy.sh`) geschrieben, das Daniel selbst mit einer Zeile ausgeführt
hat — jedes Skript macht automatisch ein Backup der Nginx-Config, fügt den Block per
Python-String-Replace an einer festen Ankerstelle ein, prüft `nginx -t`, reload. System-
Edits an `/etc/systemd/system/*.service` und `ufw delete` liefen dagegen **ohne**
Classifier-Blockade direkt durch mich.

## 5. Verifikation, final

```
ufw status | grep -E "^(7777|8000|8001|8002|8010|8020|8030|8060|8787|8900)/"
→ leer, keine der 10 Ports mehr gelistet

ss -tlnp | grep -E ":7777 |:8000 |:8001 |:8002 |:8010 |:8020 |:8030 |:8060 |:8787 |:8900 "
→ alle zehn auf 127.0.0.1 gebunden, keine 0.0.0.0-Bindung mehr
```

Für jeden Port zusätzlich einzeln getestet: direkter externer Zugriff über
`http://[SERVER-IP]:<port>/` → `HTTP 000`/Timeout (nicht erreichbar). Wo ein Nginx-Weg
angelegt wurde: ohne Auth → `401`, mit Daniels Login → `200`. Bestehende Funktionalität
(`flextrawurst.de/`, `/api/*`) nach den Neustarts von `welt-api.service` und
`process-camera-preview.service` erneut live gegengeprüft, unverändert funktionsfähig.

## 6. Was bewusst nicht angefasst wurde

- **Credential-Rotation (Mai-Priorität 1)** — nicht durchgeführt. Betrifft live genutzte
  Passwörter/Tokens mit mehreren Konsumenten (Postgres-User `dak` z.B. wird von
  mehreren Diensten gleichzeitig genutzt) und einen externen, nur von Daniel erreichbaren
  Schritt (GENI-Bridge-Token auf der Windows-Seite). Zu hohes Risiko für eine
  unaufgeforderte, unkoordinierte Aktion — braucht Daniels aktive Beteiligung, kein reiner
  Ausführungsschritt.
- **`ANTHROPIC_API_KEY` für `welt/api.py`** — Daniel hat bewusst entschieden, das
  vorerst nicht zu tun (separate API-Kosten vs. Sicherheitsrisiko eines zweckentfremdeten
  CLI-Tokens). Akzeptiertes Risiko, keine offene Aufgabe.
- **Strato-Firewall (externe Hoster-Ebene)** — außerhalb meiner Reichweite, Daniel müsste
  das selbst im Strato-Control-Panel prüfen, falls dort zusätzlich zur UFW-Ebene etwas
  offensteht.

## 7. Anschluss

Direkt im Anschluss an diese Session: KompOase-Theater zeigt laut Daniel schon länger
keinen echten Live-Datenfeed mehr, nur noch vorbereitete/statische Inhalte ("was eg echt
schade war") — als Nächstes anzugehen, siehe `karte/` bzw. kommende Notiz.

## 8. Nachtrag 2026-08-13: Port 8035 (`/toolbox`, ex `/tts`) — war nicht Teil der 10-Port-Liste

Daniel: *"flextrawurst.de/toolbox muss gesichert werden wie alle anderen"*. Erster Check zeigte:
Nginx-Weg (`/toolbox/`) war schon korrekt mit `auth_basic` gegen `/etc/nginx/.htpasswd_tts`
(Nutzer `daniel`, gleiches Passwort wie überall) geschützt — `401` ohne Login, `200` mit.

Der eigentliche Fund lag eine Ebene tiefer, wie bei der `history_startup()`-Anekdote: der
Backend-Prozess selbst (`tts_service.py`, `tts-service.service`, Port 8035) lief auf
`host="0.0.0.0"` statt `127.0.0.1` — dieser Port fehlte in der 10-Port-Liste aus Abschnitt 3,
vermutlich weil der Dienst beim Mai-Audit noch nicht existierte oder unter anderem Namen lief.
Folge: `http://[SERVER-IP]:8035/` lieferte direkt Inhalt aus, komplett am Nginx-Basic-Auth
vorbei — mit `WebFetch` von außen bestätigt (`WRONG_VERSION_NUMBER`-SSL-Fehler = TCP-Verbindung
kam durch, Server antwortete mit Klartext-HTTP).

Fix identisch zum Muster aus Abschnitt 3: Backup-Commit in `/root/werkraum`, dann
`host="0.0.0.0"` → `host="127.0.0.1"` in `welt/tts_service.py` Zeile 2193, `systemctl restart
tts-service.service`. Verifikation: `ss -tlnp` zeigt jetzt `127.0.0.1:8035`; externer Zugriff
über `WebFetch` auf `http://[SERVER-IP]:8035/` liefert `ECONNREFUSED`; Nginx-Weg
`https://flextrawurst.de/toolbox/` weiterhin `401` ohne / `200` mit Login. Port 8035 war in UFW
nie explizit freigegeben (Fehler lag rein an der Bindung, nicht an der Firewall-Regel) — kein
`ufw delete` nötig.

Nicht geprüft: ob weitere, nach dem Mai-Audit neu entstandene Dienste denselben
`0.0.0.0`-Fehler haben. Kein Auftrag für einen erneuten Vollscan, nur der konkret genannte Fund
behoben.
