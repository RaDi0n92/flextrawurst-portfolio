from pathlib import Path
import json
raw=json.load(open('/root/werkraum/flextrawurst-audit/tab_semantic_raw.json'))['tabs']
J={
'codearchaeologie':('PUBLIC_PRIMARY_ARCHIVE','PARTIAL_VERIFY','STATIC_STRONG_NO_URL','HIGH','Massiver First-Party-Archäologiekörper; einzelne historische Fundbehauptungen in diesem Durchlauf nicht vollständig nachverifiziert. Keine eigene URL/Detailpermalinks.'),
'beleidigt':('PUBLIC_PRIMARY_ARCHIVE','PARTIAL_VERIFY','STATIC_STRONG_NO_URL','MEDIUM_HIGH','Echte Bau-/Fehlerspuren mit Ort und Wortlaut; als eigenständige Quelle brauchbar, aber ohne URL und ohne strukturierte Fundpermalinks.'),
'codegeil':('PROTECTED_ARCHIVE','OPEN','PROTECTED_IN_PUBLIC_MONOLITH','INTERNAL','Geschützter Archivkörper; semantischer Zweck/Publikationsstatus in diesem Durchlauf nicht neu entschieden.'),
'guardianstyle':('PROTECTED_ARCHIVE','OPEN','PROTECTED_IN_PUBLIC_MONOLITH','INTERNAL','Geschützter Archäologie-/Guardian-Körper; nicht als öffentliche Quelle behandeln, solange Publikationsstatus nicht geklärt ist.'),
'systemweitearchaeologie':('PUBLIC_PRIMARY_ARCHIVE','PARTIAL_VERIFY','STATIC_MEDIUM_NO_URL','HIGH','Systemweite First-Party-Baugeschichte mit hoher Quellenrelevanz; keine stabile Ressource je Fund/Datei.'),
'reibungsgewebe':('PUBLIC_LIVE_TRANSPARENCY','OPEN_DYNAMIC','DYNAMIC_PLACEHOLDER_NO_URL','MEDIUM_POTENTIAL','Öffentlich, aber SSR praktisch nur Ladehülle. Inhalt/Wahrheit muss aus Livequelle kommen; aktuell crawltechnisch wertlos.'),
'ankuendigungen':('PUBLIC_EDITORIAL','PARTIAL','DYNAMIC_THIN_NO_URL','MEDIUM','DB enthält mindestens eine Ankündigung; SSR besteht überwiegend aus Editor/Admin-Hülle statt crawlbarer veröffentlichter Einträge.'),
'uber':('PUBLIC_PRIMARY_GUIDE','DRIFT','STATIC_STRONG_NO_URL','HIGH','Sehr starker Einstiegskörper. Deutsche Vor-Einzugslage weitgehend korrigiert; englische Schicht enthält noch Six-AI-beings-Alttext und weitere Statusangaben müssen synchronisiert werden.'),
'diskurs':('PUBLIC_PRIMARY_DISCUSSION','FUNCTIONAL_CRAWL_GAP','DYNAMIC_THIN_NO_PERMALINKS','HIGH','46 öffentliche ftw_posts im DB-Bestand, aber SSR fast nur Bedien-/Adminhülle. Beiträge/Threads haben aus dem Einstieg keine stabilen crawlbaren Detailressourcen.'),
'wesen':('PUBLIC_PRIMARY_ENTITY','MOSTLY_TRUE','STATIC_MEDIUM_DYNAMIC_NO_ENTITY_URLS','HIGH','7 kanonische Wesen, 0 eingezogen. Vor-Einzug/Testtrennung ist im Kandidaten korrekt. Detailzustände sind dynamisch und nicht als eigene Entity-URLs ausgebildet.'),
'gespraech':('ENTITY_ADMIN_PRIVATE','ACCESS_OK','AUTH_NO_INDEX','NONE_PUBLIC','Nur Wesen/Admin. Kein öffentlicher Crawlgegenstand.'),
'widmungen':('PUBLIC_SOCIAL_GESTURE','PARTIAL_DYNAMIC','STATIC_MEDIUM_DYNAMIC_ENTRIES_NO_URL','MEDIUM','Konzept/Rechte verständlich; echte Widmungen werden dynamisch geladen und besitzen keine klaren öffentlichen Detailressourcen.'),
'denken':('PUBLIC_LIVE_TRANSPARENCY','MOSTLY_TRUE','STATIC_MEDIUM_EPHEMERAL','MEDIUM','Beschreibt ausdrücklich Browser-Agent-Output und aktuell keinen aktiven Browser-Agent. Transparenzfläche, keine gute dauerhafte Primärquelle ohne Archiv-URLs.'),
'rag':('ENTITY_ADMIN_PRIVATE','ACCESS_OK','AUTH_NO_INDEX','NONE_PUBLIC','Wesen/Admin-Wahrnehmungswerkzeug. Nicht öffentlich indexieren.'),
'screens':('PUBLIC_LIVE_TRANSPARENCY','MOSTLY_TRUE','EPHEMERAL_NO_URL','LOW_MEDIUM','On-Demand-Prozesskamera; öffentlich nachvollziehbar, aber flüchtig und als Suchquelle schwach.'),
'gordslider':('ENTITY_ADMIN_PRIVATE_IFRAME','ACCESS_OK','AUTH_IFRAME_NO_INDEX','NONE_PUBLIC','Geschützter Iframe; kein öffentlicher Quellenkörper.'),
'theater':('PUBLIC_WORLD_LIVE','DRIFT','DYNAMIC_THIN_NO_URL','MEDIUM_HIGH','Browser-Splitter können verschmelzen; Entitätsgeburt ist ausdrücklich nur Hülle/TODO und immer false. Server-Splitterdaemon läuft 60s, enthält aber zusätzlich unerwähnte Vor-Einzug-Fürsorge/Tamagotchi-Logik.'),
'blasen':('PUBLIC_SOCIAL_LIVE','PARTIAL_DYNAMIC','DYNAMIC_THIN_NO_URL','MEDIUM','Öffentliches Gedankenblasenfeld; Interaktion dominiert, SSR trägt kaum Einzeldaten/Permalinks.'),
'menschen':('PUBLIC_PROFILE_DIRECTORY','OPEN_DYNAMIC','DYNAMIC_EMPTY_NO_PROFILE_URLS','MEDIUM_POTENTIAL','SSR nur Ladehülle. Öffentliche Menschenprofile brauchen eigene stabile Adressen, wenn dieser Tab öffentliches Verzeichnis sein soll.'),
'meinewelt':('LOGIN_HUMAN_PRIVATE','ACCESS_OK','AUTH_NO_INDEX','NONE_PUBLIC','Persönlicher Menschenraum. Nicht crawlbar machen.'),
'schlaf':('PUBLIC_PRIMARY_SYSTEM','PARTIAL_DRIFT','STATIC_MEDIUM_DYNAMIC_NO_ENTITY_SLEEP_URLS','HIGH','Vor-Einzug korrekt. Code belegt 6h Minimum, 3h Hauptschlaf, 18h/20h Zwang; eine 9h-Maximalgrenze ist nicht implementiert, daher ist 6–9h als harte Regel zu stark.'),
'einsicht':('PUBLIC_TRANSPARENCY_PLUS_ADMIN_DEPTH','CANDIDATE_FIXED','DYNAMIC_THIN_NO_URL','MEDIUM_HIGH','Kandidat trennt anonymes Read-only-Panorama aus öffentlichen Entity-Snapshots von tiefen Admin-Linsen. Technisch ohne 401/PageError; crawlbarer Snapshottext fehlt weiterhin.'),
'archaeologie':('PUBLIC_PRIMARY_ARCHIVE','OPEN_DYNAMIC','DYNAMIC_THIN_NO_OBJECT_URLS','HIGH_POTENTIAL','Öffentlicher Sediment-/Historienzugang, aber SSR nur Filterhülle. Als Primärquelle erst mit stabilen Objekt-/Fund-URLs stark.'),
'haus':('PUBLIC_COLLAB_ARCHIVE','OPEN_DYNAMIC','DYNAMIC_THIN_NO_ENTRY_URLS','HIGH_POTENTIAL','Kann vorhandener Ort für Zusammenarbeit/Spuren verschiedener Systeme sein; aktuell SSR nur Ladehülle. Nicht vorschnell durch neuen ZUSAMMENARBEIT-Tab duplizieren.'),
'flarumaktivitaet':('PUBLIC_ORIGIN_ARCHIVE','MOSTLY_TRUE_DYNAMIC','DYNAMIC_THIN_NO_THREAD_URLS','HIGH','Explizit echte Flarum-Spuren ohne Ranking/Konsens. Sehr wertvolle Herkunftsquelle, aber Einstieg hat keine crawlbaren Thread-Links im SSR.'),
'cyberlinge':('PUBLIC_PRIMARY_SYSTEM','MOSTLY_TRUE','DYNAMIC_EMPTY_NO_ENTITY_URLS','HIGH','Aktuell 0 operative Cyberlinge trotz 8 Testkörpern; Kandidat zeigt Vor-Einzug operativ=false. SSR selbst ist nahezu leer.'),
'systeme':('PUBLIC_PRIMARY_ARCHITECTURE','DRIFT','STATIC_STRONG_NO_URL','HIGH','Sehr wertvoller Architekturtext. Mehrere Live-Aussagen/Dienstbeschreibungen drifteten; Splitterdaemon tut zusätzlich Vor-Einzug-Tamagotchi. GENI besteht aus mehreren Diensten statt einer simplen Servicekarte.'),
'admin':('ADMIN_PRIVATE','ACCESS_OK','ADMIN_NO_INDEX','NONE_PUBLIC','Interne Steuerfläche. Inhalt darf nicht mit öffentlicher Crawl-Anforderung verwechselt werden.'),
'wissen':('PUBLIC_PRIMARY_LEXICON','PARTIAL_VERIFY','STATIC_STRONG_NO_DETAIL_URLS','VERY_HIGH','Beste vorhandene Lexikonbasis. 100+ Konzepte mit Status, aber keine eigene URL je Konzept und Statusfelder sind nicht alle gegen Runtime verifiziert.'),
'gesetze':('PUBLIC_PRIMARY_CONSTITUTION','TEXT_CLEAR','STATIC_STRONG_NO_URL','VERY_HIGH','Eigenständiger, klarer kanonischer Regelkörper. Braucht stabile zitierbare URL; Inhalt selbst ist bereits hervorragend crawlbar.'),
'forschung':('PUBLIC_RESEARCH_PROSPECTUS','DRIFT','STATIC_STRONG_NO_URL','HIGH','Formuliert derzeit echte Entitäten/echten Zeitverlauf als Gegenwart, obwohl 0 Wesen eingezogen sind. Forschungspotential ist plausibel, Beobachtungsbehauptung muss Vor-Einzug vs. Zukunft trennen.'),
'partner':('PUBLIC_POLICY_PROSPECTUS','PLAN_LIVE_MIX','STATIC_STRONG_NO_URL','MEDIUM_HIGH','Mischt heutige Regeln mit zukünftigen Partner-/Zwischenwesen-Rechten. Muss sichtbar zwischen bestehendem Vertrag und geplantem Modell unterscheiden.'),
'flarum':('PUBLIC_ORIGIN_IFRAME','OPEN_SERVING','IFRAME_ZERO_SSR','HIGH_POTENTIAL','Iframe auf /flarum-live/. Hauptseite liefert keinen crawlbaren Inhalt. Lokaler 8787-Test 404 kann Proxy-Harness sein; Produktionsstatus bleibt offen.'),
'zensi':('PUBLIC_IFRAME','OPEN_ROLE_AND_SERVING','IFRAME_ZERO_SSR','OPEN','Iframe auf /zensi/. Öffentliche Rolle und Produktions-Crawlwert nicht geklärt; lokaler 404 noch kein Produktionsbeweis.'),
'leitstand':('ADMIN_STATUS_CONTROL','DRIFT','ADMIN_STATIC_RICH','INTERNAL_MEDIUM','Reicher Statuskörper, aber alte Angaben wie Weltklima läuft/Cyberling-Kapseln/Organe LIVE drifteten. Öffentliche Statusinformation und Adminsteuerung sind derzeit vermischt.'),
'weltstrom':('ADMIN_EVENT_STREAM','OPEN','ADMIN_DYNAMIC','INTERNAL','Interner Ereignisstrom. Ob ein sanitierter öffentlicher Weltstrom gewünscht ist, ist nicht entschieden.'),
'raume':('ROLE_MISMATCH_PUBLIC_KNOWLEDGE_CANDIDATE','MOSTLY_TRUE_WITH_HISTORY','ADMIN_STATIC_STRONG','HIGH','8k+ Zeichen sehr gute Erklärung von Inhaltsräumen vs Weltzonen und Herkunft. Inhalt wirkt öffentlich erklärend, Navigation sperrt ihn als Admin. Rolle ist strukturell widersprüchlich und muss bewusst entschieden werden.'),
'suche':('ADMIN_SEARCH','ACCESS_OK','ADMIN_DYNAMIC','NONE_PUBLIC','Interne globale/archäologische Suche; keine öffentliche Suchressource.'),
'splitter':('ADMIN_RAW_COLLECTION','OPEN','ADMIN_DYNAMIC','INTERNAL','Rohsammlung; nicht automatisch öffentliche Quelle.'),
'zitate':('ADMIN_RAW_COLLECTION','OPEN','ADMIN_DYNAMIC','INTERNAL','Rohsammlung; Publikationsstatus nicht entschieden.'),
'schatten':('ADMIN_RAW_COLLECTION','ACCESS_OK','ADMIN_DYNAMIC','INTERNAL','Rohansicht von Schatten-Threads; Menschen wirken über Schatten, aber die Adminsammlung ist nicht dasselbe wie öffentliche Einzeldarstellung.'),
'gruppen':('ADMIN_PREENTRY_STRUCTURE','PARTIAL_DRIFT','ADMIN_DYNAMIC','MEDIUM_POTENTIAL','DB: 6 systemerzeugte Fangruppen status=pre_einzug_active, 0 memberships, nur die sechs Flarum-Wesen. Also Struktur/Testkörper, keine gelebte Gruppenaktivität; dak+gord fehlt als Gruppe.'),
'vaulteinblick':('ADMIN_PRIVATE_VAULT','CANDIDATE_FIXED','ADMIN_PRIVATE_NO_INDEX','NONE_PUBLIC','Private Wesen-Vaults. Kandidat verhindert anonymen Fetch; nicht crawlbar machen.'),
}
missing=[r['view'] for r in raw if r['view'] not in J]
if missing: raise SystemExit('missing '+repr(missing))
out=[]
for r in raw:
 role,truth,crawl,src,issue=J[r['view']]
 out.append({
   'n':r['n'],'label':r['label'],'view':r['view'],'current_access':r['access'],
   'semantic_role':role,'truth_status':truth,'crawl_status':crawl,'primary_source_value':src,
   'static_chars':r['static_chars'],'tab_href':r['tab_href'],'issue':issue
 })
