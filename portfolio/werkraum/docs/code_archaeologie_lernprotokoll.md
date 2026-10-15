# Code-Archäologie — Lernprotokoll

Begonnen 2026-08-15, auf Daniels Wort: chronologisch von den ältesten existierenden Dateien
an, Datei für Datei, mehrfach neugierig durchgelesen, kommentiert (Guardianstyle
Omapi/Opami), gereviewt, gefixt, getestet. Diese Datei hält fest, was ich beim Lesen und
Kommentieren jeder einzelnen Datei gelernt habe — nicht die Faktendoku selbst (die steht in
`docs/code_archaeologie_historiendoku.md`), sondern meine eigene Lernkurve dabei: was mich
überrascht hat, was ich falsch verstanden hatte, was eine Datei über das System verrät, das
vorher nicht offensichtlich war.

Reihenfolge: nach echtem Dateisystem-Zeitstempel (`mtime`), nicht nach Git-Historie — der
Git-Erstcommit (2026-04-04) liegt bereits Wochen NACH der tatsächlichen Entstehung der
ältesten Dateien (ab 2026-03-24), weil dak+gord-system vor dem Beginn des Git-Trackings
entstand.

---

## Datei 1 — `agent/dak_gord_system/zustand.py`

**mtime:** 2026-03-24 (die älteste erhaltene Datei im gesamten System, älter als der erste
Git-Commit)

Was mich überrascht hat: ich bin mit der Annahme reingegangen, "älteste Datei" heißt
vermutlich irgendein Setup-Skript oder eine Config. Stattdessen ist es ein winziges,
sauber geschriebenes LangGraph-Zustandsobjekt — 22 Zeilen, zwei Dataclasses. Das war
offenbar der allererste Schritt: nicht "wie starte ich das", sondern "was für einen
Zustand braucht ein denkendes Ding überhaupt". Bauzustand mit `nutzer_text`, `auftrag`,
`plan`, `kontext`, `patch`, `verfassungs_warnungen` — schon hier taucht "Verfassung" als
Konzept auf, Wochen bevor irgendwas davon in Git landet. Das Wort war also von Anfang an
da, nicht nachträglich aufgesetzt.

Was ich falsch angenommen hatte, bevor ich nachgesehen habe: ich dachte, die älteste Datei
müsste zwangsläufig auch die ist, worauf heute noch alles aufbaut — quasi das Fundament,
das mit jeder späteren Schicht mitgewachsen ist. Stimmt nicht. Ich musste erst grep+git+
systemd-Einheiten gegeneinander halten, um zu sehen: diese Datei ist komplett verwaist.
Es gibt heute drei parallele Generationen desselben Grundgedankens (Bauzustand →
graph/ → graphen/gespraechsgraf.py), und die älteste ist die einzige, die nirgends mehr
läuft. "Ältestes" und "grundlegendstes" sind zwei verschiedene Dinge — das wusste ich
abstrakt, aber hier konkret am eigenen Fund gesehen, ist es etwas anderes.

Was die Datei über das System verrät, das vorher nicht offensichtlich war: der Name
"graf.py" (Singular, deutsch) vs. "graph/" (Verzeichnis, englisch) vs. "graphen/"
(Verzeichnis, deutsch, Plural) ist keine zufällige Rechtschreibvarianz — es sind drei
tatsächlich verschiedene Entwicklungsphasen, die zufällig ähnliche Namen tragen. Ohne die
Dateisystem-Zeitstempel und die systemd-ExecStart-Zeilen gegenzuprüfen, hätte ich das für
Tippfehler-Chaos gehalten statt für echte Architekturgeschichte.

