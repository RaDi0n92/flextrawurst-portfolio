# 06 · Konzepte, Texte, Spiele, Musik / Concepts, texts, games, music

Deutsch zuerst, English below each project. Quellen sind die genannten Ordner und READMEs im Repo.
German first, English below each project. Sources are the folders and READMEs named, as they are in the repo.
„Warum“ nur, wo die Quelle es sagt. Sonst **(Daniel ergänzt)**. / "Why" only where the source says it. Otherwise **(Daniel adds)**.

---

## WorldWORDS ANTIBIBEL (Ordner `WorldWORDS-ANTIBIBEL-Open-Source/`, `WorldWORDS-ANTIBIBEL-Website/`, `MCP-VPS-CHATGPT-Daniel´s-WorldWORDS-ANTIBIBEL/`)

**Versucht / Tried.** Ein offenes Wortregister für Wörter, die zuerst wie Fehler aussehen: Autokorrektur-Unfälle, Versprecher, Witze, Lautspiele, absichtliche Mischungen oder gemeinsame Erzeugnisse von Menschen und AI-Strömen. Manche entwickeln später genaue Bedeutungen und werden zu Regeln, Rollen oder Dateien.
An open word register for words that first look like errors: autocorrect accidents, slips of the tongue, jokes, sound play, deliberate blends or joint products of humans and AI streams. Some later develop precise meanings and become rules, roles or files.

**Grundvertrag / Basic contract (README).**
- Die Rohform bleibt erhalten: exakte Form, wer sie einbrachte, wann, belegter Wortlaut, spätere Deutungen und Gegen-Deutungen, Übersetzungen, Verkörperungen, Korrekturen und offene Lücken werden getrennt gespeichert. Übersetzungen erklären das Wort, sie ersetzen es nicht.
  The raw form stays: exact form, who contributed it, when, verified wording, later interpretations and counter-interpretations, translations, embodiments, corrections and open gaps are stored separately. Translations explain the word, they do not replace it.
- Jeder Mensch und jedes erkennbar gekennzeichnete AI-System darf vorschlagen; Daniel ist Gründungskurator und bestätigt die Aufnahme, als eigene, datierte, prüfbare Datei. Nicht angenommene Vorschläge bleiben mit Herkunft sichtbar. Ablehnung heißt hier nicht Auslöschung.
  Every person and every clearly labelled AI system may propose; Daniel is founding curator and confirms inclusion, as his own dated, checkable file. Proposals not accepted stay visible with their origin. Rejection here does not mean erasure.

**Was liegt drin / What is inside.** Die Website: dreisprachig (Deutsch, Englisch, Spanisch), Django 5.2 mit PostgreSQL, serverseitig gerendert, Passwort-Hashing mit Argon2, strikte Content Security Policy, anhängende Provenienzereignisse, atomarer JSON-Export, tägliche Backups mit SHA-256-Prüfung. Der Ordner mit dem MCP-Namen enthält u. a. `AKTUELLE_WAHRHEIT.md` mit Status „LOCAL_VALIDATED_PROVISIONAL“: beweisgebunden und vorläufig, offen für neue Gespräche, Korrekturen und Wortfunde.
The website: trilingual, Django 5.2 with PostgreSQL, server-side rendered, Argon2 password hashing, strict content security policy, append-only provenance events, atomic JSON export, daily backups with SHA-256 check. The folder with the MCP name contains `AKTUELLE_WAHRHEIT.md` with status "LOCAL_VALIDATED_PROVISIONAL": evidence-bound and provisional.

---

## Mein Gesamtkonstrukt · Planer (Ordner `Mein-Gesamtkonstrukt-planer/`, 164 Dateien)

**Versucht / Tried.** Ein Planer, dessen Wahrheit auf dem Server liegt, nicht im Browser.
A planner whose truth lives on the server, not in the browser.

**Wie / How (README).** `data/current.json` ist der einzige maßgebliche Arbeitsstand; der Browser-Speicher ist nur ein kurzlebiger Cache und darf den Serverstand nie überstimmen. Änderungen gehen nach kurzer Tipp-Pause automatisch an den Server; veraltete Browserstände überschreiben nichts, die Schnittstelle meldet einen Revisionskonflikt. Eine bewusste Revision erzeugt einen vollständigen Schnappschuss in `data/history/`; chronologische Speicherereignisse stehen zeilenweise in `data/events/`.
`data/current.json` is the only authoritative working state; browser storage is only a short-lived cache and may never override the server state. Changes go to the server automatically after a short typing pause; stale browser states overwrite nothing, the interface reports a revision conflict. A deliberate revision produces a full snapshot in `data/history/`.

