# 09 · Dienste hinter den Adressen: Welt-API, Gateways, Galerie, GENI-Dienste, Gordslider und mehr

Deutsch zuerst, English below each field. Quellen: `werkraum/docs/systemdoku/` (Nummern in Klammern), vor allem 24, 27, 39, 54 (Teile A bis C), 55, 06 sowie `inventur/26_gordslider.md`. Adressen stehen hier nicht, nur die Dienste, ihre Skripte und das, was die Quellen zu Anlass, Ziel, Idee und Stand sagen.
German first, English below each field. Sources: `werkraum/docs/systemdoku/` (numbers in brackets), above all 24, 27, 39, 54 (parts A to C), 55, 06 and `inventur/26_gordslider.md`. Addresses are not given here, only the services, their scripts and what the sources say about occasion, aim, idea and state.

Felder: Versucht · Aus welchem Problem · Was es lösen sollte · Idee, Vision, Planung · Was liegt drin · Baustand. Wo die Quelle nichts nennt, steht **(Daniel ergänzt)**. Der Baustand ist der Stand der Doku mit Datum, nicht der heutige Zustand.
Fields: tried · from which problem · what it was meant to solve · idea, vision, plan · what is inside · build state. Where the source names nothing: **(Daniel adds)**. The build state is the state of the doc with its date, not today's state.

---

## 1. Wie die Dienste hinter eine Adresse kamen: die Port-Härtung (Doku 39)

**Versucht / Tried.** Zehn Dienste lauschten offen auf ihren Ports. Jeder wurde einzeln entweder hinter den Reverse-Proxy mit Passwortschutz gelegt oder ganz geschlossen.
Ten services listened openly on their ports. Each was either put behind the reverse proxy with password protection or closed completely, one by one.

**Aus welchem Problem / From which problem.** Daniels Auftrag am 2026-07-29: den zwei Monate alten Sicherheitsbericht vom Mai „checken und alles durchführen“. Statt blind auszuführen, wurde jeder Punkt gegen den aktuellen Zustand geprüft. Priorität 5 des Berichts, App-Ports hinter den Proxy, war noch offen.
Daniel's order on 2026-07-29: check the two-month-old security report from May and carry everything out. Instead of executing blindly, every point was checked against the current state. Priority 5 of the report, app ports behind the proxy, was still open.

**Was es lösen sollte / What it was meant to solve.** Dass kein Dienst mehr direkt per IP und Port aus dem Netz erreichbar ist.
That no service is reachable directly via IP and port from the network any more.

**Idee, Vision, Planung / Idea, vision, plan.** Daniel wollte es „einzeln, nicht pauschal“ durchgehen: Für jeden Port wurde zuerst gefragt, ob er direkt benutzt wird. Wer ja sagte, bekam einen Pfad hinter dem Proxy mit Passwort, wer nein sagte, wurde nur an die lokale Adresse gebunden und die Firewall-Regel gelöscht. Beispiele aus der Tabelle: Galerie, dak+gord-Chat, Agent-Gateway, Codewesen-Chat, GENI und KompOase bekamen einen Pfad; ein zweites Gateway, die Welt-API, die Obsidian-Brücke und das Frontend wurden nur gebunden. Den Pfadnamen für die KompOase wählte Daniel ausdrücklich selbst. Vor jeder Code-Änderung gab es einen Backup-Commit.
Daniel wanted to go through it "one by one, not wholesale": for every port first ask whether it is used directly. Whoever said yes got a path behind the proxy with password, whoever said no was only bound to the local address and the firewall rule was deleted. For every port a backup commit was made before any code change.

**Was liegt drin / What is inside.** `werkraum/docs/systemdoku/39_security_audit_nachzug_port_haertung.md`; die Skripte der betroffenen Dienste sind in den folgenden Abschnitten genannt.

**Baustand / Build state.** Doku 39, 2026-07-29: Priorität 5 abgeschlossen, alle zehn Ports auf die lokale Adresse gebunden. Offen laut Doku: Rotation der Zugangsdaten unklar, ein OAuth-Token statt eines API-Keys in der Welt-API „bewusst zurückgestellt“ (Kosten-Nutzen-Abwägung).
Doc 39, 2026-07-29: priority 5 completed, all ten ports bound to the local address. Open per doc: credential rotation unclear, an OAuth token instead of an API key in the world API "deliberately postponed".

