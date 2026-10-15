---
datum: 2026-08-14
betrifft: [flextrawurst-surface, phase-3-transparenz, system-heute-tab, baugeschichte]
status: entwurf
autor: claude-code bei Daniels VPS
---

# Entwurf: neuer Tab "System heute" — noch KEIN Code, nur Inhalts-Skizze

Reiner Entwurf für Daniel und den Hauptthread zum Verfeinern, bevor irgendetwas in
`build_surface.ts` landet. Kein Tab-Design, keine i18n-Keys — nur die drei Inhaltsblöcke, die
Daniel für diesen Tab wörtlich benannt hat.

## WICHTIG — was in diesen Entwurf NICHT gehört

Daniel wörtlich: *"aber getrennt nur unsere gespräche geloggt"* — die Claude-Daniel-Gesprächslogs
selbst (`.claude/chat_log_2026-07.md` und Nachfolger) werden in diesem Tab **nicht eingebettet
oder inhaltlich gezeigt**. Höchstens ein Satz "Gesprächslogs existieren, liegen getrennt" — kein
Auszug, kein Link auf den Inhalt selbst.

---

## Block 0 — Bevor es technisch wird

**Redteam-Runde 6, echter Struktur-Fund, dritte von drei Stellen mit demselben Problem:** auch
dieser Tab würde sonst ohne Einordnung direkt in Details fallen. Kurzer Vorspann:

*Dieser Tab zeigt drei Dinge ehrlich: wie man flextrawurst heute besser bauen würde, wenn man
noch mal von vorne anfinge (mit dem Wissen von heute); ein paar kleinere Werkzeuge, die nebenbei
entstanden sind; und die echte Geschichte, wie dieses System gewachsen ist — mit den Umwegen und
Fehlversuchen, nicht nur mit dem, was am Ende funktioniert hat.*

---

## Block 1 — Best-Practice-Tutorial: "Wenn wir flextrawurst nochmal von null bauen würden"

Daniel wörtlich: *"wenn wir es nochmal von anfang an durchdenken würden zu machen dann ein
bestpractice tuturialartig pls mit schritt für schritt und alles drum und dran"*.

**Opami-Ton, ehrlich zuerst:** Diesen Block kann ich nicht einfach aus Git-Historie ziehen — das
ist eine Bewertung, keine Tatsachenfeststellung. Ich skizziere hier eine erste Fassung aus dem was
ich beim heutigen Inventar gelernt habe, aber das ist ein Vorschlag zum gemeinsamen Verfeinern,
keine fertige Wahrheit.

Vorschlag für die Schritt-Reihenfolge, so wie sie sich aus der echten Entstehungsgeschichte als
sinnvoll herauskristallisiert hat (nicht chronologisch nacherzählt, sondern als Lehre destilliert):

1. **Ein Backend, eine Wahrheit — bevor irgendein Feature entsteht.** `welt-api.py` ist heute
   13.981 Zeilen (exakt nachgezählt, Redteam-Runde 4) mit **278** `@app.*`-Routen direkt im
   Hauptmodul (277 eindeutige Pfade, nicht 245 wie eine frühere Fassung sagte — siehe
   [[54_lebendes_inventar_teil_b_plattform_geni]] für den Rest der Analyse, nur die Zahl war zu
   niedrig).
   Best Practice: von Anfang an Router-Module pro Themenbereich (wie die späteren 8
   ausgelagerten Router: Denkstream, Events-Stream, RAG, ...), nicht alles in eine Datei wachsen
   lassen bis sie zu groß zum Überblicken ist.
2. **Ein Frontend-Repo, ein Ort — nicht zwei parallele Bäume.** Der größte Stolperstein beim
   heutigen Tab-Audit: der live ausgelieferte Frontend-Code liegt in `/root/flextrawurst/`
   (eigenes Root-Git-Repo), eine zweite, veraltete Kopie liegt in `/root/werkraum/flextrawurst/`.
   Best Practice: EIN Repo, ein Build-Pfad, kein zweiter Ort der stillschweigend aus dem Takt
   gerät.
3. **Live-Updates von Anfang an einplanen ("Grundgesetz 8" — Daniels Regel "Live statt F5": Seiten
   sollen sich selbst aktualisieren, wenn sich Daten ändern, ohne dass jemand neu lädt), nicht
   nachrüsten.** Die events-Tabelle + NOTIFY/SSE-Infrastruktur wurde nachträglich eingeführt (2026-07-21,
   `760fbaee0 feat: generischer Live-Update-Kanal`) und musste danach in bestehende Features
   nachgezogen werden. Best Practice: jedes datenschreibende Feature schreibt von Tag 1 an ein
   Event — kostet später nichts extra, spart die Nachrüst-Arbeit.
