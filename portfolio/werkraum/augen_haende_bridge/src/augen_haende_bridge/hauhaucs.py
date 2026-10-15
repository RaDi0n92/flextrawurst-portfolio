"""Hauhaucs als optionaler Beobachter (G14): eine eigene, leere Sitzung, die auf ausgewählte Agenten achtet und erst auf Daniels Wort dokumentiert.

Drei Dinge bleiben getrennt und sichtbar (je Agent gezählt):

* **aufgezeichnet**: das Ereignisprotokoll hat das Ereignis erfasst (Skript, ohne Modell, ohne Kosten);
* **zugestellt**: das Ereignis wurde in den Kontext der Beobachter-Sitzung gelegt (`zustellen`, ebenfalls ohne Modell);
* **verarbeitet**: ein Modellaufruf hat das Ereignis tatsächlich gesehen (`jetzt_dokumentieren`).

Reine Aufnahme braucht keine Inferenz: ohne `jetzt_dokumentieren` wird das Modell nie gerufen. Bildverarbeitung ist ein eigener Schalter (aus). Stop und Budget wirken sofort: nach `stop()` wird nichts mehr aufgezeichnet,
und ein erschöpftes Budget verweigert jeden weiteren Aufruf mit Grund. Die Ausarbeitung nennt ihre **Quellen** (`[e-12]` Ereignisse, `[k-…]` Kapseln); jeder Verweis wird gegen das Protokoll geprüft, Unbekanntes steht in `unbekannte_quellen`.

Die Anbindung nimmt **nur** den Chat-Server (OpenAI-Format, Vorgabe `http://localhost:11435`) in Anspruch; die Hintergrundinstanz der Codewesen (Port 11436) und das Hauhau-System bleiben unangetastet — dieses Modul importiert keinen ihrer Skripte.
"""

from __future__ import annotations

import json
import re
import threading
import time
import urllib.error
import urllib.request
from dataclasses import dataclass

from .ereignisprotokoll import Ereignis, Ereignisprotokoll
from .kontextmischpult import Mischpult, PultFehler

CHAT_URL = "http://localhost:11435/v1/chat/completions"
MAX_AGENTEN = 3
QUELLE = re.compile(r"\[((?:e-\d+)|(?:k-[A-Za-z0-9-]+))\]")
DOKUMENTIEREN_PROMPT = ("Du dokumentierst, was die beobachteten Agenten getan und besprochen haben. Schreibe sachlich auf Deutsch. Belege jede Aussage mit der Kennung des Ereignisses in eckigen Klammern, zum Beispiel [e-12]. "
                        "Erfinde nichts, was nicht in den Ereignissen steht; benenne Lücken ausdrücklich.")


class BeobachterFehler(ValueError):
    pass


def _http_fehler(f: urllib.error.HTTPError) -> str:
    """Eine Antwort des Servers mit Fehlercode ist „erreicht, aber abgelehnt“ — nicht „nicht erreichbar“. llama.cpp meldet einen zu großen Prompt als 400 mit `n_prompt_tokens` und `n_ctx`."""
    try:
        d = json.loads(f.read().decode("utf-8", "replace"))
        e = d.get("error", d) if isinstance(d, dict) else {}
        n, c = e.get("n_prompt_tokens"), e.get("n_ctx")
        if f.code == 400 and isinstance(n, int) and isinstance(c, int) and not isinstance(n, bool) and not isinstance(c, bool):
            return f"kontext_zu_gross:{n}_von_{c}"
        if f.code == 400 and "context" in str(e.get("message", "")).lower():
            return "kontext_zu_gross"
    except (OSError, ValueError, AttributeError):
        pass
    return f"modell_antwortet_mit_fehler:{f.code}"