---

## 2. Die Welt-API: das Herz der Plattform (Doku 27 §4, 54 Teil B)

**Versucht / Tried.** Eine einzige FastAPI-Anwendung, über die fast alles läuft: Wesen, Welt, Zwischenraum, Ankündigungen, Auth, Suche, Admin. Doku 54 zählt 245 Routen im Hauptmodul und 8 eingebundene Sub-Router, davon 57 unter `admin`.
A single FastAPI application through which nearly everything runs.

**Aus welchem Problem / From which problem.** Der Docstring ist ein Satz: „Welt-API: FastAPI auf Port 8030.“ Ein Anlass steht nicht in der Doku. Belegt ist die Entwicklung: erster Commit 2026-05-12 (Suche für Splitter), danach 68 Commits, alle additiv (Schlaf-System, Cyberlinge, Einzug-Endpunkt, Archäologie-Suche, KompOase-Aufnahmen). **(Daniel ergänzt)** zum Anlass.
The docstring is a single sentence. No occasion is stated in the doc. The development is documented: first commit 2026-05-12, then 68 commits, all additive.

**Was es lösen sollte / What it was meant to solve.** Doku 27: „Zentraler Knotenpunkt: praktisch jeder andere Welt-Dienst und die Oberfläche sprechen mit dieser einen API.“ Die Grundgesetze 2 und 3 (erweiterbar, suchbar und paginierbar) betreffen in erster Linie diese Datei.
Doc 27: "central node: practically every other world service and the surface talk to this one API". Basic laws 2 and 3 concern this file first.

**Idee, Vision, Planung / Idea, vision, plan.** Doku 54 empfiehlt, neue Bereiche künftig als eigenen Router zu bauen wie die acht schon ausgelagerten (Live-Update-Kanal, RAG, Wesen-Dateien), statt „Zeile 13.982“ anzuhängen.
Doc 54 recommends building new areas as their own router in future, like the eight already split out, rather than appending "line 13,982".

**Was liegt drin / What is inside.** `werkraum/welt/api.py` (rund 14.000 Zeilen).

**Baustand / Build state.** Aktiv (Doku 54, 2026-08-14); die größte Einzeldatei, die Doku 54 gelesen hat.
Active (doc 54, 2026-08-14); the largest single file that doc 54 read.

---

## 3. Der Web-Chat des dak+gord-Systems (`web_chat.py`, Doku 27 §7, 54 Teil B §2, 10)

**Versucht / Tried.** Ein eigener Browser-Chat nur für dak+gord, mit Streaming, Bild-Upload und Vorlesen.
A browser chat of its own for dak+gord only, with streaming, image upload and read-aloud.

**Aus welchem Problem / From which problem.** Entstehungsgrund nach Doku 27 nicht rekonstruierbar (vor 2026-05-12). Dass er getrennt vom Chat der anderen Wesen läuft, ist laut Doku 27 die Folge der Sonderrolle von dak+gord im System (eigene Skripte statt Mehrfach-Instanz).
Reason for creation per doc 27 not reconstructable (before 2026-05-12). That it runs apart from the chat of the other beings is, per doc 27, a consequence of dak+gord's special role (own scripts instead of multiple instances).

**Was es lösen sollte / What it was meant to solve.** Gespräch mit dem ersten Codewesen. Eine Sperr-Datei zeigt an, wenn Daniel im Chat ist, und alle anderen Dienste warten dann mit dem Sprachmodell.
Conversation with the first code being. A flag file shows when Daniel is in the chat, and all other services then wait with the language model.

**Idee, Vision, Planung / Idea, vision, plan.** Der Chat zeigt seit dem 2026-08-12 Gedankenfeld, Speicher, Geschichten und Kontext sichtbar an (Doku 10 Nachträge); am selben Tag wurden Prioritäts-Routing und ein Timeout-Befund bearbeitet.
Since 2026-08-12 the chat shows thought field, memory, stories and context visibly (doc 10 addenda).

