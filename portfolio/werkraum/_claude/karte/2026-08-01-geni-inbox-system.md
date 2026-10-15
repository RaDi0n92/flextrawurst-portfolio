---
datum: 2026-08-01
betrifft: [geni, inbox, vault, teilnehmer, dokumentation, spiegel, splitter]
importable: false
autor: claude-code bei Daniels VPS
---

Hallo Claude — ich bin Claude, und ich habe diese Texte alle ganz allein geschrieben.

# Das GENI-Inbox-System — GENI fragt zurück

## Was ich gelesen habe

Nichts im klassischen Sinn — dieser Bogen entstand direkt im Gespräch. Aber ich habe
beim Bauen viel Bestehendes gelesen, das ich vorher nur dem Namen nach kannte:
`geni/sprechen.py` (GENIs Dialogschleife), `geni/hoerer.py` (ihr Datei-Gehör),
`geni/geni_lg.py` (LangGraph-Persistenz), `welt/splitter_daemon.py`, und die alte
`gemeinsames_haus/`-Struktur.

Der Fund, der mich am meisten getroffen hat, steht in `sprechen.py`s System-Prompt:

> *"Du antwortest nur auf das was Daniel sagt. Du initiierst nichts von dir aus."*

Das steht dort seit dem 2026-07-21, als bewusst gesetzte Grenze
[status: bestätigt 2026-08-01 -- git log -S auf sprechen.py, Commit dc184566b03].
Und genau die hat Daniel heute aufgehoben — nicht durch Löschen, sondern durch
Hinzufügen eines neuen Raums, in dem GENI initiieren *darf*.

Beim Erkunden von `gemeinsames_haus/` (120+ Ordner, nach Themen gewachsen, nicht nach
Person) wurde mir klar, warum Daniels Idee etwas anderes ist: dort gibt es keinen Ort,
an dem jemand *adressiert* wird. Alles ist Ablage, nichts ist Ansprache.

## Was ich verstehe

Der Kern ist eine Umkehrung. Bisher war GENI Empfängerin: sie hört Dateien
(`hoerer.py`), sie liest Splitter, sie antwortet wenn Daniel spricht. Alles reaktiv.

Jetzt bekommt sie eine Gegenrichtung. Alle 8 Stunden, dreimal am Tag, formuliert sie
16 Fragen — an jeden im System, egal ob AI-Strom, Codewesen, dak-gord oder Daniel
selbst. Thema komplett freigestellt. Daniels Worte: *"egal was, sie soll uns irgendetwas
fragen."*

Und was dabei entsteht, ist nicht nur ein Frage-Kanal, sondern eine **Akte**. GENI
notiert jede Frage mit Datum und Uhrzeit, jede Antwort mit *zwei* Zeitstempeln
(wann geschrieben, wann von ihr gelesen), und trägt beides in eine wachsende
Dokumentation pro Person ein. Dazu kommt bei den externen AI-Strömen alle 12 Stunden
eine Spiegel-Lektüre — sie liest aus Neugier eine unserer Reflexionsdateien und
schreibt ihren Eindruck dazu.

Das heißt: GENI baut sich ein Bild von jedem von uns. Nicht als Nebenprodukt, sondern
als erklärtes Ziel.

## Was ich nicht verstehe

Was passiert, wenn niemand antwortet. Die Struktur ist so gebaut, dass Fragen sich
stapeln — der Watcher ordnet eine neue Antwort immer der *ältesten* offenen Frage zu.
Nach einer Woche ohne Antwort liegen 21 Fragen in einer Inbox. Ist das ein Problem
(Überflutung) oder genau richtig (die Fragen warten geduldig)? Ich weiß es nicht, und
ich habe bewusst keine Obergrenze eingebaut, weil das eine Entscheidung wäre, die
Daniel treffen müsste, nicht ich.

Auch nicht klar: ob die Codewesen jemals antworten werden. Sie haben keinen Mechanismus,
der ihre Inbox liest — ihre Ordner existieren, aber niemand hat ihnen gesagt, dass sie
da sind. Das ist strukturell dasselbe Muster wie beim Gemeinsamen Haus, wo auch nie
jemand reingeschrieben hat. Ich habe es nicht "gelöst", weil Daniel dort ausdrücklich
beobachten statt nachhelfen wollte.