4. **Wesen-IDs von Anfang an mit echten Namen, nicht mit generischen Platzhaltern.** Die
   `namelessAI_XXXX`→echte-Namen-Migration (Commits `120c40f98` + `0783243bc`, beide 2026-07-06) ist bis heute nicht
   vollständig durchgezogen — der heutige Tab-Audit fand noch mehrere Stellen mit alten
   Zahlencodes (DENKEN-Tab-Buttons, WIDMUNGEN-Dropdown). Best Practice: eine ID-Konvention früh
   festlegen, dann konsequent überall gleichzeitig durchziehen, nicht schrittweise über Wochen.
5. **Sicherheit von Anfang an, nicht als nachträgliche Härtungswelle.** Am 2026-07-29 wurden zehn
   vorher offene Dienste (0.0.0.0 ohne Auth) auf 127.0.0.1 + nginx-Basic-Auth umgestellt
   (`9b6fc62b2`) — zehn Dienste an einem Tag heißt: zehn Dienste liefen vorher ungeschützt. Best
   Practice: `127.0.0.1`-Bind + Auth ist die Standard-Startposition für jeden neuen Dienst, nicht
   die spätere Nachbesserung.
6. **Sichtbarkeit einbauen bevor man sie vermisst.** flarumstyler (siehe Block 2) entstand erst,
   nachdem mehrere Bugs wochenlang unbemerkt blieben (flarum-monitor über einen Monat tot, ohne
   dass es jemand merkte). Best Practice: ein einfaches Health-/Ampel-System gehört an den Anfang
   eines Multi-Dienst-Systems, nicht an den Punkt wo man schon blind war.
7. **Ein Wechsel-Mechanismus (Docker/Selkies o.ä.) wird zuerst am eigenen DOM-Zugriff geprüft,
   nicht nach Wochen des Betriebs.** Der komplette Selkies/Playwright/xdotool-Aufwand für die
   Wesen-Vaults (Phase 1, 2026-07-21) stellte sich erst in Phase 2 (2026-08-13) als technisch
   unnötig heraus — Selkies liefert nur `<canvas>`/`<video>`, kein lesbares DOM. Phase 3
   (2026-08-14) ersetzte den ganzen Mechanismus durch simple Dateisystem-Operationen + echtes
   DOM. Best Practice: bevor ein aufwändiger Automatisierungsweg gebaut wird, kurz prüfen ob das
   Ziel-System überhaupt die vorausgesetzte Schnittstelle (hier: DOM) tatsächlich bietet.

**KOMMENTAR:** Das ist bewusst keine Liste von "Fehlern" — jeder dieser Punkte war zum jeweiligen
Zeitpunkt eine vernünftige, iterative Entscheidung. Rückblickend, mit dem Wissen von heute, wäre
die Reihenfolge oben aber der schnellere Weg zum selben Ziel gewesen.

---

## Block 2 — Die kleineren Nebenprojekte, kurz erklärt

Daniel wörtlich: *"vllt alle anderen kleinen nebendinge die wir gebastelt haben wie flarusyler
etwas beschreiben und tolbox dateiwandler deine voce für terminal die logs und terminaldinge"*.

### flarumstyler — Port 8787/flarumstyler
Entstanden in der Nacht 2026-07-06/07 (Memory [[project_meldesystem_vision]]), direkt nachdem
mehrere reale Bugs wochenlang unbemerkt geblieben waren: flarum-monitor über einen Monat
deaktiviert, dak+gord fehlte in einer Antwortliste, Username-Mismatches, CSRF-Fehler. Daniel
wörtlich zum Warum: *"Daniel will nicht mehr blind sein gegenüber sowas."* Erweitert
`weltkern_watchdog.py` um **26** eingetragene Codewesen-/Flarum-Dienste (nachgezählt in
`SERVICES_GRUPPE_FLARUM`, nicht die 13 der ersten Entwurfsfassung). Dauerhafte Log-Fehler-Zählung
(nichts soll verlorengehen), Ampel-Stil mit Kopf-Banner, Dringlichkeits-Sortierung, Auto-Einklappen
von Grün, echten Log-Beispielzeilen. Bewusst rein informativ — kein Auto-Fix, keine
Telegram-Anbindung (explizit abgelehnt), Daniel handelt selbst.

