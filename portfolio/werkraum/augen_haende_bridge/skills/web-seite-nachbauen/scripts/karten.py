#!/usr/bin/env python3
"""karten.py <html-datei> — holt ein echtes Karussell aus der Quelle, inkl. Reihenfolge.

Aufruf:  karten.py <html> <abschnitt-marker>   z.B.  karten.html 'id="tv-gallery"'
Schreibt nach /tmp/tv3/<n>.jpg und gibt die Reihenfolge aus.

Warum das ein Werkzeug und keine Regel ist: Ein Karussell liegt als EIN Block mit
translate3d() in der Quelle. Wer per regex nur die ersten n URLs nimmt, hat neun Logos
und ein Motiv. Das Skript liest die Paare und prüft die Bytegröße.
"""
import re, sys, os, time, urllib.request

UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/131 Safari/537.36"}
ZIEL = "/tmp/tv3"
MINDEST = 60000          # darunter ist es ein Platzhalter, kein Motiv


def hol(url, pfad, mindest=MINDEST, versuche=2):
    os.makedirs(os.path.dirname(pfad), exist_ok=True)
    for _ in range(versuche):
        try:
            d = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=45).read()
            if len(d) >= mindest:
                open(pfad, "wb").write(d)
                return len(d)
        except Exception:
            pass
        time.sleep(0.5)
    return 0


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    html = open(sys.argv[1], encoding="utf-8", errors="replace").read()
    marker = sys.argv[2]
    basis = "https://www.apple.com"
    i = html.find(marker)
    if i < 0:
        print(f"Marker nicht gefunden: {marker}")
        return 3
    seg = html[i:i + 400000]

    paare = re.findall(
        r'/thumb/([^/]+)/1250x\d+sr\.jpg.*?/thumb/([^/]+)/220x54', seg, re.S)
    if not paare:
        paare = [(b, b) for b in re.findall(r'/thumb/([^/]+)/1250x\d+sr\.jpg', seg)]
    print(f"karten gefunden: {len(paare)}")

    base = "https://is1-ssl.mzstatic.com/image/thumb"
    for n, (bg, lg) in enumerate(paare, 1):
        b = hol(f"{base}/{bg}/1250x668sr.jpg", f"{ZIEL}/{n}.jpg")
        hol(f"{base}/{lg}/440x109.png", f"{ZIEL}/{n}logo.png", mindest=500)
        zust = "ok" if b else "PLATZHALTER (byte < 60000)"
        print(f"  {n}: bg {b or '-':>7}  logo {lg[:18]:<18} {zust}")
        time.sleep(0.3)
    print(f"\n-> {ZIEL}/1..{len(paare)}.jpg")
    print("Nur echte Motive verwenden. Ein Platzhalter sieht auf dem Nachbau harmlos aus")
    print("und macht die Differenzzahl besser, ohne dass die Seite stimmt.")
    return 0


if __name__ == "__main__":
    sys.exit(main())