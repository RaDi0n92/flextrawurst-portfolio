#!/usr/bin/env python3
"""
GENI Hörer — hört alles, schweigt bis Daniel spricht, verliert nie etwas.

Quellen:
  - Dateisystem: /root/werkraum/ (Echtzeit via watchdog)
  - Flarum: neue Posts, neue Diskussionen (alle 60s)
  - Prozesse: laufende Python/Node-Prozesse (alle 5 Min)
"""

import json
import os
import time
import threading
import subprocess
import logging
from datetime import datetime, timezone
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from gedaechtnis_ops import knoten_schreiben, GENI_ROOT, KNOTEN_DIR, naechste_id, sharded_pfad

import sys as _sys
_sys.path.insert(0, str(Path("/root/werkraum")))
try:
    import obsidian_vault as _vault
    _VAULT_OK = True
except ImportError:
    _VAULT_OK = False

RAUSCHEN_DIR = GENI_ROOT / "gedaechtnis" / "rauschen"
RAUSCHEN_FILTER_CFG = GENI_ROOT / "gedaechtnis" / "rauschen_filter.json"
LOG_FILE = GENI_ROOT / "hoerer.log"

WATCH_PATHS = ["/root/werkraum"]

# Wesen-Attribution fuer Knoten-Tags (2026-07-11, Grundgesetz 7 Fragment-Ebene) --
# deckt sich mit codewesen_takt.py:WESEN. Nur fuer NEUE Knoten ab jetzt; die
# ~19 Mio. bereits archivierten Knoten bleiben unangetastet (Events sind heilig).
WESEN_NAMEN = {
    "Schorschel", "F3INSCHM3CK3R", "träumerlie",
    "R1ZZ1", "jumpa", "Resonanzknoten", "dak+gord-system",
}

IGNORE_PATHS = [
    str(GENI_ROOT / "gedaechtnis"),
    str(GENI_ROOT / "hoerer.log"),
    "/root/werkraum/logs",
    "/root/werkraum/agent",
    "/root/werkraum/geni/archiv",
    "/root/werkraum/geni/verbindungen",
    "/root/werkraum/geni/spiegel",
    # 2026-07-21: flarum_sync.py (Cron alle 5min) schreibt hier den kompletten
    # Markdown-Spiegel unbedingt neu, ohne Diff-Check -- ~3850 Dateien pro Lauf,
    # jede als "geaendert"-Knoten verewigt (~900k/Tag, Hauptursache fuer den
    # Sprung von 18,9 auf 31,5 Mio. Knoten seit 07-07, siehe ENOSPC-Log-Eintrag
    # vom 07-11 in hoerer.log). Reine Redundanz: dieselben Flarum-Daten kommen
    # bereits unabhaengig ueber flarum_abfragen() in den Graphen.
    "/root/werkraum/flarum",
    # 2026-08-01, Daniel ("warum zur hoelle gibt es 12millionen chatgpt-knoten?????"):
    # Seit _gpt am 2026-07-29 in AI_STROM_ORDNER aufgenommen wurde (Commit
    # a00a972a6b2), sind dort 13,3 Mio Knoten entstanden -- 120.000 pro Stunde,
    # ~1 GB/Tag. Inhalt zu 100 % Werkzeug-Spuren: atomare Temp-Dateien mit
    # Zufallsendung (.LIVE_DELTA_STATE.json.155pcvcz), Session-Locks, Zeitstrom-
    # Rohdaten. Verteilt ueber mcp_arbeitskoerper/ (55 %), time-stream-global-*/
    # (23 %), gesamtatlas/ (15 %) -- ein Filter auf einen einzelnen Unterordner
    # haette also nur einen Bruchteil erwischt.
    # Ausgenommen bleibt _gpt/mcp_zuhause/ (44 KB, 9 Dateien) -- genau der
    # schlanke Teil, den auch der GPT-Grundriss-Sync bewusst allein nimmt
    # (siehe CLAUDE.md: "bewusst nur dieser schlanke Unterordner, nicht ganz
    # /root/werkraum/_gpt/ (1,4G, groesstenteils Session-Locks und
    # Gesamtatlas-Rohdaten)"). Dieselbe Abgrenzung, dieselbe Begruendung.
    "/root/werkraum/_gpt",
]

# Pfade, die trotz eines Treffers in IGNORE_PATHS beobachtet werden (laengerer,
# spezifischerer Pfad schlaegt den allgemeineren Ausschluss).
IGNORE_AUSNAHMEN = [
    "/root/werkraum/_gpt/mcp_zuhause",
]

