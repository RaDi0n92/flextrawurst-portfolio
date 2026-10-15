"""Seeds (G15): aus einer Erfahrung (Kapsel, G13) wird ein Vorschlag, der geprüft, freigegeben, an ein Ziel ausgeliefert, wiedergefunden und **zurückgenommen** werden kann.

Ein Seed hat eine Herkunft (Kapseln), ein Ziel (`zieltyp`), Empfänger und eine Version. Lebenslauf: `vorschlag` → `freigegeben` → `aktiv` → `zurueckgezogen`; jede Änderung ist eine **neue Version**, nichts wird überschrieben.

Zieltypen:
* `ablauf`   — ein ausführbarer Handlungsgraph (G12) wird als neue Version gespeichert.
* `kontext`  — Text wird in den laufenden Kontext gewählter Agenten gelegt (wie eine Nachricht); zurücknehmen kann man nur das Wirken auf den Seed selbst, gesagt ist gesagt.
* `memory`, `dokument`, `skill` — ein **markierter Block** wird in eine Datei eingefügt (nie die Datei ersetzt, nie fremder Inhalt verändert).
* `loop`, `goal` — Wiederholung mit Budget (siehe `loops.py`); hier nur als Seed-Art geführt.

**Zielumfang:** Dateien werden nur angefasst, wenn Daniel den Pfad in `freigaben.json` ausdrücklich genannt hat (Datei oder Ordner, je Art). Ohne Eintrag geschieht nichts. Jede Auslieferung an eine Datei braucht zusätzlich Daniels Ja im Einzelfall.
**Rücknahme:** Vor dem ersten Einfügen wird das Original gesichert; `zurueckziehen` entfernt genau den Block des Seeds. Hat jemand den Block inzwischen verändert, wird **nichts** entfernt und das gesagt. Originale und fremde Dateien bleiben unberührt.
**Wissen ist Text:** Ein Seed ändert nie Modellgewichte; er legt Text, Graphen oder Aufträge ab. Das steht in jedem Export.
"""

from __future__ import annotations

import hashlib
import json
import re
import threading
import time
import uuid
from pathlib import Path

ZIELTYPEN = ("ablauf", "kontext", "memory", "dokument", "skill", "loop", "goal")
DATEI_ZIELE = ("memory", "dokument", "skill")
STATI = ("vorschlag", "freigegeben", "aktiv", "zurueckgezogen")
FREIHEITEN = ("vorschlag", "nach_freigabe", "selbststaendig")  # was ein Agent ohne Daniels Einzel-Ja darf: nur vorschlagen / ausliefern nach Ja / (nicht-Datei) selbst ausliefern
MAX_INHALT = 20_000
MAX_TITEL = 120
MAX_VERSIONEN = 100
ID = re.compile(r"^s-[0-9a-f]{8}$")
MARKE_AN = "<!-- seed:{id} v{v} -->"
MARKE_AUS = "<!-- /seed:{id} -->"


class SeedFehler(ValueError):
    pass


def _hash(daten: bytes) -> str:
    return hashlib.sha256(daten).hexdigest()


class Freigaben:
    """Daniels ausdrückliche Zielumfänge und das Freiheitsprofil, aus einer Datei, die nur er pflegt. Fehlt sie oder ist sie kaputt, ist **nichts** erlaubt und das Profil ist `nach_freigabe`."""

    def __init__(self, pfad: Path | None):
        self.pfad = Path(pfad) if pfad else None

    def _lesen(self) -> dict:
        try:
            d = json.loads(self.pfad.read_text(encoding="utf-8")) if self.pfad and self.pfad.exists() else {}
            return d if isinstance(d, dict) else {}
        except (OSError, ValueError):
            return {}

    def freiheit(self) -> str:
        f = self._lesen().get("freiheit")
        return f if f in FREIHEITEN else "nach_freigabe"

    def ziele(self) -> list[tuple[Path, frozenset]]:
        ergebnis = []
        for z in self._lesen().get("ziele", []):
            try:
                pfad = Path(z["pfad"])
                arten = frozenset(a for a in z.get("arten", []) if a in DATEI_ZIELE)
            except (KeyError, TypeError):
                continue
            if pfad.is_absolute() and arten:
                ergebnis.append((pfad.resolve(), arten))
        return ergebnis

    def erlaubt(self, pfad: str, art: str) -> bool:
        try:
            p = Path(pfad)
            if not p.is_absolute() or ".." in p.parts:
                return False
            p = p.resolve()
        except (OSError, ValueError):
            return False
        for wurzel, arten in self.ziele():
            if art in arten and (p == wurzel or wurzel in p.parents):
                return True
        return False


