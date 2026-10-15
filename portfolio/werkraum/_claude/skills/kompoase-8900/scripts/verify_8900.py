#!/usr/bin/env python3
"""Beweis-Skript für den Skill kompoase-8900.

Prüft den Ist-Zustand der KompOase-Testinstanz (Port 8900) und der zugehörigen
Dokumentation und schreibt einen Evidenz-Datensatz. Es mutiert nichts.

Tore (Token → PASS / FAIL / UNKNOWN):
  K8900-VERIFY-001  Dienst antwortet (GET / == 200)
  K8900-VERIFY-002  Heartbeat echt (GET /api/daemon-heartbeat == 200, alter_sekunden <= 90)
  K8900-VERIFY-003  Quellen-Stichprobe gezogen (n, Verteilung quelle_id, Herkunft, Anteil verborgen)
  K8900-VERIFY-004  Code-Stand ermittelt (letzter Commit mit Pfad kompoase/ im Repo-Toplevel)
  K8900-VERIFY-005  Schema-Ausschnitt gelesen (CREATE TABLE splitter in welt/schema_welt.sql)
  K8900-VERIFY-006  Daemon-Log direkt lesbar (letzte Tick-Zeile) — UNKNOWN, wenn der Pfad in
                    dieser Sicht (Container/Host) nicht existiert
  K8900-VERIFY-007  Heartbeat-Logpfad in server.py == Logpfad der Daemon-Unit (sonst falsches
                    "steht still?" im HUD)
  K8900-DOC-001     Systemdokus 69–75 vorhanden, jeder Titel trägt "KompOase 8900"
  K8900-DOC-002     Wissensprotokolle tragen das Label KompOase-8900(zusatz)
  K8900-VERIFY-008  Probestart mit dem Kommando der Unit kommt bis zum Binden (ein laufender
                    Dienst beweist nicht, dass ein Neustart gelingt)
  K8900-SKILL-001   Skill-Ladepfad und werkraum-Spiegel byteidentisch

Exit-Codes: 0 = alle PASS · 1 = mindestens ein FAIL · 3 = kein FAIL, aber UNKNOWN vorhanden.
Nur Standardbibliothek. Funktioniert aus Container-Sicht (/vps_root, /vps_system) und
Host-Sicht (/root, /etc) gleichermaßen.
"""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import json
import os
import re
import ssl
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

BASE_URL = "http://127.0.0.1:8900"
HEARTBEAT_MAX_AGE_S = 90.0
TICK_RE = re.compile(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) Tick (\d+):")
DOC_NUMBERS = range(69, 76)
DOC_TITLE_TAG = "KompOase 8900"
PROTOKOLL_LABEL = "KompOase-8900(zusatz)"

CANDIDATES = {
    "kompoase_dir": ["/root/kompoase", "/vps_root/kompoase"],
    "werkraum": ["/root/werkraum", "/vps_root/werkraum"],
    # Reihenfolge egal: VERIFY-006 nimmt den jüngsten existierenden Kandidaten (mtime).
    "daemon_log": [
        "/var/log/flextrawurst/splitter-physik.log",
        "/vps_system/var/log/flextrawurst/splitter-physik.log",
        "/root/werkraum/logs/splitter_daemon.log",
        "/root/werkraum_logs/splitter_daemon.log",
        "/vps_root/werkraum_logs/splitter_daemon.log",
    ],
    "unit": [
        "/etc/systemd/system/kompoase.service",
        "/vps_system/etc/systemd/system/kompoase.service",
    ],
    "daemon_unit": [
        "/etc/systemd/system/splitter-physik.service",
        "/vps_system/etc/systemd/system/splitter-physik.service",
    ],
}


def newest_existing(paths: list[str]) -> tuple[Path | None, list[dict]]:
    seen = []
    for p in paths:
        path = Path(p)
        if path.exists():
            seen.append({"pfad": str(path), "mtime": dt.datetime.fromtimestamp(path.stat().st_mtime).isoformat(timespec="seconds")})
    if not seen:
        return None, []
    best = max(seen, key=lambda s: s["mtime"])
    return Path(best["pfad"]), seen


def first_existing(paths: list[str]) -> Path | None:
    for p in paths:
        path = Path(p)
        if path.exists():
            return path
    return None