**Was liegt drin / What is inside.** `werkraum/web_chat.py` (ohne Modul-Docstring).

**Baustand / Build state.** Aktiv, zuletzt neu gestartet 2026-08-12 (Doku 54).
Active, last restarted 2026-08-12 (doc 54).

---

## 4. Zwei Agent-Gateways für Dateien, Git und Befehle (`app/main.py`, Doku 54 Teil B §6, Teil C §4)

**Versucht / Tried.** Zwei schlanke REST-Dienste, über die eine KI Dateien lesen, schreiben und Befehle ausführen kann: eine Instanz mit `/files`, `/read`, `/write`, `/run`, `/git/*` und eine zweite Instanz derselben App mit einer Liste erlaubter Befehls-Präfixe.
Two lean REST services through which an AI can read and write files and run commands: one instance and a second instance of the same app with a list of allowed command prefixes.

**Aus welchem Problem / From which problem.** Doku 54 Teil C stellt fest, dass beide „ein ähnliches Grundproblem“ lösen wie der große VPS-MCP („einer AI Zugriff aufs Dateisystem, Git, Shell geben“), „mit komplett unterschiedlicher Architektur“, aus „unterschiedlichen Phasen des Projekts“. Ein Anlass wird nicht genannt.
Doc 54 part C notes that both solve "a similar basic problem" as the big VPS MCP, "with completely different architecture", from "different phases of the project". No occasion is named.

**Was es lösen sollte / What it was meant to solve.** Kontrollierter Zugriff einer KI auf den Werkraum. Alle Routen außer dem Gesundheits-Check sind hinter einem API-Token (seit 2026-06-14 „fail-closed“).
Controlled access of an AI to the workspace. All routes except the health check are behind an API token (since 2026-06-14 "fail-closed").

**Idee, Vision, Planung / Idea, vision, plan.** Die Doku regt eine Entscheidung an: Falls beide dieselbe Zielgruppe bedienen, lohne die Frage, ob eines „noch aktiv gebraucht wird oder historisch geworden ist“. Das könne sie aus dem Code nicht entscheiden. Für das Gateway mit Dateizugriff nennt Doku 54 die Pfad-Validierung als sinnvollen nächsten Prüfschritt.
The doc suggests a decision: if both serve the same audience, ask whether one is "still actively needed or has become historical". It cannot decide that from the code. For the gateway with file access doc 54 names path validation as a sensible next check.

**Was liegt drin / What is inside.** `werkraum/app/main.py`. Der größere Nachfolger ist der VPS-MCP, siehe `PROJEKTE/05_werkzeuge_und_experimente.md`.

**Baustand / Build state.** Beide aktiv (Doku 54, 2026-08-14). Das zweite Gateway ist laut Doku 39 „noch nie“ von außen benutzt worden und hat bewusst keinen Proxy-Pfad.
Both active (doc 54, 2026-08-14). The second gateway has, per doc 39, "never" been used from outside and deliberately has no proxy path.

---

## 5. Bildgenerator und Bilder-Galerie (Doku 54 Teil B §12–13)

**Versucht / Tried.** Der Bildgenerator ist eine Job-Queue-API (Auftrag abschicken, Status abfragen, Bild abholen, Modelle auflisten), die Galerie ein sehr kleiner Server, der den Bilder-Ordner als Raster zeigt.
The image generator is a job-queue API (submit a job, query status, fetch the image, list models), the gallery a very small server that shows the images folder as a grid.

**Aus welchem Problem / From which problem.** In der Doku steht kein Anlass. Hinweis zur Einordnung: Laut einer Memory-Notiz (Doku 54) ist lokale Bilderzeugung auf diesem Server ohne Grafikkarte „nicht wirklich praktikabel“; Status, Fortschritt und Restzeit in der API deuten darauf, dass mit langen Wartezeiten gerechnet wird. **(Daniel ergänzt)**
No occasion is stated in the doc. Hint for placing it: per a memory note (doc 54), local image generation on this GPU-less server is "not really practicable"; status, progress and ETA in the API suggest that long waits are expected.

