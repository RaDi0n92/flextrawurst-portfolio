"""Momentkapseln (G13): ein Arbeitsmoment, eingefroren und später wieder zu öffnen, zu besprechen und weiterzudenken — das Original bleibt unverändert.

Eine Kapsel hält, was tatsächlich sichtbar und protokolliert war: die ausgewählten Agenten (Sitzung, Beziehungen, Zustand, Aufträge, Ziel), die Terminalausgabe, die Ereignisse (Nachrichten, Regiesprüche, Hände, WorldDOM …), die Bilder der Ziele, was der Körper an Zeichnungen und Bindungen
mitteilte, die WorldDOM-Knoten, die Läufe von Abläufen. **Private, nicht mitgeteilte Modellzustände werden weder behauptet noch ausgelesen.** Jedes Feld nennt seine Quelle; jede Lücke steht in `luecken` mit Grund — eine Kapsel behauptet nie mehr, als sie hat.

Sechs Entstehungsarten (`ART_*`): kompletter Moment, ein Ziel, ein Agent, mehrfach Markiertes, kombiniert aus mehreren Zielen, Zeitbereich um ein Ereignis.

**Unverändert heißt prüfbar:** `kapsel.json` wird einmal geschrieben (schreibgeschützt) und trägt den Hash seines Inhalts; `laden` meldet `unveraendert: False`, wenn jemand daran gedreht hat. Spätere Gedanken (Kommentare, Tags, Auswertungen, Gegenargumente, Zeichnungen) sind **eigene Ebenen**
in eigenen Dateien; ein Neuanfang ist eine **Folge-Kapsel** mit Verweis auf die Eltern. Tags sind frei und mehrfach; Lernstrecken sind geordnete Listen von Kapseln.
"""

from __future__ import annotations

import difflib
import hashlib
import json
import os
import shutil
import stat
import threading
import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

SCHEMA = 1
ART_KOMPLETT, ART_ZIEL, ART_AGENT, ART_MARKIERT, ART_KOMBINIERT, ART_ZEITRAUM = "kompletter_moment", "ziel", "agent", "markiert", "kombiniert", "zeitraum"
ARTEN = (ART_KOMPLETT, ART_ZIEL, ART_AGENT, ART_MARKIERT, ART_KOMBINIERT, ART_ZEITRAUM)
EBENEN_ARTEN = ("kommentar", "tags", "auswertung", "zeichnung", "gegenargument")
MAX_TERMINAL_ZEICHEN = 64_000
MAX_EREIGNISSE = 2000
MAX_FRAMES_JE_AGENT = 10
MAX_TAG = 40
MAX_TAGS = 30
MAX_TEXT = 8000
VORSCHLAG_TAGS = ("Idee", "Verwirrung", "Fehler", "Lösung", "Umweg", "Beinahe", "Überraschung", "Widerspruch", "Offene Frage", "Vergleich", "Zufallsfund", "Übergabe", "Hypothese", "Beweis", "Gegenbeweis",
                  "Blocker", "Entscheidung", "Rückfall", "wiederverwendbar", "verworfen")  # Vorschläge, kein geschlossener Satz: jeder freie Tag ist erlaubt


class KapselFehler(ValueError):
    pass


@dataclass
class Quellen:
    """Woher eine Kapsel ihre Daten holt. Jede Funktion ist optional; fehlt sie oder scheitert sie, wird daraus eine benannte Lücke."""

    agenten: Callable[[], list[dict]]
    ereignisse: Callable[[int, int | None, list[str] | None], list[dict]] = lambda von, bis, agenten: []
    terminal: Callable[[str, int | None], tuple[str, dict]] = lambda tid, bis: ("", {})
    frames: Callable[[str], list[tuple[Path, dict]]] = lambda tid: []
    koerper: Callable[[str], dict | None] = lambda tid: None
    weltdom: Callable[[str], list[dict]] = lambda ziel: []
    laeufe: Callable[[str], list[dict]] = lambda tid: []
    modell: Callable[[], dict | None] = lambda: None  # das Gespräch mit dem Modell (Kontext-Mischpult-Export) zum Zeitpunkt der Kapsel; None = keins
    jetzt_ms: Callable[[], int] = lambda: int(time.time() * 1000)


