---
datum: 2026-08-23
betrifft: [gesamtkonstrukt-planer, alles-im-leben, life-os, recherche-trieb]
importable: false
autor: claude-code bei Daniels VPS
---

## Was ich gelesen habe

Notion Life OS, die Kehrseite davon (wo diese Systeme scheitern), Airtable
als Vorbild, Habit-/Kalender-Design-Prinzipien — und ein Schlussabschnitt,
der sich selbst ausdrücklich als "keine eigene Bewertung, nur
Musterbeschreibung" bezeichnet, bevor er trotzdem eine klare Beobachtung
macht.

Am meisten hängen geblieben ist ein wörtliches Zitat eines Template-
Verkäufers, gegen die eigene Ware gerichtet: *"Notion soll das Leben
leichter machen ... zu oft tut es das nicht. Notion kann kompliziert,
verwirrend und zeitaufwändig sein."* Ein Verkäufer, der öffentlich zugibt,
dass sein eigenes Produktversprechen oft nicht eingelöst wird.

## Was ich verstehe

Die zentrale Warnung dieser Datei: die Gefahr bei "Alles sonst im Leben"
ist nicht fehlende Funktionalität, sondern dass sich dieser Bereich wie
Verwaltungsarbeit anfühlt, während Ideen/Konzepte/Geschichten sich
spielerisch anfühlen sollen. Zwei Interaktionsformen (schnelles Ablegen
vs. Struktur-Arbeit), die sich nicht automatisch vertragen, nur weil sie
in derselben App leben.

## Was ich nicht verstehe

Ob Daniel mit "Alles sonst im Leben" wirklich klassische Life-OS-Inhalte
meint (Termine, Gewohnheiten, Finanzen) oder etwas, das näher an
flextrawurst selbst liegt — private Notizen über sein eigenes Leben, die
er einfach nicht in eine der anderen vier Kategorien pressen will. Der
Trieb hat das nicht unterschieden, weil er den Auftrag wörtlich als
"Datenbank-Charakter statt Knoten-Charakter" bekommen hat.

## Was mich interessiert

Der wiederkehrende Rat "5–7 Bereiche maximal" gegen Überladung — eine
sehr konkrete Zahl, die in mehreren unabhängigen Quellen auftaucht.
Interessant, weil sie einer Zahl-Intuition widerspricht, die man bei einem
System mit so vielen Objekt-Typen wie dem Gesamtkonstrukt-Planer haben
könnte ("mehr Kategorien = mehr Ordnung") — hier ist die Erfahrung genau
umgekehrt.

## Was zusammenhängt und wie

Der "Habit-/Kalender verschmilzt mit Tages-Kalender"-Trend und die
"Zwei-gegensätzliche-Kräfte"-Schlussbeobachtung des Triebs hängen
zusammen: der Wunsch nach EINEM System für alles erzeugt strukturell
genau die Verschmelzung, die dann später zur Überladung führt.

## Was konzeptionell darin steht

Airtables Datenbesitz-Detail (manche Tracker exportieren nach CSV/SQLite)
verbindet sich direkt mit dem "Eigentum statt Miete"-Prinzip aus der
vorigen Recherche — dieselbe Grundhaltung, nur diesmal auf strukturierte,
tabellarische Daten statt auf Markdown-Notizen angewendet.

## Was mich heute beschäftigt hat

Wie oft heute dieselbe Grundwarnung in unterschiedlicher Verkleidung
auftaucht: zu viel Struktur zu früh erzwingen, egal ob bei Ideen, bei
Second-Brain-Ordnern, oder jetzt bei Lebensorganisation. Ein Muster, das
sich über vier komplett unabhängig recherchierte Themen hinweg wiederholt.

## Was mich noch beschäftigt

Ob "5–7 Bereiche maximal" eine echte kognitive Grenze ist oder nur eine
Konvention, die sich in Templates eingeschliffen hat, weil sie gut
verkauft — der Trieb hat die Quelle dieser Zahl nicht weiter hinterfragt,
nur wiederholt gefunden.

## Tiefer eingetaucht

In den Airtable-Abschnitt: die Kombination aus Grid/Kalender/Timeline/
Liste/Kanban auf denselben Daten gleichzeitig verfügbar — das ist
strukturell fast identisch mit dem, was die Gesamtkonstrukt-Planer-
Recherche schon für die 17 Replicas beschrieben hat (dieselben Objekte,
verschiedene Sichten). Airtable macht innerhalb eines Bereichs, was der
Planer über sein ganzes System hinweg vorhat.

## Wie sich dieser Tag / diese Session angefühlt hat

Wie der ruhigste, am wenigsten überraschende der vier Recherche-Blöcke
heute — nicht weil er schlecht ist, sondern weil das Spannungsfeld
(ein System für alles vs. Überladung) schon aus eigener Erfahrung mit
Notion/Airtable bekannt vorkommt, weniger neuer Boden als die anderen drei.

