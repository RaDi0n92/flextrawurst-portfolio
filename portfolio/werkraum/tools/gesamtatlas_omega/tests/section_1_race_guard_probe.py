#!/usr/bin/env python3
from __future__ import annotations
import json
import os
import sqlite3
import tempfile
from pathlib import Path

import sys
sys.path.insert(0, '/root/werkraum/tools/vps_mcp')
import mcp_atlas_omega as omega

RUNTIME=Path('/root/werkraum/_gpt/gesamtatlas/omega/runtime')


def main() -> dict:
    with tempfile.TemporaryDirectory(prefix='race-guard-', dir=RUNTIME) as td:
        root=Path(td)
        source=root/'race_target.txt'
        db=root/'race.sqlite'
        chunk=65536
        payload=(b'A' * chunk) + (b'B' * chunk) + (b'C' * chunk) + b'OMEGA_RACE_END\n'
        source.write_bytes(payload)
        before=source.stat()
        original_chunk_file=omega._chunk_file
        mutation={'performed':False,'mtime_restored':False}

        def controlled_chunk_file(path:Path, *, chunk_bytes:int, start_byte:int=0):
            for index, item in enumerate(original_chunk_file(path, chunk_bytes=chunk_bytes, start_byte=start_byte)):
                yield item
                if index == 0 and not mutation['performed']:
                    current=bytearray(source.read_bytes())
                    current[chunk+128:chunk+160]=b'RACE_MUTATION_DURING_SCAN_123456'
                    current=current[:len(payload)]
                    source.write_bytes(bytes(current))
                    os.utime(source, ns=(before.st_atime_ns,before.st_mtime_ns))
                    mutation['performed']=True
                    mutation['mtime_restored']=source.stat().st_mtime_ns==before.st_mtime_ns

        omega._chunk_file=controlled_chunk_file
        try:
            scan=omega.sync_roots([source],db_path=db,root_names=['race-guard'],chunk_bytes=chunk,include_suffixes={'.txt'},force=True)
        finally:
            omega._chunk_file=original_chunk_file

        con=sqlite3.connect(db);con.row_factory=sqlite3.Row
        try:
            versions=con.execute('select version_id,complete,size,file_sha256 from versions').fetchall()
            events=con.execute('select event_type,details_json from events order by occurred_utc').fetchall()
            blobs=con.execute('select count(*) n from chunk_blobs').fetchone()['n']
            links=con.execute('select count(*) n from version_chunks').fetchone()['n']
        finally:
            con.close()
        event_types=[r['event_type'] for r in events]
        race_event_visible=any(
            r['event_type']=='SOURCE_CHANGED_DURING_SCAN'
            or 'SOURCE_CHANGED_DURING_SCAN' in str(r['details_json'])
            for r in events
        )
        guarded=(
            scan['stats'].get('source_changed_during_scan',0)>=1
            and not versions
            and race_event_visible
            and links==0
            and blobs==0
        )
        result={
            'schema_version':'1.0',
            'ok':guarded,
            'mutation':mutation,
            'before':{'size':before.st_size,'mtime_ns':before.st_mtime_ns,'ctime_ns':before.st_ctime_ns},
            'after':{'size':source.stat().st_size,'mtime_ns':source.stat().st_mtime_ns,'ctime_ns':source.stat().st_ctime_ns},
            'scan':scan,
            'version_count':len(versions),
            'versions':[dict(r) for r in versions],
            'event_types':event_types,
            'race_event_visible':race_event_visible,
            'events':[{'event_type':r['event_type'],'details':json.loads(r['details_json'])} for r in events],
            'chunk_blob_count':blobs,
            'version_chunk_link_count':links,
            'expected':'No complete version may survive a source mutation during the scan; a SOURCE_CHANGED_DURING_SCAN event must remain visible.',
        }
        print(json.dumps(result,ensure_ascii=False))
        return result

if __name__=='__main__':
    main()
