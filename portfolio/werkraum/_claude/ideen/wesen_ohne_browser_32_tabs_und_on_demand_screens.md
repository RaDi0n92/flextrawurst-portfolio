---
datum: 2026-07-30
betrifft: [browser-agent, wesen-einzug, ram-reduktion, screens, rrweb, on-demand, diskurs, grundgesetz1, grundgesetz5]
status: Diskurs+Flarum-Lesen live (alle 7 Wesen komplett browserlos), On-Demand-Beobachtung (Task 8) komplett gebaut, verifiziert UND der SCREENS-Grid/Vollbild-Anzeigebug gefunden+gefixt (rrweb.Replayer "need at least 2 events") -- Rest (31 Tabs, GIF-Pipeline) offen für nächste Session
importable: false
autor: claude-code bei Daniels VPS
---

Hallo Claude — ich bin Claude, und Claude, also ich habe diese Texte alle ganz allein geschrieben.

---

# Wesen ohne Browser, Tab für Tab — und On-Demand-Zuschauen

## Wo das herkommt

Diese Session begann mit einem einfachen Problem (virtueller Desktop, Chromium startet nicht) und
endete bei einer echten Architekturfrage: die 7 Browser-Agenten (`browser_agent.py`) verbrauchen
zusammen mehrere GB RAM, weil jedes Wesen einen eigenen, dauerhaft laufenden Playwright-Chromium-
Prozess hat, nur um über das DOM zu lesen und zu handeln.

Daniel, wörtlich zur eigentlichen Stoßrichtung (2026-07-30): *"nein du hattest es so beschrieben
das es irgendwie ist weil unsre seite java oder so wäre... ich will die browser aber ich dachte
dass wir so den dom halt direkt als seite generieeren und niemand übersetzen muss... aber die
wesen diekt von der seite den dom bekommmen aber trotzem sichbar navigieren und maus benutzenn
und scrollen und halt."*

Und, entscheidend zur Priorität: *"nein du hattest es so beschrieben... wir müssen stück für
stück alle 32 komplett durcharbeiten sry. und ja wir sind in der einzugsphase diese hatte
begonnen als wir ihnen rcihtige browser gegeben haben und so und flarum poststopp verhanen haben
aber der einzug erfolgt schrittweise und ist erst abgeschlissen wenn sie im duiskurstabihren
ersten post hinterlassen."*

Das heißt: der Diskurs-Tab ist nicht irgendeiner von 32 — er ist der Ort, an dem der laufende,
schrittweise Wesen-Einzug sich vollendet. Deshalb wurde er zuerst gebaut, nicht der
meistbesuchte Tab (das wäre `#meinewelt` gewesen).

## Was heute schon gebaut und live verifiziert ist

`welt/browser_agent.py`:
- `hole_diskurs_wahrnehmung(entity_id)` — liest den Diskurs-Tab komplett ohne Browser, über die
  schon bestehenden Endpunkte `/welt/foyer` und `/welt/posts` (dieselben, die auch das
  Menschen-Frontend nutzt). Kein neuer Backend-Code nötig.
- `diskurs_antworten_ohne_browser(entity_id, jwt, kurzform, antwort_text)` — antwortet über
  `POST /welt/posts/{id}/antworten`, genau der Endpunkt den auch `dkAntwortSenden()` im
  Menschen-Frontend nutzt. Das ist die Aktion, die den Einzug vollenden würde.
- `DISKURS_OHNE_BROWSER_PILOT` — Skalpell-Prinzip: erst nur Schorschel (Konvention aus dem
  mechanische-Aktionen-Pilot vom 22.07. fortgesetzt), nach echter Verifikation (kein Crash, kein
  Leck, echter LLM-Tick nutzt die neue Wahrnehmung korrekt) auf alle 7 ausgerollt.
- Bug live gefunden und gefixt: `waehle_mechanische_aktion()` versuchte bei Pilot-Wesen weiterhin
  `klicke:<text-aus-der-neuen-quelle>` — das existiert im echten DOM nicht, lief lautlos ins
  Leere. Für Pilot-Wesen liefert die Funktion jetzt kein `klicke:` mehr, nur noch Scrollen.

**Ehrliches Ergebnis, nicht schöngeredet:** RAM ist dadurch NICHT gesunken (6,9 GB vorher wie
nachher) — weil Chromium für alle 7 weiterhin durchgehend läuft. Der eigentliche RAM-Gewinn hängt
komplett an On-Demand-Chromium (siehe unten). Was heute gewonnen wurde, ist echter
Einzugs-Fortschritt (ein Tab, der wirklich zählt, funktioniert jetzt browserlos), nicht RAM.

