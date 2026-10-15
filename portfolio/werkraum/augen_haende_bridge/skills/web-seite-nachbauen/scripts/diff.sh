#!/usr/bin/env python3
"""diff.sh <original.png> <nachbau.png> — die Zahl. Ohne sie ist nichts fertig.

ZWEI Zahlen, weil eine Zahl hier luegt:

  sichtbar   Pixel mit Delta > 40. Das ist die Abweichung, die man sieht.
  exakt      Pixel mit Delta >= 1. Zaehlt Anti-Aliasing mit.

Ein Nachbau, der im gleichen Chromium mit denselben Schriften gerendert wird,
hat fast immer 4-6% Anti-Aliasing-Rauschen. "exakt" misst das und sieht aus
wie ein Layoutfehler. "sichtbar" ist die Zahl, die den Aufbau beschreibt.
Beide werden genannt, weil eine Zahl allein hier betruegt.
"""
import sys
from PIL import Image, ImageChops

SCHWELLE = 40


def schnitt(p):
    im = Image.open(p).convert("RGB")
    px = im.load()
    w, h = im.size
    sp = int(w * 0.01)
    gr, last, y0 = [], None, 0
    for y in range(h):
        v = sum(px[sp, y]) / 3
        k = "hell" if v > 128 else "dunkel"
        if k != last:
            if last is not None:
                gr.append(y0)
            last, y0 = k, y
    return w, h, gr


def main():
    if len(sys.argv) < 3:
        print("diff.sh <original.png> <nachbau.png>")
        return 2
    a, b = sys.argv[1], sys.argv[2]
    wa, ha, ga = schnitt(a)
    wb, hb, gb = schnitt(b)
    print(f"original  {wa}x{ha}  grenzen: {ga[:12]}")
    print(f"nachbau   {wb}x{hb}  grenzen: {gb[:12]}")
    print(f"grenzen  {len([x for x in ga if x in gb])}/{min(len(ga), len(gb))} identisch")
    if wa != wb:
        print("breiten unterschiedlich -> kein sinnvoller Vergleich")
        return 3
    if abs(ha - hb) > 60:
        print(f"\nKEINE ZAHL. Hoehen {ha} vs {hb} unterscheiden sich um {abs(ha-hb)}px.")
        print("Gleiche Hoehe fotografieren, sonst misst du schwarze Flaeche, nicht den Aufbau.")
        return 4
    h = min(ha, hb)
    d = ImageChops.difference(Image.open(a).convert("RGB").crop((0, 0, wa, h)),
                              Image.open(b).convert("RGB").crop((0, 0, wa, h)))
    hist = d.convert("L").histogram()
    total = wa * h
    exakt = (total - hist[0]) * 100.0 / total
    sichtbar = sum(hist[SCHWELLE + 1:]) * 100.0 / total
    print(f"sichtbar  {sichtbar:.2f}%   (delta > {SCHWELLE}, das was man sieht)")
    print(f"exakt     {exakt:.2f}%   (delta >= 1, inklusive Anti-Aliasing)")
    if sichtbar > 8:
        print("UEBER 8%. Noch nicht abgeben.")
    else:
        print("unter 8%.")
    print("merke: beide zahlen messen Form, nicht Bedeutung.")
    return 0


if __name__ == "__main__":
    sys.exit(main())