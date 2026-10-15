# VPS Relay und Readback-Agent

`/root/werkraum/augen_haende_bridge/client_vps/bridge_agent.py` ist der
read-only VPS-Teil des ersten Bridge-Readback-Slices. Er entdeckt vorhandene
KDE-Konsole-Sessions über den bestehenden `TargetRegistry` und beantwortet
`target_inventory_request`; er führt keine Shell-, Terminal-Input-, Schreib-
oder Löschaktion aus.

Der aktuelle Relay-Einstieg ist
`/root/werkraum/augen_haende_bridge/client_vps/bridge_server.py`. Er startet
den Relay und diesen Agenten gemeinsam auf `127.0.0.1:19880`. Die beiden
Tokens kommen ausschließlich aus `BRIDGE_DESKTOP_TOKEN` und
`BRIDGE_AGENT_TOKEN`; sie werden nicht in Dateien, Argumente oder Logs
geschrieben.

VPS-Start:

```bash
export BRIDGE_DESKTOP_TOKEN="$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
export BRIDGE_AGENT_TOKEN="$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
PYTHONPATH=/root/werkraum/augen_haende_bridge/src:/root/werkraum/augen_haende_bridge \
  python3 /root/werkraum/augen_haende_bridge/client_vps/bridge_server.py \
  --port 19880 \
  --journal /root/werkraum/augen_haende_bridge/runtime/bridge-relay.sqlite3
```

Der Prozess bindet absichtlich nur auf Loopback. Der alte Port `9880` gehört
zu einem entfernten historischen Prototyp und wird von diesem Einstieg nicht
verwendet.

Lokaler Entwicklungsstart neben dem Relay:

```text
PYTHONPATH=src python3 client_vps/bridge_agent.py \
  --url ws://127.0.0.1:19880 \
  --token <kurzlebiges-agent-token>
```

Alternativ werden `BRIDGE_URL` und `BRIDGE_AGENT_TOKEN` gelesen. Der aktuelle
Transport bleibt absichtlich loopback-only. Windows erreicht ihn erst über den
SSH-LocalForward aus
`/root/werkraum/augen_haende_bridge/client_windows/start_with_ssh_tunnel.ps1`;
es gibt keinen öffentlichen VPS-Endpunkt.

## Terminal-Starter (Beschluss BE01/BE02)

`bridge_server.py` startet neben dem Relay den Starter `terminal_launcher.py`. Er startet nur Einträge
der Startliste `starts.json` (Name, Ort, Ordner, Programm) an den Orten aus `orte.json` (Host, vd1, vd2),
jeweils in einer eigenen Linux-PTY, die die Bridge selbst hält. Der Desktop schickt nie einen Befehl,
nur die `start_id`. Laufende, fremde Terminals werden weder gesucht noch angebunden.

Optionen des Servers: `--starts`, `--orte`, `--runtime-dir` (Vorgabe: `runtime/` im Bridge-Ordner).
`vd1`/`vd2` laufen als `docker exec -it` im Container; der Laufzeitordner erscheint dort unter dem
Pfad, den `mount_from`/`mount_to` in `orte.json` beschreiben (Host-`/root` ist im Container `/vps_root`).

Der Agent im Terminal bekommt nur `BRIDGE_TERMINAL_ID`, `BRIDGE_TERMINAL_TOKEN` und `BRIDGE_RUNTIME_DIR`,
nie die Relay-Tokens (Umgebung per Allowlist, bei Docker steht das Token nicht in der Prozessliste).
Sprechen und Sehen laufen über `bridge_cli.py`:

```bash
python3 client_vps/bridge_cli.py say "Hast du deinen Turm ungedeckt gelassen?"   # erscheint in der Raute
python3 client_vps/bridge_cli.py see                                              # Pfad des letzten Bildes vom Scanner
```

Schließen eines Terminals beendet auch die Prozesse im Container (Suche über `BRIDGE_TERMINAL_ID`,
denn `docker exec` läuft nach dem Ende des Clients sonst weiter). Tests: `tests/test_terminal_launcher.py`,
`tests/test_bridge_server_terminal.py`; der Docker-Weg ist auf dem Host gegen `virtuellerdesktop1` und
`virtuellerdesktop2` geprüft.
