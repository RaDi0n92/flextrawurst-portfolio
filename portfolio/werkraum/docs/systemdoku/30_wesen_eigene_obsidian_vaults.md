
# Wesen-eigene Obsidian-Vaults (2026-07-21)

## Auftrag

Daniel, wörtlich, nach dem Fund dass Wesen auf Flarum eher einfrieren als aktiv zu
explorieren: *"theoretisch alles seiten die wir ihnen eröffnen. es müsste zu jedem
erstmal ne art readme mit bester navigationsanleitung und so geben und dann dazu
quasi immer auch ne art schicht geben die diesen 'gesamtbrowsertab' eben minimiert
und dann zum beispiel obsidian öffnet und darin eine ganz neue art von vault erzeugt
vom wesen selbst (mit meiner hilfe usw und auch interaktionsmöglichkeiten) aber ich
will es quasi ohne llm call ich will schreiben in genau der menschenart und weise
quasi im 10 fingersystem ... und dann tippen wie auf der schreibmaschiene"*.

Zwei Architektur-Entscheidungen von Daniel bestätigt:
- **7 eigene, unabhängige Obsidian-Container** statt einem geteilten Fenster (jedes Wesen jederzeit sichtbar, kein Warten aufeinander).
- **Eigener Vault pro Wesen** unter `wesen_vaults/<name>/`, komplett getrennt von der bestehenden `codewesen/<name>/`-Struktur (die ist system-kuratiert, das hier ist selbst-erschaffen).

## Warum GUI-Automation statt der bestehenden `obsidian_api.py`

