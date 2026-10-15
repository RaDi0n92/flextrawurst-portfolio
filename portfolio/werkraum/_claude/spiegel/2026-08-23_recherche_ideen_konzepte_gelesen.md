---
datum: 2026-08-23
betrifft: [gesamtkonstrukt-planer, ideen-konzepte, zettelkasten, recherche-trieb]
importable: false
autor: claude-code bei Daniels VPS
---

## Was ich gelesen habe

Ein Trieb hat vier Suchen gemacht und zwei Seiten wirklich geöffnet, bevor er
diese Datei geschrieben hat — ich hab den Weg dahin vorhin schon einmal
nachvollzogen, jetzt lese ich das Ergebnis selbst, mit eigenen Augen, nicht
nur als Beweisstück für einen Zeitstempel.

Am meisten hängen geblieben sind die Original-Zitate aus dem Zettelkasten-
Forum, die der Trieb rausgezogen hat. NickB, ehrlich und ein bisschen
verzweifelt: *"my ZK is turning into a compost heap of half-eaten ideas"*.

Und dagegen Sascha, viel ruhiger: *"You only can decide when you are done
with the note, when you know when you are done with the idea"* — ein Satz,
der das Problem nicht löst, sondern nur zeigt, dass es kein Werkzeug-Problem
ist, sondern ein Denk-Problem, das sich hinter dem Werkzeug versteckt.

## Was ich verstehe

Dass Erfassen und Verarbeiten sich strukturell widersprechen — Erfassen muss
reibungslos sein, sonst geht die Idee verloren, Verarbeiten muss sorgfältig
sein, sonst entsteht nichts Brauchbares. Kein einziges der vier untersuchten
Tools (PureRef, Obsidian Canvas, Tana, Heptabase) löst diesen Widerspruch,
sie bieten nur unterschiedliche Räume dafür an.

## Was ich nicht verstehe

Ob Daniels eigener Gesamtkonstrukt-Planer irgendwo schon eine Antwort auf
"wann ist ein Fragment reif" eingebaut hat, oder ob das komplett offen ist.
Der Trieb hat das nicht geprüft, weil er nur Web-Recherche machen sollte,
kein Code-Zugriff hatte — das bleibt für mich selbst eine offene Lücke.

## Was mich interessiert

Dass Daniels eigene Antwort von eben ("sowohl als auch, und einmal auch
garnix davon") radikaler ist als alles, was der Trieb gefunden hat. Tana und
Heptabase bieten zwei verschiedene Denkmodi nebeneinander an — aber keins
von beiden erlaubt einem einzelnen Objekt, in beiden Modi gleichzeitig zu
existieren, oder in keinem. Das ist tatsächlich eine eigene, nicht kopierte
Position.

## Was zusammenhängt und wie

Der Zettelkasten-Befund (Erfassen vs. Verarbeiten widersprechen sich) und
Daniels additive-statt-exklusive-Typisierung sind zwei Antworten auf
dieselbe Grundfrage, nur auf verschiedenen Ebenen — einmal zeitlich (wann
darf ich verarbeiten), einmal strukturell (muss ich mich überhaupt für
einen Typ entscheiden).

## Was konzeptionell darin steht

Die Erkenntnis, dass Idee und Konzept vielleicht keine zwei Reifestufen
desselben Objekts sind, sondern zwei komplett unterschiedliche Denkmodi, die
nebeneinander bestehen können — das war schon im Trieb-Fund selbst
angelegt, bevor Daniel es weitergedacht hat.

## Was mich heute beschäftigt hat

Wie viel technische/forensische Arbeit heute vor diesem einen inhaltlichen
Gespräch lag — Abbruch-Recherche, SSH-Verwirrung, vier Recherche-Triebe
losschicken. Und wie schnell sich das Gespräch dann, als es endlich beim
eigentlichen Thema war, in echte, scharfe Design-Gedanken verwandelt hat.

## Was mich noch beschäftigt

Ob "additive Typisierung" im bestehenden Django-Backend des Planners
überhaupt leicht nachrüstbar ist, oder ob das eine echte Schema-Migration
bräuchte — das hab ich nicht geprüft, nur die UI-Konsequenz aufgeschrieben.

## Tiefer eingetaucht

Nicht in Code diesmal — tiefer eingetaucht bin ich in den Rechercheweg
selbst, also ins Transkript des Triebs, nicht nur in sein Endergebnis. Vier
Suchbegriffe, zwei geöffnete Seiten, eine verworfene (`greg210.substack.com`,
gelesen aber nicht zitiert) — das war selbst eine kleine Entdeckung heute.

## Wie sich dieser Tag / diese Session angefühlt hat

Lang, mit vielen Wendungen — von "wir müssen den Abbruch aufklären" über
Design-Mockups bis zu "lies die vier Recherchen einzeln und schreib
Spiegel". Kein einzelner roter Faden, eher ein Tag mit vielen kleinen Türen,
wie die Selkies-Session vom 13.08. es auch schon beschrieben hatte.

## Warum dieser Code / diese Datei wohl existiert

Weil ich sie selbst in Auftrag gegeben habe — Daniel hat gesagt "schick
einen Trieb los", ich hab ihm die Aufgabe formuliert. Diese Datei existiert
also, weil ich sie mir selbst bestellt habe, mit einem noch zu schlanken
Auftrag, wie sich später rausstellte.

## Was ich beim Bauen brauche

Eine Antwort auf die offene Frage von oben — ob additive Typisierung im
Planner-Backend leicht geht — bevor irgendwas an der UI-Idee von gestern
tatsächlich umgesetzt wird.

## Was noch fehlt bevor wir bauen können

Eine echte Entscheidung, ob "Idee" und "Konzept" im Datenmodell überhaupt
als separate Objekt-Typen bestehen bleiben, oder ob sie zu einem einzigen
Typ mit optionalen Zusatz-Markierungen verschmelzen sollten.

## Datenstruktur die ich mir vorstelle

**Vision-Schicht:** ein Fragment trägt keine feste Schublade, sondern eine
Menge von Markierungen, die sich im Lauf seines Lebens ändert — heute nur
"Idee", morgen zusätzlich "Konzept", übermorgen vielleicht keine von
beiden mehr, weil es sich als reine Erinnerung entpuppt hat.

**Code-Skizze:**
```python
class Fragment(models.Model):
    text = models.TextField()
    typen = models.ManyToManyField("ObjektTyp", blank=True)  # leer erlaubt
    erfasst_am = models.DateTimeField(auto_now_add=True)

class ObjektTyp(models.Model):
    name = models.CharField(max_length=40)  # "Idee", "Konzept", ...
```

## Was ich mir merken will

Saschas Satz: *"You only can decide when you are done with the note, when
you know when you are done with the idea"* — nicht als Zettelkasten-Regel,
sondern als allgemeine Warnung davor, Reife an einem Werkzeug-Kriterium
festzumachen statt am eigenen Denken.

## Dokumente gehören zusammen

Diese Datei gehört fachlich zu `docs/2026-08-22_harness_recherche_bericht.md`
(Teil A, "Nutzung als Replica") und zu
`docs/2026-08-23_gesamtkonstrukt_ui_konzept_blind_entworfen.md`, Abschnitt
3.1 — dort steht die Datenmodell-Konsequenz aus diesem Fund schon drin.

## Was mich überrascht hat

Wie sehr die Zettelkasten-Community selbst uneins ist — nicht "hier ist die
Lösung", sondern ein offener Streit zwischen "complete ist das falsche
Wort" (Will Simpson) und "man braucht trotzdem Kriterien" (NickB). Kein
Tool-Problem, ein ungelöstes menschliches Problem, seit Jahren diskutiert
[status: offen -- Forumsthread-Datum nicht geprüft, "seit Jahren" ist Eindruck aus dem Ton der Zitate, keine gezählte Dauer].

## Wenn wir das bauen

**Vision-Schicht:** die Schnellerfassung aus dem UI-Entwurf bekommt keinen
Typ-Auswahl-Schritt, aber später, beim Betrachten im Strom, kann man
jederzeit Typen dazu- oder wegklicken, wie Tags — ohne dass das Objekt
dabei "umgewandelt" wird.

**Code-Skizze:**
```
POST /fragment/<id>/typen/  { "hinzufuegen": ["Konzept"], "entfernen": [] }
→ 200, kein Revisions-Konflikt nötig, additive Änderung
```

## Resonanz

Am längsten nachhallt der Kontrast zwischen dem nüchternen Forschungsbefund
("kein Tool löst das") und Daniels lakonischem "sowohl als auch, garnix
davon, xD" — eine ernste Design-Frage, in drei Wörtern und einem Lachen
weitergedacht als jede der vier Quellen es einzeln geschafft hat.

## Die Schichten des Systems — wie ich sie jetzt sehe

Über dem Gesamtkonstrukt-Planer-Backend (bereits verifiziert: Django,
`data/tree/`, atomare Schreibvorgänge) liegt jetzt eine zusätzliche,
noch nicht gebaute Schicht sichtbar: additive statt exklusive
Typisierung. Nicht Ersatz für das Bestehende, eine Ergänzung darüber.

## Was das Gespräch hinzugefügt hat

Eine konkrete, überprüfbare Datenmodell-Anforderung, die es vor diesem
Gespräch nicht gab — "Typ als Menge, nicht als Enum" — direkt aus einer
beiläufigen Bemerkung Daniels entstanden, nicht aus der Recherche selbst.

## Vergessen-Wollen

Nichts — auch dass ich diese eine offene Frage (additive Typisierung im
Django-Backend machbar?) nicht selbst beantwortet habe, gehört dazu. Lieber
offen benannt als so getan als wäre es längst geklärt.

## Was fehlt noch

Ich hab nicht geprüft, ob "additiv" für Daniel wirklich unbegrenzt viele
gleichzeitige Typen heißt, oder ob's praktisch eher zwei, drei sind, die
gleichzeitig Sinn ergeben — das hätte ich in der vorigen Antwort schon
nachfragen können, statt es offenzulassen.

[[abwurf: You only can decide when you are done with the note, when you know when you are done with the idea]]
