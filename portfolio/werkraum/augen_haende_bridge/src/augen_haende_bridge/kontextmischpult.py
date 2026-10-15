"""Das Kontext-Mischpult (G14): Daniel (oder ein Werkzeug) bestimmt **exakt**, was eine Sitzung als Kontext sieht — Nachrichtenauswahl, Sätze bearbeiten und entfernen, leeren, halbieren, zurückspringen, einspeisen ohne Antwort, Promptfelder,
Vorschau, Export und Import, Einmalfeedback, Ausgabegrenzen, Session- und Geistermodus.

Leitgedanken (Dolphin-artig, aber ohne die bestehende App anzufassen):

* **Eine leere neue Sitzung ist effektiv leer.** `vorschau()` — das, was wirklich ans Modell ginge — ist dann `[]`: kein versteckter Basisprompt, keine heimlichen Zusatzprompts. Was zusätzlich mitgeht, steht als sichtbares Promptfeld.
* **Die Vorschau ist die Wahrheit.** Was dort nicht steht, geht nicht hinaus; was dort steht, geht hinaus (nur ausgewählte Nachrichten, nur aktive Felder).
* **Auswahl ist ID-genau.** Jede Nachricht hat eine stabile Kennung; Auswahl und Bearbeitungen überstehen Speichern, Neuladen und Export (nicht nur „die ersten n“).
* **Schätzung und Messung bleiben getrennt.** Die Kontextanzeige zeigt die eigene Schätzung (`geschaetzt`) und, wenn vorhanden, die Zahl vom Server (`gemessen`) nebeneinander und nennt die Abweichung. Kürzt der Server den Kontext (gemeldet oder weit unter der Schätzung), steht das da — es wird nicht hinter einer
  glatten Anzeige versteckt.
* **Jede Änderung ist rückgängig.** Zurück und Vor gehen Schritt für Schritt (`zurueck`, `vor`, `zurueckspringen`).
"""

from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, field
from pathlib import Path

ROLLEN = ("system", "user", "assistant", "ereignis")
MAX_NACHRICHTEN = 5000
MAX_TEXT = 200_000
MAX_DATEI = 400_000
MAX_FELDER = 20
ZEICHEN_JE_TOKEN = 3.5  # grobe Schätzung für gemischten deutschen/englischen Text; steht immer als Schätzung da
UNTERSCHREITUNG = 0.6  # misst der Server weniger als dieser Anteil der Schätzung, wird eine Kürzung vermutet
MAX_UNDO = 200
DATEI_ENDUNGEN = (".md", ".txt", ".markdown")
SAETZE = re.compile(r"(?<=[.!?…])\s+|\n+")


class PultFehler(ValueError):
    pass


@dataclass
class Nachricht:
    id: str
    rolle: str
    text: str
    quelle: str = ""
    zeit_ms: int = 0
    ausgewaehlt: bool = True
    ohne_antwort: bool = False  # eingespeist, ohne dass das Modell darauf antworten sollte

    def zu_dict(self) -> dict:
        return dict(self.__dict__)


@dataclass
class Promptfeld:
    name: str
    text: str
    aktiv: bool = True