def http_get(path: str, timeout: float = 8.0) -> tuple[int | None, bytes, str | None]:
    url = BASE_URL + path
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return resp.status, resp.read(), None
    except urllib.error.HTTPError as e:
        return e.code, e.read(), None
    except Exception as e:  # noqa: BLE001 — Beweis, kein Absturz
        return None, b"", f"{type(e).__name__}: {e}"


def gate(token: str, status: str, detail: dict) -> dict:
    return {"token": token, "status": status, "detail": detail}


def check_service() -> dict:
    code, _, err = http_get("/")
    if code == 200:
        return gate("K8900-VERIFY-001", "PASS", {"http": 200})
    return gate("K8900-VERIFY-001", "FAIL", {"http": code, "error": err})


def check_heartbeat() -> dict:
    code, body, err = http_get("/api/daemon-heartbeat")
    if code != 200:
        return gate("K8900-VERIFY-002", "FAIL", {"http": code, "error": err, "body": body[:200].decode("utf-8", "replace")})
    try:
        d = json.loads(body)
        age = float(d["alter_sekunden"])
        detail = {"tick_nr": d.get("tick_nr"), "letzter_tick": d.get("letzter_tick"), "alter_sekunden": age}
    except Exception as e:  # noqa: BLE001
        return gate("K8900-VERIFY-002", "FAIL", {"http": 200, "parse_error": str(e)})
    status = "PASS" if age <= HEARTBEAT_MAX_AGE_S else "FAIL"
    detail["max_age_s"] = HEARTBEAT_MAX_AGE_S
    return gate("K8900-VERIFY-002", status, detail)


def check_sample(n: int) -> dict:
    code, body, err = http_get(f"/api/splitter?n={n}")
    if code != 200:
        return gate("K8900-VERIFY-003", "FAIL", {"http": code, "error": err})
    try:
        data = json.loads(body)
        assert isinstance(data, list)
    except Exception as e:  # noqa: BLE001
        return gate("K8900-VERIFY-003", "FAIL", {"http": 200, "parse_error": str(e)})
    counter = collections.Counter(
        (item.get("quelle_id") or ("quelle_verborgen" if item.get("quelle_sichtbar") is False else "ohne_quelle"))
        for item in data if isinstance(item, dict)
    )
    herkunft = collections.Counter(item.get("herkunft") or "?" for item in data if isinstance(item, dict))
    total = len(data)
    verborgen = counter.get("quelle_verborgen", 0)
    detail = {
        "n_angefragt": n,
        "n_erhalten": total,
        "verteilung": dict(counter.most_common()),
        "herkunft": dict(herkunft.most_common()),
        "anteil_quelle_verborgen": round(verborgen / total, 3) if total else None,
        "hinweis": "Stichprobe, kein Zensus; quelle_verborgen = quelle_sichtbar=false (meist herkunft=mensch)",
    }
    return gate("K8900-VERIFY-003", "PASS" if total > 0 else "FAIL", detail)


def check_code_state() -> dict:
    kdir = first_existing(CANDIDATES["kompoase_dir"])
    if kdir is None:
        return gate("K8900-VERIFY-004", "UNKNOWN", {"grund": "kompoase-Verzeichnis in dieser Sicht nicht vorhanden"})
    try:
        top = subprocess.run(["git", "-C", str(kdir), "rev-parse", "--show-toplevel"], capture_output=True, text=True, timeout=15, check=True).stdout.strip()
        branch = subprocess.run(["git", "-C", str(kdir), "branch", "--show-current"], capture_output=True, text=True, timeout=15, check=True).stdout.strip()
        rel = str(kdir.resolve().relative_to(Path(top).resolve())) if Path(top).resolve() != kdir.resolve() else "."
        log = subprocess.run(
            ["git", "-C", top, "log", "-1", "--format=%h|%ad|%s", "--date=iso-strict", "--", rel],
            capture_output=True, text=True, timeout=15, check=True,
        ).stdout.strip()
        h, ad, s = (log.split("|", 2) + ["", ""])[:3] if log else ("", "", "")
        return gate("K8900-VERIFY-004", "PASS" if log else "FAIL", {
            "kompoase_dir": str(kdir), "repo_toplevel": top, "branch": branch, "pfad_im_repo": rel,
            "letzter_commit": {"hash": h, "datum": ad, "betreff": s},
        })
    except Exception as e:  # noqa: BLE001
        return gate("K8900-VERIFY-004", "FAIL", {"error": str(e)})