class SeedStore:
    def __init__(self, ordner: Path, freigaben: Freigaben | None = None, jetzt_ms=lambda: int(time.time() * 1000)):
        self.ordner = Path(ordner)
        self.freigaben = freigaben or Freigaben(self.ordner / "freigaben.json")
        self._jetzt = jetzt_ms
        self._sperre = threading.RLock()
        self._seeds: dict[str, list[dict]] = {}  # id -> Versionen (älteste zuerst)
        self.ordner.mkdir(parents=True, exist_ok=True)
        self._laden()

    # ---- Datei ---------------------------------------------------------------------------------------------------------------------
    def _datei(self) -> Path:
        return self.ordner / "seeds.json"

    def _laden(self) -> None:
        try:
            roh = json.loads(self._datei().read_text(encoding="utf-8"))
            for sid, versionen in roh.get("seeds", {}).items():
                if ID.fullmatch(sid) and isinstance(versionen, list) and versionen and all(isinstance(v, dict) and v.get("status") in STATI for v in versionen):
                    self._seeds[sid] = versionen
        except (OSError, ValueError, AttributeError):
            pass

    def _speichern(self) -> None:
        temp = self._datei().with_suffix(".tmp")
        temp.write_text(json.dumps({"version": 1, "seeds": self._seeds}, ensure_ascii=False), encoding="utf-8")
        temp.replace(self._datei())

    # ---- Vorschlagen und Versionieren --------------------------------------------------------------------------------------------
    def vorschlagen(self, *, von: str, zieltyp: str, titel: str, inhalt, empfaenger: list[str] | None = None, ziel_pfad: str | None = None, kapseln: list[str] | None = None, budget: dict | None = None,
                    seed_id: str | None = None) -> dict:
        """Ein neuer Seed oder (mit `seed_id`) eine neue Version eines bestehenden. Prüft nur die Form; ausgeliefert wird erst nach Freigabe."""
        if zieltyp not in ZIELTYPEN:
            raise SeedFehler("zieltyp_unbekannt")
        if not isinstance(titel, str) or not 1 <= len(titel.strip()) <= MAX_TITEL:
            raise SeedFehler("titel_ungueltig")
        if zieltyp == "ablauf":
            if not isinstance(inhalt, dict):
                raise SeedFehler("inhalt_ungueltig")
            if len(json.dumps(inhalt)) > MAX_INHALT:
                raise SeedFehler("inhalt_zu_gross")
        elif not isinstance(inhalt, str) or not inhalt.strip() or len(inhalt) > MAX_INHALT or "\x00" in inhalt:
            raise SeedFehler("inhalt_ungueltig")
        if zieltyp in DATEI_ZIELE and (not isinstance(ziel_pfad, str) or not ziel_pfad):
            raise SeedFehler("ziel_pfad_fehlt")
        if zieltyp == "kontext" and not empfaenger:
            raise SeedFehler("empfaenger_fehlen")
        if zieltyp in ("loop", "goal") and not (isinstance(budget, dict) and budget):
            raise SeedFehler("budget_fehlt")
        if any(not isinstance(e, str) or not e for e in empfaenger or []) or len(empfaenger or []) > 8:
            raise SeedFehler("empfaenger_ungueltig")
        if kapseln is not None and (not isinstance(kapseln, list) or any(not isinstance(k, str) or not re.fullmatch(r"k-[A-Za-z0-9-]{1,40}", k) for k in kapseln)):
            raise SeedFehler("kapseln_ungueltig")
        with self._sperre:
            if seed_id is not None:
                if seed_id not in self._seeds:
                    raise SeedFehler("seed_unbekannt")
                sid, nr = seed_id, len(self._seeds[seed_id]) + 1
                if nr > MAX_VERSIONEN:
                    raise SeedFehler("zu_viele_versionen")
            else:
                sid, nr = f"s-{uuid.uuid4().hex[:8]}", 1
            v = {"id": sid, "version": nr, "zieltyp": zieltyp, "titel": titel.strip(), "inhalt": inhalt, "empfaenger": list(empfaenger or []), "ziel_pfad": ziel_pfad, "kapseln": list(kapseln or []),
                 "budget": budget, "von": str(von)[:60], "erzeugt_ms": self._jetzt(), "status": "vorschlag", "ereignisse": [{"zeit_ms": self._jetzt(), "was": "vorgeschlagen", "von": str(von)[:60]}]}
            self._seeds.setdefault(sid, []).append(v)
            self._speichern()
        return self._kopie(v)

    # ---- Ansehen ---------------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def _kopie(v: dict) -> dict:
        return json.loads(json.dumps(v))

    def hole(self, seed_id: str, version: int | None = None) -> dict | None:
        with self._sperre:
            vs = self._seeds.get(seed_id)
            if not vs:
                return None
            v = vs[-1] if version is None else next((x for x in vs if x["version"] == version), None)
            return self._kopie(v) if v else None

    def liste(self, status: str | None = None) -> list[dict]:
        with self._sperre:
            return [{"id": sid, "version": vs[-1]["version"], "versionen": len(vs), "titel": vs[-1]["titel"], "zieltyp": vs[-1]["zieltyp"], "status": vs[-1]["status"], "von": vs[-1]["von"]}
                    for sid, vs in self._seeds.items() if status is None or vs[-1]["status"] == status]

    def pruefen(self, seed_id: str, version: int | None = None) -> dict:
        """Was würde die Auslieferung tun, und was steht ihr im Weg? Ändert nichts."""
        v = self.hole(seed_id, version)
        if v is None:
            raise SeedFehler("seed_unbekannt")
        hindernisse = []
        if v["zieltyp"] in DATEI_ZIELE:
            if not self.freigaben.erlaubt(v["ziel_pfad"], v["zieltyp"]):
                hindernisse.append("ziel_nicht_freigegeben")
        wirkung = {"ablauf": "speichert den Graphen als neue Version", "kontext": f"legt den Text in den Kontext von {', '.join(v['empfaenger']) or '-'}", "loop": "startet eine Wiederholung mit Budget",
                   "goal": "startet ein Ziel mit Budget und Abschlussbedingung"}.get(v["zieltyp"], f"fügt einen markierten Block in {v['ziel_pfad']} ein (Original wird gesichert)")
        return {"id": seed_id, "version": v["version"], "zieltyp": v["zieltyp"], "wirkung": wirkung, "hindernisse": hindernisse, "braucht_daniel": v["zieltyp"] in DATEI_ZIELE or self.freigaben.freiheit() != "selbststaendig",
                "freiheit": self.freigaben.freiheit(), "wissen": "Text, kein veränderter Modellgewicht"}

    def _ereignis(self, v: dict, was: str, von: str, **extra) -> None:
        v["ereignisse"].append({"zeit_ms": self._jetzt(), "was": was, "von": str(von)[:60], **extra})

    def _setze(self, seed_id: str, version: int | None, erlaubt: tuple, neu: str, von: str, **extra) -> dict:
        with self._sperre:
            vs = self._seeds.get(seed_id)
            if not vs:
                raise SeedFehler("seed_unbekannt")
            v = vs[-1] if version is None else next((x for x in vs if x["version"] == version), None)
            if v is None:
                raise SeedFehler("version_unbekannt")
            if v["status"] not in erlaubt:
                raise SeedFehler(f"status_{v['status']}_erlaubt_{neu}_nicht")
            v["status"] = neu
            self._ereignis(v, neu, von, **extra)
            self._speichern()
            return self._kopie(v)

    def freigeben(self, seed_id: str, von: str, version: int | None = None) -> dict:
        return self._setze(seed_id, version, ("vorschlag",), "freigegeben", von)

    # ---- Ausliefern an Dateien (markierter Block) ------------------------------------------------------------------------------------------
    def _backup_pfad(self, v: dict) -> Path:
        return self.ordner / "backups" / f"{v['id']}-v{v['version']}"

    def datei_einfuegen(self, seed_id: str, version: int | None, von: str) -> dict:
        """Den Seed als Block in seine Zieldatei legen. Nur mit Freigabe des Zielumfangs; das Original wird vorher gesichert."""
        v = self.hole(seed_id, version)
        if v is None:
            raise SeedFehler("seed_unbekannt")
        if v["zieltyp"] not in DATEI_ZIELE:
            raise SeedFehler("kein_datei_seed")
        if v["status"] != "freigegeben":
            raise SeedFehler("nicht_freigegeben")
        if not self.freigaben.erlaubt(v["ziel_pfad"], v["zieltyp"]):
            raise SeedFehler("ziel_nicht_freigegeben")
        ziel = Path(v["ziel_pfad"]).resolve()
        existierte = ziel.exists()
        alt = ziel.read_bytes() if existierte else b""
        if MARKE_AN.format(id=v["id"], v=v["version"]).encode() in alt or f"<!-- seed:{v['id']} ".encode() in alt:
            raise SeedFehler("block_schon_da")
        block = f"\n{MARKE_AN.format(id=v['id'], v=v['version'])}\n{v['inhalt'].strip()}\n{MARKE_AUS.format(id=v['id'])}\n"
        neu = alt + block.encode("utf-8")
        sicher = self._backup_pfad(v)
        sicher.mkdir(parents=True, exist_ok=True)
        (sicher / "original.bin").write_bytes(alt)
        (sicher / "meta.json").write_text(json.dumps({"ziel": str(ziel), "existierte": existierte, "original_sha256": _hash(alt), "nach_sha256": _hash(neu)}), encoding="utf-8")
        ziel.parent.mkdir(parents=True, exist_ok=True)
        temp = ziel.with_name(f".{ziel.name}.seed.tmp")
        temp.write_bytes(neu)
        temp.replace(ziel)
        return self._setze(seed_id, v["version"], ("freigegeben",), "aktiv", von, ziel=str(ziel), geschrieben_sha256=_hash(neu))

    def datei_entfernen(self, seed_id: str, version: int | None, von: str) -> dict:
        """Genau den Block des Seeds entfernen. Hat jemand den Block verändert oder sonst nicht auffindbar: nichts entfernen und das sagen."""
        v = self.hole(seed_id, version)
        if v is None:
            raise SeedFehler("seed_unbekannt")
        if v["status"] != "aktiv":
            raise SeedFehler("nicht_aktiv")
        ziel = Path(v["ziel_pfad"]).resolve()
        meta = json.loads((self._backup_pfad(v) / "meta.json").read_text(encoding="utf-8"))
        original = (self._backup_pfad(v) / "original.bin").read_bytes()
        try:
            jetzt = ziel.read_bytes()
        except OSError:
            raise SeedFehler("ziel_nicht_lesbar") from None
        anfang = MARKE_AN.format(id=v["id"], v=v["version"]).encode()
        ende = MARKE_AUS.format(id=v["id"]).encode()
        block = f"\n{MARKE_AN.format(id=v['id'], v=v['version'])}\n{v['inhalt'].strip()}\n{MARKE_AUS.format(id=v['id'])}\n".encode("utf-8")
        if block not in jetzt:
            raise SeedFehler("block_veraendert_oder_weg")  # niemand anderes Arbeit anrühren
        ohne = jetzt.replace(block, b"", 1)
        if anfang in ohne or ende in ohne:
            raise SeedFehler("block_mehrfach")
        if not meta["existierte"] and ohne == b"":
            ziel.unlink()  # die Datei hat nur wegen dieses Seeds existiert
        else:
            temp = ziel.with_name(f".{ziel.name}.seed.tmp")
            temp.write_bytes(ohne)
            temp.replace(ziel)
        return self._setze(seed_id, v["version"], ("aktiv",), "zurueckgezogen", von, wiederhergestellt=(ohne == original) or not meta["existierte"])

    # ---- Aktivieren ohne Datei, Zurückziehen, Exportieren ---------------------------------------------------------------------------
    def aktiv_setzen(self, seed_id: str, version: int | None, von: str, **extra) -> dict:
        return self._setze(seed_id, version, ("freigegeben",), "aktiv", von, **extra)

    def zurueckziehen(self, seed_id: str, version: int | None, von: str, **extra) -> dict:
        """Für Seeds ohne Datei (Ablauf, Kontext, Loop, Goal): nur der Zustand; die Wirkung zurückzunehmen ist Sache des jeweiligen Dienstes."""
        return self._setze(seed_id, version, ("vorschlag", "freigegeben", "aktiv"), "zurueckgezogen", von, **extra)

    def exportieren(self, seed_id: str) -> dict:
        with self._sperre:
            vs = self._seeds.get(seed_id)
            if not vs:
                raise SeedFehler("seed_unbekannt")
            return {"schema": 1, "id": seed_id, "versionen": self._kopie({"v": vs})["v"],
                    "hinweis": "Ein Seed ist Text, ein Graph oder ein Auftrag. Er verändert kein Modellgewicht; gewonnenes Wissen liegt in Dateien, Abläufen und Kontexten, nicht im Modell."}