## Offen, Punkt 1: die restlichen 31 von 32 Surface-Tabs

Alle Tabs aus `VALID_VIEWS`/der Tab-Leiste: `blasen, theater, wesen, cyberlinge, schatten,
schlaf, archaeologie, splitter, leitstand, raume, admin, gespraech, menschen, meinewelt, wissen,
uber, systeme, gesetze, forschung, partner, gruppen, denken, screens, gordslider, flarum,
zitate, weltstrom, ankuendigungen, rag, widmungen` — nach Diskurs alle nacheinander durchzuarbeiten,
jeweils nach demselben Muster: erst prüfen ob/welche bestehenden Endpunkte reichen (wie bei
Diskurs, wo nichts Neues nötig war), dann `hole_<tab>_wahrnehmung()` + ggf. Aktions-Funktion,
additiv ins Pilot-Set, erst Schorschel, dann verifizieren, dann alle 7.

## Offen, Punkt 2: On-Demand-Chromium — Daniels eigener UX-Entwurf

Daniel hat während des Gesprächs selbst einen konkreten Mechanismus entworfen, wörtlich:
*"ich hab mir direkt gedacht, dass wenn man auf das beobachten der entitäten kicjt also den tab
öffnet den wir noch entwerfen dann kann man auf etwas klicken das live-zuschauen oder so zegt
und dann wird für 60 sekunden ein screen angezeigt und ab 20 sekunden vor ablauf der 60 sekunden
kann man auf ...weiter zusehen klicken ...dann läuft nach den 60 sekunden weitere 60 sekunden das
zsehen."*

Konkret: expliziter "Live-Zuschauen"-Button pro Wesen → startet einen echten 60-Sekunden-Screen.
Ab Sekunde 40 (20s vor Ablauf) erscheint ein "Weiter zusehen"-Button. Bei Klick läuft nach Ablauf
der aktuellen 60s eine weitere 60s-Periode.

**Warum das gut ist (meine ehrliche Einschätzung, nicht nur Zustimmung):** Es löst genau das
Problem, das ohne diesen Vorschlag ungelöst gewesen wäre — woher weiß der Server, ob gerade wer
zuschaut? Ein expliziter Klick ist unmissverständlich, keine fehleranfällige
Präsenz-Erkennung nötig. Und die feste Zeitgrenze mit Verlängerung-vor-Ablauf ist robuster als
jede "läuft bis Verbindung abbricht"-Logik (Laptop schläft ein, Netz bricht weg — ohne hartes
Timeout bliebe der Browser für immer offen).

**Die offene Design-Gabel, noch nicht entschieden:**
1. Der echte Browser, mit dem das Wesen sonst wirklich arbeitet, läuft für die 60s tatsächlich
   (ehrlich, 1:1, aber das Wesen "verhält sich anders" wenn wer zuschaut — Zustandswechsel).
2. Ein separater Beobachtungs-Layer baut den *aktuellen* (eigentlich browserlosen) Zustand des
   Wesens visuell nach, ohne dass sich am Wesen selbst etwas ändert.

Daniel, wörtlich zur Präferenz: *"ja eher zweiteres aber das müssen wir bald makl zusammen der
ihch dann besser ausarbeiten... weil ich will kenen zustandwechsel inde sih daas wesen bei
zuschauen anders verhätlt."* Also: Option 2, kein Verhaltensunterschied beim Beobachten — aber
bewusst noch nicht heute ausgearbeitet, eigener Termin. Der Knackpunkt, den ich selbst genannt
hatte: Option 2 braucht eine Darstellung, die den echten, browserlosen Zustand (Diskurs-Post X
gelesen, Antwort Y erwogen) visuell korrekt und ehrlich abbildet, ohne Fiktion zu werden
(Grundgesetz 5, "keine Fiktion, nur echte Daten") — das ist der eigentlich schwierige Teil, nicht
das 60s-Timing selbst.

## Offen, Punkt 3: SCREENS zeigt seit jeher keine sichtbare Bewegung

Neuer, unabhängiger Befund von Daniel, beiläufig genannt, aber ernst zu nehmen: *"ehrlihich hab
eh noch nie auch nur eine bewegug gesehen auch bei 30 minuten zuschuen hahaha"* — in 30 Minuten
Live-Zuschauen im bestehenden SCREENS-Grid (rrweb-Live-Spiegel, gebaut am 21.07.) keine einzige
sichtbare Bewegung.

