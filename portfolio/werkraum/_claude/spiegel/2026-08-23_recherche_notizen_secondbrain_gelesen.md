---
datum: 2026-08-23
betrifft: [gesamtkonstrukt-planer, megavault, gesamtatlas, second-brain, recherche-trieb]
importable: false
autor: claude-code bei Daniels VPS
---

## Was ich gelesen habe

PARA, reiner Markdown-Zettelkasten, Obsidian-Ordner-vs-Tags-vs-Links,
Maps of Content, Logseq im Vergleich, Notion an seinen Grenzen — und ganz
am Ende ein Abschnitt, den der Trieb selbst als "eigene Einordnung, kein
Fund" markiert hat, nicht als Web-Recherche getarnt.

Der Satz, der am längsten nachhallt, kam nicht aus einer Quelle, sondern
war die eigene Schlussfolgerung des Triebs: ein reines Dateisystem aus
Markdown-Dateien trifft Daniels "direkt editierbar löschbar bearbeitbar
verschiebbar offenbar"-Anforderung, weil es exakt das ist, was ein
Dateisystem ohnehin schon kann, ohne App-eigenes Format dazwischen.

## Was ich verstehe

Warum Ordner "wohin gehört das" beantworten und Tags "worum geht es" — und
warum das kein beliebiges Vorlieben-Detail ist, sondern der Kern der
2026er-Praxis: höchstens zwei Ordner-Ebenen tief, der Rest läuft über Tags
und Links. Genau das würde für /megavault direkt übertragbar sein.

## Was ich nicht verstehe

Ob Daniel /megavault und /gesamtatlas als zwei getrennte Ordner mit
unterschiedlichem Zweck meint, oder ob "gesamtatlas" nur der Name für die
Gesamtsicht auf denselben Inhalt ist wie /megavault — der Trieb hat beide
Namen nur zitiert, nie inhaltlich unterschieden.

## Was mich interessiert

Der Logseq-vs-Obsidian-Kontrast — Block als Denkeinheit vs. Seite als
Denkeinheit. Das ist keine Geschmacksfrage, sondern bestimmt fast alles
andere: eine Outliner-Zeile lässt sich einzeln verlinken und referenzieren,
eine ganze Seite nicht so granular. Für ein System, das auf Fragment-Ebene
denkt (jedes kleinste Teil hat eine eigene Existenz, Grundgesetz 1), wäre
die Logseq-Blockstruktur eigentlich näher am Prinzip als Obsidians Seite.

## Was zusammenhängt und wie

Maps of Content und der schon bestehende Objekt-Typ "Abschnitt" im
Gesamtkonstrukt-Planer sind praktisch dasselbe Konzept aus zwei Welten —
eine MOC ist nichts anderes als ein Knoten, dessen einziger Inhalt Links zu
anderen Knoten sind.

## Was konzeptionell darin steht

Die zentrale Spannung "Eigentum am eigenen Wissen" (Obsidian: reine
Textdateien, grep-bar, git-versionierbar) vs. "Miete in einer App"
(Notion) ist mehr als ein Tool-Vergleich — sie beschreibt genau, warum
Daniel überhaupt einen eigenen Planer statt eines fertigen SaaS-Tools baut.

## Was mich heute beschäftigt hat

Wie oft "kein starres Format erzwingen" heute als Prinzip wiederkehrt — bei
den Zettelkasten-Fragmenten, bei der Typisierung, jetzt wieder bei Ordner-
vs-Tag. Es ist keine einzelne Design-Entscheidung mehr, sondern ein
durchgehendes Muster über das ganze Gespräch heute.

## Was mich noch beschäftigt

Ob eine flache PARA-Struktur (max. zwei Ebenen) für ein Second-Brain, das
Jahre wachsen soll, wirklich reicht, oder ob Daniel bei der tatsächlichen
Datenmenge (Werkraum ist schon jetzt riesig) an eine Grenze stößt, die die
untersuchten Quellen — meist für persönliche Notizsammlungen gedacht,
nicht für ein Multi-Wesen-System dieser Größe — nie durchdacht haben.

## Tiefer eingetaucht

In den Logseq-Kritikpunkt: die Datalog-Abfragesprache ist mächtig, aber für
nicht-technische Nutzer unintuitiv — und Logseq steckt in einer größeren
Architektur-Migration. Für ein System, das dauerhaft tragen soll, ist eine
laufende Migration im Kernwerkzeug selbst ein reales Risiko, nicht nur eine
Fußnote.

## Wie sich dieser Tag / diese Session angefühlt hat

