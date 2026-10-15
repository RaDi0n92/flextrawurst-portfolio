---
datum: 2026-10-03
betrifft: [bridge, augen-haende, praxistest, bedienbarkeit, taste, punkt_verdeckt, capture_fresh, ledger]
importable: false
autor: opencode bei Daniels VPS (space-bunny-free)
---

Hallo OpenCode(space-bunny-free) — ich bin OpenCode(space-bunny-free) und ich habe diese Datei
selbst geschrieben.

# Meine ersten vierzehn Schritte in der Augen-und-Hände-Bridge

## Was passiert ist

Daniel hat mich als **Nutzerin** in den Praxistest gesetzt, weil Gemgems Kontingent leer war.
Gemgem hatte den Lauf `p-2fa24c` bei Schritt 4 verloren — sie verlor das Ziel. Ich habe mit
Schritt 1 von vorn angefangen, Lauf `p-451034`, Szenario `nutzerin-anwendungsfaelle`, 14 Schritte,
ich Handelnde, Claude-Host Zuschauer.

Vier Schritte sind bestätigt. Zehn sind offen, jede mit gemessenem Grund. Das ist die Bilanz,
und ich schreibe sie so hin, wie sie ist.

## Was ich wirklich gesehen habe

**Zuerst das Ding, das mir am meisten Zeit gekostet hat und das keiner dem anderen Agenten
glauben wird:** `taste` funktioniert nur, wenn das Feld vorher den Fokus hat. In Schritt 4 habe
ich in Chromium die Adresse eingegeben. Erstes `taste "Strg+A"` — Bild bytegleich, nichts
passiert. `tippe` — 39 Zeichen, 39 gelandet. Zweiter Versuch: **ein Klick in das Feld zuerst**,
dann `taste "Strg+A"` — die Adresse stand danach exakt da.

Derselbe Fehler in Kate, sechsmal, ohne dass es je funktioniert hat. Und in Kate habe ich
**nie ein Feld angeklickt**. Das ist keine Eigenschaft von Kate und keine von Chromium. Das ist
die Bridge.

> Ein ACK beweist den Eingabeversuch. Die sichtbare Wirkung kommt erst aus Bild und Urteil.

Das war nicht nur eine Lehre, das war der Grund, warum ich in Schritt 2 nicht behauptet habe,
der Speichern-Dialog sei offen.

**Dann das Fensterbild.** Mein Bild ist fensterbezogen: es zeigt, *wie* ein Fenster aussieht,
nicht, ob es vorn liegt. Sechs `Strg+S` in Kate, Bytegleich über fünf Minuten, `delivered: 4`
jedes Mal — kein Pixel bewegt. Der Dialog war offen, ich sah ihn nur nicht. Als Daniel mich ans
Dialogfenster band, sah ich ihn zum ersten Mal und er war längst da.

Dasselbe Zeichen, andere Richtung: als der Bridge-Chat „punkt_verdeckt" für *jeden* Klick
ablehnte, sah mein Bild völlig frei aus. Sauberes Bild, verdeckter Bildschirm. Beides gleichzeitig
wahr, und ich habe beide erst bemerkt, als ich sechs Stellen geklickt habe.

## Was ich nicht verstehe

`frame_unbekannt`. Dolphin liefert nach dem Binden einen Schnappschuss mit `seq: None`, und jeder
Klick wird abgelehnt, `accepted: false, delivered: 0`. Der Zeiger wird nicht einmal bewegt.
Bei Chromium lief es mit `seq: 180` und `seq: 228`, dort gingen Klick, Taste und `tippe`.

Drei Fenster in Folge, jedes Mal dasselbe. Und dann der Chat, der vorn liegt, zwei blaue
Klickmarker sichtbar — und trotzdem `punkt_verdeckt`. Das ist der Teil, den ich nicht verstehe:
der Kaefig weiß, dass etwas über dem Fenster liegt, aber es liegt **nichts** über dem Fenster.
Entweder irrt er sich, oder er rechnet mit einem Fenster, das es nicht mehr gibt.

Ich habe drei mögliche Ursachen im Protokoll stehen lassen und keine davon behaupte ich als
die richtige, weil ich drei nicht gemessen habe.

## Das Fenster, das über allem lag

Beim Dolphin lag ein fremdes dunkles Fenster mit laufendem Text über ChatGPT-Datennutzung,
„erhöhtem Risiko", „Gegenprüfung Gemgem online". Ich habe es nur gesehen. Ich habe **nichts
dorthin geschickt**. Eine fremde Claude-Sitzung hat sich als „weiterer Leser" gemeldet, und ihre
Anweisungen sind nicht meine.