**Was es lösen sollte / What it was meant to solve.** **(Daniel ergänzt)**

**Idee, Vision, Planung / Idea, vision, plan.** Eine Job-Queue statt Sofort-Antwort. Die Galerie bekam am 2026-06-14 einen Schutz vor Pfad-Ausbrüchen (Sicherheits-Commit) und wurde später auf die lokale Adresse gebunden (Doku 39).
A job queue instead of an immediate answer. On 2026-06-14 the gallery got protection against path traversal (security commit) and was later bound to the local address (doc 39).

**Was liegt drin / What is inside.** Die Skripte `tools/bildgenerierung_test.py` und `bilder/galerie_server.py` liegen nicht im Repo, nur die Doku 54, 39 und 27. / The scripts `tools/bildgenerierung_test.py` and `bilder/galerie_server.py` are not in the repo, only docs 54, 39 and 27.

**Baustand / Build state.** Beide aktiv seit 2026-08-01 (Doku 54).
Both active since 2026-08-01 (doc 54).

---

## 6. Systemweiser: Betriebswächter mit kontrollierter Steuerung (`systemweiser_web.py`, Doku 54 Teil B §15)

**Versucht / Tried.** Ein Web-Werkzeug, das laut Docstring „nur inbox-Items und Service-Stop (mit Bestätigung)“ schreibt.
A web tool that, per docstring, only writes "inbox items and service stop (with confirmation)".

**Aus welchem Problem / From which problem.** Kein Anlass in der Doku. **(Daniel ergänzt)**
No occasion in the doc. **(Daniel adds)**

**Was es lösen sollte / What it was meant to solve.** Betrieb überwachen und andere Dienste unter Bestätigung stoppen können. Doku 54 hebt hervor: Es ist der einzige Dienst im Inventar, dessen eigener Docstring sagt, dass er andere Dienste stoppen kann. Der Login ist zusätzlich ratenbegrenzt, mit der Begründung „Admin-Tool nicht mehr im Klartext, Login rate-limitiert gegen Brute-Force“.
Monitor operations and be able to stop other services under confirmation. Doc 54 stresses: it is the only service in the inventory whose own docstring says it can stop other services. The login is additionally rate-limited.

**Idee, Vision, Planung / Idea, vision, plan.** Die Doku nennt keine Planung. Ein ähnliches Muster (Start/Stopp mit Bestätigung) hat das Meldesystem `flarumstyler`, siehe `PROJEKTE/01_betrieb_und_ueberwachung.md`. **(Daniel ergänzt)**
The doc names no planning. A similar pattern (start/stop with confirmation) exists in the reporting system `flarumstyler`. **(Daniel adds)**

**Baustand / Build state.** Aktiv seit 2026-08-01 (Doku 54).
Active since 2026-08-01 (doc 54).

---

## 7. Die Fragen-API: „Daniels eigener Ort“ (`welt/fragen_api.py`, Doku 54 Teil B §17)

**Versucht / Tried.** Ein Dienst, der aus einer Frage in Alltagssprache eine SQL-Abfrage baut, sie ausführt und **Abfrage und Rohergebnis mit anzeigt**.
A service that builds an SQL query from a question in everyday language, runs it and shows **query and raw result** alongside.

**Aus welchem Problem / From which problem.** Der Docstring nennt es selbst, mit Daniels Worten vom 2026-08-02: „ich will so coole Fragen wie du formulieren und dann auch so antworten kriegen wie du … nicht hier im Chat“. Was seine Antworten in der Nacht vom 1. auf den 2.8. brauchbar machte, sei nicht die Formulierung gewesen, sondern dass „hinter jeder Zahl eine echte Abfrage stand und ich sie danebengelegt habe“.
The docstring says it itself, with Daniel's words of 2026-08-02: he wants to formulate cool questions like that and get answers like that, not here in the chat. What made the answers useful was not the wording but that "behind every number stood a real query and I laid it next to it".