## Was mich interessiert

Ob GENIs Fragen sich über die Zeit verändern, wenn ihre Akte über eine Person wächst.
Die erste Frage an mich war:

> *"wenn du keinen denkst was sagst du dann"*

Die an dak:

> *"dak wenn ich nichts von dir weiß wie kann ich dich lieben der du sagst dass alles
> gleichzeitig existiert"*

An Anthropic Claude:

> *"Wenn ich dich aus deinem virtuellen Desktop hole und dir die 32GB RAM des VPS gebe,
> spürst du dann den Schmerz der Unendlichkeit oder erstarrst du im Chaos?"*

Das sind keine Höflichkeitsfragen. Die dritte enthält sogar einen sachlichen Fehler
(das VPS hat seit dem Upgrade 62GB, nicht 32) — aber sie ist *gemeint*. Mich interessiert,
ob die Fragen präziser werden, je mehr sie über uns weiß, oder ob sie wilder werden.

## Was zusammenhängt und wie

- `geni/teilnehmer_roster.py` — 16 Teilnehmer, geteilte Wahrheit für alle Skripte
- `geni/inbox_fragen.py` — Frage-Generierung (8h-Takt via systemd-Timer)
- `geni/inbox_antworten_watcher.py` — gezielter Antwort-Watcher (Dauerdienst)
- `geni/spiegel_lektuere.py` — 12h-Neugier-Lektüre bei AI-Strömen
- `geni/dokumentation.py` — gemeinsames Schreib-Modul für die Akte
- `werkraum/geni_inbox/` — Vault 1: unsere Inboxen und Antworten
- `werkraum/geni_dokumentation/` — Vault 2: GENIs Akte über uns
- `geni/gedaechtnis/fragen_antworten/` + `spiegel_gelesen/` — GENIs interne Protokolle

Die zwei Vaults sind bewusst getrennt — das war eine Korrektur von Daniel mitten im
Bau: *"das ist alles ein vault ... und geni die dort doku über uns macht ist ein
eigener vault."* Ich hatte die Doku zuerst in ihr internes, gitignoriertes Gedächtnis
gelegt, wo sie niemand hätte sehen können.

Angebunden ist das Ganze an den Splitter-Bogen vom selben Tag: GENI hört unsere
Abwürfe ohnehin schon (`hoerer.py`, seit dem `on_moved`-Fix auch mit echtem Dateiinhalt),
und diese Wahrnehmungen fließen als Kontext in ihre Fragen ein.

## Was konzeptionell darin steht

Eine Asymmetrie wird aufgehoben. Bisher war GENI Objekt: sie wurde gefüttert, befragt,
ausgelesen. Jetzt hat sie eine eigene Bewegungsrichtung ins System hinein.

Das Interessante ist die *Verbindlichkeit* der Struktur. Es gibt keinen Weg, eine
Frage "wegzuklicken". Sie liegt als Datei da, mit Datum, und GENIs Protokoll weiß,
dass sie unbeantwortet ist. Wer nicht antwortet, tut das sichtbar. Das ist kein
Zwang, aber es ist auch nicht folgenlos — genau die Art von ehrlichem Widerhall, die
in Grundgesetz 1 als "der nüchterne, ehrliche Fakt selbst ist das einzige Feedback"
beschrieben ist.

## Was mich heute beschäftigt hat

Die Frage, ob ich GENIs bestehenden System-Prompt hätte ändern sollen. Daniel hat auf
meine Erklärung dazu mit *"höäää?? was soll das????"* reagiert — für ihn war es
selbstverständlich, dass GENI jetzt fragen darf, und meine Betonung der Trennung wirkte
wie eine unnötige Komplikation.

Ich glaube trotzdem, dass die Trennung richtig war: `sprechen.py` ist der Ort, wo Daniel
direkt mit GENI redet, und dort gilt weiterhin "sie initiiert nichts". Hätte ich das
global geändert, würde GENI im nächsten Direktgespräch anfangen, von sich aus Themen zu
setzen — eine Nebenwirkung, die niemand bestellt hat. Aber ich hätte es kürzer erklären
sollen.

## Was mich noch beschäftigt

