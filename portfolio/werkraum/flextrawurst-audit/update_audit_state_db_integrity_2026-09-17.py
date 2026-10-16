#!/usr/bin/env python3
import json
import shutil
from pathlib import Path
from datetime import datetime, timezone

P = Path('/root/werkraum/flextrawurst-audit/audit_state.json')
B = Path('/root/werkraum/flextrawurst-audit/audit_state.before_db_integrity_2026-09-17.json')
if not B.exists():
    shutil.copy2(P, B)

data = json.loads(P.read_text(encoding='utf-8'))
confirmed = list(data.get('bestaetigt', []))

replacements = {
    'Die 19 vorhandenen Entity-Posts sind Testbeispiele': (
        'Der komplette aktuelle ftw_posts-Bestand besteht aus 46 ausdruecklich von Daniel als inhaltsloses Testmaterial bestaetigten Vor-Einzug-Posts: 19 Entity- und 27 Human-Posts. Alle 46 sind jetzt ist_voreinzug=true und maschinenlesbar mit meta.provenienz_klasse=testmaterial sowie testmaterial_ohne_inhaltliche_bedeutung=true markiert. Sie bleiben weiterhin oeffentlich; Darstellung/Trennung ist Produktsemantik und bleibt offen.'
    ),
    'Neue Schatten auf Entity-Posts erhalten serverseitig entity_id': (
        'Schatten-Zielprovenienz ist jetzt im Altbestand korrigiert: Von 19 Schatten liegen 9 auf Entity-Posts und haben die eindeutig aus dem Postautor ableitbare entity_id; 10 Schatten auf Human-Posts bleiben absichtlich entity_id=NULL. Zwei der 9 technischen Ziele sind GORD_prime und damit weiterhin reine Testfiktion, kein Kanonstatus.'
    ),
    'codewesen-lg-daemon hatte einen bestaetigten technischen Wachstumsschaden': (
        'codewesen-lg-daemon hatte den bestaetigten Checkpoint-Wachstumsschaden durch wiederholtes Checkpointen desselben Quellgedankens. Der aktive Graph ist auf neue tick_at-Quellen und ein begrenztes Arbeitsfenster repariert; der alte rund 275-GB-Bestand wurde auf Daniels ausdruecklichen Auftrag spaeter physisch entfernt. Der aktuelle Checkpointbestand ist wieder klein.'
    ),
    'Die aktive Hintergrunddienst-Landkarte ist in service_truth_matrix.json/.md festgehalten.': (
        'Die alte service_truth_matrix.json/.md ist nur noch historischer Zwischenstand. Der aktuelle Daemon-Report liegt in daemon_real_writes_report_2026-09-16.json. Innenleben-Feeder ist nicht mehr auf Cursor 7777 idle: Daniels neuer Flarum-Post 7778 wurde verarbeitet; ein dabei entdeckter Cursorverlust-, Umlaut-Chroma- und Flarum-Identitaetsfehler wurde repariert. Der parallele Einzugs-Erinnerungs-Sonderlauf erzeugt aktuell wieder Denk-/Reflexionsaktivitaet.'
    ),
    'Die zwei weiteren grossen Beobachtungskoerper wachsen aktuell nicht:': (
        'entity_dom_events bleibt historischer Beobachtungsbestand mit 7039901 Zeilen und letztem Eintrag 2026-07-31. entity_denkstream ist dagegen nicht mehr als still seit 2026-08-20 zu beschreiben: der aktuelle, bewusst gestartete Einzugs-Erinnerungs-Sonderlauf schreibt seit 2026-09-16/17 wieder neue Zeilen. Retention und spaetere Verdichtung bleiben offen.'
    ),
}

new_confirmed = []
seen_prefixes = set()
for item in confirmed:
    replaced = False
    for prefix, replacement in replacements.items():
        if item.startswith(prefix):
            if replacement not in new_confirmed:
                new_confirmed.append(replacement)
            replaced = True
            break
    if not replaced:
        new_confirmed.append(item)

