#!/usr/bin/env python3
"""textecheck.py <quelle.html> <nachbau.py> -- erfundenen Text finden.

Aufruf:  textecheck.py /tmp/ap_dom.html /tmp/bauen.py
Exit 1, wenn der Nachbau Text zeigt, den es in der Quelle nicht gibt.

Warum das das ernsteste Werkzeug in diesem Skill ist: Ich habe beim Nachbauen
Kacheltexte geschrieben, die es bei Apple nicht gibt -- "Erhalte eine Gutschrift von
bis zu 150 Euro bis 1.020 Euro". Die Kachel sah original aus, die Bilder waren original,
und die Zahl blieb gruen. Erfundener Text ist schlimmer als ein fehlendes Bild, weil
er beim Anschauen nicht auffaellt: Man prueft Form, nicht Behauptung.

Ein Bilddiff kann diesen Fehler nicht finden. Beide sehen gleich aus.
"""

import io
import re
import sys
import html as H


def norm(s):
    s = H.unescape(re.sub(r'<[^>]+>', ' ', s)).replace('\xa0', ' ').replace('­', '')
    return re.sub(r'\W+', ' ', s, flags=re.U).strip().lower()


def ohne_nummer(s):
    """Fuehrende Fussnoten-Nummer weg: 1./2./3. steht in der Quelle in <ol><li>,
    im Nachbau als Textpraefix. Das ist dieselbe Information, keine Erfindung."""
    return re.sub(r'^\d+\.\s*', '', s).strip()


def quelle(pfad):
    h = io.open(pfad, encoding='utf-8', errors='replace').read()
    return norm(h)


def kandidaten(pfad):
    b = io.open(pfad, encoding='utf-8').read()
    # python-codezeilen ausfiltern: kein text, was nach python aussieht
    raus = []
    for t in re.findall(r'>([^<>{}]{18,160})<', b):
        t = re.sub(r'\s+', ' ', t).strip()
        # python-zeilen aussortieren: sie enthalten =, +, oder ein keyword
        if re.search(r'(=\s|\+\s|\bfor\b|\bin\b|\blen\(|\brange\(|\.join\(|\.append\(|'
                     r'class=|href=|https?://|<\?|<!DOCTYPE)', t):
            continue
        raus.append(t)
    return raus


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    q = quelle(sys.argv[1])
    qsatz = set(filter(None, q.split('  ')))
    falsch = []
    for t in kandidaten(sys.argv[2]):
        n = norm(t)
        if not n or n in q or ohne_nummer(t) and norm(ohne_nummer(t)) in q:
            continue
        falsch.append(t)

    if not falsch:
        print("kein erfundener text gefunden.")
        print("merke: das heisst nur, dass jeder satz woertlich in der quelle steht.")
        print("      es heisst nicht, dass die seite vollstaendig ist -- dafuer ist zone.py da.")
        return 0
    print(f"{len(falsch)} TEXT(E) IM NACHBAU STEHEN NICHT IN DER QUELLE:\n")
    for t in falsch:
        print(f"  - {t[:110]}")
    print("\ndas ist keine kosmetik. der nachbau behauptet inhalt, den es nicht gibt.")
    return 1


if __name__ == '__main__':
    sys.exit(main())