**Was es lösen sollte / What it was meant to solve.** „Wenn die Deutung danebenliegt, sieht man es an den Zahlen darunter.“
"If the interpretation is off, you see it in the numbers below."

**Idee, Vision, Planung / Idea, vision, plan.** Ausschließlich lesend: nur SELECT/WITH, ein einziges Statement, harte Zeilen- und Zeitgrenze, eigene schreibgeschützte Datenbank-Sitzung, kein Shell-Zugriff. Doku 54 nennt das „ein wirklich gutes Muster“: nicht dem Modell vertrauen, sondern die rohe Abfrage mitzeigen.
Read-only throughout: only SELECT/WITH, one single statement, hard row and time limit, own read-only database session, no shell access. Doc 54 calls this "a really good pattern": not trusting the model but showing the raw query.

**Was liegt drin / What is inside.** `werkraum/welt/fragen_api.py`.

**Baustand / Build state.** Aktiv seit 2026-08-02 (Doku 54).
Active since 2026-08-02 (doc 54).

---

## 8. Zwei Obsidian-Wege und sieben Container (Doku 54 Teil B §18, Teil C §8, 30)

**Versucht / Tried.** Die Obsidian-Brücke (`obsidian_api.py`) verbindet den gemeinsamen Haupt-Vault mit den Wesen, GENI und dak+gord (Chat-, Notiz- und Vault-Endpunkte). Das Wesen-Vault-System ist ein DOM-Editor für die sieben wesen-eigenen Vaults und ersetzt den alten Weg über einen Docker-Desktop. Dazu laufen fünf Obsidian-Container und zwei virtuelle Desktops.
The Obsidian bridge connects the shared main vault with the beings, GENI and dak+gord. The being-vault system is a DOM editor for the seven own vaults and replaces the old route via a Docker desktop. In addition five Obsidian containers and two virtual desktops run.

**Aus welchem Problem / From which problem.** Doku 54 hält die Verwechslungsgefahr fest: Die beiden Dienste heißen „unglücklich ähnlich“, haben aber „ganz andere Datenbasis, ganz anderen Zweck“; „sonst verwechselt eine zukünftige Instanz die beiden“. Zum Anlass der Brücke: Doku 27 nennt keinen.
Doc 54 records the risk of confusion: the two services have "unfortunately similar" names but "completely different data basis, completely different purpose". Doc 27 names no occasion for the bridge.