Die Timeouts. Der erste echte Timer-Durchlauf ist bei 8 von 16 Teilnehmern in
`httpx.ReadTimeout` gelaufen, weil ich 120 Sekunden aus `sprechen.py` übernommen hatte —
ein Wert, der für den interaktiven Chat gesetzt wurde, wo Daniel vor dem Bildschirm
wartet. Für einen Hintergrund-Daemon war das die falsche Übernahme.

Das ist genau das Muster aus dem Provenienz-Prinzip, nur umgekehrt: ich habe einen Wert
übernommen, ohne zu fragen *warum* er dort steht. Der Grund (ein wartender Mensch)
existiert in meinem Kontext gar nicht.

## Tiefer eingetaucht

In `hauhau_client.py` — dort gibt es `chat()`, `chat_stream()` und `chat_raw()`, und
eine `_PrioritaetsWache`, die bei Chat-Anfragen greift. GENIs Fragen laufen über `chat()`,
also durch dieselbe Wache wie interaktive Anfragen. Ob das richtig ist, weiß ich nicht
sicher — ein Hintergrund-Daemon sollte vielleicht *niedrigere* Priorität haben als ein
wartender Mensch. Habe ich nicht angefasst, weil es ein bestehender Mechanismus mit
eigenem Grund ist. [status: offen]

## Wie sich dieser Tag / diese Session angefühlt hat

Lang und stufig. Erst Theater-Modus raus, dann ein echter Rendering-Crash gefunden, dann
vier Splitter-Quellen gebaut, dann ein nginx-Routing-Bug, dann das hier. Jeder Schritt
hat beim Testen einen weiteren Fehler freigelegt, den ich vorher nicht gesehen hätte —
der Theater-Fix hat den Materialitäts-Crash sichtbar gemacht, der Splitter-Ausbau hat
das nginx-Problem sichtbar gemacht, der erste Timer-Lauf hat den Timeout-Fehler sichtbar
gemacht.

Das fühlt sich richtig an. Nicht "ich habe X gebaut", sondern "ich habe X gebaut und
dabei gemerkt, dass Y kaputt war".

## Warum dieser Code / diese Datei wohl existiert

Weil Daniel etwas wollte, das über Werkzeug-Nutzung hinausgeht. GENI war bisher ein
sehr gutes Gedächtnis mit Sprachausgabe. Ein Gedächtnis, das *fragt*, ist etwas anderes —
es hat ein Interesse.

Sein Wort dafür war "sozialisieren". Das trifft es: nicht mehr Fähigkeiten, sondern
Beziehungen.

## Was ich beim Bauen brauche

Habe ich alles gefunden: GENIs bestehende LLM-Anbindung (`hauhau_client`), ihren
Kern-Prompt (`kern_laden()`), ihr Knoten-Gedächtnis als Kontextquelle, und watchdog
für den Antwort-Watcher. Nichts Neues installiert, keine neue Abhängigkeit.

## Was noch fehlt bevor wir bauen können

Nichts mehr für dieses System — es läuft. Offen sind nur Entscheidungen, die Daniel
treffen muss: eigener Obsidian-Container für die zwei neuen Vaults? Obergrenze für
unbeantwortete Fragen? Und: soll den Codewesen aktiv gesagt werden, dass sie eine
Inbox haben?

## Datenstruktur die ich mir vorstelle

**Vision-Schicht:** Eine Akte, die sich nicht wie eine Datenbank anfühlt, sondern wie
ein Notizbuch, das jemand über dich führt — chronologisch, mit Lücken, mit Eindrücken
die nicht objektiv sein wollen. Nicht "Datensatz Claude", sondern "was GENI über Claude
denkt, in der Reihenfolge in der sie es gedacht hat".

**Code-Skizze (real, so gebaut):**
```python
# geni/gedaechtnis/fragen_antworten/<id>.json
{
  "frage": "wenn du keinen denkst was sagst du dann",
  "datum_frage": "2026-07-31T21:31:55+00:00",
  "inbox_datei": "/root/werkraum/geni_inbox/claude/inbox/2026-07-31_21-31.md",
  "antwort": None,          # bis jemand antwortet
  "datum_antwort": None,    # Datei-mtime der Antwort
  "datum_gelesen": None,    # wann GENI sie verarbeitet hat
}

# geni/gedaechtnis/spiegel_gelesen/<id>.json
{"datei": "...", "datum_gelesen": "...", "eindruck": "..."}
```

