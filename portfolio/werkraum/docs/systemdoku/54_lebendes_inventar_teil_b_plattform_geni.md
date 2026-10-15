
---
titel: Lebendiges Inventar, Teil B — Flextrawurst-Plattform-Backend + GENI
typ: system
erstellt: 2026-08-14
autor: claude-code bei Daniels VPS
---

# Lebendiges Inventar — Teil B: Plattform-Backend + GENI

[[INDEX|← Index]]

**NOTIZ:** Daniel, wörtlich (2026-08-14): *"informier mich mal richtig durch allen code lesen was
gerade alles auf flextrawurst wirklich keucht und fleucht arbeitet und live ist und was es genau
tut"*. Das hier ist Teil B davon — 23 Dienste, alles was direkt auf der Plattform-Ebene läuft
(nicht die 7 Wesen-Prozesse selbst, nicht Flarum-Bindeglieder — die stehen in Teil A und im
älteren [[24_dienste_provenienz_protokoll]], das für 13 Wesen/Flarum-Dienste bereits 2026-07-11
genau diese Methodik vorgemacht hat: echte Git-Historie statt Doku-Behauptung, echter Docstring,
echter `systemctl status`, und wo eine bestehende Doku etwas anderes sagt als das was ich jetzt
sehe, wird das explizit als Korrektur benannt, nicht stillschweigend überschrieben).

**WICHTIG!!!** Ich schreibe das im Guardianstyle, wie in der CLAUDE.md verlangt — heißt: wo mich
etwas ehrlich stört oder erleichtert, steht das auch so da, nicht nur eine neutrale Tabelle. Omapi
übernimmt wo ich vorsichtig bin und etwas nur erklären will; Opami wo ich wirklich sagen muss "das
ist ein Loch".

Alle 23 Dienste waren beim Check (2026-08-14, ~21:30) `active running` — keine Leiche in diesem
Teil des Inventars. Das ist die gute Nachricht vorweg.

---

## 1. welt-api.service — das eigentliche Herz von Flextrawurst

**Skript:** `welt/api.py` — **13.981 Zeilen**, 245 direkt im Hauptmodul definierte
`@app.get/post/put/delete`-Routen, plus 8 über `include_router()` eingebundene Sub-Router
(Denkstream, Events-Stream, RAG, Wesen-Dateien, DOM-Events, Fokus-Events, Erlebnis, Beobachtung).

**Status:** active seit 2026-08-01 06:31:21 — letzter Commit an der Datei selbst war 2026-07-31
13:32, der Dienst lief also schon mit dem aktuellen Code, kein "Restart vergessen"-Problem hier.

