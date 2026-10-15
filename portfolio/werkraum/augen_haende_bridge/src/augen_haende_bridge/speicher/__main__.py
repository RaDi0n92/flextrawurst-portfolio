"""Bedienung des Ereignisspeichers: `python -m augen_haende_bridge.speicher <befehl>` (Adresse in `BRIDGE_DB_URL`).

    schema                     Tabellen und Sichten anlegen (wiederholbar)
    einlesen [ordner]          Ereignisprotokoll und alle Praxis-Ledger aus `runtime/` einlesen (wiederholbar, nichts doppelt)
    einbetten                  Ereignisse ohne Vektor einbetten
    suche "<frage>" [-n 5]     Bedeutung und Wort zusammen; `--bedeutung` nur Bedeutung, `--wort` nur Volltext
    position <lauf> <agent>    Was der Agent über seine Position im Graph erfährt (liest nur)
    weiter <lauf> <agent>      Den Graph mit den echten Prüfern von der Position aus weiterlaufen lassen (schreibt Ereignisse)
    wartet                     Wer wartet worauf seit wann
    folgen [ordner]            Dienst: neue Zeilen laufend in den Speicher schreiben (holt zuerst nach), bettet alle 30 s Neues ein
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from .ereignisspeicher import Ereignisspeicher

RUNTIME = Path(__file__).resolve().parents[3] / "runtime"


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="speicher", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="befehl", required=True)
    sub.add_parser("schema")
    e = sub.add_parser("einlesen")
    e.add_argument("ordner", nargs="?", default=str(RUNTIME))
    sub.add_parser("einbetten")
    s = sub.add_parser("suche")
    s.add_argument("frage")
    s.add_argument("-n", type=int, default=5)
    s.add_argument("--wort", action="store_true")
    s.add_argument("--bedeutung", action="store_true")
    s.add_argument("--lauf", default="")
    s.add_argument("--art", default="")
    po = sub.add_parser("position")
    po.add_argument("lauf")
    po.add_argument("agent")
    we = sub.add_parser("weiter")
    we.add_argument("lauf")
    we.add_argument("agent")
    sub.add_parser("wartet")
    fo = sub.add_parser("folgen")
    fo.add_argument("ordner", nargs="?", default=str(RUNTIME))
    a = p.parse_args(argv)

    if a.befehl == "folgen":  # braucht beim Start noch keine Verbindung: der Dienst wartet, bis die Datenbank da ist
        from .folgen import lauf

        lauf(Path(a.ordner), protokoll=lambda t: print(t, flush=True))
        return 0

    try:
        sp = Ereignisspeicher()
    except ValueError as f:
        print(f"Fehler: {f}", file=sys.stderr)
        return 2
    if a.befehl == "schema":
        sp.schema_anlegen()
        print("Schema angelegt.")
    elif a.befehl == "einlesen":
        sp.schema_anlegen()
        w = Path(a.ordner)
        for datei in sorted(w.glob("g13/protokoll/ereignisse.jsonl*")) + sorted(w.glob("praxis/*.jsonl")):
            neu, bekannt = (sp.einlesen_protokoll if "protokoll" in datei.parts else sp.einlesen_ledger)(datei)
            print(f"{datei.relative_to(w)}: {neu} neu, {bekannt} schon bekannt")
    elif a.befehl == "einbetten":
        from . import rag
        print(f"{rag.einbetten_neue(sp, rag.Einbetter(), grenze=100000)} eingebettet.")
    elif a.befehl == "suche":
        from . import rag
        treffer = (rag.volltext(sp, a.frage, a.n) if a.wort else
                   rag.suche(sp, rag.Einbetter(), a.frage, a.n, lauf=a.lauf, art=a.art) if a.bedeutung else
                   rag.hybrid(sp, rag.Einbetter(), a.frage, a.n, lauf=a.lauf, art=a.art))
        for t in treffer:
            zeit = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t["zeit_ms"] / 1000))
            ab = f" ({t['abstand']:.2f})" if "abstand" in t else ""
            print(f"#{t['id']} {zeit} {t['quelle']}/{t['art']} {t['agent']} {t['lauf']} {t['knoten']}{ab}\n    {t['text'][:200]}")
    elif a.befehl == "position":
        print(json.dumps(_graph(sp).karte(a.lauf, a.agent), ensure_ascii=False, indent=2))
    elif a.befehl == "weiter":
        from .infragraph import Infragraph
        from .pruefer import ereignis_pruefer

        print(json.dumps(Infragraph(sp, ereignis_pruefer(sp)).weiter(a.lauf, a.agent), ensure_ascii=False, indent=2))
    elif a.befehl == "wartet":
        for w in sp.wartezustand():
            print(f"{w['agent']} wartet an {w['knoten']} auf {w['worauf']} seit {(time.time() * 1000 - w['seit_ms']) / 1000:.0f} s (Lauf {w['lauf']})")
    return 0


def _graph(sp):
    from .infragraph import KNOTEN, Infragraph

    return Infragraph(sp, {k: (lambda lauf, agent: (False, "nur_lesen")) for k in KNOTEN})


if __name__ == "__main__":
    raise SystemExit(main())