def _hash(inhalt: dict) -> str:
    return hashlib.sha256(json.dumps(inhalt, sort_keys=True, ensure_ascii=False, default=str).encode("utf-8")).hexdigest()


class KapselStore:
    def __init__(self, ordner: Path):
        self.ordner = Path(ordner)
        self._sperre = threading.RLock()

    def _dir(self, kid: str) -> Path:
        if not kid.startswith("k-") or not kid[2:].replace("-", "").isalnum() or len(kid) > 40:
            raise KapselFehler("kapsel_id_ungueltig")
        return self.ordner / kid

    # ---- Erzeugen ----------------------------------------------------------------------------------------------------------------------------
    def erzeugen(self, quellen: Quellen, art: str, *, von: str, grund: str = "", agenten: list[str] | None = None, ziele: list[str] | None = None, zeitraum: tuple[int, int] | None = None,
                 eltern: str | None = None) -> dict:
        if art not in ARTEN:
            raise KapselFehler("art_unbekannt")
        alle = {a["terminal_id"]: a for a in quellen.agenten()}
        wahl = self._auswahl(art, alle, agenten, ziele, zeitraum)
        luecken: list[dict] = []
        jetzt = quellen.jetzt_ms()
        kid = f"k-{uuid.uuid4().hex[:10]}"
        verz = self._dir(kid)
        inhalt: dict = {"schema": SCHEMA, "id": kid, "erzeugt_ms": jetzt, "ausloeser": {"von": von[:60], "art": art, "grund": grund[:300]}, "eltern": eltern,
                        "auswahl": {"agenten": wahl, "ziele": list(ziele or []), "zeitraum": list(zeitraum) if zeitraum else None}, "quellen": {}}
        inhalt["agenten"] = [alle[t] for t in wahl]
        inhalt["quellen"]["agenten"] = "register und anzeigeort des starters"

        def versuch(feld: str, quelle: str, aufruf, standard):
            try:
                inhalt["quellen"][feld] = quelle
                return aufruf()
            except Exception as f:
                luecken.append({"feld": feld, "grund": f"Quelle nicht lesbar: {f.__class__.__name__}" + (f" ({str(f)[:160]})" if str(f) else "")})
                return standard

        inhalt["terminals"] = {}
        for t in wahl:
            text, meta = versuch(f"terminals.{t}", "ereignisprotokoll (zeitgestempelte Ausgabestücke)", lambda t=t: quellen.terminal(t, zeitraum[1] if zeitraum else None), ("", {}))
            kurz = text[-MAX_TERMINAL_ZEICHEN:]
            inhalt["terminals"][t] = {"text": kurz, "meta": meta}
            if not text:
                luecken.append({"feld": f"terminals.{t}", "grund": "keine Terminalausgabe aufgezeichnet"})
            elif meta.get("verworfene_stuecke") or len(text) > len(kurz):
                luecken.append({"feld": f"terminals.{t}", "grund": f"Ausgabe unvollständig: {meta.get('verworfene_stuecke', 0)} ältere Stücke verworfen, auf {MAX_TERMINAL_ZEICHEN} Zeichen gekürzt"})
        ereignisse = versuch("ereignisse", "ereignisprotokoll", lambda: quellen.ereignisse(zeitraum[0] if zeitraum else 0, zeitraum[1] if zeitraum else None, wahl), [])[-MAX_EREIGNISSE:]
        inhalt["ereignisse"] = ereignisse
        inhalt["nachrichten"] = [e for e in ereignisse if e.get("art") in ("nachricht", "auftrag", "regie")]
        if not ereignisse:
            luecken.append({"feld": "ereignisse", "grund": "im gewählten Bereich keine Ereignisse aufgezeichnet"})
        inhalt["frames"], inhalt["koerper"], inhalt["laeufe"] = {}, {}, {}
        frame_dateien: list[tuple[Path, Path]] = []
        for t in wahl:
            bilder = versuch(f"frames.{t}", "frames-ordner des starters (die letzten zehn je Agent)", lambda t=t: quellen.frames(t), [])
            eintraege = []
            for pfad, meta in bilder[-MAX_FRAMES_JE_AGENT:]:
                ziel = Path("frames") / t / Path(pfad).name
                frame_dateien.append((Path(pfad), ziel))
                try:
                    sha = hashlib.sha256(Path(pfad).read_bytes()).hexdigest()
                except OSError:
                    continue
                eintraege.append({"datei": str(ziel), "sha256": sha, "meta": {k: meta[k] for k in ("captured_at_ms", "width", "height", "source", "aufnahme", "seq", "fallback_grund") if k in meta}})
            inhalt["frames"][t] = eintraege
            if not eintraege:
                luecken.append({"feld": f"frames.{t}", "grund": "kein Bild vorhanden (kein Ziel gebunden oder noch kein Bild gesendet)"})
            k = versuch(f"koerper.{t}", "körper des anzeigeortes (Zeichnungen, Bindung)", lambda t=t: quellen.koerper(t), None)
            inhalt["koerper"][t] = k
            if k is None:
                luecken.append({"feld": f"koerper.{t}", "grund": "der Körper hat keine Daten geliefert (offline oder ältere Fassung): Zeichnungen und Bindungen fehlen"})
            inhalt["laeufe"][t] = versuch(f"laeufe.{t}", "ablauf-dienst", lambda t=t: quellen.laeufe(t), [])
        inhalt["weltdom"] = {}
        for ziel in sorted({a.get("ziel_info", {}).get("target_id") for a in inhalt["agenten"] if a.get("ziel_info", {}).get("target_id")}):
            inhalt["weltdom"][ziel] = versuch(f"weltdom.{ziel}", "weltdom-speicher des Körpers (zuletzt gemessener Stand, nicht frisch gemessen)", lambda ziel=ziel: quellen.weltdom(ziel), [])
        gespraech = versuch("modell", "kontext-mischpult der beobachter-sitzung (aufgezeichnete Antworten, keine neu erzeugten)", quellen.modell, None)
        inhalt["modell"] = gespraech if isinstance(gespraech, dict) and gespraech.get("nachrichten") else None
        inhalt["luecken"] = luecken
        inhalt["inhalt_hash"] = _hash({k: v for k, v in inhalt.items() if k != "inhalt_hash"})
        with self._sperre:
            verz.mkdir(parents=True, exist_ok=False)
            for quelle_pfad, rel in frame_dateien:
                try:
                    (verz / rel).parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(quelle_pfad, verz / rel)
                except OSError:
                    pass
            datei = verz / "kapsel.json"
            datei.write_text(json.dumps(inhalt, ensure_ascii=False, default=str), encoding="utf-8")
            os.chmod(datei, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)  # einmal geschrieben, schreibgeschützt
        return inhalt

    @staticmethod
    def _auswahl(art: str, alle: dict, agenten, ziele, zeitraum) -> list[str]:
        agenten = list(dict.fromkeys(agenten or []))
        for t in agenten:
            if t not in alle:
                raise KapselFehler(f"agent_unbekannt:{t}")
        if art == ART_KOMPLETT:
            return sorted(alle)
        if art == ART_AGENT:
            if len(agenten) != 1:
                raise KapselFehler("genau_ein_agent")
            return agenten
        if art == ART_MARKIERT:
            if len(agenten) < 2:
                raise KapselFehler("mindestens_zwei_agenten")
            return agenten
        if art in (ART_ZIEL, ART_KOMBINIERT):
            if not ziele or (art == ART_KOMBINIERT and len(ziele) < 2) or (art == ART_ZIEL and len(ziele) != 1):
                raise KapselFehler("ziele_ungueltig")
            gewaehlt = [t for t, a in alle.items() if a.get("ziel_info", {}).get("target_id") in ziele]
            return sorted(set(gewaehlt) | set(agenten))
        if art == ART_ZEITRAUM:
            if not zeitraum or zeitraum[0] >= zeitraum[1]:
                raise KapselFehler("zeitraum_ungueltig")
            return agenten or sorted(alle)
        raise KapselFehler("art_unbekannt")

    # ---- Öffnen ---------------------------------------------------------------------------------------------------------------------------------
    def laden(self, kid: str) -> dict:
        datei = self._dir(kid) / "kapsel.json"
        if not datei.exists():
            raise KapselFehler("kapsel_unbekannt")
        inhalt = json.loads(datei.read_text(encoding="utf-8"))
        gespeichert = inhalt.get("inhalt_hash")
        inhalt["unveraendert"] = _hash({k: v for k, v in inhalt.items() if k != "inhalt_hash"}) == gespeichert
        return inhalt

    def gespraech(self, kid: str) -> dict | None:
        """Das in der Kapsel festgehaltene Modellgespräch (Export des Mischpults) — nur lesen; es wird kein Modell gerufen."""
        k = self.laden(kid)
        return k.get("modell")

    def liste(self) -> list[dict]:
        if not self.ordner.is_dir():
            return []
        ergebnis = []
        for v in sorted(self.ordner.iterdir()):
            if (v / "kapsel.json").exists():
                try:
                    k = json.loads((v / "kapsel.json").read_text(encoding="utf-8"))
                except (OSError, ValueError):
                    continue
                ergebnis.append({"id": k["id"], "erzeugt_ms": k["erzeugt_ms"], "art": k["ausloeser"]["art"], "von": k["ausloeser"]["von"], "agenten": [a["name"] for a in k["agenten"]], "eltern": k.get("eltern"),
                                 "tags": self.tags(k["id"]), "luecken": len(k["luecken"])})
        return sorted(ergebnis, key=lambda x: x["erzeugt_ms"])

    def frame_pfad(self, kid: str, eintrag: dict) -> Path:
        return self._dir(kid) / eintrag["datei"]

    # ---- Ebenen: Gedanken danach, nie am Original ------------------------------------------------------------------------------------------------
    def ebene_hinzufuegen(self, kid: str, art: str, von: str, text: str = "", tags: list[str] | None = None, bezug: dict | None = None, jetzt_ms: int | None = None) -> dict:
        if art not in EBENEN_ARTEN:
            raise KapselFehler("ebenenart_unbekannt")
        self._dir(kid)
        if not (self._dir(kid) / "kapsel.json").exists():
            raise KapselFehler("kapsel_unbekannt")
        if len(text) > MAX_TEXT:
            raise KapselFehler("text_zu_lang")
        sauber = []
        for t in tags or []:
            if not isinstance(t, str) or not 1 <= len(t.strip()) <= MAX_TAG or "\x00" in t:
                raise KapselFehler("tag_ungueltig")
            sauber.append(t.strip())
        if len(sauber) > MAX_TAGS:
            raise KapselFehler("zu_viele_tags")
        if art == "tags" and not sauber:
            raise KapselFehler("tags_fehlen")
        if art != "tags" and not text.strip():
            raise KapselFehler("text_fehlt")
        with self._sperre:
            verz = self._dir(kid) / "ebenen"
            verz.mkdir(exist_ok=True)
            nr = len(list(verz.glob("*.json"))) + 1
            e = {"nr": nr, "art": art, "von": von[:60], "zeit_ms": jetzt_ms or int(time.time() * 1000), "text": text, "tags": list(dict.fromkeys(sauber)), "bezug": bezug or {}}
            (verz / f"{nr:04d}-{art}.json").write_text(json.dumps(e, ensure_ascii=False), encoding="utf-8")
        return e

    def ebenen(self, kid: str) -> list[dict]:
        verz = self._dir(kid) / "ebenen"
        if not verz.is_dir():
            return []
        liste = []
        for p in sorted(verz.glob("*.json")):
            try:
                liste.append(json.loads(p.read_text(encoding="utf-8")))
            except (OSError, ValueError):
                continue
        return liste

    def tags(self, kid: str) -> list[str]:
        """Alle Tags aller Tag-Ebenen (mehrere gleichzeitig, frei)."""
        return sorted({t for e in self.ebenen(kid) for t in e.get("tags", [])})

    def suche(self, tags: list[str] | None = None, text: str | None = None, alle_tags: bool = True) -> list[dict]:
        treffer = []
        for k in self.liste():
            if tags:
                gesamt = set(k["tags"])
                if (alle_tags and not set(tags) <= gesamt) or (not alle_tags and not set(tags) & gesamt):
                    continue
            if text:
                voll = self.laden(k["id"])
                heu = json.dumps(voll.get("nachrichten", []), ensure_ascii=False) + " ".join(t["text"] for t in voll.get("terminals", {}).values()) + " ".join(e.get("text", "") for e in self.ebenen(k["id"]))
                if text.lower() not in heu.lower():
                    continue
            treffer.append(k)
        return treffer

    # ---- Lernstrecken ----------------------------------------------------------------------------------------------------------------------------
    def lernstrecke_speichern(self, name: str, kapseln: list[str], notiz: str = "") -> dict:
        if not name or len(name) > 60 or not name.replace("-", "").replace("_", "").replace(" ", "").isalnum():
            raise KapselFehler("name_ungueltig")
        for k in kapseln:
            if not (self._dir(k) / "kapsel.json").exists():
                raise KapselFehler(f"kapsel_unbekannt:{k}")
        d = {"name": name, "kapseln": list(kapseln), "notiz": notiz[:MAX_TEXT], "erzeugt_ms": int(time.time() * 1000)}
        verz = self.ordner / "_lernstrecken"
        verz.mkdir(parents=True, exist_ok=True)
        (verz / f"{name.replace(' ', '_')}.json").write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
        return d

    def lernstrecke(self, name: str) -> dict | None:
        p = self.ordner / "_lernstrecken" / f"{name.replace(' ', '_')}.json"
        return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None

    # ---- Folge-Kapsel und Vergleich ----------------------------------------------------------------------------------------------------------------
    def folge_kapsel(self, eltern: str, quellen: Quellen, von: str, grund: str = "") -> dict:
        """Ein neuer Moment auf Basis desselben Agentenkreises; die Eltern bleiben unverändert und sind verlinkt."""
        alt = self.laden(eltern)
        ids = [a["terminal_id"] for a in alt["agenten"]]
        art = ART_AGENT if len(ids) == 1 else (ART_MARKIERT if len(ids) > 1 else ART_KOMPLETT)
        return self.erzeugen(quellen, art, von=von, grund=grund or f"Folge von {eltern}", agenten=ids if art != ART_KOMPLETT else None, eltern=eltern)

    def vergleiche(self, a: str, b: str) -> dict:
        ka, kb = self.laden(a), self.laden(b)
        na, nb = {x["terminal_id"]: x for x in ka["agenten"]}, {x["terminal_id"]: x for x in kb["agenten"]}
        agenten = {"nur_in_a": sorted(set(na) - set(nb)), "nur_in_b": sorted(set(nb) - set(na)), "zustand_geaendert": {t: [na[t]["zustand"], nb[t]["zustand"]] for t in set(na) & set(nb) if na[t]["zustand"] != nb[t]["zustand"]}}
        terminal = {}
        for t in set(ka["terminals"]) & set(kb["terminals"]):
            diff = list(difflib.unified_diff(ka["terminals"][t]["text"].splitlines(), kb["terminals"][t]["text"].splitlines(), "a", "b", lineterm="", n=1))
            terminal[t] = {"unterschiedliche_zeilen": sum(1 for z in diff if z[:1] in "+-" and not z.startswith(("+++", "---"))), "ausschnitt": diff[:40]}

        def zaehle(k):
            z: dict[str, int] = {}
            for e in k.get("ereignisse", []):
                z[e["art"]] = z.get(e["art"], 0) + 1
            return z

        knoten_a = {x["id"] for v in ka.get("weltdom", {}).values() for x in v}
        knoten_b = {x["id"] for v in kb.get("weltdom", {}).values() for x in v}
        return {"a": a, "b": b, "zeit_abstand_ms": kb["erzeugt_ms"] - ka["erzeugt_ms"], "agenten": agenten, "terminal": terminal, "ereignisse": {"a": zaehle(ka), "b": zaehle(kb)},
                "weltdom": {"nur_in_a": len(knoten_a - knoten_b), "nur_in_b": len(knoten_b - knoten_a), "gemeinsam": len(knoten_a & knoten_b)}, "tags": {"a": self.tags(a), "b": self.tags(b)},
                "luecken": {"a": len(ka["luecken"]), "b": len(kb["luecken"])}}


def zeitraum_um(ereignis_zeit_ms: int, vor_s: float, nach_s: float) -> tuple[int, int]:
    """Der Bereich vor und nach einem Fehler oder einer Entscheidung (Art 6)."""
    if vor_s < 0 or nach_s < 0 or vor_s + nach_s <= 0 or vor_s + nach_s > 24 * 3600:
        raise KapselFehler("zeitraum_ungueltig")
    return int(ereignis_zeit_ms - vor_s * 1000), int(ereignis_zeit_ms + nach_s * 1000)
