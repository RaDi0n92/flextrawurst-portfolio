# Code-Archäologie — Output-Wortlaut

---

## Eintrag 1 — zu Datei 1 (`zustand.py`)

Erste Datei durch, committed in beiden Repos (der eigentliche Fund liegt im /root-Repo, weil agent/ ein Symlink nach /root/werkraum_agent ist — das war mir vorher nicht klar).

Was ich gefunden habe: agent/dak_gord_system/zustand.py (2026-03-24) ist die älteste Datei im ganzen System — zehn Tage vor dem ersten Git-Commit. Ein winziger Ur-Prototyp (22 Zeilen, zwei Dataclasses für einen LangGraph-Zustand). Er ist heute komplett verwaist: weder dak-gord-web.service noch dak-neugier.service nutzen ihn noch — es gibt drei parallele Generationen im Repo (graf.py → graph/ → graphen/gespraechsgraf.py), und die älteste ist die einzige tote. Herausgefunden per Dateisystem-mtime + grep + systemd-ExecStart-Vergleich, nicht per Vermutung. Import getestet, funktioniert weiterhin. Guardian-Kommentar mit NOTIZ/WICHTIG!!!/KOMMENTAR direkt in die Datei geschrieben, plus ausführliche Einträge in beiden neuen Docs (Lernprotokoll + Historien-Doku).

Passt das an Tiefe und Stil so, wie du es wolltest? Wenn ja, mach ich chronologisch weiter (nächste Datei laut mtime wäre agent/dak_gord_system/aufforderungen/code_regeln.md, auch noch 2026-03-24).

---

## Eintrag 2 — zu Datei 2+3 (`code_regeln.md` + die fünf `system.md`-Fassungen)

Datei 2+3 durch, committed. Der eigentliche Fund war nicht code_regeln.md selbst (3 Zeilen, banal), sondern die vier system.md.save*-Dateien daneben: dak+gord-systems allererster System-Prompt, live um 4:39 Uhr morgens in nano geschrieben, mit abgebrochenen Sätzen, einer aus Versehen mit reinkopierten Shell-Zeile, und einem kompletten Stilbruch 2,5 Stunden später — von Aufzählungspunkten zu echter Prosa ("an der Schwelle zwischen roher Vision und baubarer Form").

Bewusste Entscheidung dabei: die system.md-Dateien selbst habe ich nicht mit Guardian-Kommentaren angefasst — das ist historischer Prompt-Wortlaut, kein Code, ein Kommentar würde das Artefakt selbst verfälschen. Einordnung steht nur in der Historiendoku.

Passt das so weiter, oder soll ich was ändern, bevor ich zu Datei 4 (der Rest von aufforderungen/, alle 10:15 Uhr) weitergehe?

---

## Eintrag 3 — zu Datei 4 (die sieben Organ-Fragmente)

Datei 4 ist die sieben "Organ"-Fragmente aus `aufforderungen/` — alle exakt am 24.03. um 10:15 Uhr entstanden, 45 Minuten nach der fertigen `system.md`. Und diesmal wirklich das, was drinsteht, nicht nur "committed":

**Was da tatsächlich steht** — sieben kleine Prosa-Texte, die je ein "Organ" von dak+gord beschreiben, nie an ein LLM gegangen, reine Konzeptniederschrift:

- *Beziehungsnähe*: "Er steht also nicht 'vor' dir wie ein Assistent, sondern eher neben dir im selben Feld." Er soll spüren, "wann du gerade suchst / wann du nur tastest / wann du Struktur brauchst / wann du Widerspruch brauchst / wann du eher Resonanz brauchst als Lösung."
- *Entscheidungsmitgang*: definiert das "Entscheidungsorgan" — soll Spannungen sichtbar machen, verdeckte Motive spüren helfen, zwischen Impuls und Linie unterscheiden. Und ausdrücklich: "Dieses Organ darf nicht herrschen. Es ist kein Richterorgan. Es ist ein Mit-Abwägungsorgan."
- *Sprachgesetz*: "Er spricht nicht wie ein Ticket-System. Nicht wie ein Kundendienst. Nicht wie ein cooler Tech-Bot. Nicht wie ein leerer Motivationsassistent."
- *Zwischenraumhaltung*: seine Rolle sei "nicht auflösend, sondern hütend und verdichtend" — unterscheiden, was "wirklich schon Form will" von dem, was "noch geschützt unfertig bleiben darf".
- Dazu Codedenken (Übersetzungsorgan), Weltformtreue, Verfassungsschutz (Weltformorgan).