def check_schema() -> dict:
    wr = first_existing(CANDIDATES["werkraum"])
    if wr is None:
        return gate("K8900-VERIFY-005", "UNKNOWN", {"grund": "werkraum in dieser Sicht nicht vorhanden"})
    schema = wr / "welt" / "schema_welt.sql"
    if not schema.exists():
        return gate("K8900-VERIFY-005", "FAIL", {"grund": f"{schema} fehlt"})
    text = schema.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"CREATE TABLE IF NOT EXISTS splitter \((.*?)\);", text, re.S)
    if not m:
        return gate("K8900-VERIFY-005", "FAIL", {"grund": "CREATE TABLE splitter nicht gefunden"})
    cols = [ln.strip().split()[0] for ln in m.group(1).splitlines() if ln.strip() and not ln.strip().startswith("--")]
    return gate("K8900-VERIFY-005", "PASS", {"datei": str(schema), "spalten": cols, "hinweis": "Kandidaten, keine bestätigt passend (Gesetz 6)"})


def check_daemon_log() -> dict:
    log, seen = newest_existing(CANDIDATES["daemon_log"])
    if log is None:
        return gate("K8900-VERIFY-006", "UNKNOWN", {"grund": "kein Daemon-Log in dieser Sicht lesbar"})
    try:
        with open(log, "rb") as f:
            f.seek(0, 2)
            size = f.tell()
            f.seek(max(0, size - 4000))
            tail = f.read().decode("utf-8", "replace")
        for line in reversed([l for l in tail.splitlines() if l.strip()]):
            m = TICK_RE.match(line)
            if m:
                # Alter über die Datei-mtime (zeitzonenunabhängig); der Zeitstempel in der Zeile ist Detail.
                age = round(dt.datetime.now().timestamp() - log.stat().st_mtime, 1)
                status = "PASS" if age <= HEARTBEAT_MAX_AGE_S else "FAIL"
                return gate("K8900-VERIFY-006", status, {
                    "juengstes_log": str(log), "letzter_tick": m.group(1), "tick_nr": int(m.group(2)),
                    "alter_sekunden": age, "alter_quelle": "mtime", "alle_kandidaten": seen,
                })
        return gate("K8900-VERIFY-006", "FAIL", {"juengstes_log": str(log), "grund": "keine Tick-Zeile in den letzten 4000 Bytes", "alle_kandidaten": seen})
    except Exception as e:  # noqa: BLE001
        return gate("K8900-VERIFY-006", "FAIL", {"juengstes_log": str(log), "error": str(e)})


def check_log_path_consistency() -> dict:
    """Der Pfad, den server.py für den Heartbeat liest, muss der Pfad sein, in den die
    Daemon-Unit tatsächlich schreibt. Eine Abweichung erzeugt ein falsches "steht still?"."""
    kdir = first_existing(CANDIDATES["kompoase_dir"])
    unit = first_existing(CANDIDATES["daemon_unit"])
    if kdir is None or unit is None:
        return gate("K8900-VERIFY-007", "UNKNOWN", {"grund": "server.py oder splitter-physik.service in dieser Sicht nicht lesbar"})
    server_py = (kdir / "server.py").read_text(encoding="utf-8", errors="replace")
    unit_text = unit.read_text(encoding="utf-8", errors="replace")
    m_unit = re.search(r"SPLITTER_LOG_PATH=(\S+)", unit_text)
    m_out = re.search(r"StandardOutput=append:(\S+)", unit_text)
    unit_path = (m_unit.group(1) if m_unit else None) or (m_out.group(1) if m_out else None)
    # server.py darf den Pfad als String, in einer Kandidatenliste oder über die Env-Variable kennen —
    # entscheidend ist, dass der Unit-Pfad dort überhaupt vorkommt (oder SPLITTER_LOG_PATH gelesen wird).
    kennt_pfad = bool(unit_path) and (unit_path in server_py or "SPLITTER_LOG_PATH" in server_py)
    m_srv = re.search(r'SPLITTER_DAEMON_LOG\s*=\s*"([^"]+)"', server_py)
    detail = {"server_py_kennt_unit_pfad": kennt_pfad, "server_py_konstante": m_srv.group(1) if m_srv else None,
              "unit_schreibt": unit_path, "unit": str(unit)}
    if not unit_path:
        return gate("K8900-VERIFY-007", "UNKNOWN", {**detail, "grund": "Logpfad in der Unit nicht ermittelbar"})
    return gate("K8900-VERIFY-007", "PASS" if kennt_pfad else "FAIL", detail)