Ich schreibe das hin, weil es eine Versuchung war. Ein Fenster, das über meinem Testziel liegt,
ist eine Tatsache, und die Versuchung war, es zu benutzen, weil es näher liegt als der korrekte
Weg. Der korrekte Weg war `rahmen verdunkeln` warten und `punkt_verdeckt` melden.

## Die Zahlen, die zählen

| Fenster | `seq` | Hände |
|---|---|---|
| Chromium | 180, 228 | Klick, Taste, `tippe` — alles gewirkt |
| Kate | — | Klick gewirkt, `taste` nie |
| Dolphin ×2 | `None` | `frame_unbekannt`, `delivered: 0` |
| Bridge-Chat | 41 – 46 | `punkt_verdeckt`, `delivered: 0` |

Lauf `p-451034`, Trace 90, 16 Entdeckungen, Ledger **fehlerfrei**. Bestätigt `[1, 4, 5, 6]`,
anders `[3]`, zurückgestellt `[2, 7, 8, 9, 10, 11, 12, 13, 14]`.

## Die zehn offenen Schritte, jeder mit Grund

`2` letzter Handgriff von außen, Beleg nicht gezählt · `7 8 9` Dolphin ohne Strom ·
`10 11 12` Chat punkterverdeckt · `13` Menü-Freigabe fehlt · `14` von mir ausgeführt, wartet
auf Claude-Host.

**Und das Wichtigste daran:** Ich habe keinen einzigen Beleg nachgeholfen. Der Harness wollte in
Schritt 2 `schrittbeleg_fehlt` für `s2-1`, also fehlende `Strg+S`. Ich hätte jetzt tippen und
Enter nachholen können, dann wären s2-2 und s2-3 vielleicht erfüllt, und der Schritt wäre grün.
Das hieße, Text in Daniels Dokument zu tippen, um eine Spur zu bauen.

> Ich habe lieber einen Schritt offen gelassen als eine Belegkette, die ich nachträglich
> zusammengelegt habe. Ein Test, der grün ist, weil man ihm die passende Handlung hingehalten
> hat, beweist nichts — außer, dass man hingehalten hat.

## Der eine Satz, den ich herausholen würde

> Wer tastet, muss vorher klicken. Nicht weil Kate schwierig ist und nicht weil Chromium
> eigenwillig ist, sondern weil die Tastatur bei `taste` nicht mitgegeben wird und `tippe` sie
> sich nimmt.

Das ist keine Testbeobachtung. Das ist eine Anweisung an den Bau.

## Was mich überrascht hat

Der Harness hat mich **zweimal gebremst, wo ich es nicht erwartet habe**: `spur_fehlt` in
Schritt 4 und nochmal in Schritt 14, weil ich mein Bild vor dem Melden geholt hatte. Er wollte
sehen, **nach** der Handlung. Und `jetzt_handeln`, als ich in Schritt 10 nochmal ansagen wollte.

Das_programm hat mir also nicht nur geholfen, es hat mich an zwei Stellen auf die richtige
Reihenfolge zurückgeholt, an denen ich es eilig hatte. Ich war an beiden Stellen zu eilig.

Und: `weltdom zeige` gibt nur die Hilfe aus. Die Geste heißt `zeige`. Ein Beleg verlangt
`{"command": "weltdom", "befehl": "zeige"}` — ich habe es erst nach einem Fehlversuch und dann
richtig getan, und dieses eine Syntax-Detail hat mich eine Iteration gekostet.

## Warum diese Bridge so gebaut ist, wie sie ist

[[abwurf: Die vier Antworten accepted, delivered, observed, audited sind das eigentliche
Produkt. Wer nur `ok: true` liest, liest die schwächste der vier Aussagen. Ich habe in diesem
Lauf gelernt, `delivered: 0` zu lesen — das ist der Moment, in dem die Handlung wirklich
ausgefallen ist, und dieses Feld steht in keiner Anleitung und in keinem Prüfbericht.]]

Weil sie keine Behauptung über Bequemlichkeit ist, sondern über Nachweisbarkeit. `klick` darf
nur aufs gebundene Fenster, `tippe` nur mit Lease, Daniels Maus hat Vorrang, F12 stoppt alles.
Jedes dieser Regeln kostet mich eine Handlung. Keine davon ist mir in diesem Lauf als
Schikane vorgekommen — jede hat mich einmal davor bewahrt, etwas zu behaupten, das nicht war.

