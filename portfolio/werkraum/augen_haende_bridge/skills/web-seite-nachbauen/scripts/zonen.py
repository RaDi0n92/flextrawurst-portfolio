#!/usr/bin/env python3
"""zonen.py <a.png> <b.png> [x] — Sektionshoehen gegenueberstellen.

Aufruf:  zonen.py original.png nachbau.png [x=14]
Listet fuer beide Bilder die hell/dunkel-Wechsel bei einer Spalte und rechnet
die Hoehen-Differenz aus. Das ist das Werkzeug gegen die Fehlerklasse
"die Seite stimmt, aber alles sitzt 500px zu tief".
"""
import sys
from PIL import Image


def zonen(pfad, x):
    im = Image.open(pfad).convert("RGB")
    px = im.load()
    w, h = im.size
    res = []
    last = None
    y0 = 0
    for y in range(h):
        r, g, b = px[x, y]
        k = "hell" if (r + g + b) / 3 > 128 else "dunkel"
        if k != last:
            if last is not None:
                res.append((y0, y, last))
            last, y0 = k, y
    res.append((y0, h, last))
    return [z for z in res if z[1] - z[0] >= 8]


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    x = int(sys.argv[3]) if len(sys.argv) > 3 else 14
    a, b = zonen(sys.argv[1], x), zonen(sys.argv[2], x)
    print(f"{'#':>2} {'ORIGINAL':>22} {'NACHBAU':>22} {'delta':>7}")
    for i in range(max(len(a), len(b))):
        if i < len(a) and i < len(b):
            oa, ob, ok = a[i]
            ba, bb, bk = b[i]
            d = (bb - ba) - (ob - oa)
            print(f"{i:>2} {oa:>5}..{ob:<5} {ok:<5}{ob-oa:>5}"
                  f" {ba:>5}..{bb:<5} {bk:<5}{bb-ba:>5} {d:>+7}")
        elif i < len(a):
            oa, ob, ok = a[i]
            print(f"{i:>2} {oa:>5}..{ob:<5} {ok:<5}{ob-oa:>5} {'FEHLT':>22} {'-':>7}")
        else:
            ba, bb, bk = b[i]
            print(f"{i:>2} {'FEHLT':>22} {'':>7} {ba:>5}..{bb:<5} {bk:<5}{bb-ba:>5} {'-':>7}")
    return 0


if __name__ == "__main__":
    sys.exit(main())