class ModellClient:
    """Ein kleiner OpenAI-kompatibler Client (nur Standardbibliothek)."""

    def __init__(self, url: str = CHAT_URL, modell: str = "", timeout_s: float = 300.0):
        self.url, self.modell, self.timeout_s = url, modell, timeout_s

    def chat(self, messages: list[dict], max_tokens: int | None = None, bilder: list[str] | None = None, temperatur: float = 0.2) -> dict:
        nachrichten = [dict(m) for m in messages]
        if bilder and nachrichten:
            letzte = nachrichten[-1]
            letzte["content"] = [{"type": "text", "text": letzte["content"]}] + [{"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b}"}} for b in bilder[:3]]
        koerper = {"messages": nachrichten, "temperature": temperatur, "stream": False, **({"max_tokens": max_tokens} if max_tokens else {}), **({"model": self.modell} if self.modell else {})}
        anfrage = urllib.request.Request(self.url, data=json.dumps(koerper).encode("utf-8"), headers={"Content-Type": "application/json"})
        t0 = time.monotonic()
        try:
            with urllib.request.urlopen(anfrage, timeout=self.timeout_s) as antwort:
                d = json.loads(antwort.read().decode("utf-8"))
        except urllib.error.HTTPError as f:
            raise BeobachterFehler(_http_fehler(f)) from None
        except (urllib.error.URLError, OSError, ValueError) as f:
            raise BeobachterFehler(f"modell_nicht_erreichbar:{f.__class__.__name__}") from None
        try:
            text = d["choices"][0]["message"]["content"] or ""
        except (KeyError, IndexError, TypeError):
            raise BeobachterFehler("modell_antwort_ungueltig") from None
        gekuerzt = d.get("truncated") if isinstance(d.get("truncated"), bool) else (d.get("timings", {}) or {}).get("truncated") if isinstance(d.get("timings"), dict) else None
        return {"text": text, "usage": d.get("usage"), "gekuerzt": gekuerzt, "dauer_s": round(time.monotonic() - t0, 2)}


@dataclass
class Budget:
    max_aufrufe: int = 5
    max_tokens: int = 50_000  # Summe aus gesendeten (geschätzten oder gemessenen) und erzeugten Tokens
    aufrufe: int = 0
    tokens: int = 0
    gestoppt: bool = False

    def erlaubt(self, geschaetzte_tokens: int) -> str:
        """'' wenn ein weiterer Aufruf in Ordnung ist, sonst der Grund."""
        if self.gestoppt:
            return "gestoppt"
        if self.aufrufe >= self.max_aufrufe:
            return "budget_aufrufe_erschoepft"
        if self.tokens + geschaetzte_tokens > self.max_tokens:
            return "budget_tokens_erschoepft"
        return ""

    def zu_dict(self) -> dict:
        return {"max_aufrufe": self.max_aufrufe, "aufrufe": self.aufrufe, "max_tokens": self.max_tokens, "tokens": self.tokens, "gestoppt": self.gestoppt}


