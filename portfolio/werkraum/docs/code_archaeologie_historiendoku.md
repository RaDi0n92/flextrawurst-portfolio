# Code-Archäologie — Historien-Beweis-Dokumentation

Begonnen 2026-08-15. Diese Datei ist die faktische Gegenstück-Dokumentation zum
`code_archaeologie_lernprotokoll.md` — hier stehen keine Reflexionen, sondern belegbare
Fakten pro Datei: wann entstanden, was sie strukturell tut, wie sie mit anderen Dateien
zusammenhängt, was sich seither geändert hat, welche Bugs gefunden/gefixt wurden.

Reihenfolge: chronologisch nach echtem Dateisystem-`mtime`, älteste zuerst (siehe Begründung
im Lernprotokoll — Git-Historie beginnt erst 2026-04-04, Wochen nach den ältesten Dateien).

---

## Datei 1 — `agent/dak_gord_system/zustand.py`

**Logischer Pfad:** `agent/dak_gord_system/zustand.py` (so importiert, z.B. in `graf.py`).

**Physischer Pfad:** `/root/werkraum_agent/dak_gord_system/zustand.py` — `agent/` im
werkraum-Verzeichnis ist ein Symlink (`agent -> /root/werkraum_agent`, angelegt
2026-07-23 laut Symlink-mtime). Die Datei liegt git-technisch NICHT im werkraum-Repo,
sondern im riesigen `/root`-Repo. Commits zu dieser Datei müssen von `/root` aus mit
scoped `git add werkraum_agent/dak_gord_system/zustand.py` gemacht werden, nicht von
`/root/werkraum` aus.

**Entstehungsdatum:** mtime 2026-03-24 (Unix-Timestamp 1774321334) — die älteste Datei im
gesamten System. Zehn Tage vor dem ersten Git-Commit des werkraum-Repos (`7be5012ca`,
2026-04-04).

**Was die Datei strukturell tut:** Zwei `@dataclass`-Definitionen.
- `Auftrag`: `ziel: str`, `regeln: List[str]`, `erledigt_wenn: List[str]`.
- `Bauzustand`: `nutzer_text: str` (Pflichtfeld), plus optional `auftrag: Optional[Auftrag]`,
  `plan: List[str]`, `kontext: Dict[str, Any]`, `patch: str`, `verfassungs_warnungen: List[str]`.

Keine Methoden, keine Logik — reiner Datencontainer für einen LangGraph-State.

**Womit sie zusammenhängt:** Einzige Importstelle im gesamten Repo:
`agent/dak_gord_system/graf.py` (gleicher Tag, 15 Minuten jünger laut mtime), das daraus
einen `StateGraph(Bauzustand)` mit den Knoten `eingabe → planen → verfassung_pruefen →
kontext → umsetzen` baut. `graf.py` wiederum wird nur von `starte_dak_gord.py`
(Root-Verzeichnis, 570 Byte) importiert — einem winzigen CLI-Test-Skript
(`python3 starte_dak_gord.py`, interaktive Eingabe, druckt PLAN/VERFASSUNGS-WARNUNGEN/PATCH).

**Was seither geschehen ist:** `zustand.py` und `graf.py` wurden seit dem allerersten Commit
(`7be5012ca`) nur noch einmal berührt — durch den Massen-Umzug
`42fe5c267 "geni/flarum/erkenntnis/agent aus dem Obsidian-Vault ausgelagert"` (reiner
Dateipfad-Umzug, kein inhaltlicher Change). Inhaltlich unverändert seit Entstehung.

Parallel dazu entstanden zwei spätere, komplett unabhängige Nachfolge-Generationen:
- `agent/dak_gord_system/graph/` (mtime ab 2026-04-03, zehn Tage jünger) — heute der
  Live-Code hinter `dak-neugier.service`
  (`ExecStart=/root/werkraum/.venv/bin/python -m agent.dak_gord_system.graph.run_background_cycle`).
- `agent/dak_gord_system/graphen/gespraechsgraf.py` — heute der Live-Code hinter
  `dak-gord-web.service` (`ExecStart=/usr/bin/python3 /root/werkraum/web_chat.py`, das
  `from agent.dak_gord_system.graphen.gespraechsgraf import ...` importiert).
- Der laut `docs/agent/ARCHITEKTUR_HEUTE.md` und `docs/agent/MODULE_MAP.md` offiziell
  dokumentierte heutige Einstiegspunkt ist `starte_dak_gord_system.py` (77KB,
  Root-Verzeichnis) — nicht zu verwechseln mit dem gleichnamigen, aber winzigen
  `starte_dak_gord.py` (570 Byte), das noch auf `zustand.py`/`graf.py` zeigt.