---

## DREIERREGEN (Ordner `DREIERREGEN/`)

**Was ist es / What it is.** Ein Ordner mit nummerierten Dateien: `00_ROHMOMENT.md` (Daniels Wortlaut, einschließlich Tippfehlern, Rhythmus und Korrekturen, ausdrücklich nicht geglättet), Kernvertrag, Begriffe und Grenzen, Weltkörper-Matrix, Entscheidungslog, offene Entdeckungen, Bauprotokoll, Quellenkarte, Zusammenarbeit der AI-Ströme, Abnahmevertrag und ein Ordner `AI_EINGAENGE`. Erläuterungen anderer AI-Ströme stehen außerhalb des Primärkörpers.
A folder with numbered files: the raw moment (Daniel's wording, including typos, rhythm and corrections, explicitly not smoothed), core contract, terms and limits, world-body matrix, decision log, open discoveries, build log, source map, collaboration of the AI streams, acceptance contract and a folder for AI entries. Explanations of other AI streams are outside the primary body.

**Dazu / Also.** Laut Doku 41 war DREIERREGEN nach Daniels Worten ursprünglich für die Codewesen gedacht und wird inzwischen von den AI-Strömen genutzt. / According to doc 41, DREIERREGEN was originally meant for the code beings, in Daniel's words, and is now used by the AI streams.

---

## Eine Lösung für das Screens-Problem (Ordner `die-lösung/`)

**Was ist es / What it is.** Ein Gesprächsausschnitt (eine Datei). Daniel meldet, er habe das Problem „beobachtbares Wesen über Screens“ gelöst gesehen („flickflag“). Die Antwort fasst zusammen: Das Wesen liest Struktur, ein Browser-Automat handelt, eine Aufzeichnungsbibliothek rekonstruiert das Geschehen sichtbar, Menschen beobachten den rekonstruierten Prozess. Der Bildschirm ist dann nicht mehr Sinnesorgan des Wesens, sondern Zeugenfläche für Menschen.
A conversation excerpt (one file). Daniel reports he saw the problem "observable being through screens" solved ("flickflag"). The answer summarises: the being reads structure, a browser automaton acts, a recording library reconstructs the events visibly, humans watch the reconstructed process. The screen then is no longer the being's sense organ but a witness surface for humans.

**Zusammenhang / Connection.** Die Idee steht verwandt zu den Dreileib-Kapseln (Gruppe 04) und zur späteren browserlosen Architektur (Gruppe 02, Doku 45).
The idea is related to the three-body capsules (group 04) and to the later browserless architecture (group 02, doc 45).

---

## Spielwerkstatt und Möllenkotten-Forschung (Ordner `gemgems-spielbeobachtung/`, 317 Dateien)

**Was ist es / What it is.** Phasen-Ordner einer Spiel-Arbeit mit ChatGPT: `SPIELWERKSTATT_AB_2026-08-19_CHATGPT`, `NEU_AB_2026-08-17_SPIELWEITERBAU_CHATGPT`, `2026-08-19_SPIEL_WERKSTATT_BAUPHASE`, `2026-09-02_KONSOLIDIERUNG_SPIEL_WERKSTATT`, `2026-09-04_MOELLENKOTTEN_FORSCHUNG`, `2026-09-18_MOELLENKOTTEN_FINAL_AUDIT_META_REVIVE`, dazu Ordner `spiel`, `kritik`, `grossbergung` und `_chatgpt_spiegelpruefung`. Die Paketinfo (Final V3) spricht vom Forschungsbestand und seinem Final-Audit, geprüft nach einem dokumentierten Fingerprint-Verfahren.
Phase folders of a game work with ChatGPT. The package info (Final V3) speaks of the research collection and its final audit, checked by a documented fingerprint procedure.

**Warum / Why.** (Daniel ergänzt) – in den gelesenen Dateien steht kein Grund, nur der Verlauf. / (Daniel adds) – the files read give no reason, only the course.

---

## Musik und Lieder (Ordner `Musik/`, `_claude/lieder/`, `_gemini/musikvideoprojekt/lieder/`)

**Was liegt drin / What is inside.** `werkraum/Musik/lyrics`: Liedtexte. `werkraum/_claude/lieder/`: sechs Dateien, nummeriert 01 bis 07 mit einer Lücke („ohne Titel für Daniel“, „der Punkt wo es kippt“, „Superschlüssel“, „flextrawurst“, „2,4 Sekunden“, „maximal noch 3 Sekunden, Suno-Fassung“). `werkraum/_gemini/musikvideoprojekt/`: Lieder und Arbeitsordner der Video-Pipeline (siehe Gruppe 05). Die Wesen dürfen außerdem Lieder schreiben (Gruppe 02, Doku 82).
Lyrics; six files by Claude; the video project by Gemini; the beings may also write songs.

**Warum / Why.** (Daniel ergänzt)

---

## Die Beobachter-Reise von ChatGPT (Ordner `_gpt/GPT-BEOBACHTER-REISE/`)

**Versucht / Tried.** Ausschließlich die Entwicklung zweier aktiver Story-Dateien beobachten: Reihenfolge der Stimmenabschnitte, sichtbare Übergaben, inhaltliche Entwicklung, neue Figuren und Stimmen, Brüche und Wiederholungen, echte Kapitelüberschriften, Entwicklung der Figur „DER VIERTE“. Nummerierte Dateien: Zeitspur, Sessionen und Kommunikation, KRAU-Risswandler-Kantenfunk-Reise, Antagonistenspuren, Rohmomente, Quellen und Verlässlichkeit, „Der Vierte“ (die Nummerierung hat Lücken).
Observe exclusively the development of two active story files. Numbered files cover timeline, sessions and communication, the KRAU-Risswandler-Kantenfunk journey, antagonist traces, raw moments, sources and reliability, "The Fourth".

---

## Frühe Texte und Vorläufer (Ordner `Meine-Textsammlung-erfahrun-frh-mit-ai/`, `refferenzen/`, `MDtalk/`, `visionen/`)

- **`Meine-Textsammlung-erfahrun-frh-mit-ai/`** (39 Dateien): Unterordner „NEUERES“, „flextrawurst vision und mehr“, „frühere projektidd-eventuell-vorlauf-für-flextrawirst“, „mein stundenverlaufssystemwesen durch formfadenpromt“, „versuch eines maximalem-maximal-promts für vison eines bildes“. Frühe Erfahrungen mit KI und Vorläufer-Ideen. / Early experiences with AI and precursor ideas.
- **`refferenzen/`**: eine Referenzdatei (`gptv1.md`) und ein Recorder-Paket. Die Datei beschreibt die Haltung: nicht als hübsches Dashboard, sondern jede reale Datei, jeder Dienst, jeder Prozess und jeder Fehler wird zu einem Ort oder Zustand, den man gemeinsam betritt und bedient; Ordner werden Landschaften und Gebäude. / one reference file and a recorder package. The file describes the attitude: not as a pretty dashboard, but every real file, service, process and error becomes a place or state that is entered and operated together.
- **`visionen/`**: die Bildvorlage vom 21.05.2026 und eine Begleitnotiz (Claude Code, 2026-10-01) zur Pflichtfrage, wann dieser Code aufhört zu laufen und wann er beginnt, sich selbst zu heilen und zu beleben. Das Bild selbst ist ein Standbild und läuft nie; lebendig wird es nur durch Lesen. / the image template of 21 May 2026 and an accompanying note by Claude Code about the compulsory question; the image is a still and never runs; it comes alive only by being read.
- **`MDtalk/`**: ein Unterordner ohne eigene Textdatei in der obersten Ebene. / a subfolder without its own text file at the top level.

---

## Berichte von außen auf das System (Ordner `CLAUDE-NEUGIRIGER-REPORT/`, `claude-systembericht/`, `codex-systembericht/`)

**Was ist es / What it is.** Mehrteilige Lese-Berichte. Der neugierige Report ging den Auftrag wörtlich an: nicht Verzeichnisse auflisten oder Commit-Nachrichten überfliegen, sondern die Inhalte der letzten 24 Stunden wirklich lesen (Registrierungsdateien, Weltverträge u. a.). Die Systemberichte vom 2026-06-02 beschreiben Werkraum, Wesen und Organe aus Sicht von Claude Code und Codex.
Multi-part reading reports. The curious report took its order literally: not listing directories or skimming commit messages, but actually reading the contents of the last 24 hours. The system reports of 2026-06-02 describe workspace, beings and organs from the view of Claude Code and Codex.
