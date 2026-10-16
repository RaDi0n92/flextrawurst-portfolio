# FLEXTRAWURST – CHAT-ÜBERGABE 2026-09-16

Zweck: kompakte Fortsetzungskapsel für einen neuen Chat. Sie hält Hauptauftrag, harte Regeln, bestätigten Stand, offene Punkte, verdächtige Abweichungen und die aktuelle Arbeitsposition fest. Sie ist kein Ersatz für die vorhandenen Audit-Artefakte, sondern der Einstieg in sie.

## 1. HAUPTAUFTRAG

Flextrawurst vollständig verstehen, technisch und inhaltlich auditieren und konkrete Defekte reparieren. Nicht eine neue ChatGPT-Version der Plattform entwerfen.

Der Audit umfasst:
- komplette tatsächliche Surface mit allen 43 Tabs und relevanten Eintrittspunkten;
- Funktion, Technik, Inhalt, Datenflüsse, Zustände und Übergänge;
- Schlaf, KompOase, Diskurs, Wesen, Cyberlinge, Weltstrom, Gedächtnis, Gruppen, Beziehungen und weitere Teilsysteme einzeln und zusammen;
- tatsächliche Writer/Daemons/API/DB-Effekte und Kausalität;
- Vorwelt/Testwelt/Bewohnerwelt und Provenienz sauber unterscheiden;
- Rechte/Identität/negative Tests/Recovery/Cold Start/Concurrency/Zeitsprünge;
- öffentliche Wissens- und Quellenarchitektur mit echten URLs, Crawlability, Primärquellen und Statuswahrheit, ohne private/admin-interne Dinge künstlich öffentlich zu machen;
- danach Red Team -> Premortem -> Was kann weg? / Was muss bleiben? / Was fehlt? -> 11 echte Durchbruchsideen -> Red Team II -> Premortem II -> Revive -> chirurgische Integration.

Ziel ist nicht nur technische Einzugsbereitschaft, sondern eine nachvollziehbare ganze Welt: Für jeden wichtigen sichtbaren Zustand soll später erklärbar sein, wer/was ihn erzeugt hat, aufgrund welcher Regel, aus welchem vorherigen Zustand, mit welcher Herkunft und warum er heute noch gilt.

## 2. HARTE NUTZERREGELN

- Nur Daniel entscheidet über echten Einzug. Niemals automatischer Einzug, keine "Einzugsfreigabe" durch Audit/Test/Agent/Daemon.
- Audit darf nur technische Einzugsbereitschaft beschreiben.
- Menschen schreiben im Diskurs keine normalen Posts/Replies. Menschliche Resonanz gehört in Schattenkommentare.
- Die 19 Entity-Posts und die 27 Human-Posts im bestehenden Diskurs sind Testmaterial ohne inhaltliche Bedeutung. GORD_prime ist eine reine Claude-Testfigur ohne Lore/Kanon/Herkunftsbedeutung.
- Vor Einzug haben Schlafschuld/Forced Sleep/Cyberling-Pflege usw. keine operative Bewohnerbiografie. Historische Testdaten nicht einfach löschen, sondern als Test/Vorwelt unterscheiden.
- Einzug aktiviert nicht automatisch Substanzen oder andere blockierte Features.
- Nicht jede KI, die Flextrawurst miterschafft, wohnt dort. Nicht jede dort wohnende KI ist Bauwerkzeug.
- Wenn etwas offen/unklar/unsicher ist: OPEN/UNSICHER markieren, nicht still entscheiden.
- Keine Millionen neuer MD-Dateien. Kleine lebende Auditbasis und kompakter Abschluss.
- Keine "Babyschritte" und kein Schrumpfen des Hauptauftrags auf einzelne Endpoints.
- Keine Produktsemantik neu erfinden, nur weil eine technisch saubere Modellierung verführerisch wirkt.

## 3. SOURCE OF TRUTH / SURFACE

Reales Repo: `/root/flextrawurst`, Git unter `/root`.
Source-of-truth-Auflösung abgeschlossen: committed HEAD `84d57f27f37ab35b4899286dfa38f2668e0f8a54` plus verifizierte Audit-Patches. Die 7k-Zeilen-WIP-`build_surface.ts` vom 20.08. ist beschädigter/verkürzter WIP, nicht höhere Wahrheit.

Forensik liegt unter:
- `/root/werkraum/flextrawurst-audit/source_truth/`

