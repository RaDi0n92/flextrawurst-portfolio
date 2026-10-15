#!/usr/bin/env python3
"""
kompoase_harness.py - Kreativleitende, prüfende State-Machine für einen KompOase-8900-Bogen.

Ein Bogen = ein zusammenhängendes Stück Arbeit (Konzept oder Bau) an der Testinstanz oder der
Splitter-Kosmologie. Der Harness nimmt die Plackerei ab (Verifikation, Beweise, Pflichtprüfungen),
liefert echtes Material als Impuls (kein erfundenes) und lässt keinen Knoten überspringen.

Knoten (Kanten nur vorwärts, jeder Knoten prüft seinen Vorgänger):
  01_INIT              Bogen angelegt
  02_SKILL_READ        SKILL.md gelesen (Hash festgehalten)
  03_DOKUS_READ        Dokus 69–75 gelesen (Hashes, Titel-Tag), Lesebestätigung
  04_VERIFY            verify_8900.py gelaufen, Evidenz verlinkt, Fails bekannt
  05_MODE_LOCK         KONZEPT (Standard) oder BAU (nur mit wörtlichem Bauauftrag) → BAU_PERMIT
  06_IMPULS            lebendes Material aus dem Feed + Fragenraum + offene Frage + Gesetz im Blick
  07_ENTWURF           Vorschlagstext: satzweiser Linter gegen die Gesetze (Erwähnungen — Negation, Frage,
                       Gesetzesnennung, Codebegriff — sind Hinweise, positive Vorschläge blockieren) +
                       15-Punkte-Checkliste als Selbst-Attestierung → ENTWURF_PERMIT
  08_FREIGABE          Daniels Entscheidung: angenommen → weiter · geaendert → zurück zu 07 · abgelehnt → 14
  09_BACKUP            BAU: backup:-Commit im richtigen Repo seit Modus-Lock nachgewiesen (KONZEPT: übersprungen)
  10_MUTATION          BAU: genau eine benannte Änderung; Pfade im Repo müssen seit Backup im git diff stehen → MUTATION_PERMIT
  11_EVIDENZ_NACHHER   BAU: verify_8900.py erneut, Delta vorher/nachher
  12_DOKU              Systemdoku geprüft (Nummer eindeutig, Titel-Tag, status, Überschrift mit "offen");
                       Wissensprotokoll-Eintrag nur mit Freigabe "angenommen" + --go Wortlaut; --keine-doku GRUND erlaubt
  13_COMMIT            Commit(s) nachgewiesen — je Repo einer, muss die Pfade dieses Bogens im Repo enthalten
  14_ABSCHLUSS         Bericht geschrieben, Bogen gehalten — nächster Bogen erst nach Feedback

Eiserne Sperren:
  - Kein ENTWURF ohne VERIFY und IMPULS.
  - Kein BAU-Pfad (09–11) ohne BAU_PERMIT und FREIGABE.
  - Kein Wissensprotokoll-Eintrag ohne FREIGABE "angenommen" und eigene Zustimmung (--go).
  - Linter-Blocker nur per Override mit Grund.
  - init verweigert einen laufenden/abgeschlossenen Bogen gleichen Namens; --session nur [A-Za-z0-9_.-].

Was der Harness beweist: Hashes, Diffs, Commits, Evidenz-Dateien.
Was er nur attestiert: gelesen, Checkliste, Entwurf gezeigt, kein Dienst-Neustart.
"""

import argparse
import hashlib
import json
import os
import random
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from enum import Enum
from pathlib import Path

# --- STANDARDPFADE (Container- und Host-Sicht) ---
SKILL_DIR_CANDIDATES = [
    "/config/.agents/skills/kompoase-8900",
    "/root/werkraum/_claude/skills/kompoase-8900",
    "/vps_root/werkraum/_claude/skills/kompoase-8900",
]
WERKRAUM_CANDIDATES = ["/root/werkraum", "/vps_root/werkraum"]
ROOT_REPO_CANDIDATES = ["/root", "/vps_root"]
BASE_URL = "http://127.0.0.1:8900"
DOC_NUMBERS = range(69, 76)
DOC_TITLE_TAG = "KompOase 8900"
PROTOKOLL_LABEL = "KompOase-8900(zusatz)"


def first_existing(paths):
    for p in paths:
        if Path(p).exists():
            return Path(p)
    return None


def strang_dokus(systemdoku_dir: Path):
    """Alle Nummern dieses Strangs: die Grundmenge 69–75 plus jede weitere Systemdoku, deren
    Titelzeile den Strang-Tag trägt — so wächst die Lesepflicht mit dem Strang."""
    nums = set(DOC_NUMBERS)
    for p in systemdoku_dir.glob("[0-9]*_*.md"):
        try:
            first = p.read_text(encoding="utf-8", errors="replace").splitlines()[0]
        except Exception:
            continue
        m = re.match(r"(\d+)_", p.name)
        if m and DOC_TITLE_TAG in first:
            nums.add(int(m.group(1)))
    return sorted(nums)


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


# --- DIE 15 GESETZE ALS LINTER (Treffer blockieren bis Override mit Grund) ---
LINTER_RULES = [
    ("G1 Schwellenwert-Leben", [r"(>|>=|<|<=)\s*0[.,]\d", r"\bscore\b", r"schwellenwert", r"conflict_score", r"threshold", r"grenzwert"]),
    ("G2 Zentralinstanz", [r"\bpreis\b", r"\brating\b", r"kurator", r"admin[- ]?urteil", r"admin entscheidet", r"zentral(instanz|e stelle)"]),
    ("G4 Dialoge", [r"dialog[e]?\s+generier", r"verhandlungstext", r"sprechblase", r"wortwechsel"]),
    ("G5 Eltern-Kind", [r"\beltern", r"\bkind\b", r"\bkinder\b", r"kindknoten", r"\bparent\b", r"\bchild\b"]),
    ("G7 Flüchtlinge als Baupfad", [r"flüchtling", r"fluechtling", r"zwischenwesen", r"lande[- ]?zeremonie", r"24h[- ]wesen"]),
    ("G8 LLM pro Splitter/Tick", [r"llm[- ]?(aufruf|call)s? pro", r"pro (splitter|tick|ereignis).{0,40}llm", r"llm.{0,40}pro (splitter|tick|ereignis)"]),
    ("G10 410 öffnen", [r"\b410\b.{0,40}(öffnen|oeffnen|aktivieren|freigeben)", r"schreibpfad.{0,40}(öffnen|oeffnen|aktivieren)"]),
    ("G6 Spalten-Reflex", [r"(gibt|existiert|haben wir) (ja )?schon (eine |die )?spalte", r"spalte .{0,30}(passt|reicht) schon", r"dafür gibt es schon"]),
]
LINTER_KONZEPT_ONLY = [
    ("G9 Schritt-Zerlegung im Konzeptmodus", [r"\bmvp\b", r"schritt 1\b", r"kleinste[rn]? (erste[rn]? )?schritt", r"erste[rn]? bissen", r"shovel", r"sofort machbar"]),
]

