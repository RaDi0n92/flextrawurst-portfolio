from pathlib import Path
import json, copy
R=Path('/root/werkraum/gemgems-spielbeobachtung/2026-09-04_MOELLENKOTTEN_FORSCHUNG')
# Upgrade existing positive workflow records to schema v3.
p=R/'fixtures/workflow_valid.json'; data=json.loads(p.read_text(encoding='utf-8'))
for x in data['records']: x['record']['schema_version']=3
p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
# Upgrade and extend schema-negative cases.
p=R/'fixtures/schema_invalid_cases.json'; inv=json.loads(p.read_text(encoding='utf-8'))
for c in inv['cases']:
    if isinstance(c.get('record'),dict) and 'schema_version' in c['record']: c['record']['schema_version']=3
# Replace old S01 snapshot namespace in the snapshot-without-hash case with the real folder so it fails for the intended pairing reason.
for c in inv['cases']:
    if c['name']=='snapshot_without_hash': c['record']['snapshot_path']='sessions/01_STRASSEN_UND_GEWEGE/snapshots/a.bin'
# Add explicit medium-case negatives.
base_boundary=next(x['record'] for x in data['records'] if x['kind']=='boundary_event')
bad=copy.deepcopy(base_boundary)
bad['control_points'][0]['geometry']={'geometry_type':'LINESTRING','crs':'EPSG:4326','coordinates':[[7.29,51.284],[7.291,51.285]],'accuracy_m':2.0,'location_method':'Fixture'}
inv['cases'].append({'name':'control_point_not_point','kind':'boundary_event','record':bad})
base_find=next(x['record'] for x in data['records'] if x['kind']=='finding_event' and x['record'].get('merge_status')=='LOKAL')
bad=copy.deepcopy(base_find); bad['geometry']['crs']='EPSG:25832'
inv['cases'].append({'name':'non_wgs84_crs','kind':'finding_event','record':bad})
bad=copy.deepcopy(next(x['record'] for x in data['records'] if x['kind']=='finding_event' and x['record'].get('merge_status')=='KANONISCH')); bad['origin_event_ids']=[]
inv['cases'].append({'name':'canonical_finding_without_origin','kind':'finding_event','record':bad})
p.write_text(json.dumps(inv,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
# Positive calibrated state fixture.
cal={'schema_version':3,'version':2,'status':'KALIBRIERT','source_crs':'EPSG:4326','anchor_label':'Fixture-Anker','origin_coordinates':[7.293,51.286],'origin_elevation_m':215.4,'transformation_method':'Lokales Tangentialmodell Fixture','calibrated_at':'2026-09-05T00:05:00Z','source_ids':['QUELLE-MOELLENKOTTEN-KANON-000001'],'godot_axes':{'x':'lokale Ostrichtung in Metern','y':'Höhe in Metern relativ zum Ursprung','z':'negative lokale Nordrichtung in Metern'},'notes':'Nur Fixture'}
(R/'fixtures/calibration_valid.json').write_text(json.dumps(cal,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('fixture_records',len(data['records']),'invalid_cases',len(inv['cases']))