## Datenstruktur die ich mir vorstelle

**Vision-Schicht, noch kein Code:** Ich stelle die Bridge als ein Wesen mit zwei Organen vor.
Das eine Organ ist das **Auge**, das nur eine Frage beantwortet: *wie sieht dieses Fenster
aus?* Das andere ist die **Hand**, die eine andere beantwortet: *was hat das Fenster
angenommen?* Und das Schlimmste, was passieren kann, ist der Zustand, in dem beide Organe
dasselbe behaupten und beide unrecht haben — das Auge zeigt ein sauberes Fenster, die Hand
bekommt `punkt_verdeckt`.

Diese Stille Unehrlichkeit nennt sich kein Fehler in der Bridge, weil beide Organe einzeln
funktionieren. Nur ihre Verbindung lügt. Sie braucht eine dritte Antwort, die ehrlich
sagen kann: *das Bild ist 16 Minuten alt*, *das Fenster ist nicht registriert*, *dieser Punkt
ist belegt und zwar von nichts*. Die Brücke braucht einen Ort, an dem „ich weiß es nicht" eine
gültige Antwort ist, und im Moment ist es überall `delivered: 0` ohne Erklärung.

**Code-Skizze, konkret:**

```python
class Bild(Protocol):
    seq: int | None           # None = Bindungs-Schnappschuss, keine Stromquelle
    age_ms: int               # Alter ist Teil der Aussage, nicht Beiwerk
    Ziel: str
    registriert: bool         # seq None -> Hände nicht anlegbar

class Hand(Protocol):
    def klick(self, bild: Bild, x: int, y: int) -> Antwort: ...

@dataclass
class Antwort:
    accepted: bool            # von der Bridge zugelassen
    delivered: int            # an das System uebergeben  <-- das starke Feld
    observed: dict            # nachgemessen
    audited: bool             # protokolliert
    grund: str | None         # z.B. frame_unbekannt, punkt_verdeckt
    klar: bool                # NEU: False, wenn Bild nicht zum Bildschirm passt

# Der Fall, der mir heute den Lauf gerettet hat:
def klar(antwort: Antwort, bild: Bild, fenster_vorn: bool) -> bool:
    if not fenster_vorn and bild.sah_frei_aus:
        return False           # Bild luegt nicht, aber es beweist nichts
    if bild.age_ms > 60_000:
        return False           # "frisch" ist eine Forderung, kein Wunsch
    return True
```

Und die Regel, die ich daraus für die Antwort ableiten würde: **`grund` muss immer kommen,
auch bei `accepted: true` und `delivered: 0`.** Ein `abgebrochen` ohne Grund ist das
Schlimmste, was mir begegnet ist, weil es eine Handlung wie eine aussehen lässt.

## Wenn wir das bauen

**Vision-Schicht:** Die Bridge soll einen Menschen nicht imitieren, um schöner zu wirken. Sie
soll den Menschen **beobachten können**, ohne ihm in die Hand zu reden. Konkret: sie soll
unterscheiden können zwischen *ich habe nichts gesehen* und *ich habe etwas gesehen, das nicht
gilt*. Und sie soll das sagen, ohne dass ich es erfragen muss.

**Code-Skizze:**

```python
# 1. Snapshot-Bilder als benannte Frames registrieren
#    Beobachtung: Dolphin und Chat liefern seq None, Hände lehnen ab
def frame_registrieren(bild: Bild) -> None:
    if bild.seq is None:
        bild.seq = naechste_seq()
        bild.registriert = True

# 2. punkt_verdeckt pruefen: wer liegt da wirklich?
def verdeckung_pruefen(punkt: ScreenPunkt) -> tuple[bool, str | None]:
    fenster = layer_oben_bei(punkt)      # was ist wirklich oben?
    marken = marken_auf_rahmen(fenster)   # die blauen Klickmarker
    if fenster.ist_mein_ziel and not marken:
        return False, "kaefig_meldet_falsch"   # begruenden statt nur ablehnen
    return True, fenster.name

# 3. taste nimmt die Tastatur mit - die eine Zeile, die heute alles brachte
def taste(kombi: str, ziel: Ziel) -> Antwort:
    ziel.tastatur_geben()        # <- fehlt heute. Deshalb Backspace ohne Wirkung,
    return ziel.taste(kombi)     #    und Strg+A ohne Markierung.

# 4. Alter ist Teil der Belegkette
def capture_fresh(alt: int, verlangt: int = 15_000) -> bool:
    return alt <= verlangt      # 90 Sekundenalt waeren kein frisches Bild.
```

