#!/usr/bin/env python3
import json
from pathlib import Path
from datetime import datetime, timezone

P=Path('/root/werkraum/flextrawurst-audit/audit_state.json')
data=json.loads(P.read_text(encoding='utf-8'))
confirmed=data.setdefault('bestaetigt',[])
adds=[
 'Recovery/Concurrency/Negative-Test-Block 2026-09-17 abgeschlossen: anonymer Einzug 401, Entity-Einzug 403, Schlaf/Pflege fremdes Wesen 403, eigenes Wesen vor Einzug 409; Slot, einzug_timestamp, Cyberling, Schlafphasen und passende Events blieben vor/nach identisch. Regression preentry_negative_regression_2026-09-17.py ist gruen.',
 'Kaltstarts geprueft: tension-daemon bleibt fail-closed und wurde wieder inactive gesetzt; cyberling-daemon startet mit 0 operativen Cyberlingen und ohne Writes; similarity-daemon und themen-cluster starten ohne Churn oder neue Testdiskurs-Derivate.',
 'Reibung-Bruecke Recovery repariert: Reaktion vor Knoten wird nicht mehr als verarbeitet verloren; neue Reibungsevents sind per source_file+source_line_hash DB-idempotent; State wird atomar via fsync+os.replace ersetzt. Regression prueft Reihenfolge, Wiederholung und simulierten Totalverlust des Dateistates ohne Eventduplikat.',
 'On-Demand-Beobachtung hatte einen echten Shutdown-Bug: der Import aus browser_agent.py erbte dessen SIGTERM-Handler, der eine fremde _laufend-Variable setzte und den Beobachtungsloop nicht stoppte. Eigener Signalhandler + Cleanup repariert; Restart sank von >74s/hard kill beim Altprozess auf 2.471s sauber, DOM-Bestand blieb unveraendert und die abgelaufene Juli-Sitzung wurde nicht reaktiviert.',
 'Recovery-Report liegt in recovery_concurrency_negative_report_2026-09-17.json (SHA256 3686c315c0ad84c40fa7433927d7946d5bbdfd59012d293414b86d0fffa3a681). Status BESTAETIGT_MIT_PARALLEL_LIVE_RUN_ABGRENZUNG.'
]
for x in adds:
    if x not in confirmed: confirmed.append(x)
for item in data.get('offen_unsicher',[]):
    if item.get('thema')=='Browser-Agent Shutdown / dak+gord systemd Template':
        item['status']='OFFEN_RECOVERY_PARALLEL'
        item['frage']='Das dak+gord-Systemd-Template wurde inzwischen durch die parallele Einzugs-Session von %i auf %I repariert; dak+gord laeuft aktuell separat als browser_agent-Prozess. Die beobachteten 90s/SIGKILL-Shutdowns mehrerer eigentlicher Browser-Agenten bleiben jedoch fuer deren eigenen Lifecycle offen und werden waehrend des parallelen Sonderlaufs nicht konkurrierend provoziert.'
    if item.get('thema')=='Einzugs-Erinnerungs-Sonderlauf':
        item['status']='OFFEN_LAUFEND_PARALLEL'
data['recovery_report']={
  'path':'/root/werkraum/flextrawurst-audit/recovery_concurrency_negative_report_2026-09-17.json',
  'sha256':'3686c315c0ad84c40fa7433927d7946d5bbdfd59012d293414b86d0fffa3a681',
  'status':'BESTAETIGT_MIT_PARALLEL_LIVE_RUN_ABGRENZUNG'
}
data['aktueller_block']='43_TABS_GEGEN_BACKEND_WAHRHEIT'
data['letzte_aktualisierung_utc']=datetime.now(timezone.utc).isoformat()
P.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'ok':True,'current_block':data['aktueller_block'],'confirmed':len(confirmed),'open':len(data.get('offen_unsicher',[]))},ensure_ascii=False,indent=2))