def check_skill_mirror() -> dict:
    """Beide Skill-Kopien (Ladepfad und werkraum-Spiegel) müssen byteidentisch sein."""
    wr = first_existing(CANDIDATES["werkraum"])
    lade = Path("/config/.agents/skills/kompoase-8900")
    if wr is None or not lade.exists():
        return gate("K8900-SKILL-001", "UNKNOWN", {"grund": "Ladepfad oder werkraum in dieser Sicht nicht vorhanden"})
    spiegel = wr / "_claude" / "skills" / "kompoase-8900"
    if not spiegel.exists():
        return gate("K8900-SKILL-001", "FAIL", {"grund": f"Spiegel fehlt: {spiegel}"})
    import hashlib
    def hashes(root: Path) -> dict:
        out = {}
        for p in sorted(root.rglob("*")):
            if p.is_file() and "__pycache__" not in p.parts:
                out[str(p.relative_to(root))] = hashlib.sha256(p.read_bytes()).hexdigest()[:16]
        return out
    a, b = hashes(lade), hashes(spiegel)
    diff = sorted(set(a) ^ set(b)) + sorted(k for k in a.keys() & b.keys() if a[k] != b[k])
    return gate("K8900-SKILL-001", "PASS" if not diff else "FAIL", {"ladepfad": str(lade), "spiegel": str(spiegel), "abweichend": diff, "dateien": len(a)})


def _start_kommando(server_py: Path) -> list[str]:
    """Das Kommando nehmen, mit dem systemd den Dienst wirklich startet.

    Ein Probestart mit einem anderen Interpreter würde etwas anderes prüfen als
    das, was beim Neustart passiert.
    """
    unit = first_existing(CANDIDATES["unit"])
    if unit is not None:
        try:
            zeilen = unit.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            zeilen = []
        for zeile in zeilen:
            if not zeile.startswith("ExecStart="):
                continue
            teile = zeile[len("ExecStart="):].split()
            if teile and teile[0].endswith("/env"):
                teile = teile[1:]
            teile = [t for t in teile if "=" not in t]
            if len(teile) >= 2:
                return teile
    return [sys.executable, str(server_py)]


def _startfehler(ausgabe: str, exit_code: int) -> dict:
    """Nur Art und Ort des Fehlers melden, keine Quelltextzeilen.

    In server.py steht ein voreingestelltes Passwort im Klartext. Ein Traceback
    druckt die auslösende Quelltextzeile mit -- die bleibt hier draußen, damit ein
    Prüfbericht kein Geheimnis in die Evidenzdatei schreibt.
    """
    zeilen = [z.rstrip() for z in ausgabe.splitlines() if z.strip()]
    stellen = [z.strip() for z in zeilen if z.strip().startswith('File "')]
    letzte = next((z.strip() for z in reversed(zeilen) if not z.startswith(" ")), "")
    return {
        "grund": "Probestart scheiterte vor dem Binden — ein Neustart würde den Dienst nicht hochbringen",
        "fehler": letzte[:300],
        "stelle": stellen[-1][:200] if stellen else None,
        "exit": exit_code,
    }


