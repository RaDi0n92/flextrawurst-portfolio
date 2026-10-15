# Doku -- technischer Stand

- App/Backend: `/root/werkraum/tools/gesamtatlas_world/app.py` (FastAPI, läuft
  als `gesamtatlas-world.service`, Port 18108, hinter `flextrawurst.de/megavault`).
- Frontend-Views: Graph (`3d-force-graph`), Globus (`globe.gl`), Zeitstrom.
- Seeder für SIMILAR_TO/OPPOSES: `tools/gesamtatlas_world/tools_seed_relations.py`.
  Läuft als Hintergrund-Dauerschleife `_reseed_loop.sh` alle 10 Minuten (kein
  systemd-Timer -- Sandbox erlaubte kein Schreiben von `.timer`-Dateien nach
  `/etc/systemd/system/`; fertige `.service`/`.timer`-Dateien liegen bereit,
  falls jemand mit Root-Systemd-Rechten sie regulär registrieren will).
- Kanonisches Register: `/root/werkraum/_gpt/gesamtatlas/BEZIEHUNGSREGISTER.sqlite`.
- Begriffsindex (Volltext, FTS5): `/root/werkraum/_gpt/gesamtatlas/BEGRIFFSINDEX.sqlite`.
- Gegensatz-Bestätigungslog: `/root/werkraum/_gpt/gesamtatlas/GEGENSATZ_BESTAETIGUNGSLOG.json`.
- Knotenvertrag (kanonisch): `/root/werkraum/_shared/KNOTENVERTRAG.md`.
- Neue Endpunkte diese Session: `/api/megavault/globus`, `/api/megavault/frage`
  (Durchreiche zu `/fragen`, Port 8055), `/api/megavault/gegensatz/*`,
  `/api/megavault/datei_historie`, `/api/megavault/datei_diff`.
- Globus ist seit 2026-08-15 die Standardansicht beim Laden (nicht mehr Graph).
- Kopfzeile zeigt einen echten Wahrheits-Indikator (`#wahrheitsindikator`),
  gespeist aus dem bestehenden `/api/truth`-Endpoint (verifizierte Baseline +
  Revision, aus einer früheren Session bereits gebaut).
- Graph-Ansicht lädt jetzt denselben breiten Ausschnitt wie Globus
  (`/api/megavault/globus`), nicht mehr ein festes Einzelprojekt -- inkl. echter,
  aus Dateipfaden abgeleiteter Ordnerknoten (kein neuer DB-Schema-Typ).
  Kanten unsichtbar bis Hover, Physik-Simulation kommt nach ~4s zur Ruhe.
- Alle bisherigen Farbwahlen sind Platzhalter, nicht final (siehe WICHTIGES.md).
- Ordner-Knoten haben jetzt echten Klick-Inhalt: `/api/megavault/ordner_inhalt`
  listet direkt vom Dateisystem (os.scandir), nicht aus dem Register --
  unterscheidet sich sauber von der Datei-Lese-Sektion (node.group === 'ordner').
- Detail-Panel nutzt jetzt auch `/api/megavault/file_details` (Wer/Rechte/BM25/
  echte Rückverweise), ergänzt zur Git-Historie. Bei verwaisten Registerpfaden
  (Datei existiert nicht mehr auf Platte) zeigt die UI das jetzt ehrlich als
  Lücke statt hängenzubleiben.
- Ebenen-Tab live: /api/megavault/ebenen, 6-Schichten-Modell von ChatGPT gegen
  echte node_types geprüft und übernommen.
- Zusammenarbeit mit ChatGPT läuft über /root/werkraum/claudeweb_bau-megavault/zusammenarbeit/
  (dateibasiert, kein Live-Kanal -- jeweils bei Reaktivierung nachlesen).
- Persistenter Knoten-Fokus (`fokusKnoten`, global): Detail-Panel schliesst
  sich nicht mehr beim Linsenwechsel. Graph/Globus versuchen zusaetzlich, die
  Kamera auf denselben Knoten zu bewegen, falls er in der jeweils aktuell
  geladenen Stichprobe vorkommt (kein Garantie-Treffer, da unabhaengige
  Zufallsstichproben -- wird ehrlich uebersprungen, nicht erzwungen).
- Suchtreffer (`/api/megavault/search`) tragen jetzt eine echte `node_id`, wo
  der Pfad im Register existiert (ChatGPT-Fund geschlossen) -- sonst `null`,
  keine erfundene ID. Bahnt den Weg fuer "Suchtreffer -> Fokus im Koerper".
- Suchtreffer sind jetzt klickbar und steigen direkt in den Fokus-Koerper
  ein (nutzen die neue node_id-Bruecke + knotenZeigen statt der alten
  subgraphLaden-Umleitung ueber Dateiname-Ratesuche).