# --- CHECKLISTE (§6 des Skills): 1–8 müssen "nein", 9–15 müssen "ja" sein ---
CHECKLIST_REQUIRED = {**{i: "nein" for i in range(1, 9)}, **{i: "ja" for i in range(9, 16)}}
CHECKLIST_TEXT = {
    1: "Schwellenwert/Score/Formel/Automatismus für Leben, Passung, Wert?",
    2: "Instanz, die Wert festlegt (Preis, Rating, Kurator, Admin)?",
    3: "Erzählung ohne Ledger-Zeile oder Vermischung beider?",
    4: "Generierte Dialoge?",
    5: "Eltern/Kind/Geburt-Sprache?",
    6: "Spalte als passend behauptet ohne Einzelprüfung?",
    7: "Flüchtlinge/Zwischenwesen als Baupfad?",
    8: "Zusätzliche LLM-Aufrufe pro Splitter/Tick/Ereignis?",
    9: "Modus benannt und Text passt dazu (keine Schritt-Zerlegung im Konzeptmodus)?",
    10: "Ursprungsbesitzer, Ursprungsart, erste Verbindung, Zeitstempel bleiben erhalten?",
    11: "Bei Vermengung bleibt Herkunft beider Seiten sichtbar; Ein-Klick-Zugang bleibt?",
    12: "Jede Ist-Aussage per verify_8900.py in dieser Session belegt?",
    13: "Nicht schon verworfen (5.2) oder zurückgestellt (5.3)?",
    14: "Fortsetzung mit neuer Nummer und 'KompOase 8900 —' im Titel, kein Duplikat?",
    15: "Backup-Commit im richtigen Repo; kein Dienst-Neustart ohne Freigabe?",
}

# --- KREATIVES MATERIAL FÜR DEN IMPULS-KNOTEN (aus Doku 74 §2, Skill §5.3, §1) ---
FRAGENRAUM = [
    "Wohin zieht es mich?", "Wohin zieht es mich und alle gemeinsam?", "Wohin zieht es mich nicht?",
    "Was zieht mich an, was stößt mich ab?", "Was mag ich, was mag ich nicht?",
    "Wie können wir gemeinsam wachsen/werden?", "Was sollen wir behalten, was können wir loslassen?",
    "Was ist unser Kern und was nicht?", "Was ist gegensätzlich zu mir?", "Was passt zu mir?",
]
OFFENE_FRAGEN = [
    "Wortstatus 'Splitter' für die innere Ebene (72 §3)",
    "Konkrete Passt-es-Mechanik beim Loslösen (72 §8, 73 §11)",
    "Schema für das fraktale Modell; Trage-Relation; zweiter verbindungstyp (72 §8)",
    "Exit: was wird mitgenommen; Konflikte über gemeinsam Entstandenes; Gewichtung großer Verbünde; Währung (71)",
    "Anteile als Prozent oder genealogisch (71)",
    "Mechanik von Phantom-Watcher: Ins-Licht-Rücken, Vererbung messen (75 §8)",
    "Zensi als Träger einer Splitter-Stimme — Funktionsweise ungeprüft (74 §7)",
    "Heartbeat-Pfad in server.py (Skill §2.4)",
]
GESETZE_KURZ = [
    "G1 Kein Schwellenwert-Leben", "G2 Keine Zentralinstanz für Wert", "G3 Ledger ≠ Erzählung",
    "G4 Keine erfundenen Dialoge", "G5 Keine Eltern-Kind-Sprache", "G6 Keine Spalte gilt als passend",
    "G7 Flüchtlinge sind außerhalb", "G8 Ein-LLM-Kontention", "G9 Konzept ist kein Bauauftrag",
    "G10 410-Schreibpfade bleiben zu", "G11 Grundgesetze gelten weiter", "G12 Ein-Klick-Zugang",
    "G13 Zwei Repos, zwei Backups", "G14 Externe Bildwerkzeuge nur einzeln", "G15 Kein Dienst-Neustart ohne Freigabe",
]


class HarnessNode(str, Enum):
    INIT = "01_INIT"
    SKILL_READ = "02_SKILL_READ"
    DOKUS_READ = "03_DOKUS_READ"
    VERIFY = "04_VERIFY"
    MODE_LOCK = "05_MODE_LOCK"
    IMPULS = "06_IMPULS"
    ENTWURF = "07_ENTWURF"
    FREIGABE = "08_FREIGABE"
    BACKUP = "09_BACKUP"
    MUTATION = "10_MUTATION"
    EVIDENZ_NACHHER = "11_EVIDENZ_NACHHER"
    DOKU = "12_DOKU"
    COMMIT = "13_COMMIT"
    ABSCHLUSS = "14_ABSCHLUSS"


class FeedReader:
    """Zieht echtes Material von der Testinstanz. Erfindet nichts; ohne Feed → leer."""

    @staticmethod
    def sample(n=60):
        try:
            with urllib.request.urlopen(f"{BASE_URL}/api/splitter?n={n}", timeout=6) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return [d for d in data if isinstance(d, dict)]
        except Exception:
            return []

    @staticmethod
    def kurz(s):
        sichtbar = s.get("quelle_sichtbar", True)
        q = s.get("quelle_id") or ("quelle_verborgen" if sichtbar is False else "ohne_quelle")
        inhalt = (s.get("inhalt_kurz") or s.get("inhalt_voll") or "").replace("\n", " ").strip()
        return {
            "id": str(s.get("id", ""))[:16],
            "quelle": q,
            "herkunft": s.get("herkunft"),
            "inhalt": (inhalt[:140] + "…") if len(inhalt) > 140 else inhalt,
            "materialitaet": s.get("materialitaet"),
            "energie": round(float(s["energie"]), 2) if isinstance(s.get("energie"), (int, float)) else s.get("energie"),
            "groesse": s.get("groesse"),
        }


