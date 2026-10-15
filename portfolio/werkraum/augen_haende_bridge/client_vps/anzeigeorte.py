"""Mehrere Desktops als Anzeigeorte (G06): Anmeldedaten je Desktop und der Verteiler, über den der Starter zu jedem Desktop spricht.

Vor G06 kannte der Relay genau einen Desktop (`desktop`) und einen Starter (`agent`). Jetzt gibt es je Desktop ein eigenes Paar: Windows behält `desktop` und `agent`,
alle anderen (kde1, kde2) bekommen `desktop-<ort>` und `agent-<ort>` mit eigenen Zugangsdaten. Die Paare bleiben 1:1 (der Relay ändert sich dafür nicht); der Starter
hält je Paar eine Verbindung und der `Verteiler` wählt je Nachricht die richtige. Zugangsdaten stehen nie in der Konfiguration und nie im Log: Windows liest sie aus
der Umgebung, die anderen aus privaten Dateien (0600), die der Relay beim ersten Start anlegt.
"""

from __future__ import annotations

import json
import os
import re
import secrets
import stat
import threading
from dataclasses import dataclass, field
from pathlib import Path

from augen_haende_bridge.transport import Principal

ORT = re.compile(r"[a-z][a-z0-9]{0,15}\Z")
MIN_TOKEN = 32


@dataclass(frozen=True)
class Desktop:
    ort: str  # windows, kde1, kde2
    name: str
    host: str
    token: str = field(default="", repr=False)  # nie in Logs oder Ausgaben
    agent_token: str = field(default="", repr=False)
    session_id: str = ""
    agent_session_id: str = ""
    target_id: str = ""

    def wire(self, online: bool) -> dict:
        return {"ort": self.ort, "name": self.name, "online": online}


class KonfigurationsFehler(ValueError):
    pass


def _token_datei(ordner: Path, name: str) -> str:
    """Token aus einer privaten Datei lesen, beim ersten Mal anlegen. Zu offene Rechte oder zu kurze Token: Abbruch (fail closed)."""
    ordner.mkdir(parents=True, exist_ok=True)
    os.chmod(ordner, 0o700)
    pfad = ordner / name
    if not pfad.exists():
        token = secrets.token_urlsafe(32)
        fd = os.open(pfad, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as datei:
            datei.write(token)
        return token
    modus = stat.S_IMODE(pfad.stat().st_mode)
    if modus & 0o077:
        raise KonfigurationsFehler(f"token_datei_zu_offen:{name}")
    token = pfad.read_text(encoding="utf-8").strip()
    if len(token) < MIN_TOKEN:
        raise KonfigurationsFehler(f"token_zu_kurz:{name}")
    return token


def lade_desktops(pfad: Path, runtime_dir: Path, umgebung: dict | None = None) -> list[Desktop]:
    umgebung = os.environ if umgebung is None else umgebung
    try:
        roh = json.loads(Path(pfad).read_text(encoding="utf-8"))
    except (OSError, ValueError) as fehler:
        raise KonfigurationsFehler(f"desktops_nicht_lesbar:{fehler!r}") from None
    eintraege = roh.get("desktops") if isinstance(roh, dict) else None
    if not isinstance(eintraege, list) or not eintraege or len(eintraege) > 8:
        raise KonfigurationsFehler("desktops_fehlen")
    desktops: list[Desktop] = []
    orte: set[str] = set()
    tokens: set[str] = set()
    for e in eintraege:
        if not isinstance(e, dict) or not isinstance(e.get("ort"), str) or not ORT.fullmatch(e["ort"]):
            raise KonfigurationsFehler("ungueltiger_ort")
        ort = e["ort"]
        if ort in orte:
            raise KonfigurationsFehler(f"ort_doppelt:{ort}")
        orte.add(ort)
        name = str(e.get("name") or ort)[:60]
        host = str(e.get("host") or "")[:60]
        if "token_env" in e:
            token, agent_token = umgebung.get(str(e["token_env"]), ""), umgebung.get(str(e.get("agent_token_env", "")), "")
            if len(token) < MIN_TOKEN or len(agent_token) < MIN_TOKEN:
                raise KonfigurationsFehler(f"zugangsdaten_fehlen:{ort}")
        else:
            ordner = Path(runtime_dir) / "tokens"
            token, agent_token = _token_datei(ordner, f"desktop-{ort}.token"), _token_datei(ordner, f"agent-{ort}.token")
        if token == agent_token or token in tokens or agent_token in tokens:
            raise KonfigurationsFehler(f"zugangsdaten_nicht_verschieden:{ort}")
        tokens.update((token, agent_token))
        if ort == "windows":  # die bisherigen Kennungen bleiben: Relay-Journal, Probes und die ausgelieferte exe kennen sie
            desktops.append(Desktop(ort, name, host, token, agent_token, "desktop", "agent", "desktop-main"))
        else:
            desktops.append(Desktop(ort, name, host, token, agent_token, f"desktop-{ort}", f"agent-{ort}", f"desktop-{ort}"))
    return desktops


def baue_principals(desktops: list[Desktop]) -> list[Principal]:
    """Je Desktop das Paar (Desktop, Starter) mit den Rechten des ersten Körpers."""
    principals: list[Principal] = []
    for d in desktops:
        principals.append(Principal(d.session_id, d.token, d.agent_session_id, d.target_id, can_publish_frames=True,
                                    can_request_inventory=True, can_control_terminals=True))
        principals.append(Principal(d.agent_session_id, d.agent_token, d.session_id, d.target_id, can_publish_inventory=True,
                                    can_serve_terminals=True))
    return principals


class Verteiler:
    """Der Starter spricht über ihn mit allen Desktops: `publish(..., ort=…)` schickt über die Verbindung dieses Desktops, eingehende Ereignisse tragen den Ort."""

    def __init__(self, desktops: list[Desktop], laufzeiten: dict[str, object]):
        self.desktops = {d.ort: d for d in desktops}
        self.laufzeiten = laufzeiten  # ort -> BridgeRuntime-artig (publish, connected)
        self.standard = desktops[0].ort
        self._sperre = threading.Lock()
        self._zuletzt_online: dict[str, bool] = {o: False for o in self.desktops}

    def publish(self, kind: str, payload: dict, *, message_id: str | None = None, ort: str | None = None) -> str:
        ort = ort or self.standard
        laufzeit = self.laufzeiten.get(ort)
        if laufzeit is None:
            raise KeyError(f"unbekannter_ort:{ort}")
        return laufzeit.publish(kind, payload, message_id=message_id)

    def online(self, ort: str) -> bool:
        laufzeit = self.laufzeiten.get(ort)
        return bool(laufzeit is not None and getattr(laufzeit, "connected", False))

    def orte_wire(self) -> list[dict]:
        return [d.wire(self.online(o)) for o, d in self.desktops.items()]

    def veraenderungen(self) -> bool:
        """True, wenn sich der Online-Zustand eines Desktops seit dem letzten Aufruf geändert hat (der Starter meldet es dann allen)."""
        with self._sperre:
            jetzt = {o: self.online(o) for o in self.desktops}
            geaendert = jetzt != self._zuletzt_online
            self._zuletzt_online = jetzt
            return geaendert

    def ereignis_von(self, ort: str, weiter):
        """Ein Empfänger für die Verbindung dieses Desktops: setzt den Ort ins Ereignis und gibt es an den Starter."""
        def empfangen(ereignis: dict) -> None:
            if isinstance(ereignis, dict):
                ereignis = {**ereignis, "_ort": ort}
            weiter(ereignis)

        return empfangen