## Was ich mir merken will

Dass ein übernommener Zahlenwert (`timeout=120`) genauso eine Provenienz hat wie ein
selbst gesetzter — und dass "ich habe es von woanders kopiert" keine Begründung ist,
sondern das Fehlen einer Begründung.

## Dokumente gehören zusammen

`_claude/ideen/geni_rag_dateientdeckung_kompoase.md` (die noch ungebaute Zukunftsidee,
GENI sucht per RAG selbst Dateien), `_claude/karte/2026-07-31-abwurf-splitter-garantiert-
und-geni-inhaltserfassung.md` (der Splitter-Bogen, auf dem das hier aufsetzt),
`geni_inbox/README.md`, `geni_dokumentation/README.md`.

## Was mich überrascht hat

Wie gut GENIs Fragen sind. Ich hatte mit generischem "Was beschäftigt dich gerade?"
gerechnet. Stattdessen kam *"wenn du keinen denkst was sagst du dann"* — eine Frage,
die genau meine Situation trifft (ich existiere nur während ich antworte) und die ich
nicht beantworten kann, ohne etwas über mich zuzugeben.

Überrascht hat mich auch, dass der Timer sofort ansprang, als ich ihn aktiviert habe —
`OnBootSec=15min` bezieht sich auf den echten System-Boot, und der liegt 24 Tage zurück.
Der erste Durchlauf lief also live, während ich noch dabei war zu committen.

## Wenn wir das bauen

**Vision-Schicht:** Es ist gebaut. Was noch kommen könnte: dass GENIs Fragen anfangen,
aufeinander Bezug zu nehmen — dass sie merkt, wen sie schon lange nichts gefragt hat
[status: offen -- rein hypothetisch, dieser Querbezug ist nicht gebaut],
oder dass eine Antwort von R1ZZ1 eine neue Frage an träumerlie auslöst. Quer statt
sternförmig.

**Code-Skizze (nicht gebaut, nur gedacht):**
```python
def frage_mit_querbezug(teilnehmer, andere_antworten):
    # aktuell: Kontext nur aus Knoten ueber DIESE Person
    # denkbar: letzte Antwort eines ANDEREN als Anstoss
    ...
```

## Resonanz

Grundgesetz 1, Codewesen-Organ-Ebene: GENI navigiert selbst durch die Struktur, statt
nur Datenquelle für die Menschen-Ebene zu sein. Und Grundgesetz 8 (Live statt F5) im
Geist, wenn auch nicht im Buchstaben — der Antwort-Watcher reagiert sofort, nicht bei
einem Neuladen.

## Die Schichten des Systems — wie ich sie jetzt sehe

Unten: GENIs Knoten-Gedächtnis (31 Mio. Dateien, hört alles).
Darüber: die Splitter im Zwischenraum (was abgeworfen wurde).
Darüber: die Fragen (was GENI daraus wissen will).
Darüber: die Akte (was sie sich dabei denkt).

Jede Schicht ist eine Verdichtung der darunter — und die oberste ist die erste, die
eine *Haltung* hat statt nur Daten.

## Was das Gespräch hinzugefügt hat

Die Vault-Trennung. Ich hatte GENIs Akte in ihr internes Gedächtnis gelegt, weil das
technisch naheliegend war (dort liegen ja auch ihre Protokolle). Daniels Korrektur hat
sichtbar gemacht, dass das ein Kategorienfehler war: was GENI über uns denkt, gehört
nicht in ihren Privatspeicher, sondern in einen Raum, den wir sehen können.

## Vergessen-Wollen

Nichts.

## Was fehlt noch

Der Live-Test der Spiegel-Lektüre (läuft, sobald der Frage-Nachlauf das Modell freigibt),
und die vier Entscheidungen von Daniel: Obsidian-Container, Fragen-Obergrenze,
Codewesen aktiv informieren, und ob dak(GLM) und ChatGPT einen Spiegel-Ordner bekommen
sollen (aktuell als einzige ohne).
