#!/usr/bin/env python3
"""misst: Schnittgrenzen aus dem Screenshot, Werte aus dem Stylesheet, Bildvarianten aus srcset."""
import re, sys, subprocess, json
from collections import Counter
from urllib.request import urlopen, Request
from html import unescape

def hol(url, ua="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/131 Safari/537.36"):
    return urlopen(Request(url, headers={"User-Agent": ua}), timeout=45).read().decode("utf-8", "replace")

def schnittgrenzen(pfad, spalte=None):
    from PIL import Image
    im = Image.open(pfad).convert("RGB"); px = im.load(); w, h = im.size
    sp = int(w * 0.01) if spalte is None else int(spalte)
    out, last, y0 = [], None, 0
    for y in range(h):
        r, g, b = px[sp, y]; v = (r + g + b) / 3
        k = "hell" if v > 128 else "dunkel"
        if k != last:
            if last is not None:
                out.append((y0, y - 1, last, y - y0))
            last, y0 = k, y
    out.append((y0, h - 1, last, h - y0))
    return w, h, sp, out

def main():
    if len(sys.argv) < 2:
        print(__doc__); return
    url = sys.argv[1] if sys.argv[1].startswith("http") else "https://" + sys.argv[1]
    print(f"== {url}")

    try:
        html = hol(url)
    except Exception as e:
        print(f"HTML nicht holbar: {e}"); return
    print(f"   html: {len(html)} bytes")

    try:
        w, h, sp, gr = schnittgrenzen(sys.argv[2]) if len(sys.argv) > 2 else (0, 0, 0, [])
    except Exception as e:
        print(f"screenshot fehlt oder unlesbar: {e}"); gr = []
    if gr:
        print(f"\n-- SCHNITTGRENZEN (x={sp}) --")
        print("   von      bis      farbe     hoehe")
        for a, b, k, hh in gr:
            if hh >= 40: print(f"   {a:<7} {b:<7} {k:<9} {hh}")

    print("\n-- BILDER (suffix = rasterpunkt) --")
    namen = re.findall(r'/v/[^"\s]+\.(?:jpg|png|webp)', html)
    c = Counter()
    for n in namen:
        for s in ("_small", "_mediumtall", "_medium", "_large", "_largetall"):
            if s in n: c[s] += 1; break
        else: c["(ohne)"] += 1
    for k, v in c.most_common(): print(f"   {k:<14} {v}")
    print("   hero-<img src>:")
    for m in re.findall(r'<img[^>]+src="(/v/[^"]+)"', html)[:4]: print("     ", m)

    css = ""
    for l in re.findall(r'href="([^"]+\.css[^"]*)"', html)[:4]:
        u = url if l.startswith("http") else url.rsplit("/", 1)[0] + l
        try: css += hol(u)
        except Exception: pass
    if not css:
        print("\n-- CSS nicht ladbar --"); return

    print(f"\n-- FARBEN (vorkommen) --")
    for v, n in Counter(re.findall(r'#[0-9a-f]{6}\b|rgba?\([^)]+\)', css, re.I)).most_common(12):
        print(f"   {v:<24} {n}")

    print("\n-- SCHRIFTGRADE --")
    print("  ", sorted({x for x in re.findall(r'font-size:\s*([\d.]+(?:px|rem|em|%)+)', css)},
                    key=lambda s: float(re.sub(r'[a-z%]+$', '', s))))
    print("\n-- BREAKPOINTS --")
    print("  ", sorted({int(x) for x in re.findall(r'min-width:\s*(\d+)px', css)}))
    print("   (ein Breakpoint ist KEINE Sektionshöhe)")

if __name__ == "__main__":
    main()