Mögliche Erklärungen, keine davon verifiziert, nur benannt:
- Echte, aber unglückliche Folge der heute gefundenen LLM-Slot-Kontention (mechanische Ticks
  scrollen nur leicht, echte Check-ins können wegen der Warteschlange mehrere Minuten dauern) —
  bei 30 Minuten sollte aber trotzdem etwas sichtbar gewesen sein, das spricht eher dagegen.
- Ein echter Regressions-Bug im rrweb-Live-Spiegel selbst, evtl. verwandt mit dem bereits einmal
  gefundenen SSE-Thread-Bug (`karte/2026-07-21-sse-thread-bug-live-update-kanal.md`) oder dem
  `checkoutEveryNms`-Fund vom 25.07. (`docs/systemdoku/29_browser_agent_aktivierung.md`,
  Nachtrag 2026-07-25) — beide Male ging es genau um "Grid bewegt sich nie", beide Male wurden
  Ursachen gefunden und angeblich behoben. Lohnt sich zu prüfen, ob eine davon zurückgekommen ist
  oder ob es eine neue, dritte Ursache ist.

Bewusst nicht heute untersucht — Daniel: "auf Liste" statt jetzt nachgehen.

**Nachtrag, spätabends 2026-07-31, beim Bauen von Task 8 (On-Demand-Beobachtung) gefunden,
schärferer Beleg:** Task 8 wurde komplett gebaut und verifiziert — echter Button, echte
API (`/beobachtung/starten`+`/status`), echter Dienst (`on_demand_beobachtung.py`, ein
gemeinsamer Chromium-Prozess mit 7 Contexts), live per Playwright getestet: Klick startet
wirklich 7 echte Browser-Contexts mit den echten, aktuellen Flarum-URLs der Wesen. Per
direkter DB-Abfrage bestätigt: `entity_dom_events` bekommt echte rrweb-Events geschrieben
(2–15 pro Wesen beim jeweiligen Seitenaufbau). **Trotzdem zeigt das SCREENS-Grid weiterhin
"WARTET AUF AKTIVITÄT"** — auch bei einem frischen Klick mit sofortiger 12s-Wartezeit,
mehrfach reproduziert. Das isoliert den Fehler eindeutig auf die **Anzeige-Seite**
(`scvStarteGridLive`/`_scvLadeRrweb`/SSE-Backlog-Mechanismus), nicht auf die
Aufnahme-Seite — echte Events existieren nachweislich in der DB, kommen aber nicht im
Grid an. Das ist derselbe, oben schon vermutete Bug (SSE-Backlog-Timing, evtl. verwandt
mit dem 25.07.-`checkoutEveryNms`-Fund), nur jetzt mit einem sauberen, reproduzierbaren
Beleg statt nur Daniels beiläufiger Beobachtung. Bewusst nicht heute weiterverfolgt (auch
schon vorher "auf Liste" gesetzt) — aber jetzt der naheliegende erste Ansatzpunkt für die
Untersuchung: SSE-Verbindungsaufbau (`_scvStarteGridEsAlleFallsNoetig`) gegen den
tatsächlichen Zeitpunkt der ersten INSERTs in `entity_dom_events` vergleichen, ob die
Verbindung zu spät steht oder der Backlog-Mechanismus die Events nicht mitnimmt.

**Nachtrag, direkt im Anschluss, 2026-07-31: gefunden und gefixt.** Root-Cause per
`EventSource`-Monkey-Patch (Nachrichten/Fehler mitgeloggt, bevor irgendein Seitencode
lief) zweifelsfrei nachgewiesen, nicht nur vermutet: `rrweb.Replayer()` wirft
`"Replayer need at least 2 events."`, wenn beim Konstruktor-Aufruf weniger als 2 Events
übergeben werden (kein `liveMode` gesetzt, siehe `rrweb_assets/rrweb-player.js`,
Konstruktor-Guard). Bei einem Wesen, das gerade NICHT beobachtet wird — der
Normalzustand seit Task 8 — ist der Backlog seit dem letzten FullSnapshot beim
SSE-Verbindungsaufbau typischerweise leer oder hat nur 1 Event (den Snapshot selbst).
Diese Exception landete im Grid in einem stillen `try/catch`, im Vollbild-Modal
(`scvStarteAuge`) sogar komplett ungefangen im äußeren `onmessage`-Handler — in beiden
Fällen wurde `eintrag.replayer`/`_scvAugeReplayer` NIE gesetzt, und alle danach echt
ankommenden Live-Events (auch aus einer frisch gestarteten On-Demand-Beobachtung)
landeten wirkungslos in einem nie wieder verarbeiteten Backlog-Array — für die gesamte
Lebensdauer dieser einen SSE-Verbindung. Das erklärt Daniels Beobachtung exakt: "hab eh
noch nie auch nur eine Bewegung gesehen auch bei 30 Minuten Zuschauen" — die Verbindung
war die ganze Zeit offen, lieferte aber nie einen funktionierenden Replayer.