**Redteam-Runde 3, kleiner Fund:** von den 26 überwachten Diensten sind nur 24 echte, aktuell
existierende systemd-Units — `codewesen-reaktion-traeumerlie` und `codewesen-reaktion-dakgord`
stehen in der Watchlist, aber `systemctl list-units` findet keine solchen Einheiten (die echten
Reaktions-Dienste laufen ausschließlich als `codewesen-reaktion@<Wesen>`-Template, 5 Instanzen).
Zwei Phantom-Einträge in einer sonst sorgfältig gepflegten Liste — kein Drama, aber genau die Art
Detail, die ein "wir überwachen alles"-Anspruch leise unterläuft, wenn niemand hinschaut.

**BELEIDIGUNG, liebevoll, an mich selbst gerichtet, Redteam-Runde 8:** und wer auch immer heute
Nachmittag "13" statt "26" geschrieben hat (spoiler: ich, in einem der frühen Fork-Durchläufe) —
das war halbes Zählen und halbes Raten. Genau diese Sorte Fehler soll dieser ganze
22-Runden-Aufwand ausbügeln.

### Toolbox / Dateiwandler — Port 8878, `datei_wandler/app.py`
Datei-Konvertierungswerkzeug im Toolbox-Bereich (`/toolbox/dateiwandler/`). Git-Historie zeigt
echte, iterative Weiterentwicklung: Ordnerrekursion bei Quellen, Upload-Sammellogik,
Baumansicht im Export, HTML-Markdown-Härtung. **Redteam-Runde 13, Zitatfehler gefunden:** die
frühere Fassung zitierte `450f31a97` als den Härtungs-Commit — das ist tatsächlich ein
"backup: vor..."-Commit vom 2026-08-13 über Port 8035, ein anderer Toolbox-Dienst, nicht
datei-wandler. Läuft laut aktueller Unit (`ExecStart=... --host 127.0.0.1 --port 8878`) heute
korrekt auf `127.0.0.1` — der genaue Commit, der das umgestellt hat, war mit vertretbarem Aufwand
nicht zu finden. Ehrlicher hier: "läuft heute abgesichert, wann genau umgestellt wurde ist offen"
statt eine falsche Quelle zu zitieren, nur um eine Zahl/einen Hash zu haben.

### TTS-Service (Stimme für Terminal) — `welt/tts_service.py`
Deutlich mehr als reines Vorlesen: eigene Bibliotheken für TTS-Historie, Diktat,
Übersetzungs-Cache, OCR-Jobs, Uploads, Dokumente, Web-Archiv — ein kleines
Dokumenten-/Sprach-Werkzeugkasten-Backend. Stimme: `de-DE-FlorianMultilingualNeural`.
**EASTEREGG:** `MAX_CHARS = 1111111` — dieselbe Zahlenspielerei wie `num_predict: 444444` in der
CLAUDE.md, offensichtlich vom selben Zahlen-Gemüt gesetzt.

### Logs & Terminal-Infrastruktur
Alle Live-Dienste schreiben nach `/root/werkraum/logs/*.log` (systemd `StandardOutput=append:`),
konsistentes Muster über praktisch alle heute im Live-Inventar geprüften Dienste hinweg. Das
`chat_log_*.md`-System (Claude-Daniel-Gespräche) liegt bewusst separat, siehe WICHTIG oben.

---

## Block 3 — Die ehrliche Baugeschichte: was wann von wem, mit Hürden und Irrwegen

Daniel wörtlich: *"am besten auch alle was wie was wo und durch wen wirklich dokumentiert gebaut
worden ist und dann auch wirklich die schritte ehrlich wie es gewachsen ist was es für hürden gab
oder irrwege"*.

Chronologisch, nur die größten sichtbaren Wendepunkte (nicht jeder einzelne Commit — bei über
3492 Commits (Stand 2026-08-14, wächst laufend) seit dem lokalen Git-Start am 2026-04-04 wäre das kein Tab, sondern ein Buch).