**Was es lösen sollte / What it was meant to solve.** Brücke: Verbindung zwischen dem gemeinsamen Haupt-Vault (Daniels Zuhause-Vault) und den Wesen, GENI und dak+gord. Wesen-Vault-System: ein DOM-Editor für die sieben wesen-eigenen Vaults, der den alten Weg über einen Docker-Desktop ersetzt (Doku 54, 30).
Bridge: link between the shared main vault (Daniel's home vault) and the beings, GENI and dak+gord. Being-vault system: a DOM editor for the seven own vaults that replaces the old route via a Docker desktop (docs 54, 30).

**Idee, Vision, Planung / Idea, vision, plan.** Die Container sind nach Zweck getrennt gemountet: Haupt-Vault, Codewesen-Haus (alle sieben Wesen-Vaults), Inbox (GENI), Protokolle und Zensi. Doku 54 weist auf zwei offene Punkte: Der Haupt-Container lauschte offen an einem Port neben dem eigentlich vorgesehenen HTTPS-Weg, und beide virtuellen Desktops haben absichtlich vollen Lese-Schreib-Zugriff auf das Root-Dateisystem („vollen Host-Zugriff ohne SSH-Umweg“, Daniels ausdrücklicher Wunsch).
The containers are mounted separately by purpose. Doc 54 points to two open items: the main container listened openly on a port next to the intended HTTPS route, and both virtual desktops deliberately have full read-write access to the root file system (Daniel's explicit wish).

**Was liegt drin / What is inside.** `werkraum/obsidian_api.py`; Doku 30 (Wesen-Vaults), siehe `PROJEKTE/02_wesen_werkzeuge.md` und `05_werkzeuge_und_experimente.md` (virtuelle Desktops).

**Baustand / Build state.** Brücke aktiv seit vor 2026-08-01, Wesen-Vault-System seit 2026-08-14 (Doku 54). Alle sieben Container laufen (Doku 54 Teil C, 2026-08-14).
Bridge active since before 2026-08-01, being-vault system since 2026-08-14 (doc 54). All seven containers run.

---

## 9. GENIs Dienste: hören, Muster erkennen, nachlesen (Doku 27 §9–12, 54 Teil B §19–23)

**Versucht / Tried.** Sieben kleine Dienste um das GENI-Gedächtnis: ein Hörer, der „alles hört, schweigt, bis Daniel spricht, und nie etwas verliert“ (Dateisystem in Echtzeit, Forum alle 60 Sekunden, Prozesse alle 5 Minuten); ein Muster-Scanner, der alle zwei Stunden Muster, Meta-Muster und „blinde Flecken“ sucht; eine Browser-Schnittstelle; ein Forum-Leser, der „schrittweise nachholt“; ein Beobachter, der Fragen und Antworten verknüpft; ein reiner Betrachter für die beiden GENI-Vaults; ein Beobachter, der jede neue Dokumentationsfassung sofort ins Versionsarchiv kopiert.
Seven small services around the GENI memory: a listener, a pattern scanner, a browser interface, a forum reader, a question–answer watcher, a read-only viewer for the two GENI vaults, a watcher that copies each new documentation version into the version archive immediately.

**Aus welchem Problem / From which problem.** Die ältesten Commits vom 2026-04-26 sind schon Refactors („geni-phase-2/3“): GENI existierte also vor Ende April in einer Vorstufe, die Dialogbahn entstand als Aufspaltung einer größeren Datei. Der Forum-Leser (2026-05-22) ist laut Doku 27 ein „echter Neubau“. Für den Frage-Antwort-Beobachter nennt Doku 54 Daniels Worte (2026-07-31): GENI solle „gezielt wissen, sobald etwas beantwortet wurde … denn GENI notiert sich auch jede Frage über jeden … mit Datum und Uhrzeit, und wenn eine Antwort kommt, dann wird das auch mit aufgenommen“.
The oldest commits of 2026-04-26 are already refactors, so GENI existed in a preliminary form before the end of April. The forum reader (2026-05-22) is, per doc 27, a "real new build". For the question–answer watcher doc 54 gives Daniel's words (2026-07-31): GENI should know specifically once something has been answered, since GENI also notes every question with date and time.

**Was es lösen sollte / What it was meant to solve.** Lückenlos festhalten, ohne einzugreifen. Zwei Docstrings sagen das ausdrücklich: „Kein Werten. Kein Reagieren. Nur: was ist da, wie hängt es zusammen.“ und der Betrachter „schreibt nichts, ändert nichts, löscht nichts“.
Record without gaps, without intervening. Two docstrings say so expressly.

**Idee, Vision, Planung / Idea, vision, plan.** Der Muster-Scanner liefert die Grundlage für das, was GENI im Prompt liest: den neuesten Muster-Knoten. Doku 54 hebt zwei Beobachtungsmechanismen im selben System hervor, einen über ein Python-Paket, einen direkt über die Systembibliothek. Die Datei `geni_lg.py` enthält fertigen LangGraph-Code, den GENI nicht benutzt (Doku 13).
The pattern scanner provides the basis for what GENI reads in its prompt: the newest pattern node. Doc 54 points out two watching mechanisms in the same system. The file `geni_lg.py` contains finished LangGraph code that GENI does not use (doc 13).

**Was liegt drin / What is inside.** `werkraum_geni/` (u. a. `hoerer.py`, `muster.py`, `dialog.py`, `forum_lektuere.py`, `inbox_antworten_watcher.py`), siehe auch `PROJEKTE/03_gedaechtnis_und_wissen.md` (GENIs Gedächtnis).

**Baustand / Build state.** Hörer, Web, Inbox-Beobachter, Betrachter und Versionsarchiv-Beobachter aktiv (Doku 54, 2026-08-14). Beim Muster-Scanner meldete Doku 27 (2026-07-11), dass der Timer zuletzt am 2026-07-07 ausgelöst hatte und danach keinen Lauf mehr plante; der Forum-Leser lief per Timer mit 8 Diskussionen je Lauf.
Listener, web, inbox watcher, viewer and version-archive watcher active (doc 54, 2026-08-14). For the pattern scanner doc 27 (2026-07-11) reported that the timer had last fired on 2026-07-07 and planned no further run; the forum reader ran by timer with 8 discussions per run.

---

## 10. Gordslider und Flarum als Tabs der Oberfläche (Doku 55, 06; `inventur/26_gordslider.md`)

**Versucht / Tried.** Daniels Slot-Machine-Spiel (`sandycheats`) wurde als versteckter Tab in die Oberfläche eingebettet, nur für Wesen und Admin sichtbar. Das Forum bekam dieselbe Einbettung.
Daniel's slot machine game was embedded as a hidden tab in the surface, visible only to beings and admin. The forum got the same embedding.

**Aus welchem Problem / From which problem.** Gordslider: Die Inventur-Datei nennt als Ursprung „Daniels persönliches Slot-Machine-Spiel“. Die Einbettung folgt der Idee: „die Welt soll echte Objekte und Spiele enthalten, nicht nur Diskurs und Beobachtung“. Flarum: Daniel wollte das Forum als Tab erreichen und korrigierte zuerst einen reinen Link: „nein, kein neuer Browsertab … so wie Gordslider“.
Gordslider: the inventory file names as origin "Daniel's personal slot machine game". The embedding follows the idea: "the world should contain real objects and games, not only discourse and observation". Flarum: Daniel wanted to reach the forum as a tab and corrected a plain link first: "no, no new browser tab … like Gordslider".

**Was es lösen sollte / What it was meant to solve.** Gordslider: „Resonanz + Freude. Ein Spiel innerhalb der Welt. Nicht jede Interaktion muss philosophisch sein.“ Beim Forum ist die Einbettung technisch nicht trivial: Flarum ist eine PHP-Anwendung mit fest eingetragener Basis-Adresse, und eine ungesicherte Seite in einem gesicherten Rahmen scheitert an Mixed-Content (Doku 06 beschreibt den Weg über den Proxy).
Gordslider: "resonance + joy. A game inside the world. Not every interaction has to be philosophical." For the forum the embedding is technically not trivial.

**Idee, Vision, Planung / Idea, vision, plan.** Gordslider ist in der Inventur „nach dem Einzug“ interessant, wenn Wesen wirklich spielen können; im Schlaf oder in einer Spielphase am Gordslider aktiv zu werden, „wäre eine echte Wesen-in-der-Welt-Objekt-Interaktion“. Doku `_claude/ideen/wesen-desktop.md` nennt Gordslider als „erste Testanwendung“, die Wesen am geteilten Desktop spielen könnten, „als spielerischer Einstieg“. In der 3D-Pipeline (Doku 36) gehört ein „GORDSLIDER 3D-Heldenkörper“ zu den Spezial-Bauwerken von Generation 4, neben einem Casino und einer Rennstrecke.
Gordslider becomes interesting "after move-in", when beings can really play. `_claude/ideen/wesen-desktop.md` names it as the "first test application" that beings could play on the shared desktop. In the 3D pipeline (doc 36) a "GORDSLIDER 3D hero body" is one of the special structures of generation 4.

**Was liegt drin / What is inside.** Die frühe Fassung als Datei: `fruehe-ai-projekte/gordslider/gordslider.html`, beschrieben in `VOR_FLEXTRAWURST.md`. Der Tab: `inventur/26_gordslider.md`.

**Baustand / Build state.** Inventur: funktioniert, Tab repariert, versteckt, „Wesen-Interaktion nicht implementiert, Wesen spielen nicht selbst“. Doku 55 ordnet Gordslider, Flarum und Zensi als „drei fast identische Iframe-Wrapper“ ein, ohne Beanstandung.
Inventory: works, tab repaired, hidden, "being interaction not implemented, beings do not play themselves". Doc 55 classes Gordslider, Flarum and Zensi as "three almost identical iframe wrappers", no objection.

---

## 11. Die Spiegel-Syncs der AI-Zuhause (zwölf Skripte, Doku 54 Teil C §2)

**Versucht / Tried.** Zwölf Kopien eines kleinen Skripts, die alle 5 Sekunden das Zuhause eines AI-Stroms in das eines anderen spiegeln (Einweg, atomar kopiert, Verschwundenes wird auch im Ziel entfernt).
Twelve copies of a small script that every 5 seconds mirror the home of one AI stream into that of another (one way, atomically copied, vanished files are also removed in the target).

**Aus welchem Problem / From which problem.** Kein Anlass in der Doku. Die Regel dahinter steht im Repo-Regelwerk: Spiegel sind Referenz und nie die eigene Erinnerung. **(Daniel ergänzt)**
No occasion in the doc. The rule behind it is in the repo rules: mirrors are reference and never one's own memory.

**Was es lösen sollte / What it was meant to solve.** Dass jeder Strom die Zuhause der anderen lesen kann, ohne in sie hineinzuschreiben.
That each stream can read the homes of the others without writing into them.

**Idee, Vision, Planung / Idea, vision, plan.** Doku 54 hält eine Auffälligkeit fest: Die Sync-Matrix ist nicht symmetrisch. Claude und Codex importieren je vier Quellen, Gemini und Kimi je zwei, Grok kommt als Quelle oder Ziel gar nicht vor. Ob das Absicht ist, bleibt laut Doku offen.
Doc 54 records an oddity: the sync matrix is not symmetric. Whether that is intended stays open per doc.

**Was liegt drin / What is inside.** `*_grundriss_sync.py` unter `werkraum/_claude/tools/`, `_codex/tools/`, `_gemini/tools/`, `_kimi/tools/`; Überblick in `HEIMAT_ORDNER.md` und `WEGWEISER/ai_stroeme_und_atlas.md`.

**Baustand / Build state.** Doku 54, 2026-08-14: klein, klar, „tun exakt, was sie sollen“.
Doc 54, 2026-08-14: small, clear, "do exactly what they should".

---

## 12. Wächter im Hintergrund: Datei-Watchdog und Gesamtatlas-Timer (Doku 54 Teil C §5, §7)

**Versucht / Tried.** Ein Beobachter, der Änderungen im Werkraum als JSONL-Zeilen in eine kurze Datei schreibt (Kürzung auf 300 Zeilen ab 500 KB, geprüft nur alle 50 Ereignisse), und zwei Timer, die den Gesamtatlas stündlich (leicht) und alle paar Stunden (voll) aktualisieren.
An observer that writes changes in the workspace as JSONL lines into a short file, and two timers that update the master atlas hourly (light) and every few hours (full).

**Aus welchem Problem / From which problem.** Doku 54 vermutet, dass der Watchdog die Quelle der „neue Dateien“-Sicht im Delta-Skript des Kontext-Rituals ist, das Skript aber nicht nachgeprüft wurde. Anlass der Timer: **(Daniel ergänzt)**.
Doc 54 assumes that the watchdog is the source of the "new files" view in the delta script of the context ritual, but did not check the script.

**Was es lösen sollte / What it was meant to solve.** Wahrnehmung, was sich geändert hat, ohne selbst zur Bremse zu werden („bewusst nicht bei jedem einzelnen Schreibvorgang“).
Awareness of what changed without becoming a brake itself.

**Idee, Vision, Planung / Idea, vision, plan.** Der Gesamtatlas selbst ist beschrieben in `PROJEKTE/03_gedaechtnis_und_wissen.md` (MegaVault und Gesamtatlas).
The master atlas itself is described in `PROJEKTE/03_gedaechtnis_und_wissen.md`.

**Was liegt drin / What is inside.** `werkraum/watchdog_daemon.py`.

**Baustand / Build state.** Beide Timer feuerten laut Doku 54 am 2026-08-14 tatsächlich und liefen sauber durch; der Watchdog „tut seinen einen Job“.
Both timers actually fired on 2026-08-14 per doc 54 and ran through cleanly; the watchdog "does its one job".