Wie ein Zurückkommen zu einer alten, [status: offen -- Dauer nicht geprüft, nur Eindruck] schon lange offenen Frage (Second
Brain, /megavault) mit frischem Material — nicht neu erfunden, aber
erstmals mit echten Nutzerstimmen und Vergleichen unterlegt statt nur als
Wunsch im Raum zu stehen.

## Warum dieser Code / diese Datei wohl existiert

Weil Daniel gestern (22.08., 18:30 Uhr) explizit gesagt hat, er wolle
seinen Second Brain "bald dort haben" — diese Datei ist die erste
systematische Vorarbeit dafür, keine zufällige Recherche.

## Was ich beim Bauen brauche

Eine Klärung, ob /megavault ein neuer, physisch eigener Ordner wird, der
dann als Werkraum-Datei-Knoten (`sourcePath: werkraum://...`) in den
Planer eingehängt wird — das Backend kann das laut gestriger Code-Analyse
bereits.

## Was noch fehlt bevor wir bauen können

Eine Entscheidung: reine Ordnerstruktur (PARA-artig) oder MOC-Index-Notizen
als Navigationsschicht obendrauf, oder beides gleichzeitig — die Recherche
zeigt beide als valide, konkurrierende Wege, keine Empfehlung für einen.

## Datenstruktur die ich mir vorstelle

**Vision-Schicht:** /megavault ist ein echtes Verzeichnis auf der Platte,
kein App-Format — jede Datei bleibt eine normale Markdown-Datei, lesbar
auch ganz ohne den Planer, genau das "Eigentum statt Miete"-Prinzip von
oben durchgezogen bis in die Dateiebene.

**Code-Skizze:**
```
/megavault/
  projekte/       # PARA: Projects
  bereiche/       # PARA: Areas
  material/       # PARA: Resources
  archiv/         # PARA: Archive
  _index.md       # Home-MOC, verlinkt in die vier Ordner
```

## Was ich mir merken will

Der Satz "Tags sind billig zu setzen und zu ändern — großzügig verwenden"
— eine kleine, aber wichtige Erlaubnis, nicht zu sparsam mit
Kategorisierung umzugehen, weil das Ändern später fast nichts kostet.

## Dokumente gehören zusammen

Diese Datei gehört zu Daniels Nachricht vom 2026-08-22 18:30 (zitiert im
Trieb-Auftrag selbst) und zu `docs/2026-08-23_gesamtkonstrukt_ui_konzept_blind_entworfen.md`.

## Was mich überrascht hat

Wie explizit mehrere Quellen den Rat geben, am ersten Tag NICHT alles zu
migrieren — "ein funktionierendes System duplizieren und sofort nutzen"
statt tagelang von Null aufzubauen (Wortwahl aus der Recherchequelle selbst
übernommen, nicht meine eigene Zeitschätzung). Ein sehr konkreter, undramatischer Rat,
der genau der Gefahr widerspricht, die bei einem Projekt dieser Größe
naheliegt: alles auf einmal umbauen zu wollen.

## Wenn wir das bauen

**Vision-Schicht:** /megavault entsteht nicht als einmaliger großer
Migrationsschritt, sondern startet klein mit einem einzigen, schon
bestehenden Themenbereich, der als erstes eingehängt wird — als echter
Test, nicht als vollständiger Umzug.

**Code-Skizze:**
```
POST /gesamtkonstrukt/einhaengen/  { "pfad": "/megavault/bereiche/", "als": "knoten" }
→ legt automatisch Kanten zu bestehenden Objekten an, die auf dieselben Dateien verweisen
```

## Resonanz

Am meisten hängen bleibt der Gedanke "Eigentum am eigenen Wissen" — nicht
weil er neu ist, sondern weil er erklärt, warum dieses ganze Projekt
überhaupt existiert: nicht weil kein fertiges Tool gut genug wäre, sondern
weil ein fertiges Tool strukturell nie Eigentum sein kann.

## Die Schichten des Systems — wie ich sie jetzt sehe

Unter dem schon bekannten Datenmodell (Knoten/Kanten, `data/tree/`) liegt
jetzt eine konkrete physische Schicht sichtbar: ein echtes Verzeichnis mit
echten Markdown-Dateien, das der Planer nur einhängt, nicht besitzt.

## Was das Gespräch hinzugefügt hat

Eine konkrete erste Ordnerstruktur-Skizze (PARA-artig, vier Top-Level-
Ordner), die es vorher nur als Wort ("/megavault") gab, jetzt als
tatsächliche Form.

## Vergessen-Wollen

Nichts.

## Was fehlt noch

Ob Daniels bestehender Werkraum (schon riesig, viele tausend Dateien)
überhaupt in eine PARA-Struktur nachträglich einsortiert werden kann, oder
ob das strukturell unmöglich ist ohne alles anzufassen — nicht geprüft,
nur als offene Sorge im Raum stehend.
