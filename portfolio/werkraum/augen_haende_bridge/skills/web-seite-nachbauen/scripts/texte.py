#!/usr/bin/env python3
"""texte.py <html> -- echte Apple-Texte und CTAs einsammeln.

Aufruf:  texte.py /tmp/ap_dom.html
Schreibt /tmp/apimg2/apple_texte.json und druckt die gefundenen Bloecke.

Warum das ein Werkzeug ist: Ich habe beim Nachbauen Texte geschrieben, die es bei
Apple nicht gibt. "Erhalte eine Gutschrift von bis zu 150 Euro bis 1.020 Euro" steht
nirgends in der Quelle. Wer den Nachbau mit den Kacheln des Originals vergleicht,
sieht denselben Kasten und dieselben Bilder -- und haelt ihn fuer original.
Eine erfundene Zeile ist schlimmer als ein fehlendes Bild, weil sie beim Anschauen
nicht auffaellt. Dieses Skript macht den Textpruef-Teil vom Nachbauen zur Taste.
"""

import io
import json
import re
import sys
import html as H

ZIEL = '/tmp/apimg2/apple_texte.json'


def txt(s):
    s = re.sub(r'<br\s*/?>', '\n', s)
    s = re.sub(r'<sup[^>]*>', '^', s)
    s = re.sub(r'</sup>', '', s)
    s = re.sub(r'<[^>]+>', '', s)
    s = H.unescape(s).replace('\xa0', ' ')
    return re.sub(r'[ \t]+', ' ', s).strip()


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    h = io.open(sys.argv[1], encoding='utf-8', errors='replace').read()

    kacheln = []
    for m in re.finditer(r'class="tile-copy-wrapper[^"]*"[^>]*>(.*?)(?=<div class="tile-copy-wrapper|<footer|</main)', h, re.S):
        b = m.group(1)
        head = txt((re.search(r'class="tile-headline[^"]*"[^>]*>(.*?)</', b, re.S) or ['', ''])[1]) \
            if re.search(r'class="tile-headline', b) else ''
        sub = txt((re.search(r'class="tile-subhead[^"]*"[^>]*>(.*?)</', b, re.S) or ['', ''])[1]) \
            if re.search(r'class="tile-subhead', b) else ''
        cta_m = re.search(r'class="tile-ctas[^"]*"[^>]*>(.*?)</div>', b, re.S)
        ctas = re.findall(r'>([^<>]{3,40})</a>', cta_m.group(1)) if cta_m else []
        if head or sub:
            kacheln.append({'headline': head, 'subhead': sub,
                            'ctas': [c.strip() for c in ctas if c.strip()]})

    fein = []
    for m in re.finditer(r'<p class="footnote"[^>]*>(.*?)</p>', h, re.S):
        t = txt(m.group(1))
        if len(t) > 40:
            fein.append(t)
    if not fein:
        i = h.find('Qualifizierte')
        if i > 0:
            roh = txt(h[i:i + 6000])
            for abschnitt in re.split(r'\n(?=\d\.|[A-ZÄÖÜ][a-zäöüß]+\s)', roh):
                if len(abschnitt) > 80:
                    fein.append(abschnitt)

    daten = {'kacheln': kacheln, 'feindruck': fein}
    io.open(ZIEL, 'w', encoding='utf-8').write(json.dumps(daten, ensure_ascii=False, indent=2))

    print(f'kacheln: {len(kacheln)}   feindruck-abschnitte: {len(fein)}')
    print(f'-> {ZIEL}\n')
    for i, k in enumerate(kacheln, 1):
        print(f'{i:>2}. {k["headline"] or "-"}')
        if k['subhead']:
            print(f'    {k["subhead"][:88]}')
        print(f'    cta: {", ".join(k["ctas"]) or "-"}')
    return 0


if __name__ == '__main__':
    sys.exit(main())