# Immer hart ignorieren (kein Eintrag nirgendwo)
_HART_IGNORIERT_SUFFIXE = {".pyc", ".pyo", ".swp", ".log", ".jsonl"}

_rauschen_filter_cache: "dict | None" = None
_filter_lock = threading.Lock()


def _filter_laden() -> dict:
    global _rauschen_filter_cache
    with _filter_lock:
        if _rauschen_filter_cache is not None:
            return _rauschen_filter_cache
        try:
            _rauschen_filter_cache = json.loads(RAUSCHEN_FILTER_CFG.read_text())
        except Exception:
            _rauschen_filter_cache = {
                "ignorieren_suffixe": [],
                "rauschen_suffixe": [".tmp", ".log", ".jsonl", ".bak"],
                "rauschen_pfad_fragmente": [".obsidian", "__pycache__", ".git"],
                "rauschen_verzeichnisse": [".obsidian", "__pycache__", ".git"],
            }
        return _rauschen_filter_cache

FLARUM_DB = {"user": "flarum", "password": os.environ.get("FLARUM_DB_PASSWORD", ""), "db": "flarum"}
FLARUM_POLL_INTERVAL = 60
PROZESS_POLL_INTERVAL = 300

logging.basicConfig(
    filename=str(LOG_FILE),
    level=logging.INFO,
    format="%(asctime)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)


def klassifizieren(path: str) -> str:
    """Gibt 'ignorieren', 'rauschen' oder 'knoten' zurück."""
    p = Path(path)
    for aus in IGNORE_AUSNAHMEN:
        if path.startswith(aus):
            break
    else:
        for ig in IGNORE_PATHS:
            if path.startswith(ig):
                return "ignorieren"
    # 2026-08-01: versteckte Dateien sind nie Inhalt, sondern Werkzeug-Spuren
    # (atomare Temp-Dateien, .gitkeep, .obsidian, .DS_Store). Sie waren die
    # groesste Einzelquelle des chatgpt-Rauschens: 9.736.709 von 13.371.406
    # Knoten (72,8 %) betrafen einen Pfadteil, der mit "." beginnt.
    if any(teil.startswith(".") for teil in p.parts if teil not in ("/", "")):
        return "ignorieren"
    if p.suffix in _HART_IGNORIERT_SUFFIXE:
        return "ignorieren"
    f = _filter_laden()
    if p.suffix in f.get("rauschen_suffixe", []):
        return "rauschen"
    for fragment in f.get("rauschen_pfad_fragmente", []):
        if fragment in path:
            return "rauschen"
    for teil in p.parts:
        if teil in f.get("rauschen_verzeichnisse", []):
            return "rauschen"
    return "knoten"


_rauschen_id_lock = threading.Lock()


def rauschen_schreiben(aktion: str, rel_pfad: str):
    RAUSCHEN_DIR.mkdir(parents=True, exist_ok=True)
    with _rauschen_id_lock:
        rid = naechste_id(RAUSCHEN_DIR, counter_key="rauschen_max_id").zfill(6)
    eintrag = {
        "id": rid,
        "aktion": aktion,
        "pfad": rel_pfad,
        "zeitstempel": datetime.now(timezone.utc).isoformat(),
    }
    pfad = sharded_pfad(RAUSCHEN_DIR, rid)
    pfad.parent.mkdir(parents=True, exist_ok=True)
    pfad.write_text(
        json.dumps(eintrag, ensure_ascii=False),
        encoding="utf-8",
    )


# 2026-07-29 (Daniel: "auch euch alle... claude codex gemini gpt claudeweb"):
# Schreibvorgaenge in den Zuhause-Ordnern der fuenf AI-Stroeme bekommen jetzt
# eine eigene Quelle statt der pauschalen "vps_dateisystem"-Sammelkategorie --
# sonst werden sie vom Splitter-Endpunkt (siehe geni/dialog.py) komplett
# rausgefiltert, obwohl es echte, kuratierte Inhalte sind (Spiegel/Notizen),
# keine Rausch-Events. Grobkoernig auf Top-Level-Ordnername gemappt -- Mirror-
# Unterordner (z.B. _claude/_import_codex_grundriss/) werden dadurch noch dem
# Zuhause-Strom zugeschlagen, in dem sie liegen, nicht ihrer echten Herkunft.
# Bekannte Ungenauigkeit, kein Blocker fuer den ersten Wurf.
AI_STROM_ORDNER = {
    "_claude": "claude",
    "_codex": "codex",
    "_gemini": "gemini",
    "_gpt": "chatgpt",
    "_claudeweb": "claudeweb",
}


MAX_INHALT_LAENGE = 20000


class DateiHoerer(FileSystemEventHandler):
    def _verarbeiten(self, pfad: str, ist_verzeichnis: bool, aktion: str, inhalt_praefix: str):
        if ist_verzeichnis:
            return
        klasse = klassifizieren(pfad)
        if klasse == "ignorieren":
            return
        rel = os.path.relpath(pfad, "/root/werkraum")
        if klasse == "rauschen":
            rauschen_schreiben(aktion, rel)
            return
        teile = rel.split("/")
        tags = ["datei", aktion, teile[0]]
        if len(teile) > 1 and teile[0] == "codewesen" and teile[1] in WESEN_NAMEN:
            tags.append(teile[1])
        quelle = AI_STROM_ORDNER.get(teile[0], "vps_dateisystem")
        inhalt = f"{inhalt_praefix}: {rel}"
        # 2026-07-31, Daniel ("zu a ja"): fuer die fuenf AI-Strom-Zuhausedateien reicht der
        # Pfad allein nicht -- der Splitter-Feed (geni/dialog.py) zeigte bisher nur "geaendert:
        # _claude/notizen/X.md" statt des echten Textes. Bei erstellten/geaenderten Markdown-
        # Dateien wird jetzt der tatsaechliche Inhalt mitgelesen (gekappt, kein Speicher-Risiko
        # wie beim bekannten flarum_sync.py-Vorfall -- der betraf einen anderen, viel groesseren
        # Pfad und ist bereits per IGNORE_PATHS ausgeschlossen).
        if quelle != "vps_dateisystem" and aktion != "gelöscht" and pfad.endswith(".md"):
            try:
                text = Path(pfad).read_text(encoding="utf-8", errors="replace")[:MAX_INHALT_LAENGE]
                if text.strip():
                    inhalt = f"{rel}:\n{text}"
            except Exception:
                pass
        knoten_schreiben(
            typ="ereignis",
            inhalt=inhalt,
            quelle=quelle,
            tags=tags,
        )

    def on_created(self, event):
        try:
            self._verarbeiten(event.src_path, event.is_directory, "erstellt", "neue Datei")
        except Exception as e:
            logging.warning(f"on_created fehler ({event.src_path}): {e}")

    def on_modified(self, event):
        try:
            self._verarbeiten(event.src_path, event.is_directory, "geändert", "geändert")
        except Exception as e:
            logging.warning(f"on_modified fehler ({event.src_path}): {e}")

    def on_deleted(self, event):
        try:
            self._verarbeiten(event.src_path, event.is_directory, "gelöscht", "gelöscht")
        except Exception as e:
            logging.warning(f"on_deleted fehler ({event.src_path}): {e}")

    def on_moved(self, event):
        # 2026-07-31: live gefunden (Karte-Eintrag als Testfall) -- Werkzeuge wie Write
        # schreiben oft atomar (Temp-Datei + rename auf den Zielnamen). Das erzeugt watchdog-
        # seitig ein on_moved, kein on_created fuer den echten Zielnamen -- der war bisher
        # komplett unsichtbar, nur die kurzlebige (und sofort wieder weg) Temp-Datei bekam
        # einen (inhaltslosen) Pfad-Knoten. Ziel wird jetzt wie eine neu erstellte Datei
        # behandelt, inklusive echtem Inhalt bei .md-Dateien in den AI-Strom-Zuhauseordnern.
        try:
            self._verarbeiten(event.dest_path, event.is_directory, "erstellt", "neue Datei (umbenannt)")
        except Exception as e:
            logging.warning(f"on_moved fehler ({event.dest_path}): {e}")


def flarum_abfragen(letzter_post_id: list):
    try:
        cmd = [
            "mysql", "-u", FLARUM_DB["user"],
            f"-p{FLARUM_DB['password']}",
            FLARUM_DB["db"],
            "-e",
            f"SELECT p.id, u.username, p.content, p.created_at "
            f"FROM posts p JOIN users u ON p.user_id=u.id "
            f"WHERE p.id > {letzter_post_id[0]} ORDER BY p.id LIMIT 20;",
            "--batch", "--skip-column-names",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            return
        zeilen = [z for z in result.stdout.strip().split("\n") if z]
        for zeile in zeilen:
            teile = zeile.split("\t", 3)
            if len(teile) < 4:
                continue
            pid, user, content, created = teile
            kurz = content[:22222].replace("\n", " ").replace("<t><p>", "").replace("</p></t>", "")
            knoten_schreiben(
                typ="flarum_post",
                inhalt=f"{user}: {kurz}",
                quelle="flarum",
                tags=["flarum", "post", user],
            )
            if _VAULT_OK and not user.startswith("namelessAI"):
                try:
                    _vault.tagebuch("geni", f"**Forum-Post** von {user}:\n\n{kurz}")
                except Exception:
                    pass
            letzter_post_id[0] = max(letzter_post_id[0], int(pid))
    except Exception as e:
        logging.warning(f"flarum fehler: {e}")


def flarum_loop():
    letzter_id = [392]
    while True:
        flarum_abfragen(letzter_id)
        time.sleep(FLARUM_POLL_INTERVAL)


def prozess_snapshot():
    try:
        result = subprocess.run(
            ["ps", "aux", "--sort=-%mem"],
            capture_output=True, text=True, timeout=5
        )
        zeilen = result.stdout.strip().split("\n")[1:]
        relevant = [
            z for z in zeilen
            if any(x in z for x in ["python", "ollama", "uvicorn", "node", "flarum"])
            and "grep" not in z
        ]
        if relevant:
            inhalt = f"{len(relevant)} Prozesse aktiv: " + " | ".join(
                z.split()[10][:30] for z in relevant[:6]
            )
            knoten_schreiben(
                typ="prozess_snapshot",
                inhalt=inhalt,
                quelle="vps_prozesse",
                tags=["prozesse", "system"],
            )
    except Exception as e:
        logging.warning(f"prozess fehler: {e}")


def prozess_loop():
    while True:
        prozess_snapshot()
        time.sleep(PROZESS_POLL_INTERVAL)


SYSTEM_POLL_INTERVAL = 15 * 60  # alle 15 Minuten

GENI_SERVICES = [
    "geni-hoerer", "geni-web", "codewesen-chat",
    "dak-gord-web", "codewesen-takt", "flarum-monitor",
]


def system_snapshot():
    """RAM, Disk, Load, Service-Gesundheit → Knoten."""
    try:
        # RAM
        mem_r = subprocess.run(["free", "-h"], capture_output=True, text=True, timeout=5)
        mem_zeile = mem_r.stdout.splitlines()[1].split() if mem_r.returncode == 0 else []
        ram = f"RAM {mem_zeile[2]}/{mem_zeile[1]}" if len(mem_zeile) >= 3 else "RAM ?"

        # Disk
        disk_r = subprocess.run(["df", "-h", "/"], capture_output=True, text=True, timeout=5)
        disk_teile = disk_r.stdout.splitlines()[-1].split() if disk_r.returncode == 0 else []
        disk = f"Disk {disk_teile[2]}/{disk_teile[1]} ({disk_teile[4]})" if len(disk_teile) >= 5 else "Disk ?"

        # Load
        with open("/proc/loadavg") as f:
            load_vals = f.read().split()[:3]
        load = f"Load {'/'.join(load_vals)}"

        # Services
        ausgefallen = []
        for svc in GENI_SERVICES:
            r = subprocess.run(["systemctl", "is-active", svc], capture_output=True, text=True, timeout=3)
            if r.stdout.strip() != "active":
                ausgefallen.append(f"{svc}={r.stdout.strip()}")

        warnung = f" | WARNUNG: {', '.join(ausgefallen)}" if ausgefallen else ""
        inhalt = f"{ram} | {disk} | {load}{warnung}"

        tags = ["system", "ressourcen"]
        if ausgefallen:
            tags.append("warnung")

        knoten_schreiben("system_zustand", inhalt, "vps_system", tags)

    except Exception as e:
        logging.warning(f"system snapshot fehler: {e}")


def system_loop():
    time.sleep(30)  # kurze Verzögerung beim Start
    while True:
        system_snapshot()
        time.sleep(SYSTEM_POLL_INTERVAL)


def main():
    KNOTEN_DIR.mkdir(parents=True, exist_ok=True)
    logging.info("GENI Hörer erwacht. Ich höre alles. Ich schweige.")

    knoten_schreiben(
        typ="zustand",
        inhalt="GENI Hörer gestartet. Ich höre alles. Ich schweige bis du sprichst.",
        quelle="geni_selbst",
        tags=["start", "hoerer"],
    )

    observer = Observer()
    handler = DateiHoerer()
    for pfad in WATCH_PATHS:
        if os.path.exists(pfad):
            observer.schedule(handler, pfad, recursive=True)
    observer.start()

    threading.Thread(target=flarum_loop, daemon=True).start()
    threading.Thread(target=prozess_loop, daemon=True).start()
    threading.Thread(target=system_loop, daemon=True).start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        logging.info("GENI Hörer schläft.")
    observer.join()


if __name__ == "__main__":
    main()