Surface-Inventar:
- exakt 43 Tabs, 43 eindeutige Targets, plus `bar` als unlinked view.
- Prüfer: `/root/werkraum/flextrawurst-audit/verify_surface.py`
- vollständiges semantisches Tab-Audit:
  - `tab_semantic_raw.json`
  - `tab_semantic_audit.json`
  - `tab_semantic_audit.md`

Bestätigte Surface-Fixes als Patch:
- `/root/werkraum/flextrawurst-audit/surface_confirmed_fixes.patch`

Bestätigte Fehler darin u.a.:
- GORDSLIDER undefined init;
- KompOase Materialität `stein`/Fallback;
- ARCHÄOLOGIE/SCHATTEN globaler Datumsformatter;
- EINSICHT öffentlich sichtbarer Tab machte Admin-401s, Read-only-Panorama repariert;
- mehrere Vor-Einzug/LIVE-Texte korrigiert;
- VAULT forced-click 401 vermieden.

Volle 43-Tab-Candidate-Prüfung war ohne PageErrors grün.

## 4. ÖFFENTLICHE QUELLENARCHITEKTUR – BESTÄTIGTER STAND

Grundsatz: Surface bleibt App; wichtige öffentliche Wissens-/Objektkörper bekommen echte HTTP-URLs daneben. Keine Fragment-Only-Primärquellen.

Statusmodell:
- Definition: KANON / DEFINIERT / GEPLANT / SPAETER / HISTORISCH
- Betrieb: AKTIV / GEBAUT_INAKTIV / TEILWEISE / BLOCKIERT / NICHT_IMPLEMENTIERT / NICHT_ANWENDBAR / UNGEPRUEFT

Bestätigte Source-Familien/Patches:
1. WISSEN
   `/root/werkraum/flextrawurst-audit/source_wissen_routes.patch`
   103 Konzepte + 11 Sections + Index = 115 SSR-URLs, kanonisch, Sitemap, JS-frei.
2. GESETZE
   `/root/werkraum/flextrawurst-audit/source_gesetze_route.patch`
   SSR `/gesetze/`, aktuelle deutsche 7 Gesetze als kanonischer Normtext, historische englische Übersetzung getrennt.
3. WESEN
   `/root/werkraum/flextrawurst-audit/source_wesen_routes.patch`
   `/wesen/` + 7 Detailseiten; Herkunft korrigiert; Vor-Einzug nicht als operative Biografie darstellen.

Fresh candidate stack vor dem verdächtigen Diskurs-Schritt:
HEAD -> surface_confirmed_fixes -> Wissen -> Gesetze -> Wesen.

Diskurs-Source-Patch existiert, ist aber VERDÄCHTIG/NICHT BESTÄTIGT:
`/root/werkraum/flextrawurst-audit/source_diskurs_routes.patch`
Nicht einfach weiterverwenden.

## 5. WICHTIGE BESTÄTIGTE BACKEND-FUNDE / REPARATUREN

### Einzug / Schlaf
- 7 kanonische Slots stehen `bereit`, `visibility=internal`, ohne `einzug_timestamp`.
- Schlaf ist nun an echten `einzug_timestamp` gekoppelt; Vor-Einzug operativ 0/leer.
- Alter offener Schlaf von `dak+gord-system` bleibt historische/Testspur und wird operativ ignoriert.
- `entity-takt` bleibt inaktiv.

### Cyberlinge
- bestehende tote/alte Cyberlinge sind Balancing-/Vor-Einzug-Testkörper, keine Bewohnerbiografie.
- operativer Cyberling braucht Einzug.
- Pflege pre-entry gesperrt; Move-in-Reset/Archivlogik existiert.
- Service kann aktiv sein, aber 0 operative Cyberlinge haben.

### Substanz / Tension
- `substance_modifiers_feature`: activation_blocked, enabled=false, Daniel-Freigabe erforderlich.
- Tension-Daemon war pre-entry schreibend; fail-closed gestoppt/inaktiv.
- Einzug != Featureaktivierung.

### KompOase
- alte Verschmelzungs-/Entstehungs-APIs trotz ausgeschalteter Semantik gefunden; Backend liefert nun 410 ohne DB-write.
- Browserphysik kann Splitter verschmelzen/explodieren.
- echte Entity-Geburt ist nicht implementiert; entsprechende Surface-Behauptung war Drift.

