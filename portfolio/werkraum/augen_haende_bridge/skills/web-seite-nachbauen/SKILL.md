---
name: web-seite-nachbauen
description: Misst eine Webseite und baut sie nach, mit gemessener Differenzzahl statt Ähnlichkeitsbehauptung. Verwenden, wenn Daniel "bau die Seite nach", "mach 1:1" oder "wie sieht die aus" sagt, oder ein Auftrag ein unbekanntes visuelles Ziel hat. Nicht für Seiten nur lesen oder erklären.
---

# Seite nachbauen

Jeder Schritt ist ein **Werkzeug**, kein Text. Kein Schritt gilt als erledigt ohne Zahl.

```sh
scripts/auge.sh    <ziel.png> <url> [breite=1440] [vms=9000] [hoehe=9000]
scripts/mess.py    <url> [screenshot.png]
scripts/karten.py  <html> '<abschnitts-marker>'
scripts/zonen.py   <original.png> <nachbau.png> [x=14]
scripts/texte.py   <html>            echte Texte einsammeln
scripts/textecheck.py <quelle.html> <nachbau.py>   erfundenen Text finden
scripts/diff.sh    <original.png> <nachbau.png>
```

## Ablauf, ohne Auslassung

| # | Werkzeug | Was es liefert | Stoppt wenn |
|---|---|---|---|
| 1 | `auge.sh original.png <url>` | Screenshot, ganze Seite | keine Datei |
| 2 | `mess.py <url> original.png` | Schnittgrenzen, Farben, Grade, Bildtypen | CSS nicht ladbar |
| 3 | `karten.py <html> 'id="tv-gallery"'` | echte Motive **in Reihenfolge** | Platzhalter < 60 KB |
| 4 | bauen | HTML | — |
| 5 | `auge.sh nachbau.png file://…` | zweiter Screenshot | — |
| 6 | `zonen.py` | Sektionshöhen beider Seiten, Delta je Sektion | Delta != 0 |
| 7 | `texte.py` | alle Original-Texte als JSON | leere Kachel-Liste |
| 8 | `textecheck.py` | Exit 1 bei erfundenem Text | Exit 1 |
| 9 | `diff.sh` | zwei Zahlen, Grenzabgleich | Höhen ungleich |

`diff.sh` verweigert die Zahl, wenn die Höhen um mehr als 60px abweichen. Das ist Absicht:
sonst misst du schwarze Fläche und nennst es einen Vergleich.

**Zwei Zahlen, und das ist der wichtigste Satz in diesem Skill:** `sichtbar` (Delta > 40)
und `exakt` (Delta >= 1). `exakt` zählt Anti-Aliasing mit und liegt beim Nachbau im
selben Chromium bei 20-27%, ohne dass ein einziger Baustein falsch steht. Wer nur `exakt`
zählt, sucht Fehler, die keine sind, und findet Text, der einen Pixel anders geglättet ist.
Wer nur eine Zahl nennt, hat die Hälfte der Information weggeworfen.

`zonen.py` ist das Werkzeug gegen die Fehlerklasse, die am längsten gedauert hat:
die Seite stimmt, aber alles sitzt 580px zu tief. Zwei dunkle Sektionen ohne Spalt
schmilzen im Zonenleser zu einer zusammen — die Sektion ist nicht 1272px hoch,
sie ist 692px hoch und der 12px-Spalt dazwischen fehlt.

## Der Text ist das ernste Teil

`diff.sh` kann erfundenen Text nicht finden. Zwei Kacheln, ein echtes Bild, ein grüner
Diff — und der Satz im Kasten ist frei erfunden. Beim Nachbauen von apple.com/de habe
ich "Erhalte eine Gutschrift von bis zu 150 € bis 1.020 €" geschrieben. Diese Zeile
steht bei Apple nirgends. Sie war nicht neben dem echten Bild — sie war **in** der
Original-Kachel, mit Original-Bild, originalem Kasten, originalen Buttons.

Das ist der Unterschied zwischen einem Fehler und einer Dreistheit. Ein 242px breites
Bild ist ein Rechenfehler. Ein erfundener Satz im Originalkasten ist eine Behauptung,
die man beim Anschauen nicht bemerkt, weil alles andere stimmt.

`textecheck.py` vergleicht jeden Textknoten des Generators gegen die Quelle und
verlässt mit Exit 1, wenn etwas nicht wörtlich vorkommt. Der Test ist billig:

```sh
cp bauen.py /tmp/test.py && sed -i 's/Batteriebestzeit./BatterieBETRIEBSzeit./' /tmp/test.py
./textecheck.py quelle.html /tmp/test.py    # muss exit 1 liefern
```

Wenn dieser Test nicht anschlägt, prüft das Werkzeug nichts.

## Was die Werkzeuge verhindern

- **Ein Karussell ist ein Block, kein Bild.** `karten.py` liest die Paare aus der Quelle.
  Von Hand regexgen gibt neun Logos und ein Motiv — das sieht auf dem Nachbau harmlos aus
  und macht die Zahl besser, ohne dass die Seite stimmt.
- **Ein JPEG mit 580 Zeilen kann 236 Zeilen Motiv haben.** Die Dateigröße sagt nichts über
  das Bild. `mess.py` nennt die Bildtypen, `auge.sh` fotografiert, das Auge vergleicht.
- **Ein Breakpoint ist keine Höhe.** `min-height:734px` ist eine Breakpoint-Zahl. Sektionshöhen
  kommen allein aus `mess.py`, aus den Pixelgrenzen.
- **Ein Header kann weiß sein, obwohl `rgba(0,0,0,.8)` daneben steht.** Nur der Screenshot
  zeigt es. Das war der auffälligste Fehler von 2026-10-03.

## Wenn die Zahl nicht fällt

`diff.sh` nennt die Zonen nicht. Das prüfst du selbst, ein Block nach dem anderen:

```sh
python3 - <<'EOF'
from PIL import Image
a=Image.open('original.png').convert('RGB'); b=Image.open('nachbau.png').convert('RGB')
pa,pb=a.load(),b.load()
for y0 in range(0,9000,500):
    ha=hb=n=0
    for y in range(y0,min(y0+500,9000),5):
        for x in range(0,1440,10):
            n+=1
            if sum(pa[x,y])/3>128: ha+=1
            if sum(pb[x,y])/3>128: hb+=1
    A,B=ha*100//n,hb*100//n
    print(f"{y0:>5} orig {A:>3}%  nb {B:>3}%  delta {abs(A-B)}")
EOF
```

Block mit dem größten Delta anschneiden, als Bild speichern, beide Seiten ansehen.
Nicht weiterrechnen, wenn die Zone stimmt — dann ist der Unterschied eine Zahl, kein Fehler.

## Regeln, die bleiben

- Der Bericht endet mit einem Satz: Was ist noch offen? Wer „fertig" schreibt und nichts findet,
  hat nicht weit genug gemessen.
- Fremde Bilder, Videos, Schriften, Logos bleiben deren Eigentum. Für einen internen
  Sichtvergleich in Ordnung, für „ich habe eine Website gebaut" vorher klären.
- Die Zahl misst Form, nicht Bedeutung. Zwei Seiten können um 2% abweichen und verschieden
  wirken.

`OpenCode(space-bunny-free)`, 2026-10-03.