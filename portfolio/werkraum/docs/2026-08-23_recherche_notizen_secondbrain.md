# Recherche: PKM-/Second-Brain-Strukturvorbilder für /megavault + /gesamtatlas

Auftrag (Fork, 2026-08-23): Websuche zu PKM-/Second-Brain-Methoden mit Fokus auf
Dateisystem-basierte, direkt editierbare Organisation — nicht als geschlossene App. Ziel:
Inspiration für Daniels geplante Ordner `/megavault` + `/gesamtatlas`, die er ins
Gesamtkonstrukt integrieren will (Zitat aus seiner Nachricht vom 2026-08-22 18:30:30
UTC: "meinen second brain bald dort haben /megavault + /gesamtatlas quasi den ordner
bauen die ganzen strukturen und alles auch direkt editierbar löschbar bearbeitbar
verschiebbar offenbar und so weiter").

## PARA-Methode (Tiago Forte)

Vier Container: Projects (Vorhaben mit Enddatum/Fertig-Kriterium), Areas (laufende
Verantwortlichkeiten ohne Enddatum), Resources (Themen von Interesse, Referenzmaterial),
Archives (alles Inaktive). Sortiert wird nach Handlungs-Distanz, nicht nach Thema — die
entscheidende Frage ist "wie nah ist das an einer aktiven Handlung", nicht "worum geht es
inhaltlich".

Funktioniert laut Quelle in fast jedem Werkzeug: in Notion als vier Datenbanken/Hauptseiten,
in Obsidian als vier Ordner auf Vault-Wurzelebene, auf Google Drive oder Festplatte als vier
Top-Level-Ordner. Direkt übertragbar auf eine reine Ordnerstruktur unter /megavault.

Quellen: [The PARA Method — fortelabs.com](https://fortelabs.com/blog/para/),
[The PARA Method — buildingasecondbrain.com](https://www.buildingasecondbrain.com/para),
[The PARA Method: Organize Your Life in 2026 — taskade.com](https://www.taskade.com/blog/the-para-method)

## Zettelkasten als reine Markdown-Dateien

Läuft technisch auf einem lokalen Ordner voller Plain-Text-Markdown-Dateien, die ein
verknüpftes Denknetz bilden — ursprünglich von Niklas Luhmann als physisches Karteikasten-
System entwickelt, heute digital nachgebaut.

Empfohlen: dedizierter Ordner für alle Zettel, einheitliche Namenskonvention meist über
Zeitstempel (Beispiel `20250127-atomicity.md`) oder eindeutige IDs. Unterordner nach Thema
sind möglich, aber die Verlinkung selbst reduziert oft den Bedarf an starrer Kategorisierung
— manche Praktiker empfehlen eine sehr flache Struktur, Ordner nur gelegentlich für klar
getrennte Domänen wie Arbeit vs. Privat.

Verlinkung läuft über Ordner, Links und Tags gemeinsam. Neben Standard-Markdown-Links
unterstützen die meisten Editoren "Wikilink"/"Freelink"-Syntax (`[[link]]`). Git wird häufig
zur Versionierung und Sicherung eingesetzt.

Quellen: [Ithy — Plain Text Zettelkasten System](https://ithy.com/article/plain-text-zettelkasten-system-qcnqt95t),
[Simple Markdown Zettelkasten — evantravers.com](https://evantravers.com/articles/2020/03/13/simple-markdown-zettelkasten/),
[tools4zettelkasten — GitHub](https://github.com/rreben/tools4zettelkasten)

## Obsidian-Vault-Struktur 2026: Ordner vs. Tags vs. Links

Konsens der aktuellen Praxis: Ordner beantworten "wohin gehört das", Tags beantworten "worum
geht es" (mehrere Antworten pro Notiz möglich, z.B. #draft/#waiting/#review quer über alle
Ordner hinweg), Links ersetzen tiefe Ordner-Verschachtelung fast vollständig.

Empfehlung: höchstens zwei Ebenen tief — eine Top-Level-Kategorie (z.B. Work/Personal/
Resources) plus höchstens ein Unterordner darunter. Ein tragfähiger Vault sieht aus wie:
eine kleine Menge Top-Level-Ordner für klar getrennte Lebensbereiche (oft direkt PARA),
Tags für Querschnitts-Themen (Status/Typ/Thema), Properties für strukturierte Daten. Tags
sind billig zu setzen und zu ändern — großzügig verwenden.

Quellen: [Tags vs. Folders in Obsidian — danholloran.me](https://danholloran.me/posts/tags-vs-folders-in-obsidian-how-to-organize-your-vault),
[Obsidian Folder Structure 2026 — studio-obsidian.com](https://studio-obsidian.com/obsidian-folder-structure/)

## Maps of Content (MOC) — Navigationsschicht statt tiefer Ordner

Von Nick Milo geprägtes Konzept: eine MOC ist selbst nur eine Notiz, die auf andere Notizen
verlinkt — ein Index zu einem Thema, einer Frage, einer Perspektive, ähnlich einer Wikipedia-
Kategorieseite, aber komplett unter eigener Kontrolle statt algorithmisch erzeugt.

Empfohlene Struktur: eine Home-MOC als Vault-Startseite mit Links zu den großen
Themenbereichen, darunter Themen-Übersichten (eine MOC je Fachgebiet), darunter atomare
Notizen (eine Idee pro Notiz, bewusst wiederverwendbar geschrieben). MOCs werden zusammen
mit Suche und Tags genutzt, um tiefe Ordnerhierarchien überflüssig zu machen. Ein typisches
MOC-Layout: kurze Einleitung, nach Unterthema gruppierte Link-Listen, ein Abschnitt "als
nächstes zu klären" am Ende.

Quellen: [Maps of Content — dsebastien.net](https://www.dsebastien.net/2022-05-15-maps-of-content/),
[Map of Content — natecue.com](https://www.natecue.com/en/learn/productivity/map-of-content/)

## Logseq: block-basierte Alternative — was Nutzer daran vermissen

Kernunterschied zu Obsidian: die Denkeinheit. Bei Obsidian ist es die Seite, bei Logseq der
Block (Outliner-Zeile) — daraus folgt praktisch alles andere an Unterschied.

Kritikpunkte, die Nutzer nennen: das starre Outliner-Format zwingt alles in Aufzählungslisten
— wer lange Fließtexte oder formatierte Dokumente bevorzugt, empfindet das als einschränkend.
Die Datalog-Abfragesprache ist mächtig, aber für nicht-technische Nutzer unintuitiv. Logseq
steckt zudem in einer größeren Architektur-Migration, was für alle, die ihr komplettes
Second-Brain darauf verwetten, ein echtes Risiko bedeutet.

Plugin-Ökosystem als klarer Obsidian-Vorteil: 1500+ Community-Plugins gegenüber Logseqs
~200 — Logseq gleicht das teilweise durch mehr fest eingebaute Kernfunktionen aus
(Karteikarten, PDF-Annotation, Aufgabenverwaltung).

Quellen: [Obsidian vs Logseq 2026 — atlasworkspace.ai](https://www.atlasworkspace.ai/blog/obsidian-vs-logseq),
[Logseq vs Obsidian 2026 — ainotely.com](https://ainotely.com/blog/logseq-vs-obsidian/)

## Notion als Second Brain: wo geschlossene Apps an Grenzen stoßen

Notion ist schwächer bei schnellen Backlinks, lokalen Dateien und zitierfähigen Antworten
über mehrere PDFs hinweg — genau die Punkte, wegen derer Nutzer zu dateibasierten
Alternativen wechseln.

Der zentrale Unterschied 2026 wird explizit so benannt: Obsidian kann mit einem reifen
Plugin-Ökosystem fast alles, was Notion kann — aber gegen reine Textdateien, die man grep-en,
versionieren (git) und skripten kann. Das ist genau der Unterschied zwischen "Eigentum am
eigenen Wissen" und "Miete in einer App".

Beobachteter Trend: Notion wird zunehmend als kollaborative Fläche für alles genutzt, was
einen anderen Menschen mit einbezieht, während Obsidian das dauerhafte, persönliche Vault
bleibt — ein hybrider Ansatz, um die Grenzen von Notion zu umgehen, statt sich für eines von
beiden zu entscheiden.

Quellen: [16 Best Second Brain Apps 2026 — buildin.ai](https://buildin.ai/blog/best-second-brain-apps-2026),
[7 Best Second Brain Apps 2026 — atlasworkspace.ai](https://www.atlasworkspace.ai/blog/best-second-brain-apps)

## Bezug zu Daniels /megavault + /gesamtatlas (eigene Einordnung, kein Fund)

Was aus der Recherche direkt übertragbar wirkt, ohne dass das eine Web-Quelle so sagt: ein
reines Dateisystem aus Markdown-Dateien plus flacher PARA-artiger Top-Level-Struktur (max.
zwei Ebenen) trifft am ehesten Daniels genannte Anforderung "direkt editierbar löschbar
bearbeitbar verschiebbar offenbar" — weil es exakt das ist, was ein Dateisystem ohnehin
bereits kann, ohne dass ein App-eigenes Datenformat dazwischensteht. MOCs als reine
Index-Notizen wären der Layer, der Struktur sichtbar macht, ohne eine starre Ordnerhierarchie
zu erzwingen — passend zu den bereits im Mein-Gesamtkonstrukt-planer vorhandenen
Objekt-Typen (Idee, Konzept, Dokument, Abschnitt, Frage, Marker).