class Beobachtung:
    def __init__(self, protokoll: Ereignisprotokoll, pult: Mischpult | None = None, client: ModellClient | None = None, budget: Budget | None = None, kapsel_existiert=lambda kid: False,
                 namen=lambda tid: tid):
        self.protokoll, self.pult, self.client, self.budget = protokoll, pult or Mischpult(), client, budget or Budget()
        self._kapsel_existiert, self._namen = kapsel_existiert, namen
        self.aktiv = False
        self.chat_aufrufe = 0
        self.agenten: tuple[str, ...] = ()
        self.mit_bildern = False
        self._warteschlange: list[Ereignis] = []
        self._zaehler: dict[str, dict[str, int]] = {}
        self._zugestellt_ids: dict[str, str] = {}  # Ereignis-ID -> Nachrichten-ID im Pult
        self._verarbeitet: set[str] = set()
        self._sperre = threading.RLock()
        protokoll.abonnieren(self._ereignis)

    # ---- Steuern ---------------------------------------------------------------------------------------------------------------------------------
    def starten(self, agenten: list[str], mit_bildern: bool = False) -> dict:
        agenten = list(dict.fromkeys(agenten))
        if not 1 <= len(agenten) <= MAX_AGENTEN:
            raise BeobachterFehler(f"ein_bis_{MAX_AGENTEN}_agenten")
        with self._sperre:
            self.agenten, self.mit_bildern, self.aktiv = tuple(agenten), bool(mit_bildern), True
            self.budget.gestoppt = False
            for a in agenten:
                self._zaehler.setdefault(a, {"aufgezeichnet": 0, "zugestellt": 0, "verarbeitet": 0})
        self.protokoll.erfassen("beobachtung", text=f"Beobachtung gestartet: {', '.join(self._namen(a) for a in agenten)}", daten={"bilder": bool(mit_bildern)})
        return self.status()

    def stop(self) -> dict:
        """Wirkt sofort: nichts wird mehr aufgezeichnet, kein weiterer Modellaufruf ist erlaubt."""
        with self._sperre:
            self.aktiv = False
            self.budget.gestoppt = True
        self.protokoll.erfassen("beobachtung", text="Beobachtung gestoppt")
        return self.status()

    def bilder_schalten(self, an: bool) -> None:
        self.mit_bildern = bool(an)

    def _ereignis(self, e: Ereignis) -> None:
        with self._sperre:
            if not self.aktiv or e.agent not in self.agenten or e.art == "beobachtung":
                return
            if e.art == "frame" and not self.mit_bildern:
                return  # Bilder nur, wenn ausdrücklich zugeschaltet
            self._zaehler[e.agent]["aufgezeichnet"] += 1
            self._warteschlange.append(e)

    # ---- Zustellen (ohne Modell) ----------------------------------------------------------------------------------------------------------------------
    def zustellen(self, max_n: int = 200) -> int:
        """Die wartenden Ereignisse lesbar in den Kontext der Beobachter-Sitzung legen. Kein Modellaufruf."""
        with self._sperre:
            stapel, self._warteschlange = self._warteschlange[:max_n], self._warteschlange[max_n:]
        n = 0
        for e in stapel:
            zeit = time.strftime("%H:%M:%S", time.localtime(e.zeit_ms / 1000))
            text = f"[{e.id}] {zeit} {self._namen(e.agent)} · {e.art}" + (f" · {e.ziel}" if e.ziel else "") + (f": {e.text}" if e.text else "")
            try:
                mid = self.pult.einspeisen_text(text[:4000], rolle="ereignis", quelle=f"ereignis:{e.id}")
            except PultFehler:
                continue
            with self._sperre:
                self._zugestellt_ids[e.id] = mid
                self._zaehler[e.agent]["zugestellt"] += 1
            n += 1
        return n

    def lesbar(self, agent: str, n: int = 40) -> str:
        """Der Verlauf eines Agenten als lesbarer Text (die letzten n Ereignisse), wie ihn Daniel lesen würde."""
        zeilen = []
        for e in self.protokoll.letzte(n, [agent]):
            zeit = time.strftime("%H:%M:%S", time.localtime(e.zeit_ms / 1000))
            zeilen.append(f"[{e.id}] {zeit} {e.art}" + (f": {e.text}" if e.text else ""))
        return "\n".join(zeilen)

    # ---- Dokumentieren (Modell) --------------------------------------------------------------------------------------------------------------------------
    def jetzt_dokumentieren(self, auftrag: str = "", kapseln: list[str] | None = None, bilder: list[str] | None = None) -> dict:
        """Der einzige Weg, auf dem das Modell gerufen wird. Liefert die Ausarbeitung mit geprüften Quellen oder den Grund, warum nichts geschah."""
        if self.client is None:
            return {"ok": False, "reason": "kein_modell_angebunden"}
        if self.zustellen():
            pass
        self.pult.feld_setzen("Dokumentation", DOKUMENTIEREN_PROMPT + (f"\nAuftrag von Daniel: {auftrag}" if auftrag else ""), True)
        if kapseln:
            self.pult.einspeisen_text("Zugehörige Kapseln: " + ", ".join(f"[{k}]" for k in kapseln), rolle="ereignis", quelle="kapseln")
        vorschau = self.pult.vorschau()
        zeichen = sum(len(m["content"]) for m in vorschau)
        geschaetzt = int(zeichen / 3.5) + 1
        grund = self.budget.erlaubt(geschaetzt)
        if grund:
            return {"ok": False, "reason": grund, "budget": self.budget.zu_dict()}
        if bilder and not self.mit_bildern:
            return {"ok": False, "reason": "bilder_nicht_zugeschaltet"}
        anfrage = self.pult.anfrage_bauen()
        try:
            antwort = self.client.chat(anfrage["messages"], anfrage.get("max_tokens"), bilder if self.mit_bildern else None)
        except BeobachterFehler as f:
            return {"ok": False, "reason": str(f)}
        self.budget.aufrufe += 1
        usage = antwort.get("usage") or {}
        self.budget.tokens += int(usage.get("total_tokens") or (usage.get("prompt_tokens", 0) + usage.get("completion_tokens", 0)) or geschaetzt)
        self.pult.server_gemessen(usage, anfrage["gesendete_zeichen"], antwort.get("gekuerzt"))
        text = antwort["text"][: anfrage.get("max_zeichen") or len(antwort["text"])]
        self.pult.hinzufuegen("assistant", text, quelle="hauhaucs")
        gesehen = {m["content"].split("]")[0].lstrip("[") for m in vorschau if m["content"].startswith("[e-")}
        with self._sperre:
            for e_id in gesehen:
                if e_id not in self._verarbeitet:
                    self._verarbeitet.add(e_id)
                    ereignis = self.protokoll.ereignis(e_id)
                    if ereignis is not None and ereignis.agent in self._zaehler:
                        self._zaehler[ereignis.agent]["verarbeitet"] += 1
        genannt = list(dict.fromkeys(QUELLE.findall(text)))
        gueltig = [q for q in genannt if (self.protokoll.ereignis(q) is not None if q.startswith("e-") else self._kapsel_existiert(q))]
        unbekannt = [q for q in genannt if q not in gueltig]
        self.protokoll.erfassen("beobachtung", text="Ausarbeitung erstellt", daten={"quellen": len(gueltig), "unbekannt": len(unbekannt), "dauer_s": antwort["dauer_s"]})
        return {"ok": True, "text": text, "quellen": gueltig, "unbekannte_quellen": unbekannt, "ohne_quellenbezug": not genannt, "usage": usage, "kontext": self.pult.anzeige(), "dauer_s": antwort["dauer_s"], "budget": self.budget.zu_dict()}

    # ---- Freies Gespräch (Daniel chattet selbst mit dem Modell) -----------------------------------------------------------------------------------------------
    def chatten(self, text: str, bilder: list[str] | None = None) -> dict:
        """Daniel schreibt, das Modell antwortet; beides bleibt im Kontext-Mischpult (kürzbar, bearbeitbar, speicherbar). Kein Beobachtungs-Budget, kein Stop der Beobachtung:
        das ist ein Gespräch, keine Aufzeichnung. Es gelten nur die Ausgabegrenzen und der Kontext des Pults."""
        if self.client is None:
            return {"ok": False, "reason": "kein_modell_angebunden"}
        text = text.strip() if isinstance(text, str) else ""
        if not text:
            return {"ok": False, "reason": "text_leer"}
        mid = self.pult.hinzufuegen("user", text, quelle="daniel")
        anfrage = self.pult.anfrage_bauen()
        try:
            antwort = self.client.chat(anfrage["messages"], anfrage.get("max_tokens"), bilder[:3] if bilder else None)
        except BeobachterFehler as f:
            self.pult.entfernen([mid])  # die Frage bleibt nicht ohne Antwort im Verlauf hängen
            return {"ok": False, "reason": str(f)}
        usage = antwort.get("usage") or {}
        self.pult.server_gemessen(usage, anfrage["gesendete_zeichen"], antwort.get("gekuerzt"))
        antwort_text = antwort["text"][: anfrage.get("max_zeichen") or len(antwort["text"])]
        self.pult.hinzufuegen("assistant", antwort_text, quelle="hauhaucs")
        self.chat_aufrufe += 1
        return {"ok": True, "text": antwort_text, "usage": usage, "kontext": self.pult.anzeige(), "dauer_s": antwort["dauer_s"]}

    # ---- Stand ------------------------------------------------------------------------------------------------------------------------------------------
    def status(self) -> dict:
        with self._sperre:
            return {"aktiv": self.aktiv, "agenten": [{"id": a, "name": self._namen(a), **self._zaehler.get(a, {"aufgezeichnet": 0, "zugestellt": 0, "verarbeitet": 0})} for a in self.agenten], "wartend": len(self._warteschlange),
                    "bilder": self.mit_bildern, "budget": self.budget.zu_dict(), "kontext": self.pult.anzeige(), "modell_angebunden": self.client is not None, "chat_aufrufe": self.chat_aufrufe}