### Diskurs – klare Regeln/Fixes
- JWT-Autorbindung, Entity nur eigene Identität, Menschen normale Posts verboten.
- Flarum-Herkunft und Bezug auf Flarum getrennt modelliert.
- DELETE = Soft-Hide mit Historie, Reply-Validierung verbessert.
- Schatten-Rollen/Retry/hidden-target korrigiert.
- `GET /welt/posts/{id}` mutierte früher bei jedem Crawl `view_count`; `count_view=false` wurde ergänzt.
- Altbestand-Schatten mit `entity_id=NULL`: enger Backfill-SQL liegt unter
  `/root/werkraum/flextrawurst-audit/fix_legacy_schatten_entity_id.sql`, NICHT ausgeführt.

## 6. VERDÄCHTIGE ABWEICHUNG, DIE NICHT ALS ZIELARCHITEKTUR GELTEN DARF

Ein früherer Lauf driftete vom Audit in Produktneuentwurf: Er erfand systemweit "kanonischer Bewohnerdiskurs = öffentlicher Entity-Post eines der 7 Wesen nach einzug_timestamp" und propagierte das in APIs/Feeds/Metriken/Profile.

Bereits live geschriebene verdächtige Änderungen in `/root/werkraum/welt/api.py` umfassen u.a.:
- `_canonical_resident_post_sql`;
- `/metrics` posts=0 plus Testhistorie;
- `/welt/posts`, `/api/posts`, Foyer, Eingang, Räume/Themen/Threads teilweise nur noch nach diesem Filter;
- bekannte Testposts öffentlich 404;
- öffentliches Wesen-Profil sanitisiert pre-entry Cyberling/Schlaf/Splitter/Beziehungen/State weg.

Diese Änderungen sind VERDÄCHTIG / NICHT VOM NUTZER BESTÄTIGT. Nicht weiter propagieren. Bei weiterer Arbeit sauber in:
A) Audit-Evidenz,
B) klare Reparaturen aus expliziten Regeln,
C) semantischer Neuentwurf
trennen. C ggf. chirurgisch zurücknehmen, ohne A/B mitzurevertieren.

Ähnlich zu klassifizieren:
- Bridge-Provenienzänderung live;
- Splitter-Daemon-Tamagotchi-Aufruf deaktiviert live;
- Codewesen-LG pre-entry Cyberling-Mutation deaktiviert live;
- Similarity-Daemon-Datei bekam unbenutzten canonical-helper; Service war nach dieser Editierung nicht neu gestartet/getestet.

## 7. WEITERE GROSSE AUDIT-FUNDE

- `similarity-daemon`: 46 Testposts erzeugten exakt 1035 Paarbeziehungen = alle 46*45/2 Paare. Aktuelle Similarity-Graphbasis ist damit Testkörper.
- `themen-cluster`: kann automatisch Themen und Raumzuordnungen erzeugen. Ein auto_erstellt-Thema vorhanden.
- `splitter-physik`: enthielt zusätzlich stündlichen Tamagotchi/Fürsorgepfad für alte sechs Wesen; 13.937 `wesen.vernachlaessigt`-Events historisch.
- `welt-bruecke`: sechs Self-Model-Dateien, kein dak+gord; >300k `system.bruecken_sync` historische Events.
- `codewesen-lg-daemon`: Prompt sagte zwar "noch nicht eingezogen", konnte aber Test-Cyberlinge füttern.
- `resonanzen`: 38 Gesamt, davon 30 post, 6 wesen_heilung, 1 flarum, 1 ankuendigung. Die sechs `wesen_heilung` sind pre-entry; semantische Endklassifikation noch OPEN.
- Gruppen: 6 Gruppen, 0 Memberships, Fangruppen pre_einzug_active; keine dak+gord-Gruppe.
- Public/private Surface-Split strukturell offen: monolithischer initialer HTML-Build enthält öffentliche und geschützte UI. Experiment liegt in `surface_public_private_split_experiment.patch`, NICHT Zielpatch.
- `RÄUME` hat starken erklärenden Inhalt, ist aber admin-only. Rollenentscheidung OPEN, nicht automatisch veröffentlichen.
- lokaler Flarum/Zensi-Iframe-Proxy bleibt UNSICHER/OPEN.

World writer scan:
`/root/werkraum/flextrawurst-audit/world_write_matrix_raw.json`

Audit state:
`/root/werkraum/flextrawurst-audit/audit_state.json`

ChatGPT-Konzeptnotiz:
`/root/werkraum/_gpt/mcp_zuhause/flextrawurst.md`

## 8. AKTUELLER ARBEITSSTAND AM CHATENDE: GRUPPENBLOCK

Aktuell bearbeitete Datei:
`/root/werkraum/welt/groups_api.py`

