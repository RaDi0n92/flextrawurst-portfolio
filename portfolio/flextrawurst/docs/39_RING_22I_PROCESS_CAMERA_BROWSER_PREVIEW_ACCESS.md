# Ring 22I — Process Camera Browser Preview Access

**Status:** aktiv  
**Schutzsatz:** Preview-Server serviert nur statische Artefakte. Kein Live-State. Keine Aktivierung. Keine Runtime.

---

## Was dieser Ring baut

Ring 22I schließt die Lücke zwischen Datei-Output und Browser-Erlebbarkeit.

Ring 22D–H hat die statische Prozesskamera gebaut und ihren Output auf Disk geschrieben.  
Ring 22I macht diesen Output über eine Browser-URL erreichbar.

Kein neuer Inhalt. Keine neue Logik. Nur Zugang.

---

## Datei-Output ≠ Browser-Erlebbarkeit

```
out/process_camera/process_camera_worldblick.html
```

Diese Datei liegt auf dem VPS. Das reicht nicht.  
Sie ist nicht erlebbar, solange sie nicht über eine URL im Browser geöffnet werden kann.

Browser-Erlebbarkeit heißt: URL eingeben → Seite erscheint.

---

## Zugriff über Browser-URL

```
http://localhost:8787/
http://localhost:8787/process_camera_worldblick.html
http://localhost:8787/process_camera_model.json
```

Vorher build ausführen:
```bash
npm run process-camera
```

Dann Preview-Server starten:
```bash
npm run process-camera:serve
```

Oder beides in einem Schritt:
```bash
npm run process-camera:preview
```

---

## Architektur

```
scripts/serve_process_camera_preview.ts
  └── node:http  (kein Framework, keine externe Dependency)
  └── serviert nur out/process_camera/
  └── Allowlist: genau 2 Routen
  └── kein Directory Traversal möglich
  └── Port 8787, Host 0.0.0.0

scripts/build_and_serve_process_camera.ts
  └── baut zuerst (wie process-camera Script)
  └── startet danach den Preview-Server
  └── kein Watch, kein Auto-Rebuild, kein Daemon
  └── Foreground-Prozess
```

---

## Externer Zugriff (VPS)

Der Server bindet auf `0.0.0.0:8787`.

Externe URL: `http://[SERVER-IP]:8787/`

Firewall-Freigabe (einmalig):
```bash
ufw allow 8787/tcp
```

---

## Betrieb auf VPS / systemd

Der Preview-Server läuft als supervised systemd-Service.  
Auto-Restart bei Crash, automatischer Start nach Serverneustart — auf expliziten Wunsch eingerichtet.

Service-Unit im Repo: `ops/systemd/process-camera-preview.service`  
Live installiert unter: `/etc/systemd/system/process-camera-preview.service`

```bash
systemctl status process-camera-preview
systemctl start process-camera-preview
systemctl stop process-camera-preview
systemctl restart process-camera-preview
journalctl -u process-camera-preview -f
```

Auto-Restart: `Restart=on-failure` (RestartSec=3)  
Boot-Start: `enabled` via `systemctl enable process-camera-preview`

**Schutzsatz:**  
Dieser Service serviert statische Prozesskamera-Artefakte.  
Er startet keine Welt-Runtime.  
Er erzeugt keine AI-Aktivität.  
Er aktiviert keine Wesen.  
Er liest kein Forum live.  
Er ist Preview-Zugang, nicht Weltbetrieb.

---

## Zur "kein Daemon"-Formulierung

Ring 22I wurde zunächst mit "kein Daemon" dokumentiert.  
Das meinte: kein versteckter Hintergrundprozess, kein Watch-Loop, kein Auto-Rebuild.

Auf expliziten Wunsch läuft der Preview-Server jetzt als systemd-Service.  
Das ist kein Widerspruch — es ist ein explizit eingerichteter, namentlich bekannter,  
statisch beschränkter Preview-Zugang. Kein Weltbetrieb. Keine AI. Nur HTTP-Dateizugang.

---

## Was dieser Ring ausdrücklich NICHT ist

- Kein Live-Dashboard
- Keine Welt-Runtime
- Kein versteckter Hintergrundprozess
- Keine AI
- Kein Renderer-Framework
- Kein Postgres
- Kein WebSocket
- Kein Auto-Rebuild
- Kein Watch-Loop