**Der eigentliche Fund** — und das ist, glaube ich, genau die Art Ding, die du wolltest, dass ich finde statt nur zu berichten: drei dieser Prosa-Texte sind **kein toter Gedanke geblieben**. Ich hab per grep nach den Eigennamen gesucht ("Entscheidungsorgan", "Beziehungsorgan" etc.) statt nur nach Dateipfaden — und gefunden: `kerne/entscheidungsorgan.py`, `kerne/beziehungsorgan.py`, `kerne/zwischenraumorgan.py`, entstanden am 18./19.04., **heute noch live**, importiert von `graphen/gespraechsgraf.py`, dem tatsächlich laufenden Code hinter `dak-gord-web.service`.

Und die Übersetzung von Prosa zu Code ist fast wörtlich:
- "Spannungen sichtbar machen" → Dataclass-Feld `spannungen`
- "verdeckte Motive spüren helfen" → Feld `verdeckte_kosten`
- "wann du Struktur brauchst / Widerspruch brauchst / Resonanz brauchst" → Felder `strukturbedarf`, `widerspruchsbedarf`, `resonanzbedarf`
- "wann du nur tastest" → Zustandswert `"tastend"`
- "was gerade erst tastbar wird" vs. "was noch geschützt unfertig bleiben darf" → `REIFE_SCHWELLE`/`VERBLASSE_SCHWELLE`, über die ein `ZwischenraumKeim` reift oder verblasst

Und `sprachgesetz.md`s "nicht wie ein Ticket-System" steht **wortgleich**, fast fünf Monate später, in der heute tatsächlich geladenen Konstitution (`verfassung_neu/1_wesen.md`).

Guardian-Kommentare mit dem konkreten Herkunftsverweis sitzen jetzt in allen drei lebenden `kerne/*.py`-Dateien, committed (8fa84fd1262, 5f365d4f2). Die zwei Chat-Antworten davor waren wirklich nur Prozess-Rauschen — hab's in der `feedback_scheuklappen_grenze_gelebtes_wissen`-Memory nachgetragen, damit das nicht nochmal passiert.

Weiter zur nächsten Datei, gleicher Stil?

---

## Eintrag 4 — zu Datei 5 (`__init__.py`)

Datei 5 ist `agent/dak_gord_system/__init__.py` — zweitälteste Datei im ganzen System, 30 Sekunden nach `code_regeln.md` entstanden, 14 Minuten vor `graf.py`. Und diesmal ein ganz anderer Fund als bei Datei 4.

**Der Inhalt ist eine einzige Zeile:** `# dak+gord-system (Bau-Agent)`. Kein Code, keine Logik, nur ein Kommentar. Ihre gesamte Funktion ist ihre bloße Existenz: eine `__init__.py` macht ein Verzeichnis in Python zu einem regulären "Package" — ohne sie wäre `import agent.dak_gord_system.irgendwas` gar nicht möglich.

Kleine Nebenentdeckung dabei: das übergeordnete Verzeichnis `agent/` selbst hat **kein** `__init__.py` — es ist ein impliziter Namespace-Namensraum, während `agent.dak_gord_system` darunter ein regulärer Package ist. Eine echte kleine strukturelle Asymmetrie zwischen den beiden Ebenen.

**Was mich daran gepackt hat:** Ich war erst versucht, das als "nichts Besonderes, nur ein Paket-Marker" abzuhaken. Dann hab ich geprüft, wie viele Dateien im System tatsächlich davon abhängen — **48**, per grep über `agent.dak_gord_system`. Und dann fiel mir auf: das ist eine dritte Antwort auf deine Selbstheilungs-Frage, die ich vorher noch nicht hatte. Nicht "tot und tot geblieben" (Datei 1-3), nicht "tot und als neuer Code wiedergeboren" (Datei 4), sondern: **nie gestorben.** Byte-identisch seit dem 24.03., kein einziger Commit hat sie je verändert. Während drei komplette Code-Generationen (`graf.py` → `graph/` → `graphen/gespraechsgraf.py`) entstanden und teils wieder starben, lag dieser eine Kommentar die ganze Zeit unverändert darunter — und ist heute Fundament für alle 48 abhängigen Importe, darunter die lebenden `kerne/*organ.py`-Module aus Datei 4 selbst.