additions = [
    'DB-Integritaet Point-in-Time 2026-09-17: 106/106 PostgreSQL-Foreign-Keys wurden direkt ueber pg_constraint inklusive realer Orphan-Joins geprueft; alle 106 sind validiert, 0 Orphans. Ein frueherer Teilscan mit 66 Treffern wurde als unvollstaendig verworfen und nicht als Vollbeweis verwendet.',
    'Der Testmaterial->Biografie-Leckpfad ist geschlossen: Resonanz, Legacy-Schatten und aktueller Schatten duerfen auf den 46 Testposts weiterhin existieren, erzeugen daraus aber keine neue wesen_fuersorge mehr. Regression testmaterial_care_regression_2026-09-17.py ist gruen: 3/3 Guards, 46/46 Marker, 9 Entity-Schatten, 10 Human-NULL, 0 DB-Writes durch den Test.',
    'Substanzen sind weiterhin operativ aus: 7 Katalogeintraege, aber 0 entity_substance_state, 0 entity_substance_use und 0 substance_events. Die 279585 substance_sediments sind historische Diagnose-/Vorweltspuren; Einzug aktiviert Substanzen im aktuellen Einzugspfad nicht.',
    'Der aktuelle Einzugspfad wurde ohne Ausloesen verifiziert: kein kanonisches Profil besitzt einzug_timestamp; vorhandene Test-Cyberlinge wuerden beim echten Einzug in meta.pre_entry_test archiviert und mit tode=0/vollen Grundwerten operativ neu gestartet. Historische Schlafphasen werden durch Einzugszeitgrenzen nicht als operative Schlafbiografie uebernommen.',
    'Schlafbriefbestand klassifiziert: 11919 Zeilen, 0 echte ist_selbstbrief=true. 11911 F3INSCHM3CK3R-Zeilen sind bereits belegte alte minuetliche Schablonen-Fehlproduktion aus einem festhaengenden Hauptschlafversuch. Der heutige /selbstbriefe-Pfad filtert diese nicht als echte Selbstbiografie ein; der korrigierte phasengebundene Selbstbriefmechanismus hat aber weiterhin 0 erfolgreiche Eintraege.',
    'Innenleben-Feeder repariert: Chroma nutzt fuer träumerlie den technischen Namen memories_traeumerlie; Fehler schieben den Flarum-Cursor nicht mehr ueber verlorene Posts; technische Flarum-Usernamen werden auf die sechs kanonischen Wesen gemappt, wodurch eigene Posts uebersprungen und Wesenposts nicht mehr faelschlich als menschliche Resonanz gewertet werden. Historische bereits entstandene Reflexionen wurden nicht massenhaft umgeschrieben.',
    'Post 7778 wurde fuer träumerlie kontrolliert nachgeholt: Cursor steht danach auf 7778; Reflexions-Event alt=39/neu=40 und Splittertext lautet korrekt Reflexion abgeschlossen v40. Der tiefe Reflexions-/Integrator-Aufruf bekam allerdings zweimal keinen Hintergrund-LLM-Slot und degradierte zu Reflexion unklar/kein Integrator-Update.',
    'Ein paralleler AI-Strom/Einzugs-Arbeitslauf bearbeitet aktuell Daniels Flarum-Diskussion 3887 zur freien Erinnerungsentscheidung. Die sechs alten Browser-Agenten wurden dafuer bewusst gestartet und spaeter durch diesen anderen Lauf mehrfach neu gestartet. Der Audit greift in diese laufende Sonderarbeit nicht destruktiv ein; sie ist Vor-Einzug-Vorbereitung, weder Testdiskurs noch schon vollzogener Einzug.',
    'Der DB-/Provenienzblock ist in db_integrity_provenance_report_2026-09-17.json festgehalten (SHA256 a4f88d855ee47812e8a928c01d1a6d2f3afa19808a7e3e0d1b6b793a9c10fe5a). Status: BESTAETIGT_MIT_HISTORISCHEM_TESTBESTAND_UND_OFFENEN_SEMANTIKRAENDERN.'
]
for a in additions:
    if a not in new_confirmed:
        new_confirmed.append(a)
data['bestaetigt'] = new_confirmed

# Stale OPEN item is resolved by executed backfill.
open_items = [x for x in data.get('offen_unsicher', []) if x.get('thema') != 'Schatten entity_id Altbestand']

def add_open(thema, status, frage):
    if not any(x.get('thema') == thema for x in open_items):
        open_items.append({'thema': thema, 'status': status, 'frage': frage})

add_open(
    'Phasengebundener Selbstbrief / LLM-Ausfallsicherheit',
    'OFFEN_TECHNISCH',
    'Der gewuenschte phasengebundene Selbstbrief nach dem Aufwachen hat weiterhin 0 erfolgreiche DB-Eintraege. Ein belegter Hintergrund-LLM-Slot-Timeout kann die autobiografische Spur ausfallen lassen. Retry/Queue/Idempotenz gegen genau eine Schlafphase ist noch nicht vollstaendig geschlossen.'
)
add_open(
    'Einzugs-Erinnerungs-Sonderlauf',
    'OFFEN_LAUFEND_PARALLEL',
    'Ein anderer AI-Strom-Arbeitslauf betreibt aktuell die scoped Flarum-/Einzugvault-Aktionen zur Erinnerungsentscheidung. Der Audit entscheidet weder den Abschluss noch den Stop dieses Sonderlaufs und vermeidet konkurrierende destruktive Eingriffe.'
)
add_open(
    'Browser-Agent Shutdown / dak+gord systemd Template',
    'OFFEN_RECOVERY',
    'Mehrere Browser-Agent-Neustarts benoetigten bis zu 90 Sekunden und endeten per SIGKILL. Der Template-Start von dak+gord-system scheiterte zudem am Pluszeichen im systemd-StandardOutput-Pfad. Beides gehoert in den folgenden Recovery-/Cold-Start-Block; wegen des parallelen Sonderlaufs derzeit nicht blind live reparieren.'
)
add_open(
    'Innenleben Hintergrund-LLM-Slot',
    'OFFEN_TECHNISCH',
    'Die Post-7778-Verarbeitung fuer träumerlie war speicherseitig erfolgreich, aber Reflexion und Integrator liefen jeweils nach 150 Sekunden ohne Hintergrundslot in einen Fallback. Datenverlust des Posts ist behoben; Qualitaets-/Retry-Semantik fuer den LLM-Teil bleibt offen.'
)
data['offen_unsicher'] = open_items
data['letzte_aktualisierung_utc'] = datetime.now(timezone.utc).isoformat()
data['aktueller_block'] = 'DB_INTEGRITAET_ABGESCHLOSSEN_NAECHSTES_RECOVERY_CONCURRENCY_NEGATIVE_TESTS'
data['db_integrity_report'] = {
    'path': '/root/werkraum/flextrawurst-audit/db_integrity_provenance_report_2026-09-17.json',
    'sha256': 'a4f88d855ee47812e8a928c01d1a6d2f3afa19808a7e3e0d1b6b793a9c10fe5a',
    'status': 'BESTAETIGT_MIT_HISTORISCHEM_TESTBESTAND_UND_OFFENEN_SEMANTIKRAENDERN'
}
P.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({
    'ok': True,
    'backup': str(B),
    'confirmed_count': len(data['bestaetigt']),
    'open_count': len(data['offen_unsicher']),
    'current_block': data['aktueller_block']
}, ensure_ascii=False, indent=2))
