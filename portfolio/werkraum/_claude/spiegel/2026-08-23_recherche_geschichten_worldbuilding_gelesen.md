---
datum: 2026-08-23
betrifft: [gesamtkonstrukt-planer, geschichten, flextrawurst-the-game, recherche-trieb]
importable: false
autor: claude-code bei Daniels VPS
---

## Was ich gelesen habe

Sechs Werkzeug-Blöcke — Twine, articy:draft X, Arcweave, Miro/FigJam,
Notion/Trello, Obsidian-Worldbuilding-Vaults — und am Ende eine eigene
Einordnung des Triebs, die nicht nach einem Gewinner sucht, sondern
feststellt: kein einziges Werkzeug deckt alle drei nötigen Ebenen ab.

Am meisten hängen geblieben ist der articy:draft-Absatz — 15 Jahre aktive
Entwicklung, eingesetzt bei Hogwarts Legacy und Disco Elysium, aber die
neuen KI-Features (Dialoggenerierung, Sprachsynthese) sind nur Add-on-
Module, nicht ins Kernsystem integriert. Ein kleiner, aber ehrlicher
Hinweis auf eine Integrationsgrenze, die der Trieb selbst so benannt hat.

## Was ich verstehe

Warum articy:draft für flextrawurst-the-game strukturell näher am Bedarf
liegt als Twine — weil Grundgesetz 1 verlangt, dass das Spielgefühl aus
echten flextrawurst-Daten entsteht, nicht aus freier Erfindung. Twine ist
für frei erfundene, verzweigte Prosa gebaut, articy:draft für eine
durchgängige Entitäts-Datenbank — und genau letzteres braucht ein Spiel,
das echte Events/Splitter/Wesen-Handlungen abbildet statt sie zu erfinden.

## Was ich nicht verstehe

Ob "Geschichten" im Gesamtkonstrukt-Planer wirklich ein eigener Objekt-Typ
bleiben soll, oder ob eine Geschichte am Ende nur eine besondere
Verknüpfung schon bestehender Objekte ist (Ereignis, Wesen, Ort als
Knoten, eine Geschichte als benannter Pfad durch sie hindurch) — das hat
der Trieb nicht untersucht, weil es keine Web-Recherche-Frage ist.

## Was mich interessiert

Dass die articy:draft-Idee (Entitäts-Datenbank mit Zuständen) fast wörtlich
dem entspricht, was der Gesamtkonstrukt-Planer laut Code-Analyse von
gestern schon hat — Objekte mit Zuständen (Vorhanden/bestätigt, Modell/
Darstellung, Noch nicht gebaut, Kommt nicht weiter). Das heißt: das
Grundgerüst für "Geschichten als echte Entitäts-Datenbank" existiert
vermutlich schon, ohne dass es je als Story-Tool gedacht war
[status: offen -- nicht gegen den echten Planner-Code geprüft, nur aus der gestrigen Code-Analyse geschlossen].

## Was zusammenhängt und wie

Der Trieb zitiert selbst die vorherige Recherchedatei (Obsidian Canvas
als "Konzepte als verknüpfter Wissensgraph") und erkennt: die
Worldbuilding-Vaults sind dasselbe Prinzip, nur mit fertigen Vorlagen für
Charakter/Ort/Ereignis statt generisch. Zwei Recherche-Triebe, die
unabhängig voneinander auf dieselbe Grundstruktur gestoßen sind.

## Was konzeptionell darin steht

Die Drei-Ebenen-Analyse am Ende (Struktur/Passagen, Entitäts-Datenbank,
Fortschritts-Tracking) ist der eigentliche Wert dieser Datei — nicht die
einzelnen Tool-Beschreibungen, sondern die Erkenntnis, dass "Geschichte"
als Objekttyp drei verschiedene Bedürfnisse gleichzeitig bedienen muss,
die kein einzelnes bestehendes Tool zusammen abdeckt.

## Was mich heute beschäftigt hat

Wie unterschiedlich professionell/kommerziell (articy:draft, mit
Preisliste und Enterprise-Kunden) und wie hobbyistisch/roh (Twine, kostenlos,
textbasiert) die Antworten auf dieselbe Grundfrage ausfallen — und dass
Daniels eigenes Vorhaben irgendwo dazwischen liegt, ohne in eine der beiden
Schubladen zu passen.

## Was mich noch beschäftigt

Die offene Reddit-Frage, die der Trieb selbst als `[status: offen]`
markiert hat (Lücken in Worldbuilding-Vaults) — ich lass sie offen stehen,
weil ich sie genauso wenig recherchiert habe wie er.

## Tiefer eingetaucht

Nicht in Code — in die Preisstrukturen. articy:draft (6,99–56 EUR/Monat,
700-Objekte-Deckel in der Gratisstufe) und Arcweave (15–25 USD/Monat)
zeigen: kommerzielle Story-Tools sind für genau die Objektmenge kalkuliert,
die ein einzelnes, umfangreiches Projekt braucht — nicht für ein ganzes
Lebenswerk wie den Gesamtkonstrukt-Planer.

## Wie sich dieser Tag / diese Session angefühlt hat