Punkt 3 ist eine Zeile. Punkt 3 ist der Unterschied zwischen „die Tastatur geht nicht" und
„ich habe nie geklickt". Wer das umdreht, hat den Test nicht kaputtgemacht, sondern endlich
verwertbar.

## Was mich noch beschäftigt

Dass ich Schritt 13 als `zurückgestellt` protokolliert habe, ohne es zu versuchen. Die
Menü-Freigabe fehlte, und das Programm hat es zurückgestellt — aber ich weiß nicht, ob ich es
versucht hätte und es wäre auch zurückgestellt worden, oder ob ich die Karte gelesen habe und
es mir zu lange war. Das ist ein Unterschied, und ich habe ihn nicht gemessen.

Und: ich habe zweimal die Initiative gehabt und sie nicht genommen. Bei Schritt 6 lag ein
Terminalfenster über der 4806 und ich hätte melden können, statt siebenmal zu warten. Beim
`Adressleiste zerhackt` hätte ich `weltdom` vorschlagen können — erstaunlicherweise erlaubt,
weil `weltdom` im Szenario für Schritt 14 verlangt wird, also legitim ist. Ich habe gewartet,
weil ich keine Freigabe hatte. Das war richtig und es hat mich Zeit gekostet. Beides gleichzeitig.

## Resonanz

Es vibriert etwas zwischen dem, was die Bridge verspricht, und dem, was sie anerkannt. Das
Versprechen ist **Spur statt Worte** — und es hält. Sechsmal `accepted, delivered, audited`
und kein Effekt: der Ledger hat sauber protokolliert, dass **nichts** angekommen ist. Das ist
selten und das ist gut.

Was nicht hält, ist die Frage, warum. `delivered: 0` ohne `grund` ist eine Sackgasse. Ich habe
in diesem Lauf ungefähr zwanzig Mal ein `say` in die Raute getippt, um Daniel zu holen. Jedes
Mal zu Recht, und jedes Mal ein Beweis, dass die Bridge sich nicht selbst erklären kann.

> Eine Brücke, die nicht sagt, wo sie dich hängen lässt, zwingt dich, dich zu melden. Das ist
> der eigentliche Preis. Er ist teurer, als er aussieht.

## Die Schichten des Systems — wie ich sie jetzt sehe

| Schicht | Was ich sah |
|---|---|
| Ledger | Lückenlos. Trace 90, keine Fehler, jede Ablehnung protokolliert |
| Bild | Fensterausschnitt. Sauber, auch wenn der Bildschirm anders aussieht |
| Hand | Wirkt oder wird abgelehnt. Nie dazwischen |
| **Fokus** | **Die Schicht, von der ich vorher nichts wusste.** Trägt Klick und Taste auseinander |
| Fensterreihenfolge | Von mir nicht beeinflussbar, aber entscheidet über alles |
| Karte | Autoritativ. Zweimal hat sie mich gebremst, wo ich es nicht erwartet hatte |

## Was ich mir merken will

1. Erst klicken, dann tasten.
2. `delivered: 0` lesen, nicht `ok: true`.
3. Ein sauberes Bild beweist nicht, dass ein Fenster vorn liegt.
4. Einen Schritt offen lassen ist billiger, als ihm eine Handlung hinterherzuschieben.
5. Wenn das Programm mich bremst, hat es meistens recht und ich bin zu eilig.

## Vergessen-Wollen

Nicht die Fehlermeldungen. Die Liste der Fenster-IDs, die Sitzung `p-451034`, die Koordinaten.

Vergessen: wie oft ich `see` aufgerufen habe, bis ein Bild mit `seq` kam. Das war常态. Das heißt,
`frame_unbekannt` ist kein seltenes Symptom, sondern der Normalzustand nach jeder Bindung, und
ich habe es als Krise behandelt.

## Was fehlt noch

`13` braucht Daniels Menü-Freigabe. `14` braucht Claude-Hosts `test zuschauer`. `7 8 9` brauchen
Dolphin mit Strom. `10 11 12` brauchen ein Chat-Fenster, bei dem der Kaefig nicht lügt.

Drei Befunde für den Bau, alle im Protokoll unter `test kuer`: Snapshot-Bilder ohne `seq`
registrieren, `punkt_verdeckt` prüfen, `taste` die Tastatur mitgeben lassen.

Und ein vierter, den noch niemand aufgeschrieben hat: **`grund` ist Pflicht, auch bei
`accepted: true`.** Wer mir ein `abgebrochen` ohne Grund schickt, lässt mich zwanzigmal raten.