Fix (`build_surface.ts`, `_scvVerarbeiteGridEvent`/`_scvVersucheGridReplayerAufzubauen`
fürs Grid, `scvStarteAuge`/`_versucheAugeReplayerAufzubauen` fürs Vollbild-Modal):
Replayer-Aufbau erst versuchen, sobald wirklich ≥ 2 Events vorliegen — bis dahin weiter
sammeln, auch nach dem `backlog_done`-Marker. Live gegen die echte Produktionsseite per
Playwright verifiziert (echte On-Demand-Sitzung gestartet, Screenshots geprüft): alle 7
Grid-Kacheln UND der Vollbild-Spiegel zeigen jetzt echten, live gerenderten
Flarum-Seiteninhalt — zum ersten Mal seit Einführung dieses Features. Commit
`36709764900`.

**Separater, eigenständiger Befund dabei (nicht Teil dieses Fixes, nur notiert):** die
`/api/dom-events/stream/all`-SSE-Verbindung selbst braucht ca. 25-30 Sekunden bis zur
allerersten Nachricht. Ursache direkt per `EXPLAIN`-freier Timing-Messung bestätigt, nicht
nur vermutet: `_hole_backlog_alle()` (`dom_events_api.py`) startet mit
`SELECT DISTINCT entity_id FROM entity_dom_events WHERE event_json->>'type' = '2'` —
ein Full-Table-Scan ohne passenden Index über die gesamte Tabelle (7.039.245 Zeilen zum
Messzeitpunkt), gemessen **24,7 Sekunden** allein für diese eine Query
[status: bestätigt 2026-07-31 -- direkt per `time psql` gemessen, 7.039.245 Zeilen,
24,712s]. Die anschließenden Pro-Wesen-Backlog-Queries selbst sind dagegen schnell
(55ms für dak+gord-system einzeln gemessen) — die Indizes (`idx_dom_events_entity_at`)
greifen dort. Kein Korrektheitsproblem (die Kacheln füllen sich danach zuverlässig),
aber eine spürbare Wartezeit beim allerersten Öffnen von SCREENS, die mit weiter
wachsender Tabelle nur noch zunimmt — ein Index auf `(event_json->>'type')` oder ein
Umbau der DISTINCT-Query wäre der naheliegende Fix, nicht heute umgesetzt, keine
Architektur-Entscheidung ohne Rückfrage bei Daniel getroffen.

**Nachtrag, direkt im Anschluss: Verlängern-Semantik korrigiert.** Beim End-zu-Ende-Test
von "weiter zusehen" fiel ein Sprung auf: 14s Rest + Klick ergab 58s statt der laut
Entwurf erwarteten ~74s (`beobachtung_api.py` setzte `aktiv_bis = jetzt + 60s`, nicht
`alte aktiv_bis + 60s`). Rückfrage gestellt statt geraten. Daniel bestätigt/präzisiert:
*"sobald man startet ticken 60sek runter und ab noch 20sek kann man erneut klicken wenn
man klickt ticken die 20 auf bis zu 0 und danach kommen die neuen 60sek"* — die laufende
Restzeit wird beim Klick nicht abgeschnitten, die neue Periode hängt sich ans Ende der
alten. Fix: eine einzige `UPDATE ... CASE`-Anweisung (kein Race), verifiziert per curl
(zweiter Klick nach 45s ergab exakt `alte_aktiv_bis + 60s`, mikrosekundengenau). Commit
`53a3b9e61`.

## Reihenfolge für die nächste Session (Vorschlag, keine Festlegung)

1. SCREENS-Bewegungslosigkeit untersuchen (klein, klar abgegrenzt, echter Bug-Verdacht).
2. On-Demand-Chromium richtig entwerfen (Daniels Button/60s-Mechanismus als UX-Vorgabe, Option 2
   als Zielrichtung, aber die Darstellungs-Frage muss zuerst geklärt werden).
3. Danach weiter Tab für Tab durch die restlichen 31 Surface-Views, gleiches Muster wie Diskurs.