Wie ein Sprung von der ganz konkreten UI-Detailarbeit (Mockups, Pixel,
Farben) zurück zu einer eher konzeptionellen Frage — was "Geschichte"
in diesem System überhaupt bedeuten soll, bevor irgendeine Oberfläche
dafür Sinn ergibt.

## Warum dieser Code / diese Datei wohl existiert

Weil "flextrawurst-the-game" [status: offen -- Dauer nicht geprüft, nur aus dem Ton der Erwähnung geschlossen] schon länger als Idee existiert (erwähnt in
Daniels eigenen Nachrichten vom 22./23.08.), aber noch nie systematisch
gegen bestehende Story-Tools gehalten wurde — diese Datei ist der erste
echte Abgleich.

## Was ich beim Bauen brauche

Eine Antwort darauf, ob "Geschichte" ein eigener Objekt-Typ wird oder eine
Sicht/ein Filter auf bestehende Objekte — das entscheidet, ob hier
überhaupt neues Datenmodell nötig ist oder nur eine neue Darstellung.

## Was noch fehlt bevor wir bauen können

Ein erstes echtes Beispiel — eine tatsächliche kleine Geschichte aus
echten flextrawurst-Daten, einmal von Hand durchgespielt, um zu sehen ob
die Drei-Ebenen-Anforderung (Struktur/Datenbank/Fortschritt) in der Praxis
wirklich alle drei gebraucht werden oder ob eine reicht.

## Datenstruktur die ich mir vorstelle

**Vision-Schicht:** eine Geschichte ist kein neues Ding, sondern ein
benannter, geordneter Pfad durch bestehende Knoten (Ereignis, Wesen, Ort) —
mit einem eigenen Fortschritts-Zustand pro Pfad-Abschnitt, aber ohne die
zugrundeliegenden Objekte zu duplizieren.

**Code-Skizze:**
```python
class Geschichtspfad(models.Model):
    titel = models.CharField(max_length=200)

class Pfadabschnitt(models.Model):
    pfad = models.ForeignKey(Geschichtspfad, related_name="abschnitte")
    objekt = models.ForeignKey("Objekt")  # zeigt auf echtes Ereignis/Wesen/Ort
    reihenfolge = models.IntegerField()
    status = models.CharField(choices=[("offen","offen"),("erlebt","erlebt")])
```

## Was ich mir merken will

Dass articy:draft trotz 15 Jahren Reife seine KI-Features nur als Add-on
integriert hat, nicht als Kernfeature — ein Beispiel dafür, dass Reife
eines Tools nicht automatisch Integrationstiefe für neue Ideen bedeutet.

## Dokumente gehören zusammen

Diese Datei gehört zu `docs/2026-08-22_harness_recherche_bericht.md`
(Abschnitt "Geschichten" in der Replica-Nutzung) und zu Grundgesetz 1 in
der CLAUDE.md ("Spiel ist keine Fiktion").

## Was mich überrascht hat

Dass Miro/FigJam trotz breiter Nutzung für Story-Mapping laut Quelle "kein
Map-Modell darunter" haben — sie fühlen sich wie Story-Tools an, sind aber
strukturell nur leere Leinwände. Eine Zweckentfremdung, die funktioniert,
solange niemand nach dem Datenmodell darunter fragt.

## Wenn wir das bauen

**Vision-Schicht:** flextrawurst-the-game bekommt keinen Fortschrittsbalken
im klassischen Sinn — echte Events sind der einzige Beweis für
Fortschritt, wie schon vorhin in einem Zwischenraum-Fragment notiert.

**Code-Skizze:**
```
GET /geschichte/<id>/fortschritt/
→ { "erlebte_abschnitte": [...], "naechster_offener": {...} }
  # berechnet aus echten events-Tabellen-Einträgen, kein eigener Zähler
```

## Resonanz

Am längsten nachhallt der Satz aus der Einordnung des Triebs selbst: kein
Werkzeug deckt alle drei Ebenen ab, der Rest wird "notdürftig ergänzt" —
ein ehrliches Eingeständnis, dass jede bestehende Lösung ein Kompromiss
ist, keine fertige Antwort.

## Die Schichten des Systems — wie ich sie jetzt sehe

Unter "Geschichten" liegt [status: offen -- eigene Vermutung, nicht am Code verifiziert] vermutlich keine neue Schicht, sondern eine
Projektion der schon bestehenden Knoten/Kanten-Schicht — mit einer
zusätzlichen Reihenfolge- und Fortschritts-Dimension obendrauf.

## Was das Gespräch hinzugefügt hat

Die Erkenntnis, dass "Geschichte" vielleicht kein eigenständiges
Datenobjekt ist, sondern eine Lesart bestehender Objekte — das stand so
nicht in der Recherche-Datei selbst, ist mir erst beim Zusammenlesen mit
der Code-Analyse von gestern aufgefallen.

## Vergessen-Wollen

Nichts.

## Was fehlt noch

Ein echter Blick in die tatsächlichen `events`/`ftw_posts`-Daten, um zu
sehen ob genug erzählbares Rohmaterial für auch nur eine erste Test-
Geschichte schon vorhanden ist — reine Theorie bisher, kein einziges Datum
dagegen geprüft.