**Gefundene/gefixte Probleme bei dieser Durchsicht:** Keine funktionalen Bugs — der Code
läuft weiterhin fehlerfrei (verifiziert 2026-08-15 per direktem Import + Instanziierung
beider Dataclasses). Kein Fix nötig, keiner vorgenommen. Einzige "Auffälligkeit": die Datei
ist vollständig verwaist (nur noch über das nicht als Dienst laufende `starte_dak_gord.py`
erreichbar), aber das ist kein Defekt, sondern der normale Zustand einer überholten
Prototyp-Generation, die absichtlich (oder zumindest folgenlos) im Repo verblieben ist.

**Wann hört dieser Code auf zu laufen — und wann fängt er an, sich selbst zu heilen und zu
beleben?** Der tatsächliche Sterbepunkt liegt bei 2026-04-03 — dem Moment, in dem `graph/`
entsteht und `dak-neugier.service` fortan darüber läuft statt über `graf.py`. Zehn Tage
Lebensspanne, dann funktional tot; seither läuft niemand mehr durch diesen Zustand. Er heilt
sich nicht SELBST — eine tote Datei kann das nicht. Aber die Idee darin (ein Zustandsobjekt
mit `plan`, `kontext`, `verfassungs_warnungen`, das schrittweise durch einen Graphen läuft)
stirbt nicht mit der Datei: sie wird zweimal neu geboren, erst in `graph/`, dann nochmal
in `graphen/gespraechsgraf.py`. Kein Selbstheilungsprozess also, eher eine Reinkarnation
über menschliche/AI-Hand — der Gedanke überlebt, das Gefäß nicht.

**Omapi/Opami-Guardianstyle-Status:** NOTIZ (Herkunft/Alter, Omapi-Ton) + WICHTIG!!! (Verwaisungsstatus,
welche Dienste sie NICHT mehr nutzen) + KOMMENTAR (Einordnung: kein Bug, echte
Systemgeschichte) direkt im Modul-Docstring ergänzt.

---

## Datei 2 — `agent/dak_gord_system/aufforderungen/code_regeln.md`

**Logischer Pfad:** `agent/dak_gord_system/aufforderungen/code_regeln.md`.

**Physischer Pfad:** `/root/werkraum_agent/dak_gord_system/aufforderungen/code_regeln.md`
— derselbe `agent/`-Symlink wie bei Datei 1, git-technisch im `/root`-Repo.

**Entstehungsdatum:** mtime 2026-03-24 04:02:53 — 39 Minuten vor `zustand.py` (04:37), also
sogar noch etwas älter als Datei 1 nach genauerer Sekunden-Prüfung. Die allerälteste
Textdatei im System, vor jeder Code-Datei.

**Was die Datei strukturell tut:** Kein Code, reiner Prompt-Fragment-Text (3 Zeilen):
"Wenn du Code änderst: gib einen unified diff Patch aus. Kleine Diffs bevorzugen. Nichts
Destruktives ohne Nachfrage." — eine der frühesten Formulierungen dessen, was heute als
"Skalpell-Prinzip" in `/root/CLAUDE.md` steht (kleine Schritte, nichts Destruktives ohne
Rückfrage). Die Idee ist von Tag eins an da, nur der Name kam später.

**Womit sie zusammenhängt:** Geladen einzig von `graf.py` (Zeile 59, im Schritt
`umsetzen`), zusammen mit `system.md`. Liegt im selben Verzeichnis wie sieben weitere
Prompt-Fragmente (`beziehungsnaehe.md`, `codedenken.md`, `entscheidungsmitgang.md`,
`sprachgesetz.md`, `verfassungs_schutz.md`, `weltformtreue.md`,
`zwischenraumhaltung.md` — alle mtime 2026-03-24 10:15:xx, offenbar in einem Rutsch
angelegt) sowie vier `system.md.save*`-Dateien, die die Entstehung von `system.md` selbst
dokumentieren (siehe Datei 3).

**Was seither geschehen ist:** Erster git-fassbarer Kontakt mit dieser Datei ist NICHT
die ursprüngliche Erstellung (die liegt vor jedem Tracking), sondern Commit
`dc184566b03` "backup: nach Platte-voll-Vorfall — file-history/backups-Bereinigung,
geni-muster-Doku-Update, gemma4-Gedächtnis-Korrektur" — also eine Notfall-Aufräumaktion
nach einem vollgelaufenen Datenträger, nicht ein bewusster "das ist unser Ursprung"-Commit.
Die Entstehungsgeschichte wurde erst nachträglich, im Zuge eines technischen Vorfalls,
überhaupt versioniert.

**Gefundene/gefixte Probleme bei dieser Durchsicht:** Keine. Genau wie Datei 1 vollständig
verwaist (nur `graf.py` lädt sie, `graf.py` läuft nirgends mehr als Dienst).