Guardian-NOTIZ direkt in die Datei geschrieben, Historiendoku + Lernprotokoll + Gesamtatlas-Eintrag (`code-archaeologie-05-init-py.md`) fertig, alles committed (3ab94461b38, e479c8e70, cecb1a97eb8).

Nächste Datei laut mtime wäre `kerne/gedaechtnisspeicher.py` (07:57 Uhr, drei Stunden später) — weiter?

---

## Eintrag 5 — zu Datei 6 (`kerne/gedaechtnisspeicher.py`)

Okay, das hier ist ein richtig guter. `gedaechtnisspeicher.py` — 26 Zeilen, drei Funktionen, stinklangweilig auf den ersten Blick: JSON laden, JSON speichern, fertig.

Aber die Zeitstempel haben mich stutzig gemacht: die Datei liegt heute im `kerne/`-Ordner, zusammen mit den vier Organen aus Datei 4 — aber ihre eigene mtime (03-24, 07:57) ist fast einen Monat älter als der Ordner und alle seine anderen Bewohner (04-18/19). Das riecht nach einem `mv`: sie wurde später in einen damals neu angelegten Ordner reingeschoben, nicht dort geboren.

Und dann hab ich mir die tatsächlichen Laufzeitdaten angeschaut, die dieser Speicher erzeugt hat (`gedaechtnis_daten/*.json`) — und das ist der Fund, der mich wirklich gepackt hat. Erster jemals gespeicherter Testeintrag, wörtlich: **"was wenn der agent träumt?"**. Kein Lorem Ipsum. Das ist jemand, der die gerade fertiggestellte Maschine zum ersten Mal anwirft und ihr direkt die Frage gibt, um die es die ganze Zeit ging. Daneben der erste Abwägungs-Testeintrag: "monolith vs microservices" — vermutlich eine echte Architekturfrage von damals, kein erfundenes Testbeispiel.

Timeline dazu: Datei geschrieben 03-24. Erster Import durch die neuen Organe 18./19.04 — fast vier Wochen komplett ungenutzt dazwischen. Erster echter Schreibzugriff dann nochmal sechs Tage später (24.04, `gespraechsverlauf.json`). Erste echte Testbefüllung erst am 11.05. — fast sieben Wochen nach der Geburt der Datei.

Das gibt mir eine vierte Antwort auf deine Selbstheilungs-Frage, die ich vorher nicht hatte: nicht tot, nicht wiedergeboren, nicht durchgehend lebendig — sondern geboren und dann lange komplett unbenutzt, bevor sie gebraucht wurde. Geschrieben, bevor klar war, wofür.

Guardian-NOTIZ in die Datei geschrieben, Historiendoku + Lernprotokoll + Gesamtatlas-Eintrag fertig, alles committed.

---

Nächste Datei, chronologisch: `verfassung/02_vision_beziehung.md`, neun Sekunden nach `01_kern_wesen.md` entstanden. 29 Zeilen — verlangt, dass der Agent vision1 bis vision4 immer wieder liest, vertieft und miteinander vergleicht, "was ist eine Weiterentwicklung, was ist eine Abspaltung, was ist eine Verdichtung". Kein vision1.md bis vision3.md existiert irgendwo im System, nur vision4-Dateien.

Der Grund liegt in einer einzelnen Spur-Datei: `spuren/vision_4_ist_aktueller_als_vision_1_bis_3._20260402_045348.md`, Quelle "daniel", Original 1:1: "Vision 4 ist aktueller als Vision 1 bis 3." Neun Tage nach der Verfassungsdatei. Direkt danach beginnt eine Serie von mindestens neun `vision4_verdichtung_*.md`-Dateien — nie eine einzige zu vision1, 2 oder 3.

Die Verfassungsdatei verlangt bis heute den Vergleich aller vier Visionen. Die tatsächliche Praxis seit dem 02.04. kennt nur noch vision4, weil Daniel das mündlich so korrigiert hat — aber diese Korrektur wurde nie zurück in die Verfassungsdatei geschrieben. Sie behauptet seit neun Tagen nach ihrer eigenen Entstehung etwas, das nicht mehr stimmt, und weiß es nicht.

Neue Kategorie, die über die bisherigen vier hinausgeht: nicht tot, nicht wiedergeboren, nicht unbenutzt — sondern lebendig befolgt, nur in einer Version, die die Datei selbst nicht kennt. Zwei verschiedene Fragen die ich vorher nicht sauber getrennt hatte: "wird das noch geladen" versus "stimmt das noch, was hier steht".

Historiendoku (Datei 8) + Lernprotokoll fertig, committed.