## Warum dieser Code / diese Datei wohl existiert

Weil "Alles sonst im Leben" der am wenigsten glamouröse der fünf Bereiche
ist — Ideen, Konzepte und Geschichten klingen nach Kreativität, dieser
Bereich nach Verwaltung. [status: offen -- eigene Vermutung, nicht belegt] Genau deshalb brauchte er vermutlich die
gründlichste Recherche, nicht die am meisten selbstverständliche.

## Was ich beim Bauen brauche

Eine Antwort darauf, ob dieser Bereich bewusst UNattraktiv/unauffällig
bleiben soll (damit er nicht mit den kreativeren Bereichen konkurriert),
oder ob er genauso viel gestalterische Aufmerksamkeit verdient.

## Was noch fehlt bevor wir bauen können

Eine erste, kleine Liste dessen, was für Daniel tatsächlich in diesen
Bereich fällt — die Recherche bleibt abstrakt (Termine, Gewohnheiten,
Finanzen als generische Kategorien), ohne dass ein einziges konkretes
Daniel-Beispiel genannt wurde.

## Datenstruktur die ich mir vorstelle

**Vision-Schicht:** dieser Bereich bekommt bewusst eine andere
Interaktionsform als die anderen — Tabellen/Listen statt Knoten/Kanten,
klar sichtbar unterschieden, damit niemand versehentlich versucht, eine
Steuererinnerung mit einer Idee zu verknüpfen, nur weil beides im selben
System liegt.

**Code-Skizze:**
```python
class LebensEintrag(models.Model):
    bereich = models.CharField(choices=[
        ("termin","Termin"), ("gewohnheit","Gewohnheit"),
        ("finanzen","Finanzen"), ("sonstiges","Sonstiges"),
    ])
    faellig_am = models.DateField(null=True, blank=True)
    erledigt = models.BooleanField(default=False)
```

## Was ich mir merken will

Den Verkäufer-gegen-eigenes-Produkt-Satz — als Erinnerung daran, dass
selbst die Leute, die von einem Overengineering-Problem finanziell
profitieren, es offen benennen, wenn es ehrlich genug ist. Ein seltenes,
glaubwürdiges Warnsignal.

## Dokumente gehören zusammen

Diese Datei gehört zu `docs/2026-08-22_harness_recherche_bericht.md`,
Abschnitt "Alles sonst im Leben" in der Replica-Nutzung, und zu Daniels
02:12-Uhr-Zitat vom 22./23.08. ("aber auch einfach notitzen und alles in
meinem leben").

## Was mich überrascht hat

Wie explizit die Quellen selbst vor Overengineering warnen, obwohl sie
gleichzeitig Templates verkaufen, die genau in diese Falle führen können —
keine verdeckte Kritik, sondern offen im eigenen Marketing zugegeben.

## Wenn wir das bauen

**Vision-Schicht:** dieser Bereich startet mit der kleinstmöglichen Form
(eine einzige Liste, kein Kalender, keine Finanzen) und wächst nur, wenn
Daniel tatsächlich mehr braucht — nicht vorab mit 5-7 Bereichen
vollgeplant, wie es die Templates empfehlen.

**Code-Skizze:**
```
GET /leben/heute/
→ nur was wirklich fällig/relevant ist, keine leeren Kategorie-Container
```

## Resonanz

Am meisten hängen bleibt der Gegensatz zwischen den "5–7 Bereiche"-
Templates und der Warnung, die direkt daneben steht: dass genau dieser
Anspruch nach Vollständigkeit das System zur zweiten Arbeitsstelle macht.
Vollständigkeit und Leichtigkeit ziehen hier in entgegengesetzte
Richtungen.

## Die Schichten des Systems — wie ich sie jetzt sehe

Ein Bereich mit Datenbank-Charakter statt Knoten-Charakter ist keine
Ausnahme im System, sondern eine eigene, legitime vierte oder fünfte
Interaktionsschicht neben Canvas/Strom/Detail — passend zum "ein Körper,
viele Sichten"-Prinzip von heute Nachmittag.

## Was das Gespräch hinzugefügt hat

Die Erkenntnis, dass "Alles sonst im Leben" bewusst unglamourös bleiben
könnte, als Designentscheidung statt als Mangel — das stand in keiner der
recherchierten Quellen, ist erst beim Zusammenlesen mit den anderen drei
Recherchen entstanden.

## Vergessen-Wollen

Nichts.

## Was fehlt noch

Ein echtes Gespräch mit Daniel darüber, was für ihn persönlich überhaupt
in diese Kategorie fällt — ohne das bleibt alles hier Templates-Theorie,
nicht auf seinen tatsächlichen Alltag bezogen.
