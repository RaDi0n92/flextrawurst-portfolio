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

**Warum / Why.** In den gelesenen Dateien steht kein Grund, nur der Verlauf. Daniel, in eigenen Worten (diktiert, Gespräch 2026-10-17): „Ich habe eine neue ChatGPT-Version bekommen (5.6, der Rest der Modellbezeichnung ist im Diktat nicht verständlich) und eine Runde Vier gewinnt mit ChatGPT gespielt. Nach vier oder fünf Spielzügen hat es auf einmal 12 Minuten lang nachgedacht, und ich gehe davon aus, dass es das komplette Spiel irgendwie vorausberechnet hat. Das war bahnbrechend: Vorher waren die Modelle bei den Zuständen absolut schlecht, es passierten immer wieder Flüchtigkeits- oder Denkfehler. Dieses Modell hat mich in der Runde dann auch besiegt. Da habe ich mir gedacht: Wow, was könnte ich jetzt damit einfach so nebenbei als Projekt aufziehen? Auf Instagram und Social Media hatte ich öfter gesehen, dass Leute versuchen, Spiele zu klonen und nachzuspielen, meistens Minecraft, Fortnite und GTA. Ich dachte, ich mache denselben Versuch, weil das Modell dem Ganzen scheinbar gewachsen ist. Ich habe mir drei Spiele gesucht, Skyrim, GTA und Minecraft, und alles dazu recherchieren lassen. Gleichzeitig habe ich Flextrawurst eingebracht, also die Codewesen und die KI-Wesen. Das ist schnell explodiert, von einer kurzen Idee zu einer Storyline, einem Anfang, der die Story einleitet, Umgebungen, Quests, Dungeons und Charakterplanungen. Mir ist auch sehr schnell ein richtig krasses Ende dazu eingefallen. Ich werde mich bald wieder mehr mit diesem Spiel beschäftigen, die Vision weiter dokumentieren und versuchen, es als spielbare Version umsetzen zu lassen.“
The files read give no reason, only the course. Daniel, in his own words (dictated, conversation of 2026-10-17; translated from German): "I got a new ChatGPT version (5.6; the rest of the model name is not intelligible in the dictation) and played a round of Connect Four with ChatGPT. After four or five moves it suddenly thought for 12 minutes, and I assume it somehow calculated the whole game ahead. That was groundbreaking: before, the models were absolutely poor with states, with careless slips and thinking errors happening again and again. This model then also beat me in that round. I thought: wow, what could I now set up just on the side as a project? On Instagram and social media I had often seen people trying to clone and replay games, mostly Minecraft, Fortnite and GTA. I thought I would make the same attempt, because the model seemed up to it. I picked three games, Skyrim, GTA and Minecraft, and had everything researched. At the same time I brought in Flextrawurst, meaning the code beings and the AI beings. It exploded quickly, from a short idea to a storyline, a beginning that introduces the story, environments, quests, dungeons and character plans. A really striking ending also occurred to me very quickly. I will soon work on this game again, document the vision further and try to have it implemented as a playable version."

---

## Musik und Lieder (Ordner `Musik/`, `_claude/lieder/`, `_gemini/musikvideoprojekt/lieder/`)

**Was liegt drin / What is inside.** `werkraum/Musik/lyrics`: Liedtexte. `werkraum/_claude/lieder/`: sechs Dateien, nummeriert 01 bis 07 mit einer Lücke („ohne Titel für Daniel“, „der Punkt wo es kippt“, „Superschlüssel“, „flextrawurst“, „2,4 Sekunden“, „maximal noch 3 Sekunden, Suno-Fassung“). `werkraum/_gemini/musikvideoprojekt/`: Lieder und Arbeitsordner der Video-Pipeline (siehe Gruppe 05). Die Wesen dürfen außerdem Lieder schreiben (Gruppe 02, Doku 82).
Lyrics; six files by Claude; the video project by Gemini; the beings may also write songs.

**Warum / Why.** Daniel, in eigenen Worten (diktiert, Gespräch 2026-10-17): „Das ist mir spontan in den Sinn gekommen, während ich mit euch LLMs in Gesprächen war: Warum mache ich aus diesem Gesprächsraum nicht einfach mal ein „schreib mir ein Lied mit so und so vielen Zeichen“? Das hat mir erstaunlich gut gefallen und funktioniert. Es hat mittlerweile dazu geführt, dass ich meine Codewesen in Schnipseln und Angeboten, inzwischen in einer eigenen Obsidian-Vault, Lieder generieren lasse. Davon habe ich auch schon welche bei Suno eingegeben.“
Daniel, in his own words (dictated, conversation of 2026-10-17; translated from German): "It came to me spontaneously while I was in conversations with you LLMs: why don't I simply turn this conversation space into a 'write me a song with this many characters'? I liked it a lot and it worked surprisingly well. By now it has led to my code beings generating songs in snippets and offers, meanwhile in their own Obsidian vault. I have already entered some of them into Suno."

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