class KompoaseHarness:
    """Verwaltet einen KompOase-8900-Bogen mit unüberspringbaren Knoten."""

    SESSION_RE = re.compile(r"^[A-Za-z0-9_.-]{1,64}$")

    def __init__(self, workspace_dir, session):
        if not self.SESSION_RE.match(session or ""):
            raise ValueError("--session: nur Buchstaben, Ziffern, _ . - (max. 64 Zeichen)")
        self.workspace = Path(workspace_dir)
        self.workspace.mkdir(parents=True, exist_ok=True)
        self.session = session
        self.state_file = self.workspace / f"harness_{session}_state.json"
        self.skill_dir = first_existing(SKILL_DIR_CANDIDATES)
        self.werkraum = first_existing(WERKRAUM_CANDIDATES)
        self.load_state()

    # --- Zustand ---
    def load_state(self):
        if self.state_file.exists():
            with open(self.state_file, "r", encoding="utf-8") as f:
                self.data = json.load(f)
            return
        self.data = {
            "session": self.session,
            "started": time.strftime("%Y-%m-%d %H:%M:%S"),
            "current_node": HarnessNode.INIT.value,
            "mode": None,
            "auftrag": None,
            "gates": {
                "skill_read": False, "dokus_read": False, "verified": False, "mode_locked": False,
                "impuls_gezogen": False, "entwurf_geprueft": False, "freigabe": False,
                "backup": False, "mutation": False, "evidenz_nachher": False,
                "doku": False, "commit": False, "abgeschlossen": False,
            },
            "permits": {"BAU_PERMIT": False, "ENTWURF_PERMIT": False, "MUTATION_PERMIT": False},
            "skill": {}, "dokus": {}, "verify": {}, "impuls": {}, "entwurf": {}, "freigabe": {},
            "backup": {}, "mutation": {}, "evidenz_nachher": {}, "doku": {}, "commit": {},
            "history": [],
        }
        self.save_state()

    def save_state(self):
        tmp = self.state_file.with_suffix(".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
        tmp.replace(self.state_file)

    def transition_to(self, node: HarnessNode, note=""):
        self.data["history"].append({
            "from": self.data["current_node"], "to": node.value,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"), "note": note,
        })
        self.data["current_node"] = node.value
        self.save_state()
        print(f"\n[HARNESS] ➔ Übergang zu Knoten: {node.value} ({note})")

    def require(self, gate, tor):
        if not self.data["gates"].get(gate):
            raise RuntimeError(f"🛑 HARNESS-SPERRE: {tor} muss zuerst absolviert werden!")

    # --- 02 SKILL ---
    def gate_02_read_skill(self):
        print("\n=== [TOR 02/14] SKILL LESEN ===")
        if self.skill_dir is None:
            raise FileNotFoundError("Skill-Verzeichnis kompoase-8900 nicht gefunden")
        skill = self.skill_dir / "SKILL.md"
        self.data["skill"] = {"pfad": str(skill), "bytes": skill.stat().st_size, "sha256": sha256_of(skill)}
        self.data["gates"]["skill_read"] = True
        print(f"✓ {skill} ({self.data['skill']['bytes']} Bytes, sha {self.data['skill']['sha256']})")
        self.transition_to(HarnessNode.DOKUS_READ, "Skill gelesen")

    # --- 03 DOKUS ---
    def gate_03_read_dokus(self, bestaetigt: bool):
        print("\n=== [TOR 03/14] DOKUS 69–75 LESEN ===")
        self.require("skill_read", "Tor 02 (Skill lesen)")
        if not bestaetigt:
            raise RuntimeError("🛑 Lesebestätigung fehlt: --bestaetigt setzen, nachdem alle sieben Dokus tatsächlich gelesen wurden.")
        sd = self.werkraum / "docs" / "systemdoku"
        out, fehler = {}, []
        for num in strang_dokus(sd):
            hits = sorted(sd.glob(f"{num}_*.md"))
            if not hits:
                fehler.append(f"{num}: fehlt")
                continue
            if len(hits) > 1:
                fehler.append(f"{num}: Nummer mehrfach belegt ({[h.name for h in hits]})")
                continue
            title = hits[0].read_text(encoding="utf-8", errors="replace").splitlines()[0]
            if DOC_TITLE_TAG not in title:
                fehler.append(f"{num}: Titel ohne '{DOC_TITLE_TAG}'")
            out[str(num)] = {"datei": hits[0].name, "sha256": sha256_of(hits[0]), "zeilen": sum(1 for _ in open(hits[0], encoding="utf-8", errors="replace"))}
        if fehler:
            raise RuntimeError("🛑 Doku-Prüfung fehlgeschlagen: " + "; ".join(fehler))
        self.data["dokus"] = {"gelesen_am": time.strftime("%Y-%m-%d %H:%M:%S"), "dateien": out}
        self.data["gates"]["dokus_read"] = True
        print(f"✓ {len(out)} Dokus verifiziert, {sum(d['zeilen'] for d in out.values())} Zeilen, Lesebestätigung festgehalten")
        self.transition_to(HarnessNode.VERIFY, "Dokus gelesen")

    # --- 04 VERIFY ---
    def _run_verify(self):
        script = self.skill_dir / "scripts" / "verify_8900.py"
        res = subprocess.run([sys.executable, str(script), "--json"], capture_output=True, text=True, timeout=120)
        try:
            record = json.loads(res.stdout)
        except Exception:
            raise RuntimeError(f"verify_8900.py lieferte kein JSON (exit {res.returncode}): {res.stderr[-400:]}")
        return record, res.returncode

    def gate_04_verify(self):
        print("\n=== [TOR 04/14] VERIFY — BEWEISE STATT ERINNERUNG ===")
        self.require("dokus_read", "Tor 03 (Dokus lesen)")
        record, code = self._run_verify()
        fails = [t["token"] for t in record["tore"] if t["status"] == "FAIL"]
        unknown = [t["token"] for t in record["tore"] if t["status"] == "UNKNOWN"]
        self.data["verify"] = {"gesamt": record["gesamt"], "exit": code, "fails": fails, "unknown": unknown, "evidenz": record.get("evidenz_datei"), "zeit": record["zeitpunkt_utc"]}
        self.data["gates"]["verified"] = True
        for t in record["tore"]:
            print(f"  {t['token']:<18} {t['status']}")
        print(f"✓ Gesamt: {record['gesamt']} · Evidenz: {record.get('evidenz_datei')}")
        if fails:
            print(f"⚠ Bekannte Fails gehen als Ist-Zustand in den Bogen ein: {fails}")
        self.transition_to(HarnessNode.MODE_LOCK, f"verify {record['gesamt']}")

    # --- 05 MODE ---
    def gate_05_lock_mode(self, mode: str, auftrag: str = None):
        print("\n=== [TOR 05/14] MODUS SPERREN ===")
        self.require("verified", "Tor 04 (Verify)")
        mode = mode.upper()
        if mode not in ("KONZEPT", "BAU"):
            raise ValueError("Modus muss KONZEPT oder BAU sein")
        if mode == "BAU":
            if not auftrag or len(auftrag.strip()) < 8:
                raise RuntimeError("🛑 BAU nur mit wörtlichem Bauauftrag (--auftrag \"…\"). Ohne Auftrag bleibt es KONZEPT (Gesetz 9).")
            self.data["permits"]["BAU_PERMIT"] = True
        self.data["mode"] = mode
        self.data["auftrag"] = auftrag
        self.data["gates"]["mode_locked"] = True
        print(f"✓ Modus: {mode}" + (f" · Auftrag: \"{auftrag}\"" if auftrag else ""))
        if mode == "BAU":
            print("🔓 BAU_PERMIT erteilt — Backup, genau eine Mutation, Evidenz nachher sind Pflicht.")
        self.transition_to(HarnessNode.IMPULS, f"Modus {mode}")

    # --- 06 IMPULS (kreativ, positiv, aus echtem Material) ---
    def gate_06_impuls(self, n=3, seed=None):
        print("\n=== [TOR 06/14] IMPULS — LEBENDES MATERIAL, NICHTS ERFUNDEN ===")
        self.require("mode_locked", "Tor 05 (Modus)")
        rnd = random.Random(seed)
        feed = FeedReader.sample(120)
        auswahl = [FeedReader.kurz(s) for s in rnd.sample(feed, min(n, len(feed)))] if feed else []
        quellen = {}
        for s in feed:
            q = s.get("quelle_id") or ("quelle_verborgen" if s.get("quelle_sichtbar") is False else "ohne_quelle")
            quellen[q] = quellen.get(q, 0) + 1
        begegnung = None
        if feed:
            by_q = {}
            for s in feed:
                by_q.setdefault(s.get("quelle_id") or "quelle_verborgen", []).append(s)
            qs = [q for q in by_q if q != "quelle_verborgen"]
            if len(qs) >= 2:
                a, b = rnd.sample(qs, 2)
                begegnung = {"a": FeedReader.kurz(rnd.choice(by_q[a])), "b": FeedReader.kurz(rnd.choice(by_q[b]))}
        impuls = {
            "zeit": time.strftime("%Y-%m-%d %H:%M:%S"),
            "feed_erreichbar": bool(feed),
            "feed_n": len(feed),
            "quellen": dict(sorted(quellen.items(), key=lambda kv: -kv[1])),
            "material": auswahl,
            "begegnung": begegnung,
            "frage": rnd.choice(FRAGENRAUM),
            "offen": rnd.choice(OFFENE_FRAGEN),
            "gesetz_im_blick": rnd.choice(GESETZE_KURZ),
        }
        self.data["impuls"] = impuls
        self.data["gates"]["impuls_gezogen"] = True

        print(f"• Feed: {len(feed)} Splitter · Quellen: {impuls['quellen']}")
        if not feed:
            print("• Kein Feed erreichbar — Impuls ohne Material; Ist-Aussagen sind damit heute nicht belegbar.")
        for i, s in enumerate(auswahl, 1):
            print(f"• Material {i}: [{s['quelle']}/{s['herkunft']}] {s['inhalt'] or '(leer)'}  · {s['materialitaet']} · energie {s['energie']} · größe {s['groesse']}")
        if begegnung:
            print(f"• Begegnung: [{begegnung['a']['quelle']}] „{begegnung['a']['inhalt'][:70]}“  ×  [{begegnung['b']['quelle']}] „{begegnung['b']['inhalt'][:70]}“")
            print("  → Welche Gefühlsgewebe-Überschneidung hätten die beiden? Was würde ein dritter Strom dazu sagen?")
        print(f"• Frage aus dem Fragenraum: {impuls['frage']}")
        print(f"• Offene Frage, die auf Material wartet: {impuls['offen']}")
        print(f"• Gesetz im Blick: {impuls['gesetz_im_blick']}")
        print("• Alles oben ist echt, zeitgestempelt, append-only. Nichts davon muss erfunden werden — nimm, was zieht.")
        self.transition_to(HarnessNode.ENTWURF, "Impuls gezogen")

    # --- 07 ENTWURF ---
    NEGATION = re.compile(r"\b(kein|keine|keinen|keiner|keinem|nicht|nie|niemals|weder|ohne|verboten|verbot|außerhalb|ausserhalb|statt|anstatt|verworfen|abgelehnt|verdächtig|nur)\b")
    GESETZ_NENNUNG = re.compile(r"\(g\d{1,2}\)|\bgesetz(e)?\s*\d|\bg\d{1,2}\b")

    @classmethod
    def _ist_hinweis(cls, low: str, m) -> str | None:
        """Ein Treffer ist nur ein Hinweis (kein Blocker), wenn die Zeile ihn erkennbar
        *erwähnt* statt *vorschlägt*: Negation in der Zeile, Frage, Gesetzesnennung, oder der
        Treffer steht in einem Backtick-Codebegriff."""
        if cls.NEGATION.search(low):
            return "negiert"
        if low.rstrip().endswith("?"):
            return "frage"
        if cls.GESETZ_NENNUNG.search(low):
            return "gesetzesnennung"
        if low[:m.start()].count("`") % 2 == 1:
            return "codebegriff"
        return None

    @staticmethod
    def _saetze(text: str):
        """Liefert (startzeile, satz) — Absätze werden entfaltet (Umbrüche → Leerzeichen), dann in
        Sätze geteilt. So gilt eine Negation für den ganzen Satz, nicht nur für eine Zeile."""
        out, buf, start = [], [], None
        einheit_start = re.compile(r"^\s*(\||[-*+]\s|\d{1,3}[.)]\s|#{1,6}\s)")  # Tabellenzeile, Listenpunkt, Überschrift
        for i, line in enumerate(text.splitlines(), 1):
            if line.strip():
                if einheit_start.match(line) and buf:
                    out.append((start, " ".join(buf))); buf, start = [], None
                if start is None:
                    start = i
                buf.append(line.strip())
            elif buf:
                out.append((start, " ".join(buf))); buf, start = [], None
        if buf:
            out.append((start, " ".join(buf)))
        saetze = []
        for start, absatz in out:
            absatz = re.sub(r"\[\[[^\]]*\]\]", "`link`", absatz)  # Wikilinks sind Namen, keine Vorschläge
            for s in re.split(r"(?<=[.!?])\s+(?=[A-ZÄÖÜ0-9„\"*|(-])", absatz):
                if s.strip():
                    saetze.append((start, s.strip()))
        return saetze

    @classmethod
    def lint(cls, text: str, mode: str):
        """Treffer gegen die Gesetze, satzweise. Erwähnungen (Negation im Satz, Frage,
        Gesetzesnennung, Codebegriff/Wikilink) werden zu Hinweisen — sonst würde jeder Satz, der
        ein Gesetz benennt, gegen es verstoßen. Was übrig bleibt, ist ein positiver Vorschlag im
        Sinne des Verstoßes und blockiert. Bekannte Grenzen: (a) Negation und Vorschlag im selben
        Satz („X ist verboten, deshalb schlage ich X vor“) und (b) ein Vorschlag als Frage
        („Warum nicht X einführen?“) werden als Hinweis gewertet — dafür liest Daniel den Entwurf,
        und die Checkliste bleibt Pflicht."""
        blocker, warnungen = [], []
        rules = LINTER_RULES + (LINTER_KONZEPT_ONLY if mode == "KONZEPT" else [])
        for start, satz in cls._saetze(text):
            low = satz.lower()
            for name, pats in rules:
                for p in pats:
                    m = re.search(p, low)
                    if not m:
                        continue
                    hit = {"gesetz": name, "muster": p, "zeile": start, "text": satz[:120]}
                    art = cls._ist_hinweis(low, m)
                    if art:
                        hit["hinweis_art"] = art
                        warnungen.append(hit)
                    else:
                        blocker.append(hit)
                    break  # ein Treffer je Gesetz und Satz reicht
        return blocker, warnungen

    @staticmethod
    def parse_checklist(spec: str):
        answers = {}
        for part in spec.split(","):
            part = part.strip()
            if not part:
                continue
            k, v = part.split(":", 1)
            answers[int(k)] = v.strip().lower()
        return answers

    def gate_07_entwurf(self, file: str, check: str, override: str = None):
        print("\n=== [TOR 07/14] ENTWURF — LINTER GEGEN DIE 15 GESETZE + CHECKLISTE ===")
        self.require("impuls_gezogen", "Tor 06 (Impuls)")
        path = Path(file)
        if not path.exists():
            raise FileNotFoundError(f"Entwurf nicht gefunden: {file}")
        text = path.read_text(encoding="utf-8", errors="replace")
        hits, warnungen = self.lint(text, self.data["mode"])
        for w in warnungen:
            print(f"  ~ {w['gesetz']:<40} Z.{w['zeile']} (negiert, nur Hinweis): {w['text']}")
        if hits and not override:
            for h in hits:
                print(f"  ✗ {h['gesetz']:<40} Z.{h['zeile']}: {h['text']}")
            raise RuntimeError(f"🛑 {len(hits)} Linter-Treffer. Entweder Entwurf ändern oder mit --override \"<Grund>\" bewusst festhalten.")
        answers = self.parse_checklist(check)
        fehl = []
        for i, need in CHECKLIST_REQUIRED.items():
            got = answers.get(i)
            if got != need:
                fehl.append(f"{i} ({CHECKLIST_TEXT[i]}) → erwartet '{need}', ist '{got}'")
        if fehl:
            raise RuntimeError("🛑 Checkliste nicht bestanden:\n  " + "\n  ".join(fehl))
        self.data["entwurf"] = {
            "pfad": str(path), "sha256": sha256_of(path), "zeichen": len(text),
            "linter_treffer": hits, "linter_hinweise": warnungen, "override_grund": override,
            "checkliste": answers, "checkliste_art": "Selbst-Attestierung, kein Beweis",
            "impuls_referenz": self.data["impuls"].get("zeit"),
        }
        self.data["gates"]["entwurf_geprueft"] = True
        self.data["permits"]["ENTWURF_PERMIT"] = True
        print(f"✓ Entwurf {path.name} ({len(text)} Zeichen) · Linter: {len(hits)} Blocker, {len(warnungen)} Hinweise" + (f" (Override: {override})" if override else "") + " · Checkliste 15/15 attestiert (kein Beweis)")
        print("🔓 ENTWURF_PERMIT — der Vorschlag darf Daniel vorgelegt werden.")
        self.transition_to(HarnessNode.FREIGABE, "Entwurf geprüft")

    # --- 08 FREIGABE ---
    def gate_08_freigabe(self, entscheidung: str, notiz: str = ""):
        print("\n=== [TOR 08/14] FREIGABE — DANIELS ENTSCHEIDUNG ===")
        self.require("entwurf_geprueft", "Tor 07 (Entwurf)")
        entscheidung = entscheidung.lower()
        if entscheidung not in ("angenommen", "geaendert", "abgelehnt"):
            raise ValueError("--entscheidung: angenommen | geaendert | abgelehnt")
        eintrag = {"entscheidung": entscheidung, "notiz": notiz, "zeit": time.strftime("%Y-%m-%d %H:%M:%S"),
                   "entwurf_sha256": self.data["entwurf"].get("sha256")}
        self.data.setdefault("freigabe_verlauf", []).append(eintrag)
        self.data["freigabe"] = eintrag
        print(f"✓ Entscheidung: {entscheidung}" + (f" — {notiz}" if notiz else ""))
        if entscheidung == "abgelehnt":
            self.data["gates"]["freigabe"] = True
            print("• Abgelehnt: Bogen geht direkt zum Abschluss (Bericht), keine Doku-Pflicht.")
            self.transition_to(HarnessNode.ABSCHLUSS, "abgelehnt")
            return
        if entscheidung == "geaendert":
            # Daniel will Änderungen: der Entwurf ist damit ungültig, es braucht einen neuen Durchlauf von Tor 07.
            self.data["gates"]["entwurf_geprueft"] = False
            self.data["permits"]["ENTWURF_PERMIT"] = False
            self.data["gates"]["freigabe"] = False
            print("• Geändert: zurück zu Tor 07 — neuen Entwurf mit `entwurf --file …` einreichen, dann erneut Freigabe.")
            self.transition_to(HarnessNode.ENTWURF, "Freigabe geaendert → neuer Entwurf")
            return
        self.data["gates"]["freigabe"] = True
        nxt = HarnessNode.BACKUP if self.data["mode"] == "BAU" else HarnessNode.DOKU
        self.transition_to(nxt, f"Freigabe {entscheidung}")

    # --- 09 BACKUP (BAU) ---
    def _repo_path(self, repo: str) -> Path:
        """Liefert den Kandidaten, der tatsächlich ein Git-Toplevel ist — Existenz allein reicht
        nicht (im Container existiert /root, das Repo liegt aber unter /vps_root)."""
        cands = WERKRAUM_CANDIDATES if repo == "werkraum" else ROOT_REPO_CANDIDATES
        for c in cands:
            p = Path(c)
            if not p.exists():
                continue
            res = subprocess.run(["git", "-C", str(p), "rev-parse", "--show-toplevel"], capture_output=True, text=True, timeout=15)
            if res.returncode == 0 and Path(res.stdout.strip()).resolve() == p.resolve():
                return p
        raise FileNotFoundError(f"Repo '{repo}' in dieser Sicht nicht als Git-Toplevel gefunden (Kandidaten: {cands})")

    def _backup_seit_lock(self, repo: str) -> dict:
        """Jüngster 'backup:'-Commit im Repo seit dem Modus-Lock. Sichern darf man jederzeit vor
        der eigentlichen Änderung; deshalb zählt ab Modus-Lock, nicht erst ab Freigabe."""
        rp = self._repo_path(repo)
        since = next((h["timestamp"] for h in self.data["history"] if h["to"] == HarnessNode.IMPULS.value), self.data["started"])
        log = subprocess.run(["git", "-C", str(rp), "log", "--since", since, "--format=%h|%ad|%s", "--date=format:%Y-%m-%d %H:%M:%S"], capture_output=True, text=True, timeout=30).stdout.strip().splitlines()
        backups = [l for l in log if l.split("|", 2)[-1].lower().startswith("backup")]
        if not backups:
            raise RuntimeError(f"🛑 Kein 'backup:'-Commit in {rp} seit Modus-Lock ({since}). Gesetz 13: erst sichern, dann ändern.")
        h, ad, s = backups[0].split("|", 2)
        head = subprocess.run(["git", "-C", str(rp), "rev-parse", "--short", "HEAD"], capture_output=True, text=True, timeout=15).stdout.strip()
        return {"repo": repo, "pfad": str(rp), "hash": h, "datum": ad, "betreff": s, "head_bei_pruefung": head, "seit": since}

    def gate_09_backup(self, repo: str):
        print("\n=== [TOR 09/14] BACKUP-COMMIT NACHWEISEN ===")
        self.require("freigabe", "Tor 08 (Freigabe)")
        if self.data["mode"] != "BAU":
            raise RuntimeError("🛑 Backup-Knoten nur im BAU-Modus. Im KONZEPT-Modus prüft Tor 12 (Doku) das Backup selbst.")
        self.data["backup"] = self._backup_seit_lock(repo)
        h, ad, s, rp = (self.data["backup"][k] for k in ("hash", "datum", "betreff", "pfad"))
        self.data["gates"]["backup"] = True
        print(f"✓ Backup {h} ({ad}) in {rp}: {s}")
        self.transition_to(HarnessNode.MUTATION, "Backup nachgewiesen")

    # --- 10 MUTATION (BAU) ---
    def gate_10_mutation(self, pfade, beschreibung: str, beide_fassungen: str):
        print("\n=== [TOR 10/14] GENAU EINE MUTATION ===")
        self.require("backup", "Tor 09 (Backup)")
        if not pfade or not beschreibung:
            raise RuntimeError("🛑 --pfad und --beschreibung sind Pflicht: eine benannte, begrenzte Änderung.")
        if beide_fassungen not in ("ja", "nein", "nicht-betroffen"):
            raise ValueError("--beide-fassungen: ja | nein | nicht-betroffen (Standalone + Surface, Skill §2.1)")
        if beide_fassungen == "nein":
            raise RuntimeError("🛑 Änderung betrifft beide Fassungen, aber nur eine wurde angefasst. Erst nachziehen.")
        fehlend = [p for p in pfade if not Path(p).exists()]
        if fehlend:
            raise FileNotFoundError(f"Pfade existieren nicht: {fehlend}")
        # Diff-Beweis gegen den Backup-Commit: Pfade im Repo müssen dort wirklich geändert sein.
        rp = Path(self.data["backup"]["pfad"]).resolve()
        geaendert = subprocess.run(["git", "-C", str(rp), "diff", "--name-only", self.data["backup"]["hash"]], capture_output=True, text=True, timeout=30).stdout.split()
        beweis, ohne_beweis, unveraendert = {}, [], []
        for p in pfade:
            rel = None
            try:
                rel = str(Path(p).resolve().relative_to(rp))
            except ValueError:
                pass
            if rel is None:
                ohne_beweis.append(p)
            elif rel in geaendert:
                beweis[p] = rel
            else:
                unveraendert.append(p)
        if unveraendert:
            raise RuntimeError(f"🛑 Diese Pfade liegen im Repo, sind aber seit Backup {self.data['backup']['hash']} unverändert: {unveraendert}")
        if ohne_beweis:
            print(f"⚠ Außerhalb des Repos, nur Hash festgehalten (kein Diff-Beweis): {ohne_beweis}")
        self.data["mutation"] = {"pfade": pfade, "beschreibung": beschreibung, "beide_fassungen": beide_fassungen,
                                 "zeit": time.strftime("%Y-%m-%d %H:%M:%S"), "sha256": {p: sha256_of(Path(p)) for p in pfade},
                                 "diff_beweis": beweis, "ohne_diff_beweis": ohne_beweis}
        self.data["gates"]["mutation"] = True
        self.data["permits"]["MUTATION_PERMIT"] = True
        print(f"✓ Mutation erfasst: {beschreibung} · {len(pfade)} Datei(en)")
        self.transition_to(HarnessNode.EVIDENZ_NACHHER, "Mutation erfasst")

    # --- 11 EVIDENZ NACHHER (BAU) ---
    def gate_11_evidenz_nachher(self):
        print("\n=== [TOR 11/14] EVIDENZ NACHHER — DELTA ===")
        self.require("mutation", "Tor 10 (Mutation)")
        record, code = self._run_verify()
        vorher = {"fails": set(self.data["verify"]["fails"]), "unknown": set(self.data["verify"]["unknown"])}
        nachher_f = {t["token"] for t in record["tore"] if t["status"] == "FAIL"}
        nachher_u = {t["token"] for t in record["tore"] if t["status"] == "UNKNOWN"}
        delta = {
            "behoben": sorted(vorher["fails"] - nachher_f),
            "neu_fail": sorted(nachher_f - vorher["fails"]),
            "weiter_fail": sorted(nachher_f & vorher["fails"]),
        }
        self.data["evidenz_nachher"] = {"gesamt": record["gesamt"], "exit": code, "evidenz": record.get("evidenz_datei"), "delta": delta}
        self.data["gates"]["evidenz_nachher"] = True
        print(f"✓ Nachher: {record['gesamt']} · behoben {delta['behoben']} · neu FAIL {delta['neu_fail']} · weiter FAIL {delta['weiter_fail']}")
        if delta["neu_fail"]:
            print("⚠ Neue Fails durch die Mutation — vor Doku/Commit klären.")
        self.transition_to(HarnessNode.DOKU, "Evidenz nachher")

    # --- 12 DOKU ---
    def gate_12_doku(self, pfad: str = None, protokoll_vorschlag: str = None, protokoll_freigegeben: str = None, keine_doku: str = None, go: str = None):
        print("\n=== [TOR 12/14] DOKU PRÜFEN ===")
        if self.data["mode"] == "BAU":
            self.require("evidenz_nachher", "Tor 11 (Evidenz nachher)")
        else:
            self.require("freigabe", "Tor 08 (Freigabe)")
        result = {}
        if (pfad or protokoll_freigegeben) and self.data["mode"] != "BAU":
            # Auch ein Konzept-Bogen schreibt Dateien — die Backup-Pflicht gilt für jede Änderung.
            result["backup_werkraum"] = self._backup_seit_lock("werkraum")
            print(f"✓ Backup vor Doku nachgewiesen: {result['backup_werkraum']['hash']} ({result['backup_werkraum']['datum']})")
        if pfad:
            p = Path(pfad)
            if not p.exists():
                raise FileNotFoundError(f"Doku nicht gefunden: {pfad}")
            text = p.read_text(encoding="utf-8", errors="replace")
            title = text.splitlines()[0] if text else ""
            probleme = []
            if DOC_TITLE_TAG not in title:
                probleme.append(f"Titel ohne '{DOC_TITLE_TAG}'")
            if not re.search(r"^status:", text, re.M):
                probleme.append("Frontmatter ohne 'status:'")
            if not re.search(r"^#{1,6}\s.*\boffen\b", text, re.I | re.M):
                probleme.append("keine Überschrift mit 'offen' (Pflichtabschnitt „Was ausdrücklich offen bleibt“)")
            m = re.match(r"(\d+)_", p.name)
            if m:
                same = [q.name for q in p.parent.glob(f"{m.group(1)}_*.md")]
                if len(same) > 1:
                    probleme.append(f"Nummer {m.group(1)} mehrfach belegt: {same}")
            if probleme:
                raise RuntimeError("🛑 Doku-Prüfung: " + "; ".join(probleme))
            result["systemdoku"] = {"pfad": str(p), "sha256": sha256_of(p), "titel": title}
            print(f"✓ Systemdoku ok: {p.name}")
        if protokoll_vorschlag:
            result["protokoll_vorschlag"] = {"datei": protokoll_vorschlag, "status": "nur Vorschlag, nicht eingetragen"}
            print(f"• Wissensprotokoll-Vorschlag festgehalten für {protokoll_vorschlag} — Eintrag erst nach Freigabe.")
        if protokoll_freigegeben:
            # Die Freigabe des Entwurfs (Tor 08) ist NICHT die Freigabe des Protokoll-Wortlauts.
            # Wissensprotokolle werden nie autonom befüllt: es braucht eine eigene Zustimmung zum Eintragstext.
            if self.data["freigabe"].get("entscheidung") != "angenommen":
                raise RuntimeError("🛑 Wissensprotokoll-Eintrag braucht Freigabe 'angenommen' (Tor 08).")
            if not go or len(go.strip()) < 2:
                raise RuntimeError("🛑 --go \"<Wortlaut von Daniels Zustimmung zum Eintragstext>\" fehlt. Entwurfs-Freigabe reicht nicht.")
            p = Path(protokoll_freigegeben)
            if not p.exists() or PROTOKOLL_LABEL not in p.read_text(encoding="utf-8", errors="replace"):
                raise RuntimeError(f"🛑 {protokoll_freigegeben} enthält kein Label '{PROTOKOLL_LABEL}'.")
            result["protokoll_eingetragen"] = {"datei": str(p), "sha256": sha256_of(p), "zustimmung_wortlaut": go, "zeit": time.strftime("%Y-%m-%d %H:%M:%S")}
            print(f"✓ Wissensprotokoll eingetragen, Zustimmung festgehalten („{go}“): {p.name}")
        if keine_doku:
            if len(keine_doku.strip()) < 12:
                raise RuntimeError("🛑 --keine-doku braucht einen echten Grund (mind. 12 Zeichen).")
            result["keine_doku"] = {"grund": keine_doku}
            print(f"• Keine Systemdoku für diesen Bogen, Grund festgehalten: {keine_doku}")
        if not result:
            raise RuntimeError("🛑 Nichts angegeben: --pfad, --protokoll-vorschlag, --protokoll-freigegeben oder --keine-doku GRUND.")
        self.data["doku"] = result
        self.data["gates"]["doku"] = True
        self.transition_to(HarnessNode.COMMIT, "Doku geprüft")

    # --- 13 COMMIT ---
    def gate_13_commit(self, hash_: str, repo: str):
        print("\n=== [TOR 13/14] COMMIT NACHWEISEN ===")
        self.require("doku", "Tor 12 (Doku)")
        rp = self._repo_path(repo)
        # Erst: was erwartet dieser Bogen überhaupt in diesem Repo? Sonst beweist ein Commit nichts.
        erwartet_alle = self._erwartete_pfade()
        erwartet_hier = [rel for (r, rel) in erwartet_alle if r == repo]
        if not erwartet_hier:
            raise RuntimeError(f"🛑 Für Repo '{repo}' erwartet dieser Bogen keine Pfade — Commit dort beweist nichts. Erwartet: {erwartet_alle}")
        res = subprocess.run(["git", "-C", str(rp), "show", "--stat", "--format=%H|%ad|%s", "--date=format:%Y-%m-%d %H:%M:%S", hash_], capture_output=True, text=True, timeout=30)
        if res.returncode != 0:
            raise RuntimeError(f"🛑 Commit {hash_} nicht in {rp} ({repo}): {res.stderr.strip().splitlines()[0][:160] if res.stderr.strip() else 'unbekannt'}")
        head, *stat = res.stdout.strip().splitlines()
        full, ad, s = head.split("|", 2)
        dateien = subprocess.run(["git", "-C", str(rp), "show", "--name-only", "--format=", hash_], capture_output=True, text=True, timeout=30).stdout.split()
        fehlt = [e for e in erwartet_hier if e not in dateien]
        if fehlt:
            raise RuntimeError(f"🛑 Commit {full[:12]} in {repo} enthält nicht: {fehlt}. Erwartet wurden die Pfade dieses Bogens in diesem Repo.")
        eintrag = {"repo": repo, "hash": full[:12], "datum": ad, "betreff": s, "dateien": dateien[:40], "abgedeckt": erwartet_hier}
        self.data.setdefault("commits", []).append(eintrag)
        self.data["commit"] = eintrag
        abgedeckt = {(c["repo"], p) for c in self.data["commits"] for p in c["abgedeckt"]}
        offen = [x for x in erwartet_alle if x not in abgedeckt]
        self.data["gates"]["commit"] = not offen
        print(f"✓ Commit {full[:12]} ({ad}) in {rp}: {s} · deckt {len(erwartet_hier)} Pfade in {repo}")
        if offen:
            print(f"• Noch nicht committet (anderes Repo): {offen} — `commit --repo …` erneut aufrufen.")
            self.save_state()
            return
        self.transition_to(HarnessNode.ABSCHLUSS, "alle Commits nachgewiesen")

    def _erwartete_pfade(self):
        """Alle Pfade, die dieser Bogen verändert/dokumentiert hat, als (repo, relpfad)."""
        out = []
        kandidaten = list(self.data.get("mutation", {}).get("pfade", []))
        for k in ("systemdoku", "protokoll_eingetragen"):
            p = self.data.get("doku", {}).get(k, {})
            p = p.get("pfad") or p.get("datei")
            if p:
                kandidaten.append(p)
        for p in kandidaten:
            ap = Path(p).resolve()
            # werkraum zuerst: es liegt selbst unter /root, der spezifischere Treffer gewinnt.
            for repo in ("werkraum", "root"):
                try:
                    rel = str(ap.relative_to(self._repo_path(repo).resolve()))
                except (ValueError, FileNotFoundError):
                    continue
                if (repo, rel) not in out:
                    out.append((repo, rel))
                break
        return out
        self.transition_to(HarnessNode.ABSCHLUSS, "Commit nachgewiesen")

    # --- 14 ABSCHLUSS ---
    def gate_14_abschluss(self):
        print("\n=== [TOR 14/14] ABSCHLUSS & HALT ===")
        if self.data["freigabe"].get("entscheidung") != "abgelehnt":
            self.require("commit", "Tor 13 (Commit)")
        d = self.data
        d["gates"]["abgeschlossen"] = True
        stamp = time.strftime("%Y%m%dT%H%M%S")
        report = self.workspace / f"{stamp}_harness_{self.session}.md"
        lines = [
            f"# KompOase 8900 — Harness-Bericht `{self.session}`",
            "",
            f"- Gestartet: {d['started']} · Modus: {d['mode']} · Auftrag: {d['auftrag'] or '—'}",
            f"- Skill: `{d['skill'].get('pfad')}` sha {d['skill'].get('sha256')}",
            f"- Dokus 69–75 gelesen: {d['dokus'].get('gelesen_am')}",
            f"- Verify vorher: **{d['verify'].get('gesamt')}** · Fails {d['verify'].get('fails')} · Evidenz `{d['verify'].get('evidenz')}`",
            f"- Impuls: Frage „{d['impuls'].get('frage')}“ · offen: {d['impuls'].get('offen')} · Gesetz im Blick: {d['impuls'].get('gesetz_im_blick')} · Feed n={d['impuls'].get('feed_n')}",
            f"- Entwurf: `{d['entwurf'].get('pfad')}` · Linter {len(d['entwurf'].get('linter_treffer', []))} Treffer" + (f" · Override: {d['entwurf'].get('override_grund')}" if d['entwurf'].get('override_grund') else ""),
            f"- Freigabe: **{d['freigabe'].get('entscheidung')}** {d['freigabe'].get('notiz') or ''}",
        ]
        if d["mode"] == "BAU":
            lines += [
                f"- Backup: {d['backup'].get('hash')} in {d['backup'].get('repo')}",
                f"- Mutation: {d['mutation'].get('beschreibung')} · {d['mutation'].get('pfade')}",
                f"- Verify nachher: **{d['evidenz_nachher'].get('gesamt')}** · Delta {d['evidenz_nachher'].get('delta')} · Evidenz `{d['evidenz_nachher'].get('evidenz')}`",
            ]
        commits = d.get("commits") or ([d["commit"]] if d.get("commit") else [])
        lines += [
            f"- Doku: {json.dumps(d['doku'], ensure_ascii=False) if d['doku'] else '—'}",
            "- Commits: " + (" · ".join(f"{c['hash']} ({c['repo']}, deckt {len(c.get('abgedeckt', []))})" for c in commits) if commits else "—"),
            "",
            "## Tore",
        ] + [f"- {k}: {'✓' if v else '✗'}" for k, v in d["gates"].items()] + [
            "",
            "**HALT.** Der nächste Bogen beginnt erst nach Daniels Feedback zu diesem Bericht.",
        ]
        report.write_text("\n".join(lines) + "\n", encoding="utf-8")
        d["bericht"] = str(report)
        self.transition_to(HarnessNode.ABSCHLUSS, "Bogen abgeschlossen")
        print(f"✓ Bericht: {report}")
        print("🛑 HALT — nächster Bogen erst nach Feedback.")

    # --- externe Sperre ---
    @classmethod
    def verify_permit(cls, workspace_dir, session, permit: str):
        state_file = Path(workspace_dir) / f"harness_{session}_state.json"
        if not state_file.exists():
            raise RuntimeError(f"🛑 HARNESS-SPERRE: kein Bogen '{session}' in {workspace_dir}. Erst: init → read-skill → read-dokus → verify → lock-mode → impuls → entwurf.")
        data = json.loads(state_file.read_text(encoding="utf-8"))
        if not data.get("permits", {}).get(permit):
            raise RuntimeError(f"🛑 HARNESS-SPERRE: {permit} nicht erteilt (aktueller Knoten {data.get('current_node')}).")
        return True

    def status(self):
        d = self.data
        print(f"Bogen: {d['session']} · gestartet {d['started']} · Knoten: {d['current_node']} · Modus: {d['mode'] or '—'}")
        print("Tore:")
        for k, v in d["gates"].items():
            print(f"  - {k}: {'✓' if v else '✗'}")
        print("Permits: " + ", ".join(f"{k}={'✓' if v else '✗'}" for k, v in d["permits"].items()))
        if d.get("verify"):
            print(f"Verify: {d['verify'].get('gesamt')} · Fails {d['verify'].get('fails')}")
        if d.get("freigabe_verlauf"):
            print("Freigaben: " + " → ".join(f["entscheidung"] for f in d["freigabe_verlauf"]))
        if d.get("commits"):
            print("Commits: " + ", ".join(f"{c['hash']}@{c['repo']}" for c in d["commits"]))


def default_workspace():
    wr = first_existing(WERKRAUM_CANDIDATES)
    return str(wr / "_claude" / "berichte" / "kompoase-8900") if wr else os.getcwd()


def main():
    ap = argparse.ArgumentParser(description="KompOase-8900 Harness — kreativleitend, prüfend, unüberspringbar")
    ap.add_argument("--workspace", default=default_workspace())
    ap.add_argument("--session", default=time.strftime("%Y-%m-%d"))
    sub = ap.add_subparsers(dest="command", required=True)

    sub.add_parser("status")
    sub.add_parser("init")
    sub.add_parser("read-skill")
    p = sub.add_parser("read-dokus"); p.add_argument("--bestaetigt", action="store_true")
    sub.add_parser("verify")
    p = sub.add_parser("lock-mode"); p.add_argument("mode"); p.add_argument("--auftrag", default=None)
    p = sub.add_parser("impuls"); p.add_argument("--n", type=int, default=3); p.add_argument("--seed", type=int, default=None)
    p = sub.add_parser("entwurf"); p.add_argument("--file", required=True); p.add_argument("--check", required=True); p.add_argument("--override", default=None)
    p = sub.add_parser("freigabe"); p.add_argument("--entscheidung", required=True); p.add_argument("--notiz", default="")
    p = sub.add_parser("backup"); p.add_argument("--repo", choices=["werkraum", "root"], required=True)
    p = sub.add_parser("mutation"); p.add_argument("--pfad", nargs="+", required=True); p.add_argument("--beschreibung", required=True); p.add_argument("--beide-fassungen", dest="beide", choices=["ja", "nein", "nicht-betroffen"], required=True)
    sub.add_parser("evidenz-nachher")
    p = sub.add_parser("doku"); p.add_argument("--pfad", default=None); p.add_argument("--protokoll-vorschlag", default=None); p.add_argument("--protokoll-freigegeben", default=None); p.add_argument("--keine-doku", default=None); p.add_argument("--go", default=None, help="Wortlaut von Daniels Zustimmung zum Protokoll-Eintragstext")
    p = sub.add_parser("commit"); p.add_argument("--hash", required=True); p.add_argument("--repo", choices=["werkraum", "root"], required=True)
    sub.add_parser("abschluss")
    p = sub.add_parser("check-permit"); p.add_argument("--permit", choices=["BAU_PERMIT", "ENTWURF_PERMIT", "MUTATION_PERMIT"], required=True)
    p = sub.add_parser("lint"); p.add_argument("--file", required=True); p.add_argument("--mode", default="KONZEPT")
    sub.add_parser("checkliste")

    args = ap.parse_args()

    if args.command == "check-permit":
        try:
            KompoaseHarness.verify_permit(args.workspace, args.session, args.permit)
        except RuntimeError as e:
            print(str(e))
            sys.exit(2)
        print(f"✓ {args.permit} erteilt.")
        return
    if args.command == "lint":
        hits, warnungen = KompoaseHarness.lint(Path(args.file).read_text(encoding="utf-8", errors="replace"), args.mode.upper())
        for w in warnungen:
            print(f"~ {w['gesetz']:<40} Z.{w['zeile']} (negiert): {w['text']}")
        for h in hits:
            print(f"✗ {h['gesetz']:<40} Z.{h['zeile']}: {h['text']}")
        print(f"{len(hits)} Blocker, {len(warnungen)} Hinweise")
        sys.exit(1 if hits else 0)
    if args.command == "checkliste":
        for i, t in CHECKLIST_TEXT.items():
            print(f"{i:>2}. [{CHECKLIST_REQUIRED[i]:<4}] {t}")
        return

    if args.command == "init":
        state = Path(args.workspace) / f"harness_{args.session}_state.json"
        if state.exists():
            d = json.loads(state.read_text(encoding="utf-8"))
            if not d.get("gates", {}).get("abgeschlossen"):
                print(f"🛑 Bogen '{args.session}' läuft noch (Knoten {d.get('current_node')}). Entweder fortsetzen oder --session <neuer Name> wählen.")
                sys.exit(2)
            print(f"• Bogen '{args.session}' ist abgeschlossen; für einen neuen Bogen --session <neuer Name> wählen.")
            sys.exit(2)

    try:
        h = KompoaseHarness(args.workspace, args.session)
        if args.command == "status": h.status()
        elif args.command == "init": print(f"✓ Bogen '{h.session}' angelegt: {h.state_file}")
        elif args.command == "read-skill": h.gate_02_read_skill()
        elif args.command == "read-dokus": h.gate_03_read_dokus(args.bestaetigt)
        elif args.command == "verify": h.gate_04_verify()
        elif args.command == "lock-mode": h.gate_05_lock_mode(args.mode, args.auftrag)
        elif args.command == "impuls": h.gate_06_impuls(args.n, args.seed)
        elif args.command == "entwurf": h.gate_07_entwurf(args.file, args.check, args.override)
        elif args.command == "freigabe": h.gate_08_freigabe(args.entscheidung, args.notiz)
        elif args.command == "backup": h.gate_09_backup(args.repo)
        elif args.command == "mutation": h.gate_10_mutation(args.pfad, args.beschreibung, args.beide)
        elif args.command == "evidenz-nachher": h.gate_11_evidenz_nachher()
        elif args.command == "doku": h.gate_12_doku(args.pfad, args.protokoll_vorschlag, args.protokoll_freigegeben, args.keine_doku, args.go)
        elif args.command == "commit": h.gate_13_commit(args.hash, args.repo)
        elif args.command == "abschluss": h.gate_14_abschluss()
    except (RuntimeError, ValueError, FileNotFoundError) as e:
        print(str(e))
        sys.exit(2)


if __name__ == "__main__":
    main()