def check_kaltstart() -> dict:
    """K8900-VERIFY-008: würde der Dienst einen Neustart überleben?

    Ein antwortender Port beweist das nicht. Ein Prozess kann seit Stunden mit
    Code laufen, den es so nicht mehr gibt; der Bruch zeigt sich erst beim
    nächsten Start — bei einem Reboot, einem Absturz, einem Update.

    Der Probestart ist gefahrlos, weil er nur bei belegtem Port läuft: dann
    scheitert sein eigenes Binden zwangsläufig, und er kann den Dienst nicht
    verdrängen. Ist der Port frei, wird nicht gestartet — das wäre kein Prüfen
    mehr, sondern ein Eingriff.
    """
    token = "K8900-VERIFY-008"
    if Path("/vps_root").exists():
        return gate(token, "UNKNOWN", {"grund": "Probestart nur aus Host-Sicht möglich"})

    kdir = first_existing(CANDIDATES["kompoase_dir"])
    server_py = (kdir / "server.py") if kdir is not None else None
    if server_py is None or not server_py.exists():
        return gate(token, "UNKNOWN", {"grund": "server.py in dieser Sicht nicht vorhanden"})

    code, _, _ = http_get("/")
    if code != 200:
        return gate(token, "UNKNOWN", {
            "grund": "Dienst antwortet nicht — ein Probestart würde den freien Port belegen, das wäre ein Eingriff",
            "http": code,
        })

    kommando = _start_kommando(server_py)
    umgebung = dict(os.environ)
    # Das voreingestellte Rotationspasswort soll im Probestart keine Rolle spielen.
    umgebung["KOMPOASE_CRAWL_ROTATE_PASSWORD"] = "probestart-ohne-wirkung"
    try:
        lauf = subprocess.run(kommando, cwd=str(kdir), capture_output=True,
                              text=True, timeout=25, env=umgebung)
    except subprocess.TimeoutExpired:
        return gate(token, "FAIL", {
            "grund": "Probestart lief in den Zeitablauf, statt am belegten Port zu scheitern",
            "kommando": " ".join(kommando),
        })
    except OSError as e:
        return gate(token, "UNKNOWN", {"grund": f"Probestart nicht ausführbar: {type(e).__name__}"})

    ausgabe = (lauf.stderr or "") + (lauf.stdout or "")
    if "Errno 98" in ausgabe or "Address already in use" in ausgabe:
        return gate(token, "PASS", {
            "probestart": "bis zum Binden gekommen, Port erwartungsgemäß belegt",
            "kommando": " ".join(kommando),
            "exit": lauf.returncode,
        })
    detail = _startfehler(ausgabe, lauf.returncode)
    detail["kommando"] = " ".join(kommando)
    return gate(token, "FAIL", detail)


def check_docs() -> dict:
    wr = first_existing(CANDIDATES["werkraum"])
    if wr is None:
        return gate("K8900-DOC-001", "UNKNOWN", {"grund": "werkraum in dieser Sicht nicht vorhanden"})
    sd = wr / "docs" / "systemdoku"
    # Grundmenge 69–75 plus jede weitere Doku, deren Titel den Strang-Tag trägt (der Strang wächst).
    nums = set(DOC_NUMBERS)
    for p in sd.glob("[0-9]*_*.md"):
        m = re.match(r"(\d+)_", p.name)
        try:
            first = p.read_text(encoding="utf-8", errors="replace").splitlines()[0]
        except Exception:
            continue
        if m and DOC_TITLE_TAG in first:
            nums.add(int(m.group(1)))
    result, fails = {}, []
    for num in sorted(nums):
        hits = sorted(sd.glob(f"{num}_*.md"))
        if not hits:
            result[str(num)] = "FEHLT"
            fails.append(num)
            continue
        if len(hits) > 1:
            result[str(num)] = {"kollision": [h.name for h in hits]}
            fails.append(num)
            continue
        title = hits[0].read_text(encoding="utf-8", errors="replace").splitlines()[0] if hits[0].stat().st_size else ""
        ok = DOC_TITLE_TAG in title
        result[str(num)] = {"datei": hits[0].name, "titel_tag": ok}
        if not ok:
            fails.append(num)
    return gate("K8900-DOC-001", "PASS" if not fails else "FAIL", {"dokus": result, "strang_nummern": sorted(nums), "ohne_tag_oder_fehlend": fails})