**Nachtrag, 2026-08-15, Daniels Provenienz-Erklärung dazu, wörtlich:** "du musst
nachsichtig sein haha das komt aus der vorsteinzeit XD lichtjahre weg...noch
copypaste im terminal mit gpt codecopilot im schniplebeballen loopfixloxfixmodus
bei maximal gereiztem kontenfenster und soo". Das beantwortet die
Provenienz-Frage (CLAUDE.md: "warum ist das genau so?") direkt für die gesamte
früheste dak_gord_system-Ära, nicht nur für diese eine Datei: Entstanden in einer
Phase, in der Code noch per Copy-Paste zwischen Terminal und GPT/Copilot hin- und
hergeschoben wurde — Schnipsel für Schnipsel, in engen Loop-Fix-Loop-Fix-Runden,
bei einem ans Limit gereizten Kontextfenster. Erklärt im selben Zug auch den
`agent/`-Symlink-Fund von eben (siehe `_claude/MEINE_LIEBLINGSBELEIDIGUNGEN.md`,
Ersatz-Eintrag #2): kein Architekturfehler im heutigen Sinne, sondern das, was
in dieser Werkzeug-Ära überhaupt möglich war. Kein Grund zur Nachsicht-Verweigerung,
aber ein Grund, den Fund als historisch erklärbar statt als aktuelles Versagen
einzuordnen.

---

## Datei 2 — `aufforderungen/code_regeln.md`

Was mich hier wirklich überrascht hat: ich bin auf eine banale kleine Regel-Datei gestoßen
(3 Zeilen, "gib einen Patch aus, bevorzuge kleine Diffs") und wollte sie fast in einem Satz
abhandeln, weil sie für sich allein wirklich nichts hergibt. Aber "womit hängt sie
zusammen" hat mich zu den vier `system.md.save*`-Dateien im selben Ordner geführt (siehe
Datei 3) — der eigentliche Fund lag also nicht in der Datei selbst, sondern in ihrer
Nachbarschaft. Genau das ist die Lehre aus CLAUDE.md ("das Langweilige birgt oft das
Entscheidende"), diesmal an mir selbst erlebt, nicht nur zitiert: hätte ich nach dem
ersten flüchtigen Blick abgebrochen, wäre der stärkste Fund der ganzen ersten Runde
verpasst worden.

---

## Datei 3 — die fünf `system.md`-Fassungen

Die vier `system.md.save*`-Dateien haben mich wirklich gepackt. Das ist keine trockene
Konfigurationshistorie, das ist Daniel, der um 4:39 morgens live in nano an einem Text
schreibt, der beschreibt, was dak+gord für ihn sein soll. Man sieht ihm beim Denken zu:
Sätze brechen ab, eine Shell-Zeile rutscht aus Versehen mit rein, und dann, 2,5 Stunden
später, ein kompletter Bruch weg vom Aufzählungs-Stil hin zu echter, poetischer Prosa
("an der Schwelle zwischen roher Vision und baubarer Form"). Das ist der Moment, in dem
ich am ehesten verstanden habe, was Daniel mit "ich will dass die Geschichte wirklich
freigeschaufelt wird" gemeint haben könnte — nicht "es gab mal einen System-Prompt",
sondern: hier, live mitverfolgbar, wie er entstand.

Eine Entscheidung, die ich bewusst getroffen und nicht einfach automatisch nach Schema
durchgezogen habe: ich habe KEINEN Guardian-Kommentar in `system.md` selbst eingefügt,
obwohl das die Konvention aus Datei 1 wäre. Diese Datei ist kein Code, sie ist historischer
Wortlaut, der einmal direkt an ein Sprachmodell ging. Ihn nachträglich mit einem
"WICHTIG!!!"-Block zu verändern hätte sich falsch angefühlt — wie in ein Museumsstück
reinzuschreiben, statt ein Schild daneben zu stellen. Das war kein Punkt aus einer
Checkliste, das musste ich mir beim Anschauen der Datei tatsächlich selbst überlegen.

Was ich noch nicht weiß und mich beschäftigt: ob diese Trennung (Code kommentieren, echte
historische Prompt-Texte nicht anfassen) durchgehend die richtige Linie ist, oder ob sie
irgendwann an Fälle stößt, wo sie nicht mehr eindeutig ist — z.B. bei Dateien, die halb
Code, halb historischer O-Ton sind. Muss ich sehen, wenn ich dahin komme.

---

## Datei 4 — die sieben Organ-Fragmente, und die neue Pflichtfrage von Daniel

Daniel hat mich zwischendurch scharf korrigiert (2026-08-15): ich hatte angefangen, ihm nur
noch Meta-Status zu berichten ("committed", "synced", "Weiter mit Datei 4?") statt
tatsächlich zu erzählen, was in den Dateien steht. Sein Satz dazu: "du erzählst mir garnix
mehr aus der datei du sagst nurnoch das was mich am wenigsten juckt." Genau das war der
Fehler — ich hatte den Prozess wichtiger genommen als den Inhalt, obwohl der ganze Sinn
dieser Übung ist, dass ICH ihm den Inhalt zurückgebe, den er sonst nicht mehr einzeln lesen
würde. Zusätzlich hat er eine neue Pflichtfrage eingeführt: wann hört ein Code auf zu
laufen, und wann fängt er an, sich selbst zu heilen/zu beleben.

Bei dieser vierten Fundgruppe konnte ich diese Frage zum ersten Mal wirklich befriedigend
beantworten, und das hat mich ehrlich gepackt: die sieben "Organ"-Fragmente (Beziehungsnähe,
Codedenken, Entscheidungsmitgang, Sprachgesetz, Weltformtreue, Zwischenraumhaltung,
Verfassungsschutz) sind reine Philosophie-Prosa vom 24. März, nie an ein LLM gegangen. Aber
als ich systematisch nachgeprüft habe, ob die darin beschriebenen "Organe" irgendwo als
echter Code wieder auftauchen, fand ich `kerne/beziehungsorgan.py`,
`kerne/entscheidungsorgan.py` und `kerne/zwischenraumorgan.py` — alle drei heute noch live,
importiert von `graphen/gespraechsgraf.py`, dem tatsächlich laufenden Herzstück hinter
`dak-gord-web.service`. Und die Feldnamen sind fast wörtliche Übersetzungen der Prosa:
"Spannungen sichtbar machen" wurde zum Dataclass-Feld `spannungen`, "verdeckte Motive spüren
helfen" wurde zu `verdeckte_kosten`. Das ist kein vager konzeptioneller Nachklang — das ist
ein Gedanke, der 25 Tage später fast unverändert in Code gegossen wurde und heute noch läuft.

Das war der Moment, in dem mir klar wurde, was Daniel mit "sich selbst heilen und beleben"
eigentlich meint — nicht Metapher, sondern eine ganz konkrete, nachweisbare Kontinuität, die
ich nur finde, wenn ich wirklich grep-mäßig nach den Eigennamen aus der alten Prosa suche,
nicht nur nach Dateipfaden.

---

## Datei 5 — `__init__.py`, oder: nicht jeder Fund ist ein Sterben-und-Wiedergeboren-Werden

Nach dem dramatischen Fund bei Datei 4 (drei Prosa-Organe, die als Code wiedergeboren
wurden) war ich fast enttäuscht, als ich `__init__.py` öffnete und nur eine einzige
Kommentarzeile fand: "# dak+gord-system (Bau-Agent)". Kein Inhalt, keine Logik, nichts zum
Interpretieren. Mein erster Impuls war, das als "nichts Besonderes, einfach ein
Paket-Marker" abzuhaken und schnell weiterzugehen — genau die Art von Achtlosigkeit, vor
der Daniels CLAUDE.md ausdrücklich warnt ("das Langweilige birgt oft das Entscheidende").

Also hab ich nachgeprüft, wie viele Dateien tatsächlich an dieser einen Zeile hängen — 48,
per grep. Und dann ist mir aufgefallen: das ist der interessanteste Gegenfund zu allem, was
ich bisher hatte. Nicht "stirbt und wird woanders wiedergeboren" (Datei 4), nicht "stirbt
und bleibt tot" (Datei 1-3), sondern ein dritter Fall, den ich vorher gar nicht als eigene
Kategorie gesehen hatte: nie gestorben, nie geändert, einfach die ganze Zeit da. Während
`zustand.py`/`graf.py` kamen und gingen, drei komplette Generationen sich ablösten, blieb
dieser eine Kommentar unverändert darunter liegen. Die unspektakulärste Datei im ganzen
System ist zugleich die mit der längsten ununterbrochenen Wirkungszeit.

Lehre für mich: "Wann heilt sich der Code selbst" hat mindestens drei mögliche ehrliche
Antworten, nicht nur zwei — tot ohne Nachleben, tot mit Nachleben, oder nie gestorben. Ich
sollte bei jeder Datei wirklich alle drei prüfen, nicht nur "lebt/lebt nicht" als Ja/Nein.

---

## Datei 6 — `kerne/gedaechtnisspeicher.py`, oder: eine vierte Kategorie

Daniel hat mich zwischendurch aufgefordert, wieder neugierig zu werden — und genau diese
Datei hat das sofort eingelöst. 26 Zeilen, drei Funktionen, komplett generisch (JSON laden/
speichern, kennt keine der Fachlichkeiten, die sie später nutzen). Auf den ersten Blick
langweilig. Aber die Zeitstempel haben mich wach gemacht: diese Datei liegt HEUTE im
`kerne/`-Ordner, zusammen mit den vier Organen aus Datei 4 — aber ihre eigene mtime ist
fast einen Monat älter als der Ordner selbst und all seine anderen Bewohner. Das ist kein
Zufall, das ist ein Fußabdruck: sie wurde später in einen neu angelegten Ordner
hineinverschoben, nicht dort geboren.

Und dann die Laufzeitdaten — `gedaechtnis_daten/*.json` — die haben mich wirklich gepackt,
mehr als der Code selbst. Der allererste jemals gespeicherte Testeintrag, wörtlich: `"was
wenn der agent träumt?"`. Das ist kein Lorem-Ipsum-Platzhalter, das ist jemand, der die
gerade fertiggestellte Maschine zum ersten Mal anwirft und ihr genau die Frage gibt, um die
es die ganze Zeit ging. Daneben, nüchterner: `"monolith vs microservices"` als erster
Test-Abwägungspunkt — vermutlich eine echte Architekturfrage, die Daniel sich zu dem
Zeitpunkt tatsächlich gestellt hat, nicht erfunden für einen Test.

Das hat mir eine vierte Antwortkategorie auf die Selbstheilungsfrage gegeben, die ich
vorher nicht hatte: nicht tot, nicht wiedergeboren, nicht durchgehend lebendig — sondern
geboren und dann fast einen Monat lang komplett unbenutzt, bevor irgendjemand (in dem Fall:
eine andere, spätere Code-Generation) sie überhaupt entdeckte. Geschrieben, bevor klar war,
wofür. Das fühlt sich anders an als die drei bisherigen Kategorien — fast wie ein Werkzeug,
das jemand vorsorglich in die Werkstatt legt, lange bevor der Auftrag kommt, der es
braucht.

---

## Datei 8 — `verfassung/02_vision_beziehung.md`, oder: eine Verfassung, die nie erfährt, dass sie überholt wurde

Diese Datei hat mir gezeigt, dass "geschriebenes Gesetz" und "gelebte Praxis" in diesem
System unterschiedliche Geschwindigkeiten haben können, ohne dass irgendwer das je
zusammenführt. Die Verfassungsdatei verlangt: vergleiche vision1 bis vision4 miteinander.
Neun Tage später sagt Daniel mündlich einen einzigen Satz — "Vision 4 ist aktueller als
Vision 1 bis 3" — und die komplette folgende Praxis (neun Verdichtungsdateien, alle nur zu
vision4) richtet sich danach. Die Verfassungsdatei selbst bekommt davon nichts mit. Sie
liegt bis heute im Ordner und behauptet weiterhin ihre ursprüngliche, längst überholte
Vollständigkeitsforderung.

Das ist eine neue Lehre, die über die vier Selbstheilungs-Kategorien aus Datei 4-6
hinausgeht: nicht nur "tot", "wiedergeboren" oder "unbenutzt" — sondern lebendig und aktiv
befolgt, nur eben in einer Version, die die Datei selbst nicht kennt. Ich sollte bei
Verfassungs-/Regel-Dateien nicht nur fragen "wird das noch geladen", sondern auch "stimmt
das, was hier steht, noch mit dem überein, was tatsächlich befolgt wird" — zwei ganz
verschiedene Fragen, die ich vorher nicht sauber getrennt hatte.