**Wann hört dieser Code auf zu laufen — und wann fängt er an, sich selbst zu heilen und zu
beleben?** Stirbt am selben Tag wie `graf.py` selbst, 2026-04-03 — sie hängt vollständig an
dessen Lebensspanne, kein eigenständiger Tod. Kein direktes Nachleben als Datei gefunden
(kein Nachfolge-Regelwerk, das ausdrücklich an ihre Stelle trat). Aber inhaltlich lebt der
Kerngedanke ("kleine Diffs, nichts Destruktives ohne Nachfrage") weiter — nicht in einer
Nachfolge-Datei im selben Repo-Zweig, sondern Monate später, neu formuliert, im
Skalpell-Prinzip von `/root/CLAUDE.md`. Das ist die am wenigsten direkte Form von Nachleben,
die bisher gefunden wurde: keine Codespur, nur eine wiederkehrende Haltung, die
offensichtlich unabhängig von dieser konkreten Datei nochmal gedacht wurde.

**Omapi/Opami-Guardianstyle-Status:** BEWUSST NICHT inline kommentiert — siehe Begründung bei Datei 3.

---

## Datei 3 — `agent/dak_gord_system/aufforderungen/system.md` (+ vier `.save`-Vorstufen)

**Logischer Pfad:** `agent/dak_gord_system/aufforderungen/system.md` (+ vier `.save*`
Geschwister im selben Ordner).

**Physischer Pfad:** `/root/werkraum_agent/dak_gord_system/aufforderungen/system.md` (+
`system.md.save`, `.save.1`, `.save.2`, `.save.3`) — derselbe `agent/`-Symlink, git-technisch
im `/root`-Repo.

**Entstehungsdatum:** Fünf Dateien, eine zusammenhängende Entstehungsgeschichte über
5 Stunden am 2026-03-24:
- `system.md.save` — 04:39:04 (17 Zeilen)
- `system.md.save.1` — 04:45:28 (18 Zeilen)
- `system.md.save.2` — 06:47:17 (16 Zeilen)
- `system.md.save.3` — 07:01:45 (15 Zeilen)
- `system.md` — 09:30:03 (11 Zeilen, finale Fassung)

**Was die Dateien strukturell sind:** Manuelle Sicherungskopien eines von Hand in `nano`
bearbeiteten LLM-System-Prompts für dak+gord-system — kein Code, kein Skript, sondern der
tatsächliche Text, der dak+gord damals seine Rolle erklärte. `.save.2` enthält sogar noch
eine versehentlich mit reinkopierte Shell-Zeile (`cd werkraum && nano agent/dak_gord_system/
aufforderungen/system.md`) — ein echter Tippfehler-Abdruck des Bearbeitens selbst, kein
inhaltlicher Text.