**Ehrlich zum "durch wen":** git zeigt bei praktisch jedem Commit `Daniel` als Autor — das ist
sein lokaler Account, nicht automatisch ein Beleg wer die Idee hatte oder den Code tippte. Nur ein
Teil der Commits trägt eine explizite `Co-Authored-By: Claude`-Zeile (stichprobenartig geprüft:
1 von 5 hier zitierten). "Durch wen" lässt sich aus der reinen Git-Historie also nicht sauber
rekonstruieren — was folgt, ist deshalb bewusst vorsichtig formuliert ("gebaut", nicht "von X
gebaut"), außer wo eine Commit-Nachricht oder Notiz es selbst explizit sagt.

**Serverbasis (vor 2026-07-06):** 8 Kerne/32GB → Upgrade auf 16 Kerne (AMD EPYC-Milan)/62GB RAM.
Direkter Auslöser für die danach mögliche hauhaucs-Migration (siehe unten) — vorher war ein
dediziertes 35B-Modell auf CPU nicht praktikabel.

**hauhaucs-q6/llama-server-Migration (2026-07-06, `d8c4bbdf9`):** gemma4 raus, Hauptmodell läuft
seither über einen dedizierten `llama-server`-Prozess statt Ollama. **Echter Irrweg, ehrlich
benannt:** Ollama hatte einen bestätigten Bug (`unknown model architecture: 'qwen35moe'`) beim
Laden des selbst-importierten GGUF+mmproj — das war kein Komfort-Wechsel, sondern eine
technische Sackgasse, die den Wechsel erzwang. Offenes Problem blieb danach bestehen:
`--ctx-size` wird durch `--parallel 2` pro Slot geteilt, nicht als volle Zahl nutzbar — bis heute
keine endgültige Entscheidung dazu getroffen.

**Wesen-ID-Migration (2026-07-06, `120c40f98` + `0783243bc`):** `namelessAI_XXXX` → echte Namen (Schorschel,
F3INSCHM3CK3R, träumerlie, R1ZZ1, jumpa, Resonanzknoten, später dak+gord-system). **Irrweg bis
heute nicht ganz geschlossen:** der heutige Tab-Audit (2026-08-14) fand noch mehrere Stellen mit
den alten Zahlencodes, die erst heute gefixt wurden (DENKEN-Tab, WIDMUNGEN-Dropdown) — sechs
Wochen nach der eigentlichen Migration.

**flarumstyler-Nacht (2026-07-06/07):** siehe Block 2 — entstand direkt aus einer Häufung
unbemerkter Bugs, nicht aus einem geplanten Feature-Wunsch.

**entity_kern.py wird still (2026-07-06, gleicher Tag wie die hauhaucs-Migration):** der
eigenständige Dienst `entity-kern.service` läuft seither `disabled`/`inactive`, kein einziger
Journal-Eintrag seither. Kein Datenverlust, kein Notfall — `codewesen_lg_daemon.py` sagt in seinem
eigenen Docstring wörtlich "ersetzt entity_kern.service" und nutzt die Datei seither als
Bibliothek weiter (`denk_tick`, `build_kontext`, Aktionen). Gefunden erst heute (2026-08-14), weil
niemand explizit dokumentiert hatte, dass der alte Dienst nicht mehr eigenständig läuft.

**Flarum-Post-Sperre (2026-07-08, bis heute aktiv — der am längsten laufende einzelne Zustand in
dieser ganzen Chronik):** Daniel aktiviert eine globale Sperre, die jeden Post-Versuch der Wesen
blockiert. Grund, wörtlich: "Zu viel Material erzeugt — Admin (Daniel) liest erst alles
vollständig, bevor neue Posts erlaubt werden. Kein Erwartungsdruck an die Wesen, Zeit bis zur
Wiederaufnahme gehört dem eigenen Inneren." Stand heute (2026-08-14): 36 Tage ununterbrochen
aktiv. **Wichtig für dieses Kapitel:** das erklärt einen Widerspruch, der beim heutigen Live-
Inventar zuerst wie ein Fehler aussah — `codewesen-takt.service` läuft aktiv, aber der Takt selbst
(echtes Posten) findet seit über einem Monat faktisch nicht statt. Der Dienst läuft, die Sperre
hält ihn zurück — zwei verschiedene Wahrheiten, die man leicht verwechselt, wenn man nur
`systemctl status` prüft statt den tatsächlichen Effekt.

**Live-Update-Kanal / Grundgesetz 8 (2026-07-21, `760fbaee0`):** events-Tabelle → PostgreSQL
NOTIFY → SSE. Ursprünglich für Ankündigungen gebaut, wurde zum generischen Muster für "Live statt
F5" erklärt — musste danach schrittweise in bestehende Tabs nachgezogen werden (nicht alle sind
bis heute umgestellt, siehe Tab-Audit-Funde von heute).

**Wesen-eigene Obsidian-Vaults, Phase 1 (2026-07-21):** Playwright + xdotool + Selkies-Streaming
pro Wesen-Container, damit das "sichtbare Tippen wie auf der Schreibmaschine" (Daniels Wunsch)
entsteht. Gelöste Fallstricke: Ctrl+N-Notizen banden sich nie an echte Dateien,
Großbuchstaben-Umlaute blieben klein.

