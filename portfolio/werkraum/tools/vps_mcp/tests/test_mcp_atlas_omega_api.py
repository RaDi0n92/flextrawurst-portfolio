from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import mcp_atlas_omega as omega
import mcp_atlas_omega_api as api


class OmegaMCPReadAPITest(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.source = self.root / 'source'
        self.source.mkdir()
        self.db = self.root / 'omega.sqlite'
        self.marker = 'OMEGA_MCP_EXACT_MARKER'
        self.file = self.source / 'large.txt'
        self.file.write_text('A' * 70000 + '\n' + self.marker + '\nTAIL', encoding='utf-8')
        omega.sync_roots([self.source], db_path=self.db, root_names=['test'], chunk_bytes=16384)

        core_path = Path(omega.__file__).resolve()
        core_sha = api._sha256_file(core_path)
        self.core_ready = self.root / 'CORE_READY.json'
        self.core_ready.write_text(json.dumps({
            'checkpoint_id': 'CORE_READY',
            'status': 'PASS',
            'core': {'sha256': core_sha},
        }), encoding='utf-8')
        core_ready_sha = api._sha256_file(self.core_ready)
        self.monsterlab = self.root / 'MONSTERLABOR_DYNAMIC_READY.json'
        self.monsterlab.write_text(json.dumps({
            'checkpoint_id': 'MONSTERLABOR_DYNAMIC_READY',
            'status': 'PASS',
            'core': {'sha256': core_sha},
            'core_ready': {'sha256': core_ready_sha},
        }), encoding='utf-8')
        self.env = mock.patch.dict(os.environ, {
            'GESAMTATLAS_OMEGA_DB': str(self.db),
            'GESAMTATLAS_OMEGA_CORE_READY': str(self.core_ready),
            'GESAMTATLAS_OMEGA_MONSTERLAB_READY': str(self.monsterlab),
        })
        self.env.start()

    def tearDown(self) -> None:
        self.env.stop()
        self.tempdir.cleanup()

    def test_read_only_api_lifecycle(self) -> None:
        health = api.health({})
        self.assertTrue(health['ok'])
        self.assertEqual(health['omega_contract']['scope'], 'OMEGA_READ_ONLY_MCP')
        self.assertTrue(health['omega_contract']['read_only'])

        search = api.search({'query': self.marker, 'limit': 20})
        self.assertEqual(search['result_count'], 1)
        hit = search['results'][0]
        expected_offset = self.file.read_bytes().find(self.marker.encode('utf-8'))
        self.assertEqual(hit['first_match_byte'], expected_offset)
        self.assertEqual(hit['path'], str(self.file))

        obj = api.object_view({'path_or_object': str(self.file)})
        self.assertEqual(obj['object']['object_id'], hit['object_id'])
        self.assertEqual(len(obj['versions']), 1)

        original = api.read_original({
            'path_or_object': hit['object_id'],
            'start_byte': expected_offset,
            'max_bytes': len(self.marker.encode('utf-8')),
        })
        self.assertEqual(original['text'], self.marker)
        self.assertEqual(original['start_byte'], expected_offset)
        self.assertEqual(original['returned_bytes'], len(self.marker.encode('utf-8')))

        timeline = api.timeline({'path_or_object': hit['object_id']})
        self.assertEqual(timeline['object_id'], hit['object_id'])
        self.assertEqual(len(timeline['versions']), 1)
        self.assertTrue(timeline['events'])

    def test_gate_rejects_hash_mismatch_and_empty_queries(self) -> None:
        with self.assertRaises(api.OmegaAPIError):
            api.search({'query': ''})
        broken = json.loads(self.monsterlab.read_text(encoding='utf-8'))
        broken['core']['sha256'] = '0' * 64
        self.monsterlab.write_text(json.dumps(broken), encoding='utf-8')
        with self.assertRaises(api.OmegaAPIError):
            api.health({})


if __name__ == '__main__':
    unittest.main(verbosity=2)
