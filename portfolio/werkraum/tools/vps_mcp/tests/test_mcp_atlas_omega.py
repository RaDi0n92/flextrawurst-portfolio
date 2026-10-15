import base64
import os
import shutil
import sqlite3
import tempfile
import time
import unittest
from unittest import mock
from pathlib import Path

import mcp_atlas_omega as omega


class OmegaCoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix='omega-test-'))
        self.root = self.tmp / 'root'
        self.root.mkdir()
        self.db = self.tmp / 'omega.sqlite'
        self.big = self.root / 'big.txt'
        self.marker = 'OMEGA_MARKER_BEYOND_49152'
        self.big.write_text('A' * 70000 + '\n' + self.marker + '\n' + 'B' * 9000, encoding='utf-8')
        self.log = self.root / 'events.jsonl'
        self.log.write_text('{"n":1,"marker":"OLD_REWRITE_MARKER"}\n', encoding='utf-8')
        self.copy = self.root / 'big-copy.txt'
        shutil.copyfile(self.big, self.copy)
        self.hard = self.root / 'big-hard.txt'
        os.link(self.big, self.hard)
        self.mention = self.root / 'mention.md'
        self.mention.write_text(f'Siehe exakt {self.big}\n', encoding='utf-8')
        self.symlink = self.root / 'big-link.txt'
        self.symlink.symlink_to(self.big.name)
        self.broken = self.root / 'broken.txt'
        self.broken.symlink_to('missing-target.txt')
        self.binary_payload = (b'PK\x03\x04\x00\xffOMEGA_BINARY\x00' * 4096) + b'BINARY_END'
        self.binary_a = self.root / 'capsule-a.zip'
        self.binary_b = self.root / 'capsule-b.zip'
        self.binary_a.write_bytes(self.binary_payload)
        self.binary_b.write_bytes(self.binary_payload)
        self.opaque_payload = (b'\x00OMEGA_EXTENSIONLESS\xfe' * 2048) + b'OPAQUE_END'
        self.opaque = self.root / 'opaque_body'
        self.opaque_copy = self.root / 'opaque-copy.data'
        self.opaque.write_bytes(self.opaque_payload)
        self.opaque_copy.write_bytes(self.opaque_payload)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def sync(self):
        return omega.sync_roots([self.root], db_path=self.db, root_names=['test'], chunk_bytes=16384)

    def test_full_core_lifecycle(self):
        first = self.sync()
        self.assertTrue(first['ok'])
        self.assertGreaterEqual(first['stats']['versions_created'], 4)
        health = omega.health(db_path=self.db)
        self.assertTrue(health['ok'], health)

        hit = omega.search_full(self.marker, db_path=self.db, limit=20)
        self.assertTrue(any(r['path'] in {str(self.big), str(self.hard)} and r['start_byte'] > 49152 for r in hit['results']), hit)
        expected_marker_byte = self.big.read_bytes().find(self.marker.encode('utf-8'))
        self.assertGreater(expected_marker_byte, 49152)
        self.assertTrue(any(r['first_match_byte'] == expected_marker_byte for r in hit['results']), hit)

        big_obj = omega.object_view(str(self.big), db_path=self.db)
        hard_obj = omega.object_view(str(self.hard), db_path=self.db)
        copy_obj = omega.object_view(str(self.copy), db_path=self.db)
        self.assertEqual(big_obj['object']['object_id'], hard_obj['object']['object_id'])
        self.assertNotEqual(big_obj['object']['object_id'], copy_obj['object']['object_id'])
        self.assertTrue(any(e['edge_type'] == 'SAME_CONTENT' and e['dst_object_id'] == copy_obj['object']['object_id'] for e in big_obj['edges_out']))

        mention_obj = omega.object_view(str(self.mention), db_path=self.db)
        self.assertTrue(any(e['edge_type'] == 'PATH_MENTIONS' and e['dst_object_id'] == big_obj['object']['object_id'] for e in mention_obj['edges_out']))
        self.assertTrue(any(e['edge_type'] == 'SYMLINK_TARGET' for e in omega.object_view(str(self.symlink), db_path=self.db)['edges_out']))

        binary_a_obj = omega.object_view(str(self.binary_a), db_path=self.db)
        binary_b_obj = omega.object_view(str(self.binary_b), db_path=self.db)
        self.assertNotEqual(binary_a_obj['object']['object_id'], binary_b_obj['object']['object_id'])
        self.assertIsNotNone(binary_a_obj['object']['current_version_id'])
        self.assertTrue(any(e['edge_type'] == 'SAME_CONTENT' and e['dst_object_id'] == binary_b_obj['object']['object_id'] for e in binary_a_obj['edges_out']))
        binary_original = omega.read_original(str(self.binary_a), db_path=self.db, max_bytes=len(self.binary_payload))
        self.assertEqual(base64.b64decode(binary_original['raw_base64']), self.binary_payload)
        self.assertEqual(binary_original['file_sha256'], omega.sha256_bytes(self.binary_payload))

        opaque_obj = omega.object_view(str(self.opaque), db_path=self.db)
        opaque_copy_obj = omega.object_view(str(self.opaque_copy), db_path=self.db)
        self.assertIsNotNone(opaque_obj['object']['current_version_id'])
        self.assertTrue(any(e['edge_type'] == 'SAME_CONTENT' and e['dst_object_id'] == opaque_copy_obj['object']['object_id'] for e in opaque_obj['edges_out']))
        opaque_original = omega.read_original(str(self.opaque), db_path=self.db, max_bytes=len(self.opaque_payload))
        self.assertEqual(base64.b64decode(opaque_original['raw_base64']), self.opaque_payload)

        page1 = omega.read_original(str(self.big), db_path=self.db, start_byte=65000, max_bytes=10000)
        self.assertIn(self.marker, page1['text'])
        self.assertTrue(page1['has_more'])
        self.assertEqual(page1['returned_bytes'], 10000)

        old_obj_id = big_obj['object']['object_id']
        moved = self.root / 'moved.txt'
        self.big.rename(moved)
        second = self.sync()
        self.assertTrue(second['ok'])
        moved_obj = omega.object_view(str(moved), db_path=self.db)
        self.assertEqual(old_obj_id, moved_obj['object']['object_id'])
        self.assertTrue(any(p['path'] == str(self.big) and p['exists_flag'] == 0 for p in moved_obj['paths']))

        with self.log.open('a', encoding='utf-8') as f:
            f.write('{"n":2,"marker":"APPEND_MARKER_OMEGA"}\n')
        third = self.sync()
        self.assertEqual(third['stats']['versions_appended'], 1, third)
        log_timeline = omega.timeline(str(self.log), db_path=self.db)
        self.assertEqual(len(log_timeline['versions']), 2)
        self.assertEqual(log_timeline['versions'][0]['change_kind'], 'APPEND')
        self.assertTrue(omega.search_full('APPEND_MARKER_OMEGA', db_path=self.db)['results'])

        before = self.copy.stat()
        payload = self.copy.read_bytes()
        changed = bytearray(payload)
        mid = len(changed) // 2
        changed[mid:mid+16] = b'CHANGED_MIDDLE!!'
        changed = bytes(changed[:len(payload)])
        self.copy.write_bytes(changed)
        os.utime(self.copy, ns=(before.st_atime_ns, before.st_mtime_ns))
        fourth = self.sync()
        self.assertGreaterEqual(fourth['stats']['versions_rewritten'], 1, fourth)
        copy_timeline = omega.timeline(str(self.copy), db_path=self.db)
        self.assertEqual(len(copy_timeline['versions']), 2)
        self.assertEqual(copy_timeline['versions'][0]['change_kind'], 'REWRITE')

        hist = omega.read_original(str(self.copy), db_path=self.db, version_id=copy_timeline['versions'][1]['version_id'], start_byte=mid-20, max_bytes=80)
        current = omega.read_original(str(self.copy), db_path=self.db, start_byte=mid-20, max_bytes=80)
        self.assertNotEqual(hist['range_sha256'], current['range_sha256'])

    def test_historic_search_and_integrity(self):
        self.sync()
        self.log.write_text('REWRITE_ONLY_MARKER\n', encoding='utf-8')
        self.sync()
        current = omega.search_full('REWRITE_ONLY_MARKER', db_path=self.db)
        self.assertTrue(current['results'])
        old = omega.search_full('OLD_REWRITE_MARKER', db_path=self.db, include_historic=True)
        self.assertTrue(old['results'])
        with sqlite3.connect(self.db) as con:
            self.assertEqual(con.execute('pragma integrity_check').fetchone()[0], 'ok')

    def test_source_change_during_scan_rolls_back_partial_version(self):
        race_root = self.tmp / 'race-root'
        race_root.mkdir()
        race_db = self.tmp / 'race.sqlite'
        race_file = race_root / 'race.jsonl'
        race_file.write_text('R' * 120000 + '\nRACE_ORIGINAL\n', encoding='utf-8')
        original_chunk_file = omega._chunk_file
        changed = {'done': False}

        def mutating_chunk_file(path, *, chunk_bytes, start_byte=0):
            for item in original_chunk_file(path, chunk_bytes=chunk_bytes, start_byte=start_byte):
                yield item
                if Path(path) == race_file and not changed['done']:
                    with race_file.open('ab') as f:
                        f.write(b'RACE_MUTATION_DURING_SCAN\n')
                        f.flush()
                        os.fsync(f.fileno())
                    changed['done'] = True

        with mock.patch.object(omega, '_chunk_file', mutating_chunk_file):
            result = omega.sync_roots([race_root], db_path=race_db, root_names=['race'], chunk_bytes=16384)
        self.assertTrue(result['ok'])
        self.assertEqual(result['stats']['source_changed_during_scan'], 1, result)
        self.assertEqual(result['stats']['errors'], 1, result)
        with sqlite3.connect(race_db) as con:
            self.assertEqual(con.execute('SELECT count(*) FROM versions').fetchone()[0], 0)
            self.assertEqual(con.execute('SELECT count(*) FROM version_chunks').fetchone()[0], 0)
            self.assertEqual(con.execute('SELECT count(*) FROM chunk_blobs').fetchone()[0], 0)
            self.assertIsNone(con.execute("SELECT current_version_id FROM objects WHERE current_primary_path=?", (str(race_file),)).fetchone()[0])
            event = con.execute("SELECT details_json FROM events WHERE event_type='INDEX_ERROR' AND path=?", (str(race_file),)).fetchone()
            self.assertIsNotNone(event)
            self.assertIn('SOURCE_CHANGED_DURING_SCAN', event[0])

        stable = omega.sync_roots([race_root], db_path=race_db, root_names=['race'], chunk_bytes=16384)
        self.assertEqual(stable['stats']['errors'], 0, stable)
        self.assertEqual(stable['stats']['versions_created'], 1, stable)
        self.assertTrue(omega.search_full('RACE_MUTATION_DURING_SCAN', db_path=race_db)['results'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