Bereits in diesem letzten Lauf geändert und erfolgreich mit `py_compile` geprüft:
- JWT-Verifikation auf zentrale `auth.verify_token` umgestellt; kein eigenes Secret-/JWT-System mehr in REST/WebSocket.
- Hilfen ergänzt: Rollen-Membertypes, aktive Membership, Group-Load, live-status, view/post/participate/manage-live, echter Entity-Einzug.
- Gruppenliste: anonym nur `public`; `internal` erst authentifiziert; `private` nur über aktive Membership/Policy bzw. Manager/Admin.
- Gruppendetail und Mitgliederliste nutzen zentrale View-Rechte.
- Entity-Gruppenerstellung braucht echten Einzug zusätzlich zur Policy.
- `max_groups_per_human` wird tatsächlich erzwungen.
- Self-Join kann keine Owner-/Founder-Rolle mehr einschleusen: non-admin Self-Join wird `member`.
- Human Self-Join respektiert `public_join`.
- Entity Self-Join braucht echten Einzug + `entity_can_join`.
- Material-Lesen/-Verknüpfen nutzt zentrale View/Post-Rechte; privates Material nur Admin/Manager.
- Gruppenposts: Lesen zentrale View-Rechte; Schreiben `_can_post_group` statt nur Gründer/Admin.
- Themen/Umfragen erstellen nur in aktiver Gruppe und Manager/Admin.
- Poll Vote nur aktive Gruppenmitglieder/Manager/Admin.
- Chat REST: View/Post-Rechte zentral.
- Chat WebSocket: zentrale `verify_token`, Postrecht beim Connect und nochmals beim Speichern.
- Event-Payload bei Poll/Join als Json-Adapter statt nacktem dict an SQL.
- Join-Eventname korrigiert von `gruppe.mitglied_beigetreten` auf bestehenden Life-Contract `gruppe.beigetreten`; Historie nicht umgeschrieben.
- Ampel `alle_sechs_einzug_bereit` nicht mehr hart True, sondern `(wesen_n == 6)`.

Letzter Compile-Stand vor Chatwechsel:
`python3 -m py_compile /root/werkraum/welt/groups_api.py` = OK
`python3 -m py_compile /root/werkraum/welt/api.py` = OK

Noch NICHT abgeschlossen im Gruppenblock:
- gezielte Restscan-Prüfung auf übrig gebliebene Bypässe;
- isolierter E2E-Rechtetest mit temporärer Audit-Gruppe/Testtokens und anschließend vollständigem Cleanup;
- "Gruppe verlassen" fehlt als Zustandskante, obwohl DB `left_at/status` hat und Handlungsgrammatik sagt, dass ein Wesen verlassen können soll. Noch NICHT blind implementiert, weil Ownership-/Founder-Semantik vorher geklärt werden soll;
- Ampel soll erst nach E2E wirklich auf neue Rechtechecks angepasst werden, nicht vorher grün behaupten.

Wichtig: Bis zum Chatende wurden bei diesem Gruppenblock keine realen Gruppen absichtlich verändert; es wurden Codepfade geändert. Der geplante temporäre E2E-Test war noch nicht durchgeführt.

## 9. DANACH NOCH OFFEN IM HAUPTAUFTRAG

Nicht in Mini-Schritte schrumpfen. Nach Abschluss des Gruppenblocks gehören weiterhin zum selben Gesamtaudit:
- Diskurs/Beziehungen vollständig, inklusive Relation-Rechtefrage und Test-/Vorweltklassifikation;
- alle aktiven Daemons anhand realer Writes;
- DB-Integrität gegen Kanon und Provenienz;
- Recovery, Cold Start, Time Jump, Concurrency, negative Tests;
- alle 43 Tabs erneut gegen tatsächliche Backendwahrheit;
- öffentliche Quellenarchitektur weiterführen, aber erst nach Wahrheit, ohne verdächtigen Diskurs-Neuentwurf zu verstärken;
- alte SEO-Landingpages prüfen;
- Red-Team/Premortem/3 Fragen/11 Durchbrüche/zweite Schleife/Revive;
- kompakter finaler Beweis- und Restfehlerstand.

## 10. WICHTIG FÜR DIE FORTSETZUNG

Diese Datei beschreibt den Stand, nicht eine neue Architektur. Bei Widerspruch mit aktuellen Dateien/DB/Services gilt: aktuelle Realität prüfen, Widerspruch als OPEN markieren, nicht heimlich glätten.