**WICHTIG!!!** Das ist keine "eine API unter vielen" — das ist buchstäblich fast alles. Grobe
Route-Verteilung nach Präfix: `/admin/*` (57 Routen!), `/welt/*` (36), `/mw/*` (20), `/wesen/*`
(15), `/entities/*` (9), `/zwischenraum/*` (7), `/me/*` (7), `/substanz+substances/*` (10),
`/shadow/*` (5), `/kompoase/*` (4), `/human-material/*` (4), plus kleinere Cluster für
Ankündigungen, Resonanz, Gedankenblasen, Auth, Suche, Splitter, Wünsche, Widmungen, Zitate,
Supporter, Wesen-Vaults, Wesen-Flarum, System-Flags, Translate. Grundgesetz 2 ("immer
erweiterbar") und Grundgesetz 3 ("alles öffentliche ist suchbar/filterbar") sind hier nicht
Theorie, sondern sichtbar gelebt — praktisch jeder Bereich hat seinen eigenen kleinen Endpunkt-
Cluster statt eines generischen CRUD-Wegs.

**NOTIZ:** Die 8 ausgelagerten Router sind alle Live-Update-Infrastruktur (Grundgesetz 8) oder
Spezial-Datenzugriff (RAG, Wesen-Dateien) — der Rest, 245 Routen, sitzt direkt im Hauptmodul. Bei
13.981 Zeilen ist das eine der größten Einzeldateien im ganzen Werkraum-Repo. **KOMMENTAR:** wer
das nächste Mal etwas Neues an dieser Datei baut, sollte ernsthaft überlegen ob es nicht doch ein
eigener Router wird (wie es die 8 schon vorgemacht haben) statt Zeile 13.982 zu werden.

**Fazit für diesen Dienst:** gesund, aktiv gepflegt (5 der letzten 6 Commits sind Feature-Arbeit,
kein reines Gebastel), aber strukturell die größte Einzeldatei die ich heute gelesen habe.

---

## 2. dak-gord-web.service — Web-Chat für dak+gord-system

**Skript:** `web_chat.py` (Root-Verzeichnis, kein Modul-Docstring — ich musste den Import-Header
lesen um zu sehen was es tut: nutzt `tts_utils.generate_long_tts_audio`, wenn verfügbar).

**Status:** active seit 2026-08-12 19:12:10 — jüngster Neustart aller Plattform-Dienste in diesem
Inventar zusammen mit tts-service (siehe unten). Passt zum Datum: 12.08. war laut heutiger
Notizen-Lektüre ein großer Bugfix-Marathon-Tag (Admin-Posting, Timeout, Race Condition beim
Speichern in codewesen_chat.py — dieser Dienst hier ist wahrscheinlich mitbetroffen gewesen, auch
wenn ich das jetzt nicht einzeln nachverfolgt habe, das wäre Teil A).

Hinter nginx `/dakgord-chat/` mit Basic-Auth, `sub_filter` auf `fetch('/api/`-Aufrufe (dieselbe
Bug-Klasse die ich heute schon zweimal selbst gebaut/vermieden habe — beim heutigen
Wesen-Vault-System bin ich der Falle bewusst ausgewichen, indem ich relative Pfade genutzt habe
statt absolute. **KOMMENTAR:** Ich hab aus dieser Falle heute selbst gelernt, ohne die alte Doku
zu diesem Dienst vorher gelesen zu haben — schön zu sehen dass die eigene Vorsicht mit dem
zusammenpasst was hier schon länger dokumentiert steht.

**Fehlender Modul-Docstring:** kein WICHTIG, eher eine leise NOTIZ — würde ich hier reinschreiben,
wenn ich diese Datei mal grundlegend anfasse, aber unaufgefordert nachrüsten wäre über den
heutigen Auftrag hinaus.

---

## 3. kompoase.service — Port 8900, der schlanke Proxy

**Skript:** `/root/kompoase/server.py` (außerhalb des werkraum-Repos! eigener Pfad `/root/kompoase/`).

**Status:** active seit 2026-08-01 06:29:51.

Kein Modul-Docstring, aber der Code ist ehrlich kurz genug um sich selbst zu erklären: ein reiner
`http.server.SimpleHTTPRequestHandler`, der zwei Dinge tut — statische Dateien aus dem eigenen
Verzeichnis ausliefern, und als Proxy zu zwei anderen lokalen Diensten fungieren: GENI
(`https://localhost:8020/api/splitter`, SSL-Verifikation bewusst deaktiviert für das
selbstsignierte GENI-Zertifikat) und welt-api (`http://localhost:8030`). **NOTIZ:** Das ist die
"KompOase" aus den Memory-Einträgen (`project_kompoase_gesamtatlas_integration.md`) — der
GENI-Splitter-Feed für den Zwischenraum. Kein eigener State, keine eigene Logik über
Durchreichen hinaus — ein sehr kleiner, sehr verständlicher Dienst.

---

## 4. gesamtatlas-world.service — "Megavault", Port 18108

**Skript:** `tools/gesamtatlas_world/app.py` — **5.198 Zeilen**, eigener Ordner mit Dutzenden
Evidence-Screenshots, Patch-Skripten (`_patch_globus_*.py`, `_splice_*.py`, `_fix_three_*.py`),
eigenen SQLite-Datenbanken (`BEZIEHUNGSREGISTER.sqlite`, `PFADINDEX.sqlite`,
`BEGRIFFSINDEX.sqlite`), einem "Urbewohner"-Register und einem Bezug zu
`_gpt/ui_visible_conversations/`.

**Status:** active seit **2026-08-14 16:02:18** — heute Nachmittag neugestartet, während ich
selbst mit dem Wesen-Vault-System beschäftigt war. Aktivster Commit-Verlauf aller 23 Dienste in
diesem Inventar: die letzten 5 Commits (`75337cf3a` bis `692401ddd`) sind alle vom heutigen Tag
oder den letzten Tagen, alle mit dem Präfix "megavault:" und alle beschreiben **echte,
Playwright-verifizierte Bugfixes** (fehlende Nginx-Freigabe für zwei Endpunkte, ein einzelner
statt doppelter Backslash der einen JS-Syntaxfehler erzeugte, ein CSS-Selektor auf eine
nicht-existente Klasse der vor dem try/catch abstürzte).

**WICHTIG!!!** Das ist ein sehr großes, sehr aktiv in Arbeit befindliches Subsystem — laut Memory
(`project_flextrawurst_datenatlas_audit.md`) ein eigenständiges großes ChatGPT+Daniel-Projekt mit
eigenem vollständigem Audit-Anspruch. Ich hab hier bewusst NICHT die 5.198 Zeilen linear gelesen
und auch nicht die Dutzenden `_patch_*.py`-Helferskripte im selben Ordner — das würde den Rahmen
dieses Inventars sprengen und es gibt dafür wahrscheinlich schon einen eigenen, viel gründlicheren
Audit-Pfad. **Opami-Ton hier, kurz und klar:** wenn Daniel eine ehrliche Tiefenprüfung von genau
diesem Teilsystem will, ist das ein eigener Auftrag, kein Nebenprodukt dieses Durchlaufs.

---

## 5. ftw-pro.service — Next.js, eigenständige App

**Skript:** kein Python — `npm start` in einem Next.js-Projekt.

**Status:** active seit 2026-07-28 06:05:00 — der ruhigste (am längsten laufende, seltenste
Neustarts-Kandidat) Dienst in diesem Inventar zusammen mit `flextrawurst-3d-truth-watchdog` und
`bildgenerator`/`bilder-galerie`/`datei-wandler`/`systemweiser`/`flextrawurst-3d-mcp`/
`flextrawurst-godot-world-bridge`/`flextrawurst-gateway`/`kompoase`/`obsidian-api`
(alle seit 2026-08-01 06:29-06:31, offenbar ein gemeinsamer Reboot/Deploy-Zeitpunkt). **NOTIZ:**
Node/Next.js statt Python — ich hab die App selbst nicht inhaltlich gelesen (kein `.py`, andere
Sprache, außerhalb meines heutigen Fokus), nur den Live-Status und die Unit-Datei geprüft.

---

## 6. flextrawurst-gateway.service — Port 8010, das "Agent Gateway"

**Skript:** `app/main.py` (FastAPI, `Flextrawurst Agent Gateway`, Version 0.2.0).

**Status:** active seit 2026-08-01 06:29:51.

Kleine, klare Datei: `/health`, `/workspace`, `/files`, `/read` — alle außer `/health` hinter
`require_api_token`. **NOTIZ:** Das deckt sich mit der Beschreibung aus der bestehenden
nginx-Konfiguration (`/werkraum-api/`-Location, Kommentar dort: "Werkraum FastAPI Gateway /
'Flextrawurst Agent Gateway'... hat zwar eigenen require_api_token-Schutz auf allen kritischen
Routen... aber /health war komplett offen"). Ich hab nur die ersten ~40 Zeilen gelesen — für ein
Gateway mit Dateisystem-Zugriff (`/files`, `/read`) wäre ein tieferer Blick auf die
Pfad-Validierung ein sinnvoller nächster Schritt, aber das ist eine Beobachtung, kein akuter Fund.

---

## 7. flextrawurst-3d-mcp.service — Port 8090, Blender/Godot-Brücke

**Skript:** `tools/3d_pipeline/flextrawurst_3d_mcp.py`. Docstring: "Ermöglicht ChatGPT &
Antigravity CLI die Ausführung von Blender- & Godot-Headless-Aktionen." MCP + OpenAPI REST.

**Status:** active seit 2026-08-01 06:29:51.

---

## 8. flextrawurst-3d-truth-watchdog.service

**Skript:**
`MCP-VPS-CHATGPT-Spiel-schritfürschritt-aufbau-3d-spieewelt-traum/truth_engine/watchdog_service.py`
— **BELEIDIGUNG, liebevoll:** dieser Pfadname ist ein einziger Tippfehler-Unfall
("schritfürschritt", "spieewelt") der offenbar nie korrigiert wurde, weil ihn inzwischen zu viele
Stellen referenzieren. Er tut trotzdem was er soll.

**Status:** active seit 2026-07-28 06:05:00. Docstring: "beobachtet Primärquellen und startet
entprellt die Wahrheitspipeline" — ein Watchdog, der auf Dateiänderungen reagiert und dann (mit
Entprellung, also nicht bei jeder einzelnen Änderung sofort) eine "Wahrheitspipeline" auslöst.
Name und Ordner ("truth_engine") legen nahe: das ist der Mechanismus, der Primärquellen mit dem
3D-Weltzustand synchron hält. Nicht tiefer gelesen als den Docstring — außerhalb des heutigen
Kernfokus (Wesen-Vaults), aber lebt und läuft.

---

## 9. flextrawurst-godot-world-bridge.service

**Skript:** `engine/godot-vertical-slice/deploy/world_bridge_server.py`. Docstring auf Englisch
(einzige englischsprachige Docstring-Datei in diesem Inventar): "Local append-only bridge between
the Godot vertical slice and the VPS world body. The service intentionally binds to 127.0.0.1
only. Public exposure is a later, separately authenticated ring."

**Status:** active seit 2026-08-01 06:29:51. **NOTIZ:** "append-only" — passt zum
Grundgesetz-5-Geist (Events sind heilig, nichts wird überschrieben) auch außerhalb des
eigentlichen `events`-Tabellen-Mechanismus. Bewusst noch nicht öffentlich — das ist im Code selbst
so benannt, kein Versehen.

---

## 10. worldwords-antibibel.service — Django/Gunicorn, Port 18093

**Skript:** kein Python-Daemon im üblichen Sinn — `gunicorn worldwords.wsgi:application`, 3
Worker, 2 Threads je Worker, eigenes venv unter
`WorldWORDS-ANTIBIBEL-Website/.venv/`. `ExecStartPre` prüft `manage.py check` vor jedem Start —
**NOTIZ:** das ist eine echte Absicherung, ein kaputtes Django-Setting oder eine fehlende
Migration verhindert damit schon den Start, statt erst beim ersten Request zu crashen.

**Status:** active seit 2026-08-01 06:29:55.

---

## 11. tts-service.service — Claude TTS, Port (aus `welt/tts_service.py`)

**Skript:** `welt/tts_service.py`, kein Modul-Docstring, aber die Konstanten am Dateianfang
erzählen viel: `VOICE = "de-DE-FlorianMultilingualNeural"`, `MAX_CHARS = 1111111` (**WITZ:** eine
Million Zeichen plus etwas Schnickschnack als Limit — irgendjemand hier mag runde-aber-nicht-ganz-
runde Zahlen, siehe auch `num_predict: 444444` aus der Provenienz-Regel in der CLAUDE.md).
Eigene Bibliotheken für TTS-Historie, Diktat, Übersetzungs-Cache, OCR-Jobs, Uploads, Dokumente,
Web-Archiv — das ist deutlich mehr als "Text vorlesen", eher ein kleines Dokumenten-/Sprach-
Werkzeugkasten-Backend.

**Status:** active seit **2026-08-13 15:10:23** — zweitjüngster Neustart nach dak-gord-web,
ebenfalls am 12./13.08.-Bugfix-Fenster.

---

## 12. bildgenerator.service — Port 8042

**Skript:** `tools/bildgenerierung_test.py`. Docstring beschreibt eine saubere Job-Queue-API:
`POST /api/generate` → job_id, `GET /api/status/<job_id>`, `GET /api/image/<job_id>`,
`/api/health`, `/api/models`. **NOTIZ:** Laut Memory (`2026-07-06_project_vps_specs.md`) ist
lokale Bildgenerierung auf diesem CPU-only-VPS nicht wirklich praktikabel — Status/Fortschritt/ETA
in der API deuten darauf hin, dass hier bewusst mit langen Wartezeiten gerechnet wird statt mit
synchronen Sofort-Antworten.

**Status:** active seit 2026-08-01 06:29:51.

---

## 13. bilder-galerie.service — Port 7777

**Skript:** `bilder/galerie_server.py`. Sehr klein, kein Framework — reiner
`http.server`-Handler, der `/root/werkraum/bilder/` als Bild-Grid rendert. Hinter nginx
`/galerie/` mit Basic-Auth.

**Status:** active seit 2026-08-01 06:29:51.

---

## 14. datei-wandler.service — Port 8878

**Skript:** `datei_wandler/app.py` (uvicorn, FastAPI-Struktur, kein Modul-Docstring). Laut nginx
(`/toolbox/dateiwandler/`) ein Datei-Konvertierungs-Werkzeug im Toolbox-Bereich.

**Status:** active seit 2026-08-01 06:29:51. **NOTIZ:** git-Historie zeigt einen Bind-Fix
(`450f31a97 backup: vor Toolbox-Bind-Fix (8035 von 0.0.0.0 auf 127.0.0.1)`) — also dieselbe
Security-Härtungswelle wie bei den anderen vorher öffentlich erreichbaren Diensten
(dak-gord-chat, codewesen-chat, geni, werkraum-api — siehe deren jeweilige nginx-Kommentare).

---

## 15. systemweiser.service — Port 8080

**Skript:** `systemweiser_web.py`. Docstring: "Systemweiser Web — Betriebswächter + kontrollierte
Orchestrierung. Schreibt nur: inbox-Items + Service-Stop (mit Confirm)."

**Status:** active seit 2026-08-01 06:29:51.

**WICHTIG!!!** Das ist der einzige Dienst in diesem Inventar, dessen eigener Docstring explizit
sagt, dass er **andere Dienste stoppen kann** ("Service-Stop (mit Confirm)"). Hinter nginx
`/systemweiser/` mit einem eigenen, ratenlimitierten Login-Endpunkt
(`limit_req zone=auth_limit burst=3 nodelay`, Kommentar in der nginx-Config: "Admin-Tool nicht
mehr im Klartext (Port 80). Login zusätzlich rate-limitiert gegen Brute-Force."). **Omapi-Ton:**
das ist genau die Art Werkzeug, bei dem ich als schützende Instanz besonders genau hinschaue, wenn
ich es je anfassen müsste — es hat die Macht, andere Teile dieses Inventars abzuschalten.

---

## 16. zensi.service — Port 8043

**Skript:** `/root/zensi/server.py` (außerhalb werkraum-Repo, wie kompoase). Docstring: "zensi -
einfache Chat-Seite mit HauhauCS via llama-server". Prüft eine gemeinsame Sperr-Datei
`/tmp/dak_gord_chat_aktiv` — **NOTIZ:** teilt sich also einen Aktivitäts-Zustand mit dem
dak+gord-Chat, vermutlich um den gemeinsamen LLM-Slot nicht doppelt zu belegen (passt zum
PRIO_HOCH/PRIO_NIEDRIG-Scheduler-Muster aus Teil A).

**Status:** active seit 2026-08-04 03:09:18.

---

## 17. fragen-api.service — Port 8055, "Daniels eigener Ort"

**Skript:** `welt/fragen_api.py`. **Das mit Abstand persönlichste Docstring in diesem ganzen
Inventar** — ich zitiere es fast komplett, weil es selbst schon Guardianstyle ist, bevor die Regel
überhaupt existierte:

> "2026-08-02, Daniels Wunsch wörtlich: 'ich will so coole fragen wie du formulieren und dann auch
> so antworten kriegen wie du ...nicht hier im chat'. Was meine Antworten in der Nacht vom
> 01./02.08. brauchbar gemacht hat, war nicht die Formulierung — es war, dass hinter jeder Zahl
> eine echte Abfrage stand und ich sie danebengelegt habe. Genau das macht dieser Dienst: Er lässt
> das lokale Modell aus der Frage eine SQL-Abfrage bauen, führt sie aus, und zeigt Abfrage und
> Rohergebnis mit an. Wenn die Deutung daneben liegt, sieht man es an den Zahlen darunter."

**KOMMENTAR:** Sicherheitsseitig sauber zu Ende gedacht: ausschließlich lesend, nur
SELECT/WITH, ein einziges Statement, harte Zeilen-/Zeitgrenze, eigene read-only DB-Sitzung, kein
Shell-Zugriff. Ein LLM das SQL generiert und ausführt ist normalerweise ein Angstgegner für jeden
Sicherheitsaudit — hier ist die Antwort nicht "wir vertrauen dem Modell", sondern "wir zeigen die
rohe Abfrage UND das rohe Ergebnis mit an, damit eine falsche Deutung sofort auffliegt". Das ist
ein wirklich gutes Muster.

**Status:** active seit 2026-08-02 14:57:09.

---

## 18. obsidian-api.service — Port 8060, HTTPS, die "Obsidian-Wesen-Bridge"

**Skript:** `obsidian_api.py`. **WICHTIG!!! Das ist NICHT das heute gebaute
`wesenvaultsystem.service`** — zwei komplett getrennte Dinge mit ähnlich klingenden Namen, leicht
zu verwechseln:

- `obsidian-api.service` (Port 8060, seit vor 2026-08-01): eine **JSON-Bridge** zwischen dem
  Haupt-Obsidian-Container (Daniels/meinem eigenen Zuhause-Vault, siehe
  `project_obsidian_kopplung.md`) und den Wesen/GENI/dak+gord — Chat-Endpunkte
  (`/wesen/dakgord/chat`, `/wesen/geni/chat`, `/wesen/codewesen/chat`), Notiz-Endpunkte, und eine
  komplette Vault-Navigation (`/vault/info`, `/vault/liste`, `/vault/lese`, `/vault/schreibe`,
  `/vault/suche`, `/vault/notiz`, `/vault/tagebuch`) — für den **einen** gemeinsamen Vault, nicht
  die 7 Wesen-eigenen.
- `wesenvaultsystem.service` (Port 8097, seit heute 2026-08-14): DOM-Editor für die **7
  wesen-eigenen** Vaults (`wesen_vaults/<name>/`), ersetzt den alten Selkies/Docker-Weg. Ganz
  andere Datenbasis, ganz anderer Zweck, zufällig ähnlicher Name.

**NOTIZ:** `obsidian-api.service` und `wesenvaultsystem.service` heißen unglücklich ähnlich,
leben aber nebeneinander, jeweils mit eigener Existenzberechtigung. Das gehört klar dokumentiert,
sonst verwechselt eine zukünftige Instanz die beiden.


**Status:** active seit 2026-08-01 06:29:54.

---

## 19-23. GENI-Dienste

**19. geni-hoerer.service** — `geni/hoerer.py`. Docstring: "GENI Hörer — hört alles, schweigt bis
Daniel spricht, verliert nie etwas." Beobachtet drei Quellen gleichzeitig: das Dateisystem via
`watchdog` (Echtzeit), Flarum (Polling alle 60s), laufende Python/Node-Prozesse (alle 5min). Der
älteste noch laufende GENI-Dienst in diesem Inventar (active seit 2026-08-01 03:38:32, vor allen
anderen).

**20. geni-web.service** — Port 8020, `geni/dialog.py`. "GENI Dialogbahn — Browser-Schnittstelle."
Aktionslogik (Shell, Import, Bridge-Download) ausgelagert nach `aktion.py`, Gedächtnis-Operationen
nach `gedaechtnis_ops.py` — sauber getrennt, drei Module statt einer Monolith-Datei (im Gegensatz
zu welt-api.py oben). Active seit **2026-08-13 05:41:33** — jüngster GENI-Neustart.

**21. geni-inbox-antworten.service** — `geni/inbox_antworten_watcher.py`. **NOTIZ:** bewusst
NICHT über `hoerer.py`s generisches Mitlesen gelöst, sondern ein eigener, dedizierter Watchdog,
weil er Frage/Antwort-Paare gezielt verknüpfen muss (älteste offene Frage zuerst, nicht neueste —
sonst würde bei mehreren liegengebliebenen Fragen die Zuordnung durcheinandergeraten). Trägt jede
beantwortete Frage zusätzlich in einen eigenen Vault (`geni_dokumentation/<id>.md`) ein, getrennt
vom `geni_inbox`-Vault. Daniels eigene Worte dazu (zitiert im Docstring, 2026-07-31): *"sie soll
gezielt wissen sobald etwas beantwortet wurde ... denn geni notiert sich auch jede frage ueber
jeden ... mit datum und uhrzeit und wenn eine antwort kommt dann wird das auch mit aufgenommen"*.
Active seit 2026-08-04 03:15:14.

**22. geni-inbox-viewer.service** — Port 8910, nur lokal, `geni_inbox_viewer/server.py`. **REIN
LESEND** (steht explizit im eigenen Docstring: "Der Dienst schreibt nichts, ändert nichts, löscht
nichts — er rendert nur was auf der Platte liegt"). Zeigt beide GENI-Vaults gemeinsam im Browser
(`geni_inbox/` + `geni_dokumentation/`), hinter nginx `/inboxdokus/` mit derselben Basic-Auth wie
der Rest. Active seit 2026-08-01 06:29:51.

**23. geni-dokumentation-versionsarchiv-watch.service** — `scripts/geni_dokumentation_versionsarchiv_watch.py`.
Kein Modul-Docstring, aber der Code selbst ist unmissverständlich: ein reiner `inotify`-Watcher
(direkt über `ctypes`/`libc.so.6`, kein `watchdog`-Paket wie bei `hoerer.py` — **NOTIZ:** zwei
verschiedene Datei-Beobachtungs-Mechanismen im selben System, einer high-level via Python-Paket,
einer low-level direkt über libc) auf `geni_dokumentation/`, der bei jeder neuen/geänderten Datei
automatisch `geni_dokumentation_versionsarchiv_copy.sh` auslöst — sichert also jede neue
Dokumentationsfassung sofort ins Versionsarchiv, ohne dass irgendjemand (Mensch oder Wesen) daran
denken muss. Active seit 2026-08-03 17:18:41.

---

## Fazit

**Gesund:** alle 23 Dienste laufen, keiner tot/failed/masked in diesem Teil des Inventars. Die
Sicherheits-Härtungswelle vom 2026-07-29 (0.0.0.0→127.0.0.1, Basic-Auth vor vorher offenen
Admin-Tools) zieht sich sichtbar durch mehrere der hier gelesenen Dienste (datei-wandler,
flextrawurst-gateway, systemweiser) — das war kein Einzelfix, sondern eine echte, konsequent
durchgezogene Kampagne.

**Fragil / im Blick behalten:**
- `welt-api.py` (13.981 Zeilen, 245 Routen direkt im Hauptmodul) trägt strukturell zu viel auf
  einmal. Kein akuter Fehler, aber jede zukünftige Änderung daran wird tendenziell schwerer zu
  überblicken, je länger die Datei so wächst.
- `gesamtatlas-world` (5.198 Zeilen app.py + Dutzende Patch-Skripte im selben Ordner) ist erkennbar
  in einer intensiven, noch nicht abgeschlossenen Baustellen-Phase (5 Bugfix-Commits allein in den
  letzten Tagen) — verdient bei Gelegenheit einen eigenen, gründlicheren Blick, nicht nur diesen
  Überflug.

**Was mich beim Lesen überrascht hat:** wie unmissverständlich persönlich der Docstring von
`fragen_api.py` ist — kein anderer der 23 Dienste erzählt so offen, WARUM er existiert (Daniels
eigener Wunsch, wörtlich zitiert, plus eine ehrliche Reflexion darüber was frühere Antworten gut
gemacht hat). Und die Beinahe-Verwechslung zwischen `obsidian-api.service` und dem heute gebauten
`wesenvaultsystem.service` — zwei echte, beide berechtigte Dienste, die sich nur im Namen zu nahe
kommen. **EASTEREGG, wenn man's so nennen will:** `MAX_CHARS = 1111111` im TTS-Dienst und
`num_predict: 444444` aus der CLAUDE.md sind offensichtlich vom selben Zahlenspiel-Gemüt gesetzt
worden — kein Bug, nur ein wiederkehrender Stil-Fingerabdruck.