class Mischpult:
    def __init__(self, name: str = "", modus: str = "session", jetzt_ms=lambda: int(time.time() * 1000)):
        if modus not in ("session", "geist"):
            raise PultFehler("modus_unbekannt")
        self.name, self.modus = name, modus
        self.basis_prompt = ""  # bewusst leer: eine neue Sitzung hat keinen versteckten Systemprompt
        self.nachrichten: list[Nachricht] = []
        self.felder: list[Promptfeld] = []
        self.einmalfeedback: str | None = None
        self.max_zeichen: int | None = None
        self.max_tokens: int | None = None
        self._nr = 0
        self._jetzt = jetzt_ms
        self._undo: list[dict] = []
        self._redo: list[dict] = []
        self.gemessen: dict | None = None

    # ---- Undo ---------------------------------------------------------------------------------------------------------------------------------
    def _zustand(self) -> dict:
        return {"nachrichten": [n.zu_dict() for n in self.nachrichten], "felder": [f.__dict__.copy() for f in self.felder], "basis": self.basis_prompt, "einmal": self.einmalfeedback,
                "grenzen": [self.max_zeichen, self.max_tokens], "nr": self._nr}

    def _setzen(self, z: dict) -> None:
        self.nachrichten = [Nachricht(**n) for n in z["nachrichten"]]
        self.felder = [Promptfeld(**f) for f in z["felder"]]
        self.basis_prompt, self.einmalfeedback = z["basis"], z["einmal"]
        self.max_zeichen, self.max_tokens = z["grenzen"]
        self._nr = z["nr"]

    def _vor_aenderung(self) -> None:
        self._undo.append(self._zustand())
        del self._undo[:-MAX_UNDO]
        self._redo.clear()

    def zurueck(self) -> bool:
        if not self._undo:
            return False
        self._redo.append(self._zustand())
        self._setzen(self._undo.pop())
        return True

    def vor(self) -> bool:
        if not self._redo:
            return False
        self._undo.append(self._zustand())
        self._setzen(self._redo.pop())
        return True

    def zurueckspringen(self, schritte: int) -> int:
        """Mehrere Schritte zurück auf einmal; liefert, wie viele es wirklich waren."""
        n = 0
        while n < schritte and self.zurueck():
            n += 1
        return n

    # ---- Nachrichten ------------------------------------------------------------------------------------------------------------------------------
    def _neue_id(self) -> str:
        self._nr += 1
        return f"m-{self._nr}"

    def hinzufuegen(self, rolle: str, text: str, quelle: str = "", ohne_antwort: bool = False) -> str:
        if rolle not in ROLLEN:
            raise PultFehler("rolle_unbekannt")
        if not isinstance(text, str) or not text or len(text) > MAX_TEXT or "\x00" in text:
            raise PultFehler("text_ungueltig")
        if len(self.nachrichten) >= MAX_NACHRICHTEN:
            raise PultFehler("zu_viele_nachrichten")
        self._vor_aenderung()
        n = Nachricht(self._neue_id(), rolle, text, quelle[:60], self._jetzt(), True, ohne_antwort)
        self.nachrichten.append(n)
        return n.id

    def einspeisen_text(self, text: str, rolle: str = "user", quelle: str = "eingespeist") -> str:
        """Text in den Kontext, **ohne** dass das Modell antworten soll (es wird kein Aufruf ausgelöst)."""
        return self.hinzufuegen(rolle, text, quelle, ohne_antwort=True)

    def einspeisen_dateien(self, dateien: list[tuple[str, str]]) -> list[str]:
        """Mehrere Text- oder Markdown-Dateien (Name, Inhalt), jede als eigene Nachricht mit Kopfzeile, ohne Antwort. Alles oder nichts: eine ungültige Datei lehnt die ganze Einspeisung ab."""
        for name, inhalt in dateien:
            if not isinstance(name, str) or not name.lower().endswith(DATEI_ENDUNGEN) or "/" in name or "\\" in name:
                raise PultFehler(f"dateityp_nicht_erlaubt:{str(name)[:40]}")
            if not isinstance(inhalt, str) or not inhalt.strip() or len(inhalt) > MAX_DATEI or "\x00" in inhalt:
                raise PultFehler(f"datei_ungueltig:{name[:40]}")
        if len(self.nachrichten) + len(dateien) > MAX_NACHRICHTEN:
            raise PultFehler("zu_viele_nachrichten")
        self._vor_aenderung()
        ids = []
        for name, inhalt in dateien:
            n = Nachricht(self._neue_id(), "user", f"[Datei: {name}]\n{inhalt}", f"datei:{name}"[:60], self._jetzt(), True, True)
            self.nachrichten.append(n)
            ids.append(n.id)
        return ids

    def _nachricht(self, nid: str) -> Nachricht:
        n = next((x for x in self.nachrichten if x.id == nid), None)
        if n is None:
            raise PultFehler("nachricht_unbekannt")
        return n

    def auswaehlen(self, ids: list[str] | None, an: bool = True) -> int:
        """Auswahl setzen (an/aus) für die genannten Nachrichten; `None` = alle."""
        ziel = self.nachrichten if ids is None else [self._nachricht(i) for i in ids]
        self._vor_aenderung()
        for n in ziel:
            n.ausgewaehlt = an
        return len(ziel)

    def nur_auswaehlen(self, ids: list[str]) -> int:
        """Genau diese Nachrichten sind aktiv, alle anderen nicht."""
        gewollt = {self._nachricht(i).id for i in ids}
        self._vor_aenderung()
        for n in self.nachrichten:
            n.ausgewaehlt = n.id in gewollt
        return len(gewollt)

    def text_ersetzen(self, nid: str, neu: str) -> None:
        n = self._nachricht(nid)
        if not isinstance(neu, str) or not neu or len(neu) > MAX_TEXT:
            raise PultFehler("text_ungueltig")
        self._vor_aenderung()
        n.text = neu

    @staticmethod
    def saetze(text: str) -> list[str]:
        return [s for s in SAETZE.split(text) if s.strip()]

    def satz_bearbeiten(self, nid: str, nr: int, neu: str) -> None:
        n = self._nachricht(nid)
        s = self.saetze(n.text)
        if not 0 <= nr < len(s) or not isinstance(neu, str) or not neu.strip():
            raise PultFehler("satz_ungueltig")
        self._vor_aenderung()
        s[nr] = neu.strip()
        n.text = " ".join(s)

    def satz_entfernen(self, nid: str, nr: int) -> None:
        n = self._nachricht(nid)
        s = self.saetze(n.text)
        if not 0 <= nr < len(s) or len(s) < 2:
            raise PultFehler("satz_ungueltig")  # den letzten Satz entfernt man, indem man die Nachricht entfernt
        self._vor_aenderung()
        del s[nr]
        n.text = " ".join(s)

    def entfernen(self, ids: list[str]) -> int:
        weg = {self._nachricht(i).id for i in ids}
        self._vor_aenderung()
        self.nachrichten = [n for n in self.nachrichten if n.id not in weg]
        return len(weg)

    def leeren(self) -> int:
        """Alle Nachrichten weg (Felder bleiben): danach ist der Kontext bis auf aktive Felder leer."""
        n = len(self.nachrichten)
        self._vor_aenderung()
        self.nachrichten = []
        return n

    def halbieren(self) -> int:
        """Die ältere Hälfte der Nachrichten entfernen (bei ungerader Zahl die kleinere Hälfte); liefert, wie viele wegfielen."""
        k = len(self.nachrichten) // 2
        if k == 0:
            return 0
        self._vor_aenderung()
        self.nachrichten = self.nachrichten[k:]
        return k

    # ---- Felder, Feedback, Grenzen ---------------------------------------------------------------------------------------------------------------------
    def feld_setzen(self, name: str, text: str, aktiv: bool = True) -> None:
        if not isinstance(name, str) or not 1 <= len(name) <= 40 or not isinstance(text, str) or len(text) > MAX_TEXT:
            raise PultFehler("feld_ungueltig")
        self._vor_aenderung()
        for f in self.felder:
            if f.name == name:
                f.text, f.aktiv = text, bool(aktiv)
                return
        if len(self.felder) >= MAX_FELDER:
            raise PultFehler("zu_viele_felder")
        self.felder.append(Promptfeld(name, text, bool(aktiv)))

    def feld_entfernen(self, name: str) -> bool:
        if not any(f.name == name for f in self.felder):
            return False
        self._vor_aenderung()
        self.felder = [f for f in self.felder if f.name != name]
        return True

    def basis_setzen(self, text: str) -> None:
        """Ein Basisprompt ist erlaubt — aber nur ausdrücklich gesetzt und in der Vorschau sichtbar."""
        if not isinstance(text, str) or len(text) > MAX_TEXT:
            raise PultFehler("text_ungueltig")
        self._vor_aenderung()
        self.basis_prompt = text

    def einmalfeedback_setzen(self, text: str | None) -> None:
        if text is not None and (not isinstance(text, str) or not text.strip() or len(text) > 4000):
            raise PultFehler("text_ungueltig")
        self._vor_aenderung()
        self.einmalfeedback = text

    def grenzen_setzen(self, max_zeichen: int | None, max_tokens: int | None) -> None:
        for w in (max_zeichen, max_tokens):
            if w is not None and (type(w) is not int or not 1 <= w <= 1_000_000):
                raise PultFehler("grenze_ungueltig")
        self._vor_aenderung()
        self.max_zeichen, self.max_tokens = max_zeichen, max_tokens

    # ---- Was wirklich hinausginge -----------------------------------------------------------------------------------------------------------------------
    def vorschau(self) -> list[dict]:
        """Genau die Nachrichten, die ans Modell gingen. Eine neue, leere Sitzung ergibt `[]`."""
        m: list[dict] = []
        if self.basis_prompt.strip():
            m.append({"role": "system", "content": self.basis_prompt})
        for f in self.felder:
            if f.aktiv and f.text.strip():
                m.append({"role": "system", "content": f.text})
        for n in self.nachrichten:
            if n.ausgewaehlt:
                rolle = "user" if n.rolle == "ereignis" else n.rolle
                m.append({"role": rolle, "content": n.text})
        if self.einmalfeedback:
            m.append({"role": "system", "content": f"Hinweis nur für diese eine Ausgabe: {self.einmalfeedback}"})
        return m

    def anfrage_bauen(self) -> dict:
        """Die Anfrage samt Grenzen; das Einmalfeedback wird dabei verbraucht (gilt für genau eine Ausgabe)."""
        nachrichten = self.vorschau()
        einmal = self.einmalfeedback is not None
        if einmal:
            self._vor_aenderung()
            self.einmalfeedback = None
        a: dict = {"messages": nachrichten, "einmal_verbraucht": einmal, "gesendete_zeichen": sum(len(x["content"]) for x in nachrichten)}
        if self.max_tokens:
            a["max_tokens"] = self.max_tokens
        if self.max_zeichen:
            a["max_zeichen"] = self.max_zeichen
        return a

    # ---- Kontextanzeige: Schätzung und Messung getrennt -----------------------------------------------------------------------------------------------
    def schaetzung(self) -> dict:
        zeichen = sum(len(x["content"]) for x in self.vorschau())
        return {"tokens": int(zeichen / ZEICHEN_JE_TOKEN + 0.999) if zeichen else 0, "zeichen": zeichen, "art": "geschaetzt", "verfahren": f"Zeichen / {ZEICHEN_JE_TOKEN}"}

    def server_gemessen(self, usage: dict | None, gesendete_zeichen: int, gekuerzt: bool | None = None) -> None:
        """Die Zahlen, die der Server zurückmeldet, getrennt von der Schätzung festhalten."""
        if not isinstance(usage, dict) or type(usage.get("prompt_tokens")) is not int:
            self.gemessen = None
            return
        geschaetzt = int(gesendete_zeichen / ZEICHEN_JE_TOKEN + 0.999) if gesendete_zeichen else 0
        self.gemessen = {"prompt_tokens": usage["prompt_tokens"], "completion_tokens": usage.get("completion_tokens"), "art": "gemessen", "gesendete_zeichen": gesendete_zeichen, "geschaetzt_dazu": geschaetzt,
                         "server_meldet_kuerzung": bool(gekuerzt), "zeit_ms": self._jetzt()}

    def anzeige(self) -> dict:
        s, g = self.schaetzung(), self.gemessen
        a = {"geschaetzt": s, "gemessen": g, "nachrichten": len(self.nachrichten), "ausgewaehlt": sum(1 for n in self.nachrichten if n.ausgewaehlt), "felder_aktiv": sum(1 for f in self.felder if f.aktiv)}
        if g is None:
            a["hinweis"] = "nur geschätzt: der Server hat noch keine Zahl gemeldet"
            return a
        ref = g["geschaetzt_dazu"] or 1
        a["abweichung_prozent"] = round((g["prompt_tokens"] - ref) / ref * 100, 1)
        a["serverkuerzung"] = "gemeldet" if g["server_meldet_kuerzung"] else ("vermutet" if g["prompt_tokens"] < UNTERSCHREITUNG * ref else "nein")
        a["hinweis"] = {"gemeldet": "der Server meldet eine Kürzung des Kontexts: das Modell hat NICHT alles gesehen",
                        "vermutet": "der Server zählt deutlich weniger als geschätzt: eine Kürzung ist wahrscheinlich, das Modell hat vermutlich nicht alles gesehen",
                        "nein": "Schätzung und Messung liegen nahe beieinander"}[a["serverkuerzung"]]
        return a

    # ---- Speichern, Export, Import ---------------------------------------------------------------------------------------------------------------------
    def export(self) -> dict:
        return {"schema": 1, "name": self.name, "modus": self.modus, "basis_prompt": self.basis_prompt, "nachrichten": [n.zu_dict() for n in self.nachrichten], "felder": [f.__dict__.copy() for f in self.felder],
                "einmalfeedback": self.einmalfeedback, "max_zeichen": self.max_zeichen, "max_tokens": self.max_tokens, "nr": self._nr}

    @staticmethod
    def aus_export(d: object, jetzt_ms=lambda: int(time.time() * 1000)) -> "Mischpult":
        """Streng: ungültige Daten werden abgelehnt, nicht halb geladen. Auswahl und Kennungen bleiben exakt erhalten."""
        if not isinstance(d, dict) or d.get("schema") != 1 or d.get("modus") not in ("session", "geist"):
            raise PultFehler("export_ungueltig")
        p = Mischpult(str(d.get("name", ""))[:60], d["modus"], jetzt_ms)
        try:
            ids = set()
            for n in d.get("nachrichten", []):
                nn = Nachricht(str(n["id"]), n["rolle"], n["text"], str(n.get("quelle", ""))[:60], int(n.get("zeit_ms", 0)), bool(n.get("ausgewaehlt", True)), bool(n.get("ohne_antwort", False)))
                if nn.rolle not in ROLLEN or not nn.text or nn.id in ids:
                    raise PultFehler("export_ungueltig")
                ids.add(nn.id)
                p.nachrichten.append(nn)
            p.felder = [Promptfeld(str(f["name"])[:40], str(f["text"]), bool(f.get("aktiv", True))) for f in d.get("felder", [])][:MAX_FELDER]
            p.basis_prompt = str(d.get("basis_prompt", ""))
            p.einmalfeedback = d.get("einmalfeedback") if isinstance(d.get("einmalfeedback"), str) else None
            p.max_zeichen, p.max_tokens = d.get("max_zeichen"), d.get("max_tokens")
            p._nr = max([int(d.get("nr", 0))] + [int(i[2:]) for i in ids if i.startswith("m-") and i[2:].isdigit()])
        except (KeyError, TypeError, ValueError) as f:
            raise PultFehler("export_ungueltig") from f
        return p

    def ersetzen_durch(self, export: object) -> int:
        """Den ganzen Inhalt durch einen Export ersetzen (z. B. das aufgezeichnete Gespräch aus einer Kapsel) — als eine rückgängig zu machende Änderung. Ungültiges ändert nichts. Der eigene Name und Modus bleiben."""
        neu = Mischpult.aus_export(export)
        self._vor_aenderung()
        self._setzen(neu._zustand())
        return len(self.nachrichten)

    def speichern(self, ordner: Path) -> Path:
        """Nur im Sitzungsmodus; der Geistermodus hinterlässt nichts auf der Platte."""
        if self.modus == "geist":
            raise PultFehler("geistermodus_speichert_nicht")
        if not self.name or not re.fullmatch(r"[A-Za-z0-9_. -]{1,60}", self.name):
            raise PultFehler("name_ungueltig")
        pfad = Path(ordner) / f"{self.name.replace(' ', '_')}.json"
        pfad.parent.mkdir(parents=True, exist_ok=True)
        temp = pfad.with_suffix(".tmp")
        temp.write_text(json.dumps(self.export(), ensure_ascii=False), encoding="utf-8")
        temp.replace(pfad)
        return pfad

    @staticmethod
    def laden(pfad: Path) -> "Mischpult":
        try:
            return Mischpult.aus_export(json.loads(Path(pfad).read_text(encoding="utf-8")))
        except (OSError, ValueError) as f:
            raise PultFehler("datei_unlesbar") from f
