#!/usr/bin/env python3
import hashlib
import importlib.util
import json
import tempfile
from pathlib import Path

MOD_PATH = '/root/werkraum/welt/reibung_bruecke.py'
spec = importlib.util.spec_from_file_location('reibung_bruecke_under_test', MOD_PATH)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class FakeCursor:
    def __init__(self):
        self.nodes = {}  # code -> id
        self.events = []
        self.event_sources = set()  # (source_file, source_line_hash)
        self._one = None
        self._next_id = 1

    def execute(self, query, params=()):
        q = ' '.join(str(query).split())
        if q.startswith("SELECT id FROM reibungsknoten WHERE meta->>'kurzcode' = %s"):
            code = params[0]
            self._one = (self.nodes[code],) if code in self.nodes else None
        elif q.startswith("SELECT id FROM reibungsevents WHERE meta->>'source_file' = %s"):
            key = (params[0], params[1])
            self._one = (1,) if key in self.event_sources else None
        elif q.startswith('INSERT INTO reibungsknoten'):
            meta = json.loads(params[3]) if isinstance(params[3], str) else params[3]
            code = meta['kurzcode']
            self.nodes[code] = self._next_id
            self._next_id += 1
            self._one = None
        elif q.startswith('INSERT INTO reibungsevents'):
            meta = params[4]
            if hasattr(meta, 'adapted'):
                meta = meta.adapted
            self.events.append(tuple(params[:4]))
            self.event_sources.add((meta['source_file'], meta['source_line_hash']))
            self._one = None
        elif q.startswith("UPDATE reibungsknoten SET zustand = 'geschlossen'"):
            self._one = None
        else:
            raise AssertionError(f'Unerwartetes SQL: {q}')

    def fetchone(self):
        return self._one

text = 'Race-Test: Knoten kommt alphabetisch nach seiner Reaktion.'
code = m.kurzcode(text)
reaction_line = f'REIBUNG-REAKTION({code}): frage Ist der Knoten jetzt da?'
node_line = f'REIBUNG: {text}'
reaction_hash = hashlib.sha256(reaction_line.encode('utf-8')).hexdigest()
node_hash = hashlib.sha256(node_line.encode('utf-8')).hexdigest()

with tempfile.TemporaryDirectory(prefix='reibung_ordering_') as td:
    root = Path(td)
    # Alphabetisch wird claude vor gemini gescannt: Reaktion zuerst, Knoten danach.
    (root / '2026-09-17_claude_an_gemini.md').write_text(reaction_line + '\n', encoding='utf-8')
    (root / '2026-09-17_gemini_an_claude.md').write_text(node_line + '\n', encoding='utf-8')
    m.BRIEFKASTEN_DIR = root
    m.INDEX_DATEI = root / 'reibungsgewebe_index.md'

    cur = FakeCursor()
    state = {'verarbeitete_zeilen': {}}

    changed1 = m.verarbeite_briefe(cur, state)
    first_reaction_state = state['verarbeitete_zeilen']['2026-09-17_claude_an_gemini.md']
    first_node_state = state['verarbeitete_zeilen']['2026-09-17_gemini_an_claude.md']
    assert code in cur.nodes
    assert len(cur.events) == 0
    assert reaction_hash not in first_reaction_state, first_reaction_state
    assert node_hash in first_node_state, first_node_state
    assert changed1 is True  # Knoten wurde erzeugt.

    changed2 = m.verarbeite_briefe(cur, state)
    assert len(cur.events) == 1, cur.events
    assert reaction_hash in state['verarbeitete_zeilen']['2026-09-17_claude_an_gemini.md']
    assert changed2 is True

    changed3 = m.verarbeite_briefe(cur, state)
    assert len(cur.events) == 1, 'Dritter Lauf darf kein Duplikat erzeugen'
    assert changed3 is False

    # Simulierter Totalverlust/Korruption des Dateistates NACH DB-Commit:
    # Der DB-Herkunftsschluessel muss das Event trotzdem idempotent halten und
    # den verlorenen Dateistate wieder aufbauen.
    lost_state = {'verarbeitete_zeilen': {}}
    changed_after_state_loss = m.verarbeite_briefe(cur, lost_state)
    assert len(cur.events) == 1, 'State-Verlust darf DB-Event nicht duplizieren'
    assert reaction_hash in lost_state['verarbeitete_zeilen']['2026-09-17_claude_an_gemini.md']
    assert node_hash in lost_state['verarbeitete_zeilen']['2026-09-17_gemini_an_claude.md']
    assert changed_after_state_loss is False

    # Atomarer State-Write: Ziel existiert vollständig, temporäre Datei bleibt
    # nach erfolgreichem os.replace nicht liegen.
    m.STATE_DATEI = root / '.state.json'
    m.speichere_state(lost_state)
    reloaded = json.loads(m.STATE_DATEI.read_text(encoding='utf-8'))
    assert reloaded == lost_state
    assert not (root / '.state.json.tmp').exists()

print(json.dumps({
    'ok': True,
    'scenario': 'reaction_file_sorted_before_node_file',
    'code': code,
    'first_cycle': {'node_created': True, 'reaction_deferred_and_unhashed': True},
    'second_cycle': {'reaction_inserted_once': True, 'reaction_hash_persisted': True},
    'third_cycle': {'duplicate_event': False, 'changed': False},
    'simulated_state_loss_after_db_commit': {'duplicate_event': False, 'state_rebuilt': True},
    'atomic_state_replace': True
}, ensure_ascii=False, indent=2))