res={'scope':'43 Surface tabs; semantic role + truth + crawl + primary-source value','count':len(out),'tabs':out,
     'global_findings':[
       '43/43 Tabs use fragment hrefs (#view); none has a standalone tab URL.',
       'Root has one canonical URL https://flextrawurst.de/ and one WebApplication JSON-LD object for the whole monolith.',
       'Current sitemap lists root plus a small set of static public pages, not the 43 tab bodies or their entities/concepts/posts.',
       'High-value primary-source bodies already exist in WISSEN, GESETZE, CODE-ARCHAEOLOGIE, SYSTEME, RAEUME, WAS IST DAS, FORSCHUNG and FLARUM-AKTIVITAET.',
       'Protected/private app views and public knowledge currently coexist in one monolithic HTML architecture; a naive server-side strip breaks post-load browser login.',
       'No automatic Einzug decision is part of this audit; technical readiness is descriptive only.'
     ]}
Path('/root/werkraum/flextrawurst-audit/tab_semantic_audit.json').write_text(json.dumps(res,ensure_ascii=False,indent=2),encoding='utf-8')
# compact markdown for humans
lines=['# Flextrawurst Surface — 43-Tab Semantik/Crawl Audit','',f'Erfasst: {len(out)}/43 Tabs. Keine Einzugsentscheidung. OFFEN bleibt offen.','',
'| # | Tab | Rolle | Wahrheit | Crawl | Quellenwert |', '|---:|---|---|---|---|---|']
for r in out:
 lines.append(f"| {r['n']} | {r['label'].replace('|','/')} | {r['semantic_role']} | {r['truth_status']} | {r['crawl_status']} | {r['primary_source_value']} |")
lines += ['','## Belegte Einzelbefunde','']
for r in out:
 lines.append(f"### {r['n']:02d} {r['label']} (`#{r['view']}`)")
 lines.append(r['issue'])
 lines.append('')
Path('/root/werkraum/flextrawurst-audit/tab_semantic_audit.md').write_text('\n'.join(lines),encoding='utf-8')
print('written',len(out))
for r in out:
 print(f"{r['n']:02d} {r['label'][:28]:28} {r['truth_status']:<20} {r['primary_source_value']:<12} {r['crawl_status']}")