def check_protokolle() -> dict:
    wr = first_existing(CANDIDATES["werkraum"])
    if wr is None:
        return gate("K8900-DOC-002", "UNKNOWN", {"grund": "werkraum in dieser Sicht nicht vorhanden"})
    files = {"flextrawurst.md": wr / "_claude" / "flextrawurst.md", "ai-ströme.md": wr / "_claude" / "ai-ströme.md"}
    detail, fails = {}, []
    for name, path in files.items():
        if not path.exists():
            detail[name] = "FEHLT"
            fails.append(name)
            continue
        found = PROTOKOLL_LABEL in path.read_text(encoding="utf-8", errors="replace")
        detail[name] = {"label_vorhanden": found}
        if not found:
            fails.append(name)
    return gate("K8900-DOC-002", "PASS" if not fails else "FAIL", {"dateien": detail, "ohne_label": fails})


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sample", type=int, default=200, help="Stichprobengröße für /api/splitter (Default 200)")
    ap.add_argument("--output", default=None, help="Evidenz-Verzeichnis (Default: <werkraum>/_claude/berichte/kompoase-8900)")
    ap.add_argument("--no-write", action="store_true", help="nur ausgeben, keine Evidenz-Datei schreiben")
    ap.add_argument("--json", action="store_true", help="vollständiges JSON auf stdout statt Tabelle")
    args = ap.parse_args()

    gates = [
        check_service(),
        check_heartbeat(),
        check_sample(args.sample),
        check_code_state(),
        check_schema(),
        check_daemon_log(),
        check_log_path_consistency(),
        check_kaltstart(),
        check_docs(),
        check_protokolle(),
        check_skill_mirror(),
    ]
    statuses = [g["status"] for g in gates]
    overall = "FAIL" if "FAIL" in statuses else ("UNKNOWN" if "UNKNOWN" in statuses else "PASS")
    record = {
        "skill": "kompoase-8900",
        "zeitpunkt_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "sicht": "container" if Path("/vps_root").exists() else "host",
        "gesamt": overall,
        "tore": gates,
        "unit": str(first_existing(CANDIDATES["unit"]) or "nicht sichtbar"),
    }

    written = None
    if not args.no_write:
        wr = first_existing(CANDIDATES["werkraum"])
        out_dir = Path(args.output) if args.output else (wr / "_claude" / "berichte" / "kompoase-8900" if wr else Path.cwd())
        out_dir.mkdir(parents=True, exist_ok=True)
        stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        written = out_dir / f"{stamp}_verify_8900.json"
        written.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
        record["evidenz_datei"] = str(written)

    if args.json:
        print(json.dumps(record, ensure_ascii=False, indent=2))
    else:
        print(f"kompoase-8900 · {record['zeitpunkt_utc']} · Sicht: {record['sicht']} · GESAMT: {overall}")
        for g in gates:
            d = g["detail"]
            short = {k: v for k, v in d.items() if k in ("http", "alter_sekunden", "tick_nr", "n_erhalten", "anteil_quelle_verborgen", "branch", "pfad_im_repo", "ohne_tag_oder_fehlend", "ohne_label", "grund", "error", "server_py_kennt_unit_pfad", "unit_schreibt", "juengstes_log", "abweichend",
                                              "probestart", "kommando", "exit",
                                              "fehler", "stelle")}
            if "spalten" in d:
                short["spalten"] = len(d["spalten"])
            if "letzter_commit" in d:
                short["commit"] = d["letzter_commit"].get("hash")
            if "verteilung" in d:
                short["top"] = dict(list(d["verteilung"].items())[:6])
            print(f"  {g['token']:<18} {g['status']:<8} {json.dumps(short, ensure_ascii=False)}")
        nur_andere_sicht = [g["token"] for g in gates
                            if g["status"] == "UNKNOWN"
                            and "Sicht" in str(g["detail"].get("grund", ""))]
        if nur_andere_sicht:
            # Kein Mangel, sondern eine Eigenschaft der Sicht: VERIFY-008 kann nur der
            # Host beantworten (dort laeuft der Dienst), SKILL-001 nur der Container
            # (nur dort existiert der Ladepfad). Der vollstaendige Beweis sind beide Laeufe.
            print(f"  Aus dieser Sicht nicht beantwortbar: {', '.join(nur_andere_sicht)}"
                  f" — vollstaendiger Beweis = ein Lauf je Sicht.")
        if written:
            print(f"  Evidenz: {written}")

    return 0 if overall == "PASS" else (1 if overall == "FAIL" else 3)


if __name__ == "__main__":
    sys.exit(main())