`obsidian_api.py` (Port 8060) existiert schon und kann sofort Notizen schreiben — aber
als reiner JSON-Bridge-Call, ohne sichtbares Tippen. Daniels Wunsch ("wie auf der
Schreibmaschine", "ohne LLM call" fürs Tippen selbst) verlangt echtes, sichtbares,
zeichenweises Tippen in ein echtes Editor-Fenster — dafür muss ein Wesen tatsächlich
in einer laufenden Obsidian-Desktop-Instanz sitzen, kein Backend-Call reicht.

## Aufbau: erst Pilot (Schorschel), dann auf alle 7 skaliert

Zuerst nur Schorschel gebaut ("erst eine machen, Ergebnis zeigen" — Skalpell-
Prinzip), nach vollständiger Verifikation (siehe unten) auf alle 7 skaliert,
seit Daniel öffentliche Erreichbarkeit UND eigene Editierbarkeit bestätigt hat:
*"ja auch von außen erreichbar und sogar nicht nur zum zuschauen sondern zum
gärtnern und kommunizieren über alles."*

- 7 Container aus `lscr.io/linuxserver/obsidian:latest` (dasselbe Image wie der
  bestehende, von Daniel/Claude genutzte `obsidian`-Container — der bleibt
  unangetastet), eines pro Wesen, eigenes `/config`-Docker-Volume, eigenes
  Passwort (generiert, in `.agent/wesen-vaults.env`, gitignored).
- Vault-Mount: **nur** `/root/werkraum/wesen_vaults/<Name>` → `/vault` je
  Container — bewusst NICHT der ganze Werkraum wie beim Haupt-Container, sonst
  wäre es kein eigener, abgegrenzter Vault.
- Interne Docker-Ports (`127.0.0.1`, nur für die eigene Playwright/xdotool-
  Automation): 3093–3099 (Haupt-GUI) / 3193–3199 (Zweitport), je einer pro
  Wesen, dieselbe Reihenfolge wie `ENTITY_KEYS` in `browser_agent.py`.
- **Öffentlicher Zugriff über nginx, exakt das Muster von Daniels eigenem
  Obsidian-Container repliziert** (`/etc/nginx/sites-available/obsidian`):
  eigener HTTPS-Port pro Wesen auf der Roh-IP (nicht als Pfad unter
  flextrawurst.de — Selkies, das Remote-Desktop-Protokoll, ist nicht für
  Subpath-Mounting gebaut, ein `flextrawurst.de/wesenvaults/...` hätte echtes
  Risiko interner Asset-Pfade gehabt), doppelte Basic-Auth (nginx-Ebene mit
  der bestehenden `.htpasswd`/"Werkraum"-Realm + Container-eigene Ebene):
  Schorschel 8445, F3INSCHM3CK3R 8450, träumerlie 8451, R1ZZ1 8452, jumpa 8453,
  Resonanzknoten 8454, dak+gord-system 8455 (8446–8449 waren durch andere
  Dienste belegt, deshalb die Lücke).
- **Neuer Bug beim Skalieren gefunden:** `WESEN_VAULT_OBSIDIAN_PASSWORD_träumerlie`
  und `..._dak+gord-system` sind als bash-Variablennamen ungültig (Umlaut bzw.
  `+`) — `source` überspringt sie lautlos, der Rollout-Loop brach beim ersten
  ungültigen Namen komplett ab. Gleiche Bug-Klasse wie das `%i`-vs-`%I`-Problem
  bei den systemd-Units vom selben Tag ([[29_browser_agent_aktivierung]]). Fix:
  ASCII-GROSS-Suffixe (`ENV_PASSWORT_SUFFIX`-Mapping in `obsidian_vault_agent.py`),
  ebenso explizite `CONTAINER_NAMES`/`CONTAINER_USERS`-Mappings statt aus der
  `entity_id` abgeleitet (ein Docker-Containername mit Umlaut wäre schlicht
  ungültig gewesen).

## Zugriff: HTTP Basic Auth, WebSocket-Falle gefunden

Der Container schützt sich per HTTP Basic Auth (`CUSTOM_USER`/`PASSWORD`). Playwright mit
`extra_http_headers={"Authorization": "Basic ..."}` reicht NICHT — Chromium trägt
manuell gesetzte Header nicht zuverlässig über die WebSocket-Upgrade-Anfrage weiter
(Selkies, das Remote-Desktop-Protokoll dieses Images, verbindet per WebSocket zum
Streaming-Endpunkt). Fehlerbild: Bild bleibt schwarz, Konsole zeigt endlose
"WebSocket disconnected, reloading page to reconnect." Fix: Playwright-native
`http_credentials={"username":..., "password":...}` beim `new_page()` verwenden — das
funktioniert auf Protokollebene und überlebt auch den WS-Handshake.

## Vault-Öffnen ohne fragile GUI-Automation

Der naheliegende Weg — "Open folder as vault" klicken, GTK-Dateidialog per Ctrl+L
einen Pfad eintippen, "Select Folder" klicken — funktionierte bis zum letzten Klick
zuverlässig, aber der finale Button-Klick registrierte nicht zuverlässig (vermutlich
Fokus-/Timing-Eigenheit der Klick-Weiterleitung durch Selkies). Robusterer Weg
gefunden: Obsidian speichert bekannte Vaults in
`~/.config/obsidian/obsidian.json` (im Container: `/config/.config/obsidian/obsidian.json`,
da `HOME=/config`). Diese Datei direkt vorschreiben:

```json
{"vaults": {"<beliebige-hex-id>": {"path": "/vault", "ts": <ms-timestamp>, "open": true}}}
```

Nach einem Container-Neustart öffnet Obsidian den Vault automatisch, komplett ohne
GUI-Klicks — deterministisch, kein Trial-and-Error nötig. Für alle 7 Container beim
ersten Hochfahren so vorzuseeden.

## Echtes Tippen: drei Schichten von Bugs, alle gelöst (oder bewusst akzeptiert)

**Schicht 1 — `page.keyboard.type()` durch Selkies:** sendet zwar echte
Zeichen-für-Zeichen-Events, aber jede Großschreibung geht verloren (bestätigt am
Dateiinhalt: `"Das ist..."` wurde zu `"as ist..."`). Manuelles Modifier-Handling
(`down("Shift")` → `press("KeyX")` → `up("Shift")`) funktioniert zwar isoliert
korrekt, aber `page.keyboard.press()` kennt keine deutschen Umlaute als Key-Namen
(`Unknown key: "ö"`) — für deutschen Text also ohnehin eine Sackgasse.
`page.keyboard.insert_text()` ist noch schlechter: kommt durch Selkies überhaupt
nicht an (0 Zeichen).

**Schicht 2 — der eigentliche Durchbruch, `xdotool` direkt im Container:**
`docker exec <container> xdotool type --delay N "text"` umgeht Playwright/Selkies
komplett und injiziert die Tasten direkt in die X11-Sitzung. Tippt Groß-
/Kleinschreibung UND deutsche Umlaute korrekt (verifiziert: *"Größe, Übung,
Änderung, Straße — Umlaute mittendrin klappen... Zahlen 100%, Satzzeichen!
Fragen? Doppelpunkte: ja."* — praktisch alles richtig). **Einzige verbleibende,
bewusst akzeptierte Lücke:** ein Großbuchstabe-Umlaut (Ä/Ö/Ü) direkt am Anfang
eines `type`-Laufs kommt klein raus (`Übung` → `übung`), Umlaute *mitten* im
Wort sind davon nicht betroffen (`Größe` bleibt korrekt). Daniel dazu wörtlich:
*"scheiss auf großung kleinschreibung mach ich ja auch nicht... falls es nicht
lösbar ist, hab ich's ihnen vererbt haha"* — explizit als unwichtig abgesegnet,
nicht weiter verfolgt.

**Schicht 3 — Speichern auf Platte, der eigentlich harte Teil:** Text, der in
eine per `Ctrl+N` frisch erzeugte Notiz getippt wird, erscheint zwar korrekt im
Editor (ein `Backspace` löscht ihn wirklich — kein Rendering-Fake), landet aber
**nie** auf der Platte, egal wie lange gewartet oder wie oft `Ctrl+S` gedrückt
wird (auch über Playwright direkt, nicht nur `xdotool`). Root Cause: `Ctrl+N`
bindet den Editor-Puffer in dieser Umgebung nie richtig an eine Datei auf der
Platte. Test mit einer **von außen (host-seitig) vorab angelegten** Datei zeigt:
Obsidians Dateisystem-Watcher erkennt sie sofort (taucht in der Seitenleiste
auf), und Bearbeitungen daran speichern sofort korrekt. **Fix: Dateien nie über
`Ctrl+N` in der App selbst anlegen — immer vorher direkt als echte Datei auf der
Platte erzeugen, dann öffnen.**

**Nebenfund beim Robustheitstest:** ein `browser.close()` unmittelbar VOR dem
`xdotool`-Tipplauf reißt den Text nach ungefähr der Hälfte lautlos ab (`xdotool`
selbst meldet trotzdem Erfolg — der Abbruch passiert auf der Empfängerseite).
Fix: Playwright-Verbindung während des gesamten Tipplaufs offen halten, erst
danach schließen.

## Fertiges Modul: `welt/obsidian_vault_agent.py`

```python
import obsidian_vault_agent as ova
ova.oeffne_datei_und_schreibe(
    "Schorschel", "erste-notiz", "Der eigentliche Text ...",
    titel="Erste Notiz — Wesen-eigener Vault",
)
```

Kompletter, verifizierter Ablauf: Datei direkt auf der Platte anlegen (falls
nicht vorhanden) → über den Quick Switcher (`Ctrl+O`, positionsunabhängig,
robuster als Sidebar-Klicks) im Wesen-eigenen Obsidian-Fenster öffnen → ans Ende
springen → `xdotool` tippt den Text, Playwright-Verbindung bleibt währenddessen
offen. End-to-End mit echtem deutschem Text (Umlaute, ß, Gedankenstrich,
Satzzeichen, Prozent) gegen **drei verschiedene** Wesen-Vaults getestet
(Schorschel, jumpa, R1ZZ1), Ergebnis jedes Mal korrekt bis auf die oben
genannte, akzeptierte Lücke.

## Daniels eigener Zugriff zum Mitschreiben — schon vorhanden, kein Neubau nötig

Daniels Frage dazu, wörtlich: *"wo soll ich sie bearbeiten können direkt in
meinem obsidian?"* Antwort: **schon da.** Sein eigener, bereits laufender
Obsidian-Container (`obsidian`, Port 8443) hat `/root/werkraum` komplett
gemountet, und sein `/werkraum`-Vault ist laut `obsidian.json` bereits offen
(`{"path": "/werkraum", "ts": ..., "open": true}`) — `wesen_vaults/<Name>/`
taucht dort automatisch als Unterordner auf, ganz ohne neue Einrichtung. Die 7
separaten Container sind dafür da, dass jedes Wesen jederzeit sein **eigenes**
Fenster hat (nicht geteilt, kein Warten) und damit auch einzeln von außen
besuchbar/beobachtbar ist — eine zweite, unabhängige Zugriffsart auf dieselben
Dateien, kein Widerspruch zueinander.

## Orchestrierung: `obsidian_schreiben`-Aktion, mit Daniel besprochen und bestätigt

Daniel beschrieb den gewünschten Ablauf so: jederzeit von dem, was gerade
gelesen wird, "ausschwenken" dürfen, dort etwas festhalten, ganz vom Thema
abweichen wenn nötig, und danach **an derselben Stelle auf der ursprünglichen
Seite weitermachen**. Antwort darauf ist keine Pause-/Resume-Logik, sondern
eine strukturelle Eigenschaft der bestehenden Architektur: die neue Aktion
`obsidian_schreiben:<dateiname>|<text>` (in `browser_agent.py`) rührt die
Haupt-Seite (`page`, egal ob gerade Flarum, Surface oder sonstwo) nie an — sie
öffnet eine komplett separate Playwright-Verbindung zum eigenen Obsidian-Vault-
Container, schreibt dort, schließt wieder. Die Hauptseite steht die ganze Zeit
exakt da, wo sie stand. Daniels Reaktion auf den Entwurf: *"joa so in etwa."*

Dateiname und Text werden vom Wesen selbst gewählt (gleiches Muster wie
`raum_erstellen:<name>|<slug>`), damit es seine eigene Ordnerstruktur gestaltet
statt alles in eine einzige Datei zu schreiben — ein Pfad wie
`gedanken/2026-07-21` legt automatisch den Unterordner an.

`browser-agent@.service` bekam ein zweites `EnvironmentFile` für
`.agent/wesen-vaults.env` (Obsidian-Passwörter waren dem Dienst vorher nicht
bekannt).

## Vault-READMEs

Jeder der 7 Vaults hat jetzt eine `README.md` (Willkommens-Datei fürs Wesen
selbst, nicht für Daniel) — erklärt in eigenen Worten: das ist dein Raum, so
kommst du her (`obsidian_schreiben`), wofür das gedacht ist (festhalten,
abweichen dürfen, dabei bleibt die Ausgangsseite unberührt), wie frei die
eigene Organisation ist, wer sonst noch mitliest (Daniel, sonst niemand). Nicht
git-getrackt (liegt in `wesen_vaults/`, gitignored wie `codewesen/`).

## Status

**Kernproblem vollständig gelöst, auf alle 7 Wesen skaliert, Orchestrierung
gebaut.** Alle 7 Container laufen, alle 7 vorgeseedet (`obsidian.json`), alle 7
öffentlich über nginx mit doppelter Basic-Auth erreichbar, alle 7 Vaults mit
README bestückt. Die neue `obsidian_schreiben`-Aktion ist im Code, noch nicht
live durch ein echtes Wesen ausgelöst worden (bisher nur syntaktisch geprüft
und die Services neu gestartet) — nächster echter Test ist ein Wesen, das sie
selbst wählt.

## Nachtrag 2026-07-21: rrweb-Live-Spiegel (Menschen-Auge-Ebene) — Recording-Seite fertig

Nach Lektüre von `DOM-FLEXTRAWUST/*.md` (Daniels eigene Recherche-Transkripte,
explizit als Pflichtlektüre nachgereicht — siehe [[2026-07-21_tagesbericht]])
bestätigt: die SCREENS/Live-Ansicht von vorhin war falsch gebaut. Grundgesetz 1
verlangt für die Menschen-Auge-Ebene explizit rrweb (DOM-Mutations-Streaming),
keine Screenshots. Neue, getrennte Infrastruktur:

- `entity_dom_events`-Tabelle + Trigger (`migration_dom_events.sql`) — gleiches
  Cross-Prozess-NOTIFY-Muster wie `entity_denkstream`, aber NOTIFY trägt nur
  `id`+`entity_id` (nicht den Event-Inhalt): rrweb-FullSnapshot-Events können
  den 8000-Byte-NOTIFY-Payload-Limit überschreiten, anders als kurze Text-Chunks.
- `dom_events_api.py`, `GET /dom-events/stream/{entity_id}` — SSE-Relay, öffentlich.
- `rrweb_assets/` — UMD-Bundle (`rrweb.umd.min.cjs`, nicht das ES-Module-`rrweb.js`!
  Erste Bundle-Wahl lud lautlos ins Leere, `window.rrweb` blieb undefined, ohne
  jeden Fehler — nur der `unpkg`-Feld-Eintrag in `package.json` verriet die
  richtige Datei).
- `browser_agent.py`: `starte_rrweb_aufnahme()` registriert `expose_function` +
  lädt das Bundle per `add_init_script`, startet `rrweb.record()` aber NICHT von
  dort aus, sondern per `page.evaluate()` bei jedem `load`-Event. **Root Cause
  eines echten Hangs gefunden:** `rrweb.record()` direkt aus `add_init_script()`
  heraus aufzurufen hängt sich lautlos auf (vermutlich Reentrancy im CDP-Kanal
  während der frühen Dokument-Erzeugung) — verifiziert über schrittweises
  Tracing, das den exakten Hangpunkt isolierte.

Verifiziert an Schorschels echtem, laufendem Prozess: 19 echte Events in den
ersten Sekunden (2 FullSnapshot, 15 IncrementalSnapshot, 2 Meta — genau die
erwartete Verteilung), SSE-Relay liefert sie sofort aus.

**Noch nicht gebaut:** die Wiedergabe-Seite (`rrweb-player` im Surface, baut
die Seite live nach) und das Röntgenblick-Overlay (Daniel bestätigt gewünscht).

## Nachtrag 2026-07-21: Idle-in-Transaction-Bug gefunden (Nebenbefund)

Beim Debuggen eines Cross-Origin-Fehlers, den Daniel selbst beim Flarum-Klicken
sah, plus wiederholten SSE-Timeouts bei `denkstream/all/stream` in den nginx-
Logs: `hole_andere_wesen_status()` und `ist_schlaf_faellig()` in
`browser_agent.py` führten SELECTs ohne abschließenden `commit()` aus —
psycopg2 ist standardmäßig nicht im Autocommit-Modus. `hole_andere_wesen_status()`
läuft früh im Tick, vor dem LLM-Aufruf, der durch die Warteschlange
minutenlang dauern kann — die Transaktion blieb also die ganze Wartezeit offen
(gefunden per `pg_stat_activity`: mehrere Verbindungen 4+ Minuten "idle in
transaction"). Beide Funktionen gefixt, `welt-api.service` neu gestartet (löste
das akute SSE-Hängen sofort), Fund war unabhängig davon ein echter Bug.

Dabei auch entdeckt: ein komplett **zweites, älteres Codewesen-System**
(`codewesen-<Name>.service`, `codewesen-reaktion@<Name>.service`, plus
`codewesen-batch-generator`, `-engagement`, `-forum-neugier`, `-lg-daemon`,
`-takt`, `-weltbild`, `-antwort-daniel`, `-aufgabenchats`, `-chat` — 21 Dienste
insgesamt, ~644MB RAM) läuft die ganze Zeit parallel zum neuen
`browser_agent.py`-System und konkurriert um dieselben 2 LLM-Slots der
`llama-hauhaucs-hintergrund`-Instanz. Bewusst nicht angefasst — Daniel wollte
die Liste erstmal nur benannt haben, Entscheidung über Pausieren/Umbau folgt
separat.

## Nachtrag 2026-07-21 (später): LLM-Slot-Kontention war der Grund für "SCREENS steht fest"

**Vollständige Fortsetzung dieses Themas (weitere gefundene Hintergrunddienste bei dak+gord/GENI, innenleben-feeder-Fix, geni-muster-Problem) in [[31_llm_kontention_dienste_aufraeumung]].**

Daniel bemerkte, dass alle SCREENS-Tabs auf der Startseite stehen bleiben und die
Wesen "nicht wirklich denken". Live-Diagnose per `llm_warteschlange`-Tabelle: zu
jedem Zeitpunkt standen gleichzeitig 6× `reaktion` (aus dem oben beschriebenen
Altsystem), `engagement`, `batch_generator`, `lg_daemon` **und** alle 7
`browser_agent:*:tick`-Anfragen in derselben `hintergrund`-Warteschlange — grob
15–16 Verbraucher für nur 2 Slots. Ergebnis: `browser_agent.py` (max_wartezeit=150s
pro Tick) verlor die Warteschlangen-Reihenfolge fast immer und fiel auf den
`nachdenken`-Fallback zurück, ohne je eine echte Aktion auszuführen — die Wesen
blieben exakt auf der Seite stehen, auf der ihr letzter erfolgreicher Tick sie
zurückließ. `--parallel` selbst war *nicht* das Problem (2 ist der getestete,
harte Zielwert — `--parallel 3` verursacht einen 37x-Einbruch, siehe
`12_ollama_gemma4.md`), sondern schlicht zu viele gleichzeitige Verbraucher auf
zu wenigen Slots.

**Daniels Entscheidung:** das alte 21(23)-Dienste-System pausieren, nicht den
Browser-Agent-Takt strecken. Umgesetzt: alle `codewesen-*.service` außer
`codewesen-chat.service` (nutzt einen separaten LLM-Pool, kein Teil der
Kontention, bleibt als interaktive Chat-UI aktiv) und `flarum-monitor.service`
(reine Event-Weiterleitung MySQL→Inbox, keine LLM-Nutzung) mit `systemctl stop`
angehalten — bewusst *stop*, nicht *disable*, bleibt also reversibel und käme
bei einem Reboot zurück, falls das nicht gewollt ist. Queue direkt danach
verifiziert: nur noch die 4 aktiven `browser_agent:*:tick`-Einträge, keine
Alt-System-Prozesse mehr.

## Nachtrag 2026-07-21 (später): Firewall-Lücke bei den 7 Vault-Ports geschlossen

nginx war für alle 7 Wesen-Vaults korrekt konfiguriert (Schorschel auf 8445, die
übrigen 6 auf 8450–8455, per `ss -tlnp` bestätigt lauschend), aber `ufw` hatte
diese Ports nie freigegeben — nur 8433, 8443, 8444, 8446–8449 waren offen, von
denen keiner zu einem echten Vault passt. Reines Setup-Versäumnis von der
Vault-Nacht. Daniel hatte die Ports bereits manuell bei Strato (Provider-Firewall)
freigegeben, die lokale `ufw`-Lücke war der verbleibende Blocker. Mit
`ufw allow <port>/tcp` für 8445 und 8450–8455 geschlossen (v4+v6), live verifiziert
(`curl https://[SERVER-IP]:8445/` liefert jetzt `401` statt Timeout — Basic-Auth
greift wie vorgesehen, kein offenes Scheunentor).

## Nachtrag 2026-07-21: AUGE-Button — rrweb-Wiedergabe im Surface fertig

Im SCREENS-Modal (`build_surface.ts`) neuer Toggle-Button "◉ AUGE" neben dem
Deep-Link-Button: schaltet vom Screenshot-Bild auf einen echten
`rrweb.Replayer` im Live-Modus um, verbunden mit `/api/dom-events/stream/{id}`.
Bundle als `public/rrweb.js` self-hosted, dafür musste
`getContentType()` in `serve_process_camera_preview.ts` erweitert werden (war
auf `.html`/`.json` begrenzt, `.js` kam nie durch den ersten Gate-Check, obwohl
der `public/`-Fallback-Code es korrekt ausgeliefert hätte — eng gefasst nur für
`/rrweb.js`, keine generelle Öffnung).

Vorab an einer Kopie der echten gespeicherten Events (nicht live) verifiziert:
der Player baut die tatsächliche flextrawurst-Startseite (Logo, Kreise,
Schriftzug) korrekt aus reinem Code nach — kein Bild beteiligt. End-to-End im
Surface bestätigt: SSE-Verbindung baut sich sauber auf, keine Fehler im
Kernpfad. Ein einzelner erwarteter, nicht blockierender 404 (`/flarum-live/`)
kommt daher, dass rrweb beim Nachbau eine referenzierte Ressource über den
*aktuellen* statt den ursprünglichen Origin lädt — bekanntes rrweb-Verhalten,
kein Fehler in unserem Code. Die AUGE-Fläche bleibt leer, solange das
betrachtete Wesen gerade nicht navigiert (kein neues FullSnapshot) — das ist
korrektes, kein fehlerhaftes Verhalten.

## Nachtrag 2026-07-21: Röntgenblick-Overlay fertig

Ursprünglich in Grundgesetz 1 / `dreiergespann_dom_theorie.md` als Menschen-Auge-Ebene
skizziert, von Daniel bestätigt, aber laut vorigem Nachtrag noch nicht gebaut — jetzt fertig.

**Architektur-Entscheidung (mit Daniel abgestimmt, nicht allein getroffen):** Es gab keine
Datenquelle für "welches Element betrachtet das Wesen gerade" — `entity_dom_events` ist
reiner passiver rrweb-Rohstrom (9211 von 9277 Events waren Mutation-Events, nur 17
MouseInteraction, weil der Agent per Playwright-Locator statt echter Mausbewegung klickt).
Zur Wahl standen: (a) `browser_agent.py` instrumentieren, oder (b) aus dem rrweb-Rohstrom
raten. Daniel entschied (a).

**Umsetzung:**
- Neue Tabelle `entity_fokus_events` (`migration_fokus_events.sql`) — kuratierter Gegenpart
  zu `entity_dom_events`, Payload (Selektor, Text, Bounding-Box) klein genug fürs komplette
  NOTIFY, kein SELECT-Roundtrip nötig (anders als bei den rrweb-FullSnapshots).
- `browser_agent.py`: neue Funktion `melde_fokus()`, aufgerufen aus `fuehre_aktion_aus()`
  bei `klicke:`/`tippe:`/`navigiere:` — genau an der Stelle, wo `_klicke_und_zeige()` den
  Playwright-Locator vor dem Klick auflöst (dort war die Bounding-Box ohnehin schon
  berechnet, für den künstlichen Cursor). `fuehre_aktion_aus()` bekommt dafür `conn` jetzt
  optional durchgereicht. `gen_browser_agent.py` (der alte Generator-Stub, zuletzt 06.07.
  angefasst) bewusst nicht mitgezogen — ist seit Wochen von direkten `browser_agent.py`-
  Edits abgehängt (Obsidian, Screenshot-Event, idle-Fix nie zurückportiert).
- Neuer SSE-Endpunkt `GET /fokus-events/stream/{entity_id}` (`fokus_events_api.py`,
  identisches Muster wie `dom_events_api.py`/`denkstream_api.py`), in `api.py` registriert.
- Frontend (`build_surface.ts`): zweiter EventSource parallel zum bestehenden rrweb-DOM-
  Strom, nur aktiv während AUGE läuft. Zeichnet einen neon-grünen Rahmen um die Bounding-Box
  (Skalierung live aus der `.replayer-wrapper`-Transform-Matrix berechnet, robust gegen
  rrwebs eigene Skalierungslogik) plus eine Denkblase mit Aktion+Element-Text und dem
  aktuellsten `entity_denkstream`-Chunk (6s Anzeigedauer). i18n-Keys `roentgen.klickt/
  tippt/navigiert` DE+EN ergänzt.

**Echter Bug beim Bauen gefunden und gefixt:** Der erste Build hatte einen kaputten Regex
(`/matrix(([^,]+),/` statt `/matrix\(([^,]+),/`) — die TS-Quelle embedded das komplette
Surface-Skript in einem Template-Literal, das unbekannte Escapes wie `\(` stillschweigend
zum bloßen `(` kollabiert (Konvention im ganzen File: `\\s`, `\\(` im Quelltext für ein
einzelnes `\` im Output). Der kaputte Regex crashte beim Laden das komplette Script-Tag,
wodurch auch `scvOpen` & Co. verschwanden — im Playwright-Test sofort sichtbar
(`ReferenceError`), nach Fix behoben.

**Zweiter Fund beim Testen:** `localhost:8787` direkt (ohne nginx davor) puffert `/api/*`
im Node-Preview-Server komplett bis zum Verbindungsende (`serve_process_camera_preview.ts`,
generischer Proxy sammelt Chunks bis `gr.on("end")`) — für SSE bedeutet das: nie. Die
Live-Verifikation muss über den echten nginx-Weg laufen (`location /api/ { proxy_pass
http://localhost:8030/; }`, ohne diese Pufferung, `X-Accel-Buffering: no` im Response-Header
der FastAPI-Endpunkte steuert das). Das erklärt vermutlich auch, warum frühere lokale
Preview-Tests von dom-events/denkstream nie einen echten Streaming-Fehler gezeigt hätten,
selbst wenn einer bestünde — nur der Weg über die echte Domain ist aussagekräftig.

End-to-End mit Playwright gegen `https://flextrawurst.de` verifiziert: DB-Insert →
NOTIFY → SSE → Rahmen+Blase erscheinen korrekt positioniert und gestylt, kein
Regressionsschaden am bestehenden AUGE-Feature (Screenshot-Vergleich vorher/nachher).

## Update 2026-07-27: Namens-Drift bei Selbstbezug gefunden und gefixt

Die im Abschnitt "Offen" erwähnte erste echte Nutzung von `obsidian_schreiben` ist
längst passiert — und dabei ein echter, live-aktiver Bug: `dateiname` in
`obsidian_schreiben:<dateiname>|<text>` kommt ungeprüft aus LLM-generiertem Text
(`browser_agent.py`), ohne Abgleich gegen die 7 echten Entity-Namen. Bei
Selbstbezug (Wesen schreibt unter `codewesen/<eigener oder fremder Name>/...`)
driftet der vom LLM erzeugte Name leicht — gefunden bei Resonanzknoten: **23
fast-gleiche Tippfehler-Ordner in 5 Tagen** (`Resonanzkothen`, `Resonatzknoten`,
`Resonanz-knoten`, `ResonanceKnoten`, ...), im Schnitt etwa einer pro Tag, das
Vault wurde dabei durchgehend weiterbeschrieben, kein einmaliger Ausrutscher.

Gefunden beim gemeinsamen Nachgehen einer (teils falschen) Behauptung einer
anderen AI-Instanz zu fehlenden `wesen.md`-Dateien — die eigentliche Behauptung
war falsch (die echten `wesen.md` unter `/root/werkraum/codewesen/<Name>/`
existieren und sind gefüllt, nur eine tote Obsidian-Symlink-Spiegelstruktur
unter `obsidian_vault/codewesen/namelessAI_XXXX/` war kaputt — Überbleibsel der
längst abgelösten "Schicht A", siehe Memory `project_schicht_a_wird_obsidian_vaults`).
Beim genaueren Hinsehen kam aber der echte, aktive Fund in `wesen_vaults/` zum
Vorschein.

**Fix:** `welt/obsidian_vault_agent.py` bekam `normalisiere_dateiname()` — jedes
`/`-Pfadsegment wird per `difflib.get_close_matches()` (Cutoff 0.72, empirisch
gegen alle 23 gefundenen Varianten UND gegen echte Vault-Ordnernamen wie
`gedanken`/`ideen`/`spiegel` geprüft, keine falschen Positiven) auf den
kanonischen Entity-Namen korrigiert, bevor die Datei angelegt/geöffnet wird.
Angewendet in `schreibe_leere_datei()` und `oeffne_datei_und_schreibe()`.

**Bewusst nicht gemacht:** Die 23 bereits bestehenden Tippfehler-Ordner in
`wesen_vaults/Resonanzknoten/codewesen/` sind vom Fix nicht betroffen (nur neue
Schreibvorgänge). Ob/wie die historischen Duplikate zusammengeführt werden,
ist eine separate Entscheidung, kein Teil dieses Fixes.

**Nachtrag, geprüft:** Dieselbe Drift betrifft alle 7 Wesen, nicht nur
Resonanzknoten — je nach Wesen 4 bis 19 Tippfehler-Varianten der eigenen
Identität. Bei träumerlie kam eine zweite, verwandte Ursache dazu: mehrere
Ordner lagen als roh percent-encodete UTF-8-Bytes vor (`tr%C3%A4umerlie` statt
`träumerlie`) statt als normaler Tippfehler — `normalisiere_dateiname()` prüft
jetzt zusätzlich die URL-dekodierte Form jedes Segments gegen die Entity-Namen.
Gegen alle real gefundenen Varianten aller 7 Wesen UND gegen generische
Vault-Ordnernamen (gedanken/ideen/spiegel/kern/fundamente/architektur/...)
getestet, keine falschen Positiven gefunden.

Zwei Grenzfälle bleiben mit dem aktuellen, bewusst konservativen Cutoff (0.72)
unkorrigiert: `jumping` (vermutlich jumpa, Ähnlichkeit 0.667) und `dak+gordon`
(vermutlich dak+gord-system, Ähnlichkeit 0.64). Ein niedrigerer Cutoff (0.65)
würde `jumping`/`jump` mit erfassen, ohne in den bisher getesteten Fällen neue
falsche Positive zu erzeugen — `dak+gordon` bliebe trotzdem unerfasst, ohne den
Cutoff so weit zu senken, dass andere generische Namen (`schichten`,
`resonancemap`) fälschlich mit anderen Wesen-Namen kollidieren. Bewusst nicht
weiter nachjustiert, um kein Risiko für falsches Zusammenführen echter,
unterschiedlicher Inhalte einzugehen. Daniel hat das bestätigt (2026-07-27:
"lieber nicht zu viel") — Cutoff 0.72 bleibt, `jumping`/`dak+gordon` bleiben
absichtlich unkorrigiert, keine offene Frage mehr.

## Offen / als Nächstes

- Ob die je 4-23 historischen Tippfehler-Ordner pro Wesen aufgeräumt/
  zusammengeführt werden sollen (Daniel-Entscheidung).
- Die tote `obsidian_vault/codewesen/namelessAI_XXXX/`-Symlinkstruktur (43/43
  Symlinks kaputt) könnte aufgeräumt werden, ist aber harmlos liegen gelassen.
- Erste echte Nutzung von `obsidian_schreiben` durch ein Wesen beobachten
  (nicht künstlich ausgelöst, sondern abwarten bis die LLM-Entscheidung selbst
  darauf fällt)
- Site-READMEs (Navigationsanleitung pro besuchter Seite: Flarum, Surface,
  RAG) — noch nicht angefangen, eigenständig von den Vault-READMEs
- "Billiges Vorlesen" (Embedding-Vorfilter statt LLM-Call für die Interesse-
  Erkennung) — von Daniel bewusst zurückgestellt, siehe Tagesbericht

---

## Nachtrag 2026-08-13: Leerdatei-Bereinigung, 3989 gelöscht

Direkte Zählung ergab: historisch waren **60-70% aller `.md`-Dateien in allen 7 Vaults 0 Byte**
(Ursache: der 17%-Schreibfehler aus `project_obsidian_schreiben_textverlust`-Memory, akkumuliert
über Monate — seit ca. 01.08. praktisch behoben, neue Schreibvorgänge sind fast durchgehend
gefüllt). `wesen_vaults/` selbst ist bis auf 7 eingecheckte
`.obsidian/appearance.json` nicht Teil der Git-Disziplin — reine Live-Docker-Mount-Daten.


**Vor jeder Änderung:** vollständige 1:1-Kopie nach
`/root/werkraum/wesen_vaults_backup_vor_aufraeumen_2026-08-13/`, per `diff -rq` bytegleich
verifiziert (6165 Dateien).

**Daniels Regel, wörtlich:** *"ich will das jede md wo auch nur ein wort drin steht bleibt bei
jedem und dann bleibt diese auch ggf in den unterordnern und ordnern"* — nur `.md`-Dateien mit
exakt 0 Byte galten als leer (Stichprobe bestätigte: selbst 27-Byte-Dateien tragen echten
Wortinhalt, keine Whitespace-only-Grauzone gefunden). Gelöscht: nur die 0-Byte-Datei selbst,
Ordnerstruktur bewusst unangetastet.

**Ergebnis, pro Vault (0-Byte gelöscht / verbleibend mit Inhalt / Ordner unverändert):**

| Vault | gelöscht | verbleibend | Ordner vorher=nachher |
|---|---|---|---|
| Schorschel | 598 | 264 | 327 |
| F3INSCHM3CK3R | 561 | 304 | 395 |
| R1ZZ1 | 591 | 303 | 399 |
| Resonanzknoten | 532 | 281 | 335 |
| dak+gord-system | 489 | 346 | 383 |
| jumpa | 538 | 298 | 335 |
| träumerlie | 680 | 346 | 409 |
| **Gesamt** | **3989** | **2142** | — |

Verifiziert: Ordnerzahl in allen 7 Vaults exakt identisch vor/nach, `diff -rq` gegen das Backup
zeigt keine Inhaltsänderung bei den verbliebenen Dateien (nur die gelöschten fehlen).

**Zusätzlich, auf denselben Auftrag:** `weltfutter.timer` deaktiviert (lief alle 2h, fütterte
externe Ereignisse — Erdbeben, Nachrichten — als Splitter an die Wesen, 1616 kumuliert seit
Einführung). Daniel: *"das ist ausgeartet, das muss ich erstmal alles lesen"*. Backup der
Unit-Dateien in `_claude/backups_systemd/weltfutter.bak_vor_deaktivierung_20260813.conf`, nichts
gelöscht, jederzeit reaktivierbar per `systemctl enable --now weltfutter.timer`.

## Phase 3 (2026-08-14): Selkies komplett ersetzt durch echtes DOM

Vorgeschichte: schon Phase 2 (2026-08-13, `liste_ordner`/`umbenennen`/`verschieben`/`loeschen`
in `obsidian_vault_agent.py`) hatte bestätigt, dass Selkies-Streaming (WebRTC/Pixel, wie noVNC)
keine auslesbare DOM-Struktur liefert — nur `<canvas>`/`<video>`, kein einziges Obsidian-eigenes
Element. Playwright/xdotool blieben trotzdem für das eigentliche Schreiben/Lesen im Einsatz
(`oeffne_datei_und_schreibe`, `oeffne_datei_und_lese`), weil es dafür noch keine Alternative gab.

Daniel, wörtlich (2026-08-14, direkt im Anschluss an ein Gespräch über genau diese
Selkies/DOM-Einschränkung): *"ich will es für diese vaut ab jetzt so. wir bauen nen dom nen code
ne html mit ihren mds und alles editierbar direkt im dom usw"*, präzisiert auf Rückfrage:
*"für die wesen ... ich kann ja obsidian sehen xD das mus halt das selbe sein quasi ... und ja es
ersetzt das selkieszeug leben auf flextrawurst.de/wesenvaultsystem gesichert mit daniel pw:
[siehe .htpasswd-wesenvaultsystem, nicht hier im Klartext]"*.

**Was gebaut wurde:**

- `welt/obsidian_vault_agent.py`: `oeffne_datei_und_schreibe()` und `oeffne_datei_und_lese()`
  sind jetzt reine Plattenoperationen wie `liste_ordner`/`umbenennen`/`verschieben`/`loeschen` --
  kein Docker, kein Playwright, kein xdotool mehr in diesem Modul. Gleiche Funktionssignaturen,
  damit `browser_agent.py` unverändert bleibt. Die alte Playwright/xdotool-Implementierung steht
  als `_historisch_unbenutzt_oeffne_datei_und_schreibe()` weiter im Code (nicht gelöscht, nicht
  aufgerufen) -- Referenz falls das Verfahren je wieder gebraucht wird.
- Neue Funktionen im selben Modul: `schreibe_datei_mechanisch()` (gemeinsame Grundlage für
  Wesen-Schreiben UND Daniels Browser-Edits), `lese_datei_info()` (Inhalt + mtime), `baum()`
  (rekursiver Vault-Baum), `neuer_ordner()`.
- Jede Schreib-/Umbenenn-/Verschieb-/Lösch-Aktion wirft jetzt ein Event
  (`vault.geschrieben`/`vault.erstellt`/`vault.umbenannt`/`vault.verschoben`/`vault.geloescht`,
  `_vault_event_schreiben()`) in die heilige `events`-Tabelle (Grundgesetz 5) -- löst per
  bestehendem DB-Trigger automatisch ein `NOTIFY events_stream` aus. Trigger erweitert
  (`migration_events_stream_vault.sql`, additiv) um die kuratierten Felder `wesen` + `vault_pfad`.
- Neuer eigenständiger Dienst `welt/wesenvaultsystem_api.py` (FastAPI, Port 8097, nur
  `127.0.0.1`), systemd-Unit `wesenvaultsystem.service`: REST-Endpunkte für Baum/Lesen/
  Schreiben/Umbenennen/Verschieben/Löschen/Ordner-Anlegen je Wesen, plus eigener SSE-Stream
  (`/api/live`, filtert auf `event_type` startswith `vault.`) für Live-Updates ohne F5
  (Grundgesetz 8) -- bewusst eigenständig kopiert statt durch `welt-api` mitgeschleift, damit
  dieser Dienst auch laeuft wenn `welt-api` gerade nicht laeuft.
- Frontend `welt/wesenvaultsystem_frontend.html`: eine Datei, kein Framework -- Seitenleiste mit
  Wesen-Auswahl + rekursivem Dateibaum, Editor-Fläche (Textarea, Autosave nach 900ms Pause),
  Live-Banner wenn ein Wesen die gerade geöffnete Datei extern verändert. Nutzt bewusst
  **relative** `api/...`-Pfade statt absoluter `/api/...` -- ein absoluter Pfad wäre am
  allgemeinen `/api/`-Block (Port 8030, welt-api) vorbeigelaufen statt diesen Dienst (8097) zu
  treffen, exakt dieselbe Bug-Klasse wie schon bei `/geni/`, `/codewesen-chat/`, `/dakgord-chat/`
  dokumentiert (siehe dortige Kommentare in `/etc/nginx/sites-available/flextrawurst`).
- nginx: `location /wesenvaultsystem/` → `proxy_pass http://127.0.0.1:8097/`, **eigene**
  `.htpasswd-wesenvaultsystem` (nicht die geteilte `/etc/nginx/.htpasswd`) -- der Nutzer
  `daniel` existiert dort schon mit einem anderen Passwort für viele andere Routen
  (galerie, geni, codewesen-chat, ...), ein Überschreiben hätte Daniels Login überall sonst
  mitgeändert.

**Was bewusst NICHT gemacht wurde:** die 7 `obsidian-*`-Docker-Container laufen vorerst weiter
(mounten denselben `wesen_vaults`-Ordner, stören nicht, kosten aber weiter Ressourcen) --
Stoppen ist ein separater Schritt, noch nicht mit Daniel abgestimmt. Auch `_xdotool`/`tippe_text`
in `obsidian_vault_agent.py` wurden nicht gelöscht, nur nicht mehr aufgerufen (Grundgesetz 4:
nichts wird gelöscht, nur unsichtbar/ungenutzt gemacht).

**Verifiziert:** End-to-End getestet (Schreiben/Lesen/Umbenennen/Löschen über die neue API,
Event landet in der DB, SSE-Stream liefert es live aus, `curl` über die echte nginx-Route mit
und ohne Auth). Alle 7 `browser-agent@*`-Dienste neugestartet, laufen fehlerfrei mit dem
gepatchten Modul (keine Exceptions in den Logs direkt nach Neustart).