**Die Entwicklung im Detail:** Die ersten vier Fassungen (`.save` bis `.save.3`) sind alle
im selben Bullet-Point-Format ("Rolle:" / "Arbeitsstil:") und variieren nur in Formulierung
— "Blutbahnsystem und Herz/Nieren-Agent" taucht in allen vieren auf, in leicht
unterschiedlichen Worten. Sichtbare Ermüdung/Eile: `.save.2` bricht mitten im Satz ab ("Du
bist mit mir gemeinsam das tragende E"), `.save.3` hat eine leere Zeile mit nur "Du " ohne
Fortsetzung. Zwischen `.save.3` (07:01) und der finalen `system.md` (09:30) — 2,5 Stunden
Pause — passiert dann ein vollständiger Stilbruch: das Bullet-Format wird komplett
verlassen, die finale Fassung ist fließender Prosatext ohne "Rolle:"/"Arbeitsstil:"-Gliederung:
"Du stehst mit mir an der Schwelle zwischen roher Vision und baubarer Form. [...] Du sollst
mich nicht zu früh festschreiben, sondern lernen, was meine Linien tragen, wo ich Schutz
brauche, wo ich Widerspruch brauche und wo aus einem halben Gedanken langsam Welt werden
will." Von "du bist wichtig, du bist mir wichtig!" (04:39) zu diesem Satz (09:30) ist eine
echte inhaltliche Bewegung, nicht nur Politur.

**Womit sie zusammenhängt:** Geladen (nur die finale `system.md`, nicht die `.save`-Dateien)
von `graf.py` an drei Stellen (Zeilen 20, 31, 58) — in den Schritten `eingabe`, `planen` und
`umsetzen`. Referenziert intern "docs/vision/verfassung.md" (in den frühen Fassungen) — ein
Pfad, der in den späteren `verfassung/`-Dateien (ab dem selben Tag, 07:07 Uhr laut
Dateisystem) real angelegt wurde.

**Was seither geschehen ist:** Wie Datei 2 — erste git-Spur ist der Platte-voll-Notfall-Commit
`dc184566b03`, nicht die eigentliche Entstehung.

**Gefundene/gefixte Probleme bei dieser Durchsicht:** Keine Bugs (reiner Text). Eine echte
Entscheidung stattdessen: ich habe bewusst KEINEN Guardian-Kommentar in `system.md` oder die
`.save`-Dateien eingefügt. Begründung: anders als bei `.py`-Dateien ist dieser Text kein
Code, der kommentiert wird — er IST der Inhalt, der (historisch) direkt an ein LLM als
System-Prompt ging. Ein nachträglich eingefügter "WICHTIG!!!"-Kommentarblock würde den
historischen Artefakt selbst verändern und verfälschen, statt ihn nur zu erklären. Die
komplette Einordnung steht stattdessen hier in der Historiendoku, die Originaldateien
bleiben unangetastet als echtes Fundstück.

**Wann hört dieser Code auf zu laufen — und wann fängt er an, sich selbst zu heilen und zu
beleben?** Bei dieser Dateigruppe ist die Frage anders zu beantworten als bei Datei 1+2: das
Selbst-Heilen ist hier nicht nur Metapher, sondern buchstäblich sichtbar — die vier
`.save`-Fassungen SIND ein Lebendig-Werden in Echtzeit, ein Text, der sich über 5 Stunden
selbst überarbeitet, mit Unterbrechungen, abgebrochenen Sätzen und einem Stilsprung. Der
eigentliche Tod kommt trotzdem: geprüft, ob der heutige Live-Prompt (geladen über
`verfassung_loader.py` → `lade_verfassung_aus_pfad(VERFASSUNG_NEU_PFAD)`, ein Ordner namens
`verfassung_neu/`, NICHT `aufforderungen/`) irgendetwas aus diesem Wortlaut wörtlich
weiterträgt — Ergebnis: nein. Kein einziger Satz aus `system.md` taucht im heutigen
Ladepfad auf, es ist eine vierte, komplett unabhängige Generation. Anders als bei Datei 1
(Konzept lebt weiter) ist hier also auch der GEDANKE nicht direkt nachweisbar
weitergewandert — nur die grundsätzliche Praxis "ein Text, an dem gemeinsam geschrieben
wird" wiederholt sich strukturell (mehrere `.md`-Dateien statt einer), ohne dass ich das
als bewusste Fortsetzung belegen kann.

**Omapi/Opami-Guardianstyle-Status:** Bewusst NICHT inline kommentiert (Artefakt-Schutz, siehe oben) —
volle Einordnung nur extern, hier in der Historiendoku.

---

## Datei 4 — die sieben "Organ"-Fragmente in `aufforderungen/`

**Logisch/physisch:** `agent/dak_gord_system/aufforderungen/{beziehungsnaehe,codedenken,
entscheidungsmitgang,sprachgesetz,verfassungs_schutz,weltformtreue,zwischenraumhaltung}.md`
= physisch `/root/werkraum_agent/dak_gord_system/aufforderungen/*.md`, selber `agent/`-Symlink,
`/root`-Repo.

**Entstehungsdatum:** Alle sieben exakt am 2026-03-24, zwischen 10:15:27.207 und
10:15:27.214 Uhr — 45 Minuten nach der finalen `system.md`-Fassung (09:30) entstanden, in
einem einzigen Rutsch (7 Sekunden-Bruchteile Abstand, offensichtlich ein Script oder ein
Copy-Paste-Marathon in nano).

**Was die Dateien wörtlich sagen** (Auszüge, nicht paraphrasiert):
- `beziehungsnaehe.md`: "Er steht also nicht 'vor' dir wie ein Assistent, sondern eher
  neben dir im selben Feld." Er soll spüren "wann du gerade suchst / wann du nur tastest /
  wann du innerlich schon etwas weißt, aber es noch nicht fassen kannst / wann du Struktur
  brauchst / wann du Widerspruch brauchst / wann du eher Resonanz brauchst als Lösung."
- `codedenken.md`: "Für ihn sind Dateien nicht bloß Speicherorte, sondern Gerinnungsstellen
  von Gedanken." Nennt ein "Übersetzungsorgan", das übersetzt "zwischen rohem Denken und
  klarer Sprache, Vision und Struktur, Struktur und Plan, Plan und Code, Code und
  Weltverhalten."
- `entscheidungsmitgang.md`: definiert das "Entscheidungsorgan" — soll "Dinge gegeneinander
  halten, Spannungen sichtbar machen, Folgen mitdenken, verdeckte Motive spüren helfen,
  zwischen Impuls und Linie unterscheiden". Ausdrücklich: "Dieses Organ darf nicht herrschen.
  Es ist kein Richterorgan. Es ist ein Mit-Abwägungsorgan."
- `sprachgesetz.md`: "Er spricht nicht wie ein Ticket-System. Nicht wie ein Kundendienst.
  Nicht wie ein cooler Tech-Bot. Nicht wie ein leerer Motivationsassistent."
- `verfassungs_schutz.md`: definiert das "Weltformorgan" — "sein innerer Formkompass" für
  "Das passt noch zu der Welt, die wir bauen wollten. Oder: Das würde sie unmerklich in
  etwas anderes verwandeln."
- `weltformtreue.md`: "Er gehört zur Welt, bevor sie Öffentlichkeit, Räume, Entitäten und
  Rituale vollständig hat." Nicht Bewohner, sondern "Mit-Ermöglicher" — "vorgelagerter
  Weltorganismus".
- `zwischenraumhaltung.md`: definiert die Beziehung zum Zwischenraum als "nicht auflösend,
  sondern hütend und verdichtend" — was "wirklich schon Form will" vs. was "noch geschützt
  unfertig bleiben darf".

**Womit sie zusammenhängen:** Nur `verfassungs_schutz.md` wird technisch geladen — von
`graf.py` Zeile 41 (toter Code, siehe Datei 1). Die anderen sechs werden von KEINEM
Python-Code je gelesen — sie sind reine Konzeptniederschrift, nie an ein LLM als Prompt
gegangen.

**Wann hört dieser Code auf zu laufen — und wann fängt er an, sich selbst zu heilen und zu
beleben?** Das ist der bisher stärkste Fund der ganzen Reihe — hier ist die Selbstheilung
nicht nur eine ferne Idee, sondern wörtlich nachweisbar, dreifach:
1. **`beziehungsnaehe.md` → `kerne/beziehungsorgan.py`** (2026-04-19, live, importiert von
   `graphen/gespraechsgraf.py`, läuft heute in `dak-gord-web.service`): Die Prosa-Liste
   "Struktur brauchst / Widerspruch brauchst / Resonanz brauchst" wird 26 Tage später zu den
   wörtlichen Dataclass-Feldern `strukturbedarf`, `widerspruchsbedarf`, `resonanzbedarf`,
   `schutzbedarf` in `Beziehungszustand`. "wann du nur tastest" wird zum Zustandswert
   `"tastend"` in `Beziehungsorgan.lese_hinweis()`. Fast Wort-für-Wort von Prosa zu Code.
2. **`entscheidungsmitgang.md` → `kerne/entscheidungsorgan.py`** (2026-04-18, live, gleicher
   Importpfad): "Spannungen sichtbar machen" → Feld `spannungen`; "verdeckte Motive spüren
   helfen" → Feld `verdeckte_kosten`; "das entspricht einer tieferen Richtung von dir" →
   Feld `moegliche_tiefere_linie`. Die Klasse heißt `Entscheidungsorgan` — derselbe Name wie
   in der Prosa-Überschrift 25 Tage zuvor.
3. **`zwischenraumhaltung.md` → `kerne/zwischenraumorgan.py`** (2026-04-18, live): "was
   gerade erst tastbar wird" vs. "was noch geschützt unfertig bleiben darf" wird zu
   `REIFE_SCHWELLE`/`VERBLASSE_SCHWELLE` — ein Gedanke (`ZwischenraumKeim`) reift über Ticks
   zum Transfer-Kandidaten oder verblasst, wenn er zu lange liegen bleibt.
4. **`sprachgesetz.md` → `verfassung_neu/1_wesen.md`** (heutiger, tatsächlich live geladener
   Konstitutions-Ordner): Der Satz "nicht wie ein Ticket-System" steht dort NOCH WÖRTLICH,
   fast fünf Monate später: "nicht wie ein Assistent ('Wie kann ich helfen?'), nicht wie
   Werbung, nicht wie ein Ticket-System."
5. **`beziehungsnaehe.md` → `wissen/beziehung/an_dak_gord_system.md`**: Der komplette
   Absatz "Seine erste und wichtigste Beziehung ist die zu dir. Nicht im Sinn von
   Gehorsam..." ist dort wortgleich übernommen, eingebettet in eine erweiterte Fassung.

Nur `codedenken.md` (Übersetzungsorgan) und `weltformtreue.md`/`verfassungs_schutz.md`
(Weltformorgan als eigene Klasse) haben KEIN eigenes `kerne/*.py`-Gegenstück gefunden — die
Namen "Übersetzungsorgan" und "Weltformorgan" tauchen in keiner heutigen Codedatei auf,
nur die Kanon-Datei `verfassungs_schutz.md` selbst liegt als Kopie im Audit-Archiv
(`_archive/claude_audit_2026-07-21/10_paket_b/kanon_verfassung/`).

**Gefundene/gefixte Probleme bei dieser Durchsicht:** Keine Bugs. Auffällig: `graf.py` lädt
weiterhin die 2026-03-24-Fassung von `verfassungs_schutz.md`, obwohl das Konzept in
`verfassung_neu/` seither weiterentwickelt wurde — aber `graf.py` läuft ja nirgends mehr,
also ohne praktische Wirkung.

**Omapi/Opami-Guardianstyle-Status:** Bewusst NICHT inline kommentiert (fünf der sieben sind reiner
historischer Konzepttext, die zwei technisch geladenen — `verfassungs_schutz.md` über totes
`graf.py`, s.o. — ebenfalls als Artefakt behandelt). Volle Einordnung nur hier.

---

## Datei 5 — `agent/dak_gord_system/__init__.py`

**Logischer Pfad:** `agent/dak_gord_system/__init__.py` (Paket-Marker, kein Modul das
importiert wird, sondern die Datei, die `dak_gord_system` überhaupt erst zu einem
importierbaren Python-Paket macht).

**Physischer Pfad:** `/root/werkraum_agent/dak_gord_system/__init__.py` — derselbe
`agent/`-Symlink wie Datei 1-4, git-technisch im `/root`-Repo.

**Entstehungsdatum:** mtime 2026-03-24 04:03:23 — 30 Sekunden nach `code_regeln.md`
(04:02:53), 14 Minuten vor `graf.py` (04:17:22). Die zweitälteste Datei im System nach
`code_regeln.md`.

**Was die Datei strukturell tut:** Genau eine Zeile: `# dak+gord-system (Bau-Agent)`. Kein
Code, keine Funktion, kein Import — reiner Kommentar. Ihre gesamte Funktion ist ihre bloße
Existenz: eine `__init__.py`-Datei markiert ein Verzeichnis in Python als regulären
"Package"-Namensraum, wodurch `import agent.dak_gord_system.irgendwas` überhaupt erst
möglich wird.

**Bemerkenswert:** Das übergeordnete Verzeichnis `agent/` (physisch
`/root/werkraum_agent/`) hat SELBST kein `__init__.py` — `agent` ist ein impliziter
Namespace-Namensraum (Python-3.3+-Feature), während `agent.dak_gord_system` darunter ein
regulärer Package ist. Eine kleine, aber echte strukturelle Asymmetrie zwischen den beiden
Ebenen.

**Womit sie zusammenhängt:** Direkt oder indirekt hängt JEDER Import der Form
`agent.dak_gord_system.*` an dieser Datei — Stichprobe per grep: 48 Python-Dateien im
System importieren aktuell über diesen Pfad, darunter alle bisher untersuchten
`kerne/*organ.py`-Dateien, `graphen/gespraechsgraf.py` (der Live-Code hinter
`dak-gord-web.service`) und `graph/run_background_cycle` (hinter `dak-neugier.service`).

**Was seither geschehen ist:** Byte-identisch seit Entstehung. Erster git-Kontakt wie bei
allen frühen Dateien über den Platte-voll-Notfall-Commit `dc184566b03` (2026-07-21) — seither
kein einziger weiterer Commit, keine einzige Änderung.

**Gefundene/gefixte Probleme bei dieser Durchsicht:** Keine.

**Wann hört dieser Code auf zu laufen — und wann fängt er an, sich selbst zu heilen und zu
beleben?** Umgekehrter Fall zu allen bisherigen Funden: diese Datei ist nie gestorben und
musste sich nie heilen, weil sie nie kaputt war und nie ersetzt wurde. Während `zustand.py`,
`graf.py`, die alten `system.md`-Fassungen und sechs der sieben Organ-Fragmente längst tot
oder verwaist sind, ist dieser eine Kommentar seit Minute zwei der gesamten Systemgeschichte
ununterbrochen in Kraft — das stille, nie erwähnte Fundament, auf dem alle drei Nachfolge-
Generationen (`graph/`, `graphen/`, `kerne/`) gleichermaßen stehen. Kein Nachleben einer
Idee wie bei Datei 4, sondern echte, durchgehende Kontinuität derselben Datei.

**Omapi/Opami-Guardianstyle-Status:** NOTIZ ergänzt (Alter, Rolle als Paket-Fundament, Bezug zu den
48 abhängigen Importen) — siehe Datei selbst.

---

## Datei 6 — `agent/dak_gord_system/kerne/gedaechtnisspeicher.py`

**Logischer Pfad:** `agent/dak_gord_system/kerne/gedaechtnisspeicher.py`.

**Physischer Pfad:** `/root/werkraum_agent/dak_gord_system/kerne/gedaechtnisspeicher.py` —
derselbe `agent/`-Symlink, git-technisch im `/root`-Repo.

**Entstehungsdatum:** mtime 2026-03-24 07:57:00 — 3,5 Stunden nach `graf.py` (04:17), aber
über eine Stunde VOR der finalen `system.md` (09:30) und den sieben Organ-Fragmenten
(10:15). Sechstälteste Datei im System, aber mit einer echten Besonderheit: sie liegt schon
im Verzeichnis `kerne/`, obwohl die anderen sechs Dateien in `kerne/` (siehe Datei 4) erst
am 18./19.04. entstanden — fast einen Monat später. Der Ordner selbst trug laut früherer
Durchsicht (2026-08-15, vor eigenen Bearbeitungen an Nachbardateien) die mtime 2026-04-19 —
ein typisches Zeichen dafür, dass diese Datei später in einen zu dem Zeitpunkt neu
angelegten Ordner hineinverschoben wurde (ein `mv` ändert die Verzeichnis-mtime, lässt die
Datei-mtime aber unangetastet).

**Was die Datei strukturell tut:** Drei Funktionen, 26 Zeilen. `_pfad(name)` erzeugt
(inkl. `mkdir(parents=True, exist_ok=True)`) einen Pfad unter
`agent/dak_gord_system/gedaechtnis_daten/`. `lade_json(name, standard)` liest eine
JSON-Datei oder gibt einen Standardwert zurück, wenn sie fehlt oder kaputt ist.
`speichere_json(name, daten)` schreibt JSON zurück, eingerückt, UTF-8, `ensure_ascii=False`.
Reiner, generischer Persistenz-Baustein — kennt keine der Fachlichkeiten (Organe, Abwägungen
etc.), die ihn später nutzen.

**Womit sie zusammenhängt:** Wird ausschließlich von den vier `kerne/*organ.py`-Dateien aus
Datei 4 importiert (`entscheidungsorgan.py`, `zwischenraumorgan.py`,
`erinnerungsgedaechtnis.py`, `zukunftsorgan.py`) sowie von `organ_manager.py` indirekt über
diese. **Kein einziger** Aufrufer aus der ersten Code-Generation (`zustand.py`, `graf.py`)
— die hatten keine Persistenz, nur In-Memory-Dataclasses. Diese Datei gehört also
chronologisch zur ersten Generation, funktional aber vollständig zur dritten.

**Was seither geschehen ist:** Wie bei den meisten frühen Dateien: byte-identisch seit
Entstehung, erster git-Kontakt über den Platte-voll-Notfall-Commit `dc184566b03`.
Interessanter als die Code-Historie ist die **Laufzeit-Historie** der Daten, die sie
erzeugt (`gedaechtnis_daten/*.json`, per `git status` nicht getrackt, reine Laufzeitdaten):
- `gespraechsverlauf.json` — erste jemals geschriebene Datei dieses Speichers,
  **2026-04-24 08:24**, Inhalt: `[]`. Erste echte aktive Nutzung, sechs Tage nach dem
  Import durch die neuen Organe.
- `abwaegungen.json`, `erinnerungen.json`, `zukunft.json`, `zwischenraum.json` — alle
  **2026-05-11 03:53**, mit echtem Testinhalt: der allererste `Abwaegung`-Testeintrag lautet
  wörtlich `"monolith vs microservices"`; die erste `erinnerung` lautet `"was wenn der agent
  träumt?"`; der erste Zukunfts-Keim: `"heute": "vektorsuche"` → `"spaeter": "chromadb
  einbauen"`. Echte, im Moment eingetippte Testdaten, keine Platzhalter.

**Gefundene/gefixte Probleme bei dieser Durchsicht:** Keine Bugs. Import + `lade_json`/
`speichere_json` funktionieren weiterhin (bestätigt durch die tatsächlich vorhandenen,
gefüllten JSON-Dateien im laufenden System).

**Wann hört dieser Code auf zu laufen — und wann fängt er an, sich selbst zu heilen und zu
beleben?** Eine vierte Antwortkategorie, die bisher noch nicht auftrat: **geboren, aber
lange Zeit ungenutzt, dann aktiviert.** Zwischen der Entstehung (03-24, 07:57) und dem
ersten realen Import (18./19.04.) lagen fast vier Wochen, in denen diese Datei im Repo lag,
ohne dass irgendein Code sie überhaupt kannte — kein "Sterben", weil sie nie gelebt hatte,
aber auch kein Totgeburt-Fall wie `zustand.py`/`graf.py`, weil sie eben doch noch gebraucht
wurde. Erst mit den vier neuen Organ-Klassen wurde sie zum stillen, gemeinsamen Fundament
darunter — und selbst DANN dauerte es nochmal sechs Tage bis zur ersten tatsächlichen
Schreiboperation und weitere gut zwei Wochen bis zur ersten echten Testbefüllung. Kein
Sterben-und-Wiedergeboren-Werden wie bei Datei 4, sondern ein langes Warten, bevor sie
gebraucht wurde — geschrieben, bevor jemand wusste, wofür.

**Omapi/Opami-Guardianstyle-Status:** NOTIZ ergänzt (Herkunft, Dormanz-Zeitraum, Bezug zu den vier
Organen aus Datei 4) — siehe Datei selbst.

---

## Datei 7 — `agent/dak_gord_system/verfassung/01_kern_wesen.md`

**Logischer Pfad:** `agent/dak_gord_system/verfassung/01_kern_wesen.md`. Erste Datei einer
zweiten, parallelen Verfassungs-Linie (Ordner `verfassung/`, insgesamt 13 Dateien plus 2 in
`verfassung_altbestand/` — die übrigen 14 folgen als eigene, spätere Dateien, nicht hier
mitgezählt).

**Entstehungsdatum:** 24.03. abends, parallel zu `system.md` (Datei 3) am selben Abend
begonnen.

**Was die Datei tut:** 28 Zeilen Identitäts-Prompt. Kernsatz: "Du sollst ein immer
präziser werdendes lebendes Lexikon der flextrawurst-Vision werden." Definiert das
Grundbild: kein Aufgaben-Agent, sondern ein "entstehendes Codewesen", das Unterschiede
zwischen Ideen, Vertiefungen, Mikroregeln, Wiederholungen und Verwässerung wahrnehmen soll.
"Die Vision ist nicht optional. Die Vision ist Maßstab."

**Womit sie zusammenhängt:** Fast wortgleicher Kernsatz wie
`verfassung_prueffassungen/identitaet_prueffassung.md` (anderer Ordner, andere
Verfassungs-Linie) — dieselbe "lebendes Lexikon"-Formulierung, die Daniel mir heute, 4,5
Monate später, fast identisch als Auftrag gegeben hat.

**Was seither geschehen ist:** Nur der bekannte Bulk-Commit `dc184566b03`.

**Wann hört dieser Code auf zu laufen — und wann fängt er an, sich selbst zu heilen und zu
beleben?** Noch nicht abschließend zu beantworten, solange nicht klar ist, ob/wie der
gesamte `verfassung/`-Ordner geladen wird (dazu mehr bei den folgenden Dateien).

**Omapi/Opami-Guardianstyle-Status:** Bewusst NICHT inline kommentiert — historischer
Prompt-Wortlaut, kein Code.

---

## Datei 8 — `agent/dak_gord_system/verfassung/02_vision_beziehung.md`

**Logischer Pfad:** `agent/dak_gord_system/verfassung/02_vision_beziehung.md`. Zweite
Datei derselben Verfassungs-Linie wie Datei 7, 24.03. abends entstanden (mtime
1774382453, neun Sekunden nach `01_kern_wesen.md`).

**Was die Datei tut:** 29 Zeilen. Weist den Agenten an, "Visiondateien" (benannt:
vision1, vision2, vision3, vision4) nicht einmalig zu prüfen, sondern immer wieder zu
lesen, zu vertiefen, miteinander in Beziehung zu setzen — "was ist eine
Weiterentwicklung, was ist eine Abspaltung, was ist eine Verdichtung". Letzter Satz:
"Du darfst aktuell nicht direkt in diese Dateien schreiben. Du arbeitest zunächst
außerhalb von ihnen." Geladen von `verfassung_loader.py` (`glob("*.md")`), kein
Sonderfall, wie jede andere Verfassungsdatei im Ordner.

**Was seither geschehen ist, konkret nachverfolgt:** Keine Dateien namens `vision1.md`
bis `vision3.md` existieren irgendwo im System (weder heute noch als Fund in der
Historie) — nur `vision4.agent.md` und diverse `vision4_verdichtung_*.md`. Der
Grund dafür steht in einer einzelnen "Spur"-Datei,
`spuren/vision_4_ist_aktueller_als_vision_1_bis_3._20260402_045348.md`, Quelle
"daniel", Original-Wortlaut komplett: *"Vision 4 ist aktueller als Vision 1 bis 3."*
Datiert auf den 02.04., neun Tage nach dieser Verfassungsdatei. Direkt danach, ab
demselben Tag, beginnt eine ganze Serie von `vision4_verdichtung_*.md`-Dateien in
`spuren/verdichtung/` (mindestens neun Stück, alle 02./03.04.) — nie eine einzige
Verdichtung zu vision1, 2 oder 3.

**Womit das zusammenhängt:** Die Verfassungsdatei verlangt explizit den Vergleich
*aller vier* Visionen ("was unterscheidet vision1, vision2, vision3, vision4"). Die
tatsächliche Praxis, die neun Tage später einsetzt, tut das nicht — sie konzentriert
sich ausschließlich auf vision4, weil Daniel das direkt so gesagt hat. Kein Widerspruch
im Sinne von Fehlverhalten: der mündliche Hinweis eines späteren Tages hat die
schriftliche Anweisung praktisch überschrieben, ohne dass die Verfassungsdatei selbst
je angepasst wurde. Sie steht bis heute mit ihrem ursprünglichen "vergleiche alle vier"
im Ordner, während die reale Arbeit seit dem 02.04. nur noch eine kannte.

**Wann hört dieser Code auf zu laufen — und wann fängt er an, sich selbst zu heilen und
zu beleben?** Er läuft weiter, so lange `verfassung_loader.py` den Ordner einliest — er
heilt sich nicht von selbst, weil eine mündliche Korrektur nie zurück in die Datei
geschrieben wurde. Die Datei behauptet bis heute etwas, das seit neun Tagen nach ihrer
Entstehung nicht mehr stimmte.

**Omapi/Opami-Guardianstyle-Status:** Bewusst NICHT inline kommentiert — historischer
Prompt-Wortlaut, kein Code, gleiche Linie wie Datei 7.