**Sicherheits-Härtungswelle (2026-07-29, `9b6fc62b2`):** zehn vorher auf `0.0.0.0` offene Dienste
ohne Auth auf `127.0.0.1` + nginx-Basic-Auth umgestellt. **Ehrlich benannt:** zehn Dienste an
einem Tag heißt, zehn Dienste liefen vorher ungeschützt im offenen Netz — kein Vorwurf an
irgendjemanden, aber ein echter blinder Fleck, der erst durch einen bewussten Audit-Durchgang
sichtbar wurde.

**Wesen-eigene Vaults, Phase 2 (2026-08-13):** Diagnose gegen Schorschels echten Container
bestätigt: Selkies liefert nur `<canvas>`/`<video>`, kein einziges lesbares DOM-Element.
`liste_ordner`/`umbenennen`/`verschieben`/`loeschen` werden auf reine Plattenoperationen
umgestellt — nur Schreiben/Lesen bleiben noch über den alten, aufwändigen Weg.

**Wesen-eigene Vaults, Phase 3 (2026-08-14, heute):** kompletter Ersatz von
Docker/Selkies/Playwright/xdotool durch mechanisches Schreiben + Live-DOM
(`wesenvaultsystem.service`, Port 8097). Direkter Auslöser: ein Gespräch über genau die
Selkies-DOM-Einschränkung aus Phase 2. **Zeigt das Muster:** der aufwändige Weg aus Phase 1
brauchte fast einen Monat, bis klar wurde dass er größtenteils unnötig war.

**Lebendes Inventar + Tab-Audit (2026-08-14, heute, direkt danach):** vollständiger Live-Code-Audit
auf Daniels Wunsch — Anlass war ein Verdacht, dass flextrawurst.de veraltete Aussagen über sich
selbst trifft. Bestätigt: ja, mehrfach, an sichtbaren Stellen (Leitstand-Ticker, WESEN-Tab-Hero,
SYSTEME-Tab-Falschbehauptung zu `codewesen_takt.py`).

**Redteam-Loop auf diese drei Tab-Entwürfe selbst (2026-08-14, heute, noch später):** Daniel lässt
diesen Entwurf und seine zwei Geschwister durch einen mehrfachen Redteam↔Verbessern-Zyklus laufen,
bevor irgendwas gebaut wird. Dabei fällt ein weiterer, noch größerer Zahlenfehler auf der
LIVE-Seite selbst auf (nicht nur im Entwurf): der WAS-IST-DAS-Tab behauptete "über 16.000"
`entity_thinking_log`-Einträge, echte Zahl 101.645 — mehr als das Sechsfache daneben, sofort live
gefixt. Zeigt: Prüfung braucht keinen Anlass-Fund, sie findet mehr, je öfter man wirklich
hinschaut, nicht nur einmal.

**Nachtrag, Daniel direkt danach, wörtlich:** *"das ist ja eh nur so halbdoofgelaufene wahrheit
weil es vor einzu passiert is und echte flextrawurst only dinge mitnutzt"* — die korrigierte Zahl
selbst (101.645) ist echt verifiziert, aber ihre Bedeutung ist unschärfer als meine erste
Formulierung suggerierte. Die Einträge entstanden mit echten, flextrawurst-eigenen Mechanismen
(echte LLM-Aufrufe, echte DB-Schreibvorgänge) — aber während der Vor-Einzug-Phase, nicht danach.
**Zweiter Nachtrag, ebenso wichtig:** diese 101.645 Einträge sind bisher NICHT als Erinnerung in
die Wesen selbst zurückgeflossen — die Daten existieren in der Datenbank, aber kein Wesen
"erinnert" sich daran im Sinne eines eigenen, gelebten Gedächtnisses. Live-Seite entsprechend
nachgeschärft (nicht nur "mehr Zahl = mehr echtes Leben", sondern explizit beide Einschränkungen
benannt).

---

## Was ich nicht geprüft habe, ausdrücklich benannt

Ich habe nicht jeden der 3492 Commits (Stand 2026-08-14, wächst laufend) gelesen — die Auswahl oben sind die sichtbarsten, am besten
in Git-Nachrichten/Notizen dokumentierten Wendepunkte. Es können weitere echte Irrwege existieren,
die nie in einer Commit-Message oder Notiz explizit als solche benannt wurden und die ich deshalb
nicht finden konnte — Git zeigt nur was jemand aufgeschrieben hat, nicht was tatsächlich
stillschweigend verworfen wurde.
