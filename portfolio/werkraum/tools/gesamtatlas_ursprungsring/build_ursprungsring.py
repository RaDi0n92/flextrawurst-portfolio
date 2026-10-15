from __future__ import annotations

import datetime as dt
import hashlib
import html
import json
import os
import re
import sqlite3
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(os.environ.get('URS_RING_ROOT', '/root/werkraum/_gpt/gesamtatlas/ursprungsring'))
SOURCE_B = ROOT / 'originalzeugen/VOR_VPS_PRIMAERZEUGE_B_EXAKT.txt'
SOURCE_A = ROOT / 'originalzeugen/ZEUGE_A_ERGAENZUNG_ORIGINALZEILEN_388_636.txt'
STREAMS = ('claude', 'claudeweb', 'chatgpt', 'codex', 'gemini', 'kimi', 'glm')

WITNESSES = [
    {
        'witness_id': 'ZEUGE_A_GESPRAECHSFASSUNG',
        'original_filename': 'Eingefügter Text(136).txt',
        'bytes': 95518,
        'lines': 2664,
        'sha256': '74ab42c0752dcab452b3593f6b44b5b24c83ddc67b41d5adb1f7bf48a5d540b1',
        'role': 'reduzierte Gesprächsfassung; beginnt später; besitzt einzigartige fehlende Passagen',
        'materialization': 'FULL_ORIGINAL_IN_CHAT_SOURCE; UNIQUE_PRE_VPS_EXCERPT_ON_VPS',
        'vps_excerpt_path': str(SOURCE_A),
        'vps_excerpt_original_lines': '388-636',
        'vps_excerpt_sha256': 'b3068bd89dda56d03aaed196e2a440c149c80fc7caa7a72ade758814f4f6dd83',
    },
    {
        'witness_id': 'ZEUGE_B_SICHTVERLAUF_MIT_ARBEIT',
        'original_filename': 'Eingefügter Text (2)(9).txt',
        'bytes': 181964,
        'lines': 4883,
        'sha256': '4a9f57921cf1174f970ddeba85dc152c3a2f17997ec4cb67e089b60b9c051cf3',
        'role': 'frühester und deutlich vollständigerer Sichtverlauf; enthält sichtbare Arbeit und belegte Exportduplikate',
        'materialization': 'FULL_ORIGINAL_IN_CHAT_SOURCE; EXACT_PRE_VPS_PRIMARY_BODY_ON_VPS',
        'vps_primary_path': str(SOURCE_B),
        'vps_primary_original_lines': '1-2536',
        'vps_primary_bytes': 75196,
        'vps_primary_sha256': 'e6301a898639b4568d13c5214387a3f945107d8c9159221462960312723a5e10',
    },
]

TRUTHS = [
    ('U01', 'Zweck vor Bestand', 'Der Gesamtatlas wurde als Karte über Karten und Beziehungen gedacht, bevor VPS-Bestände gelesen wurden.', 'B:22-79', 'ORIGINAL_DANIEL_PLUS_EARLY_RESPONSE'),
    ('U02', 'Nicht bloß Dateien', 'Er soll Herkunft, Veränderung, Zusammenarbeit, Widerspruch und Übergänge sichtbar machen, nicht nur Pfade aufzählen.', 'B:26-79', 'DIRECT_EARLY_FORMULATION'),
    ('U03', 'Getrennte AI-Ströme', 'AI-Ströme bleiben eigenständige Reisende und Herkunftskörper; Verbindung bedeutet keine Verschmelzung.', 'B:63-79', 'DIRECT_EARLY_FORMULATION'),
    ('U04', 'Originale vor Nacherzählung', 'Neue Texte dürfen Originale erläutern, aber niemals ersetzen oder als ursprünglicher Wortlaut auftreten.', 'A:388-636', 'UNIQUE_WITNESS_A'),
    ('U05', 'Original, Ableitung, Reaktion', 'Tatsächlicher Wortlaut, modellierte Erkenntnis und mögliche Folgehandlung müssen sichtbar und maschinell getrennt bleiben.', 'A:573-596', 'UNIQUE_WITNESS_A'),
    ('U06', 'Mehrere Tiefen', 'Kinderansicht, normale Ansicht und Tiefenansicht zeigen denselben Gegenstand mit unterschiedlicher Detailtiefe.', 'A:430-452', 'UNIQUE_WITNESS_A'),
    ('U07', 'Einladung statt Regelkoffer', 'Technische Grenzen gehören in den Maschinenkeller; der erfahrbare Atlas soll als offener Erkenntnisraum einladen.', 'B:1304-1660; A:642-990', 'REPEATED_OR_COMPLEMENTARY'),
    ('U08', 'Selbstständiges Verstehen', 'Der Atlas soll zeigen, was geschah und wo Spuren auseinandergehen, ohne die Bedeutung vorab zu domestizieren.', 'B:1600-1660', 'DIRECT_EARLY_FORMULATION'),
    ('U09', 'Browser und Terminal verbinden', 'Browsergespräche, Terminalarbeit, Dateien, Prüfungen und spätere Korrekturen sollen eine durchgehende Provenienzkette bilden.', 'B:2008-2527', 'DIRECT_EARLY_FORMULATION'),
    ('U10', 'Sichtbare Arbeit, keine erfundenen Innenwelten', 'Bewahrbar sind sichtbare Texte, Begründungen, Werkzeuge und Wirkungen; unsichtbares inneres Denken darf nicht behauptet werden.', 'B:2501-2518', 'DIRECT_EPISTEMIC_BOUNDARY'),
    ('U11', 'Das Gebaute ist eine Entwicklung', 'Der heutige Atlas ist eine Realisierung aus dem Ursprung, nicht automatisch dessen einzig richtige endgültige Bedeutung.', 'B:2531-2536', 'INFERENCE_FROM_EXPLICIT_PRE_IMPLEMENTATION_BOUNDARY'),
    ('U12', 'Ursprung als Gegenstimme', 'Der Vor-VPS-Ring bleibt dauerhafte Prüfinstanz gegen Bestandsdrift, unnötige Verregelung und rückwirkende Selbstlegenden.', 'B:1-2536; A:388-636', 'MODELLED_REACTION_BOUND_TO_SOURCES'),
]

DRIFT = [
    ('D01', 'Getrennte AI-Ströme', 'FULFILLED', 'Sieben Stromhäuser und getrennte Mitschriften existieren.'),
    ('D02', 'Gemeinsame Suche', 'FULFILLED', 'Atlas-Volltext, spezialisierte Suchorgane und manueller Eingang existieren.'),
    ('D03', 'Originaltreue', 'PARTIAL', 'Original- und Hashkörper existieren, aber nicht jeder alte UI-Verlauf ist vollständig materialisiert.'),
    ('D04', 'Einladende Oberfläche', 'PARTIAL', 'Es gibt sichtbare Seiten; technische Verträge sind weiterhin deutlich stärker als die ursprüngliche Eingangsatmosphäre.'),
    ('D05', 'Keine Bestandsdrift', 'CORRECTED', 'Zensi wurde durch All-Roots-Scanning aufgenommen und später als föderierter Außenbestand neu klassifiziert.'),
    ('D06', 'Keine Regelkoffer-Dominanz', 'OPEN_TENSION', 'Claims, Verträge und Hashketten schützen Wahrheit, dürfen aber nicht zum eigentlichen Erlebnis des Atlas werden.'),
    ('D07', 'Drei Darstellungstiefen', 'OPEN', 'Die frühe Kinder-/Normal-/Tiefenarchitektur ist noch nicht atlasweit konsistent umgesetzt.'),
    ('D08', 'Sieben unabhängige Ursprungslesungen', 'READY_NOT_COMPLETED', 'Getrennte Lesepfade sind vorbereitet; ihre echten Antworten werden erst nach realer Lektüre gespeichert.'),
]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=f'.{path.name}.', dir=path.parent)
    temp = Path(name)
    try:
        with os.fdopen(fd, 'wb') as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp, path)
    except Exception:
        temp.unlink(missing_ok=True)
        raise


def write_json(path: Path, obj: Any) -> None:
    atomic_write(path, (json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True) + '\n').encode())


def blocks(lines: list[str]) -> list[tuple[int, int, str]]:
    result: list[tuple[int, int, str]] = []
    start = None
    buf: list[str] = []
    def flush(end_line: int) -> None:
        nonlocal start, buf
        if start is not None:
            result.append((start, end_line, '\n'.join(buf)))
            start, buf = None, []
    for number, line in enumerate(lines, 1):
        stripped = line.strip()
        if re.fullmatch(r'\d+(?:m \d+)?s nachgedacht', stripped):
            flush(number - 1)
            result.append((number, number, line))
            continue
        if stripped:
            if start is None:
                start = number
            buf.append(line)
        else:
            flush(number - 1)
    flush(len(lines))
    return result


def classify(items: list[tuple[int, int, str]]) -> list[dict[str, Any]]:
    result = []
    visible_user_lines = {22, 2535}
    gap_marker_lines = {543, 784, 863, 2002}
    duplicate_marker_lines = {41}
    for idx, (start, end, text) in enumerate(items):
        stripped = text.strip()
        if start in visible_user_lines:
            kind, speaker, status = 'DANIEL_NACHRICHT', 'daniel', 'DIRECT_PRIMARY_WITNESS'
        elif re.fullmatch(r'\d+(?:m \d+)?s nachgedacht', stripped):
            if start in gap_marker_lines:
                kind, speaker, status = 'LUECKE_BELEGT', 'unknown_missing_user', 'MISSING_USER_TURN_IN_VISIBLE_EXPORT'
            elif start in duplicate_marker_lines:
                kind, speaker, status = 'DUPLIKAT_IM_EXPORT', 'assistant_system', 'VISIBLE_EXPORT_DUPLICATION'
            else:
                kind, speaker, status = 'SICHTBARER_ARBEITSMARKER', 'assistant_system', 'DIRECT_PRIMARY_WITNESS'
        elif re.fullmatch(r'_+', stripped):
            kind, speaker, status = 'EXPORT_TRENNMARKER', 'export_ui', 'DIRECT_PRIMARY_WITNESS'
        elif re.match(r'^(Erklärte|Analysierte|Prüfte|Ordnete|Verglich|Erfasste|Überprüfte|Geplante|Aufgelistet)', stripped):
            kind, speaker, status = 'SICHTBARE_ARBEITSZUSAMMENFASSUNG', 'assistant_system', 'DIRECT_PRIMARY_WITNESS'
        elif start <= 20:
            kind, speaker, status = 'ASSISTENT_SETUP', 'assistant', 'DIRECT_PRIMARY_WITNESS'
        else:
            kind, speaker, status = 'ASSISTENT_ANTWORT', 'assistant', 'DIRECT_PRIMARY_WITNESS'
        result.append({
            'segment_id': f'VPS0-B-{idx + 1:04d}',
            'source_id': 'ZEUGE_B_SICHTVERLAUF_MIT_ARBEIT',
            'source_path': str(SOURCE_B),
            'source_lines': {'start': start, 'end': end},
            'speaker': speaker,
            'kind': kind,
            'text': text,
            'text_sha256': sha(text.encode()),
            'reconstruction_status': status,
        })
    return result


def source_html(title: str, lines: list[str], out: Path) -> None:
    rows = '\n'.join(
        f'<div class="line" id="L{i}"><a href="#L{i}" class="ln">{i}</a><span>{html.escape(line) or "&nbsp;"}</span></div>'
        for i, line in enumerate(lines, 1)
    )
    body = f'''<!doctype html><html lang="de"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)}</title>
<style>body{{margin:0;background:#0d0b16;color:#eee8ff;font:15px/1.55 ui-monospace,monospace}}header{{position:sticky;top:0;background:#181229;padding:14px 18px;border-bottom:1px solid #493c69}}main{{padding:12px 0 60px}}.line{{display:grid;grid-template-columns:72px minmax(0,1fr);padding:0 18px}}.line:target{{background:#33245a}}.ln{{color:#a995d8;text-align:right;padding-right:18px;text-decoration:none}}span{{white-space:pre-wrap;overflow-wrap:anywhere}}</style><header><a href="index.html">← Ursprungsring</a> · {html.escape(title)}</header><main>{rows}</main></html>'''
    atomic_write(out, body.encode())


def build() -> dict[str, Any]:
    if sha(SOURCE_B.read_bytes()) != WITNESSES[1]['vps_primary_sha256']:
        raise SystemExit('Primärzeuge B hat nicht den erwarteten Hash')
    if sha(SOURCE_A.read_bytes()) != WITNESSES[0]['vps_excerpt_sha256']:
        raise SystemExit('Zeuge-A-Ergänzung hat nicht den erwarteten Hash')
    lines_b = SOURCE_B.read_text('utf-8').splitlines()
    lines_a = SOURCE_A.read_text('utf-8').splitlines()
    if len(lines_b) != 2536:
        raise SystemExit(f'Unerwartete Primärzeilen: {len(lines_b)}')
    segments = classify(blocks(lines_b))
    generated = dt.datetime.now(dt.timezone.utc).isoformat()

    write_json(ROOT / 'ZEUGENREGISTER.json', {'schema_version': '1.0', 'generated_utc': generated, 'witnesses': WITNESSES, 'truth_boundary': 'Keiner der beiden Exporte ist allein der unfehlbare 1:1-Verlauf.'})
    atomic_write(ROOT / 'SEGMENTREGISTER.jsonl', ''.join(json.dumps(x, ensure_ascii=False, sort_keys=True) + '\n' for x in segments).encode())
    write_json(ROOT / 'URSPRUNGSWAHRHEITEN.json', {'schema_version': '1.0', 'generated_utc': generated, 'truths': [dict(id=i, title=t, statement=s, source_ref=r, evidence_class=c) for i,t,s,r,c in TRUTHS]})
    write_json(ROOT / 'DRIFTVERGLEICH.json', {'schema_version': '1.0', 'generated_utc': generated, 'comparisons': [dict(id=i, origin=t, status=s, current_finding=f) for i,t,s,f in DRIFT]})

    conn = sqlite3.connect(ROOT / 'REKONSTRUKTIONSREGISTER.sqlite')
    conn.executescript('''PRAGMA journal_mode=WAL; CREATE TABLE IF NOT EXISTS segments(segment_id TEXT PRIMARY KEY, source_id TEXT, start_line INTEGER, end_line INTEGER, speaker TEXT, kind TEXT, text TEXT, text_sha256 TEXT, reconstruction_status TEXT); DELETE FROM segments; CREATE INDEX IF NOT EXISTS idx_segments_kind ON segments(kind); CREATE INDEX IF NOT EXISTS idx_segments_speaker ON segments(speaker);''')
    conn.executemany('INSERT INTO segments VALUES(?,?,?,?,?,?,?,?,?)', [(x['segment_id'],x['source_id'],x['source_lines']['start'],x['source_lines']['end'],x['speaker'],x['kind'],x['text'],x['text_sha256'],x['reconstruction_status']) for x in segments])
    conn.commit(); conn.close()

    origin_md = ['# Vor-VPS-Ursprungsring', '', '> Der heutige Gesamtatlas darf seinen Ursprung nicht rückwirkend umschreiben.', '', 'Dieser Ring bewahrt die Phase, in der die Verbindung technisch bestand, aber der VPS ausdrücklich nicht durchsucht oder benutzt werden durfte. Der Zweck wurde zuerst aus Gespräch, Erinnerung und Vorstellung entwickelt.', '', '## Zwölf Ursprungswahrheiten', '']
    for i,t,s,r,c in TRUTHS:
        origin_md += [f'### {i} · {t}', '', s, '', f'- Quelle: `{r}`', f'- Evidenzklasse: `{c}`', '']
    origin_md += ['## Wahrheitsgrenze', '', 'Der Primärkörper endet unmittelbar vor dem späteren VPS-Eintritt. Er beschreibt eine konzeptionelle Architektur und keinen damals bereits gebauten Zustand.', '']
    atomic_write(ROOT / 'VOR_VPS_URSPRUNG.md', '\n'.join(origin_md).encode())

    drift_md = ['# Ursprung ↔ heutiger Atlas', '', '| Ursprung | Status | heutiger Befund |', '|---|---|---|']
    for _,t,s,f in DRIFT:
        drift_md.append(f'| {t} | `{s}` | {f} |')
    drift_md += ['', 'Das aktuell Gebaute ist weder automatisch Verrat noch automatisch Vollendung. Es ist eine überprüfbare Entwicklung aus dem Ursprung.', '']
    atomic_write(ROOT / 'DRIFTVERGLEICH.md', '\n'.join(drift_md).encode())

    stream_prompt = '''# Eigenständige Ursprungslektüre für {name}\n\nLies zuerst `../../VOR_VPS_URSPRUNG.md`, danach den Primärzeugen und die Zeuge-A-Ergänzung. Beschreibe anschließend eigenständig:\n\n1. Was wollte Daniel vor jeder VPS-Bestandssicht wirklich?\n2. Was davon erfüllt der heutige Atlas?\n3. Wo hat Technik den Ursprung erweitert, verengt oder verschoben?\n4. Welche offene Möglichkeit darf nicht verloren gehen?\n5. Welche deiner Aussagen sind Originalbeobachtung, Ableitung oder Reaktion?\n\nSchreibe die echte Lesung später in `LESUNG.md`. Übernimm keine fertige Lesart eines anderen Stroms.\n'''
    for stream in STREAMS:
        folder = ROOT / 'ai-stroeme' / stream
        folder.mkdir(parents=True, exist_ok=True)
        atomic_write(folder / 'START_HIER.md', stream_prompt.format(name=stream).encode())
        if not (folder / 'LESUNG.md').exists():
            atomic_write(folder / 'LESUNG.md', f'# {stream} · Ursprungslektüre\n\nStatus: `NOCH_NICHT_DURCHGEFUEHRT`\n'.encode())

    source_html('Primärzeuge B · Vor-VPS, Originalzeilen 1–2536', lines_b, ROOT / 'ui/source-b.html')
    source_html('Zeuge A · einzigartige Ergänzung, Originalzeilen 388–636', lines_a, ROOT / 'ui/source-a.html')

    truth_cards = ''.join(f'<article class="truth" data-search="{html.escape((t+" "+s).lower())}"><b>{i} · {html.escape(t)}</b><p>{html.escape(s)}</p><a href="source-{"a" if r.startswith("A:") else "b"}.html#L{re.search(r"\d+",r).group()}">Quelle {html.escape(r)}</a><small>{html.escape(c)}</small></article>' for i,t,s,r,c in TRUTHS)
    drift_rows = ''.join(f'<tr><td>{html.escape(t)}</td><td><code>{s}</code></td><td>{html.escape(f)}</td></tr>' for _,t,s,f in DRIFT)
    stream_cards = ''.join(f'<a class="stream" href="../ai-stroeme/{s}/START_HIER.md"><b>{s}</b><span>eigene Lesung, keine Verschmelzung</span></a>' for s in STREAMS)
    index = f'''<!doctype html><html lang="de"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Vor-VPS-Ursprungsring</title>
<style>:root{{--bg:#0d0b16;--panel:#171226;--line:#4a3d68;--text:#f2edff;--muted:#b8acd3;--accent:#c7a7ff}}*{{box-sizing:border-box}}body{{margin:0;background:radial-gradient(circle at 15% 0,#23163c,var(--bg) 38%);color:var(--text);font:16px/1.55 system-ui,sans-serif}}main{{max-width:1180px;margin:auto;padding:38px 20px 80px}}h1{{font-size:clamp(2rem,7vw,5rem);line-height:.95;margin:.2em 0}}.lead{{font-size:1.2rem;max-width:850px;color:var(--muted)}}nav,.grid,.streams{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:14px;margin:24px 0}}a{{color:var(--accent)}}.card,.truth,.stream,table{{background:#171226dd;border:1px solid var(--line);border-radius:16px;padding:18px}}.truth small,.stream span{{display:block;color:var(--muted);margin-top:10px}}a,small,code,td,th{{overflow-wrap:anywhere;word-break:break-word}}input{{width:100%;padding:14px;border-radius:12px;border:1px solid var(--line);background:#0c0913;color:var(--text);font:inherit}}table{{width:100%;max-width:100%;border-collapse:separate;border-spacing:0}}td,th{{text-align:left;padding:12px;border-bottom:1px solid #352c4c;vertical-align:top}}.triad{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}}@media(max-width:720px){{.triad{{grid-template-columns:1fr}}table{{display:block;overflow:auto}}}}.hidden{{display:none}}</style>
<main><p>GESAMTATLAS · URSPRUNGSRING</p><h1>Bevor der Bestand die Idee formte.</h1><p class="lead">Die Phase mit technischer Verbindung, aber ausdrücklichem Verbot jeder VPS-Suche. Kein Regelkoffer am Eingang: erst Originale, dann Ableitungen, dann mögliche Reaktionen.</p>
<nav><a class="card" href="source-b.html#L1">Primärzeuge B öffnen</a><a class="card" href="source-a.html#L1">Zeuge-A-Ergänzung öffnen</a><a class="card" href="../VOR_VPS_URSPRUNG.md">kopierbare Ursprungsfassung</a><a class="card" href="../DRIFTVERGLEICH.md">Driftvergleich</a></nav>
<section class="triad"><div class="card"><h2>Original</h2><p>Was tatsächlich sichtbar geschrieben wurde.</p></div><div class="card"><h2>Ableitung</h2><p>Was der Atlas darin erkennt.</p></div><div class="card"><h2>Reaktion</h2><p>Was daraus geprüft oder angestoßen werden könnte.</p></div></section>
<h2>Ursprungswahrheiten</h2><input id="q" aria-label="Ursprungswahrheiten durchsuchen" placeholder="z. B. Original, Einladung, Terminal …"><section id="truths" class="grid">{truth_cards}</section>
<h2>Ursprung ↔ heutiger Atlas</h2><table><thead><tr><th>Ursprung</th><th>Status</th><th>heutiger Befund</th></tr></thead><tbody>{drift_rows}</tbody></table>
<h2>Sieben eigenständige Lesepfade</h2><section class="streams">{stream_cards}</section>
<script>const q=document.querySelector('#q');q.addEventListener('input',()=>{{const n=q.value.toLowerCase();document.querySelectorAll('.truth').forEach(x=>x.classList.toggle('hidden',!x.dataset.search.includes(n)))}})</script></main></html>'''
    atomic_write(ROOT / 'ui/index.html', index.encode())

    start = '''# Gesamtatlas · Vor-VPS-Ursprungsring\n\n**Einladung:** Beginne mit `ui/index.html` oder `VOR_VPS_URSPRUNG.md`. Die Schutz- und Provenienztechnik liegt darunter, nicht als Hausordnung vor der Tür.\n\nDer Ring bewahrt den Zweck des Gesamtatlas, bevor der reale VPS-Bestand die Vorstellung beeinflusste. Originalzeugen, Rekonstruktion, Ableitungen und Reaktionen bleiben getrennt.\n\n- Primärzeuge: `originalzeugen/VOR_VPS_PRIMAERZEUGE_B_EXAKT.txt`\n- Zeuge-A-Ergänzung: `originalzeugen/ZEUGE_A_ERGAENZUNG_ORIGINALZEILEN_388_636.txt`\n- Segmentregister: `SEGMENTREGISTER.jsonl` und `REKONSTRUKTIONSREGISTER.sqlite`\n- Driftvergleich: `DRIFTVERGLEICH.md`\n- getrennte AI-Lesepfade: `ai-stroeme/`\n'''
    atomic_write(ROOT / 'START_HIER.md', start.encode())

    manifest = {
        'schema_version': '1.0', 'generated_utc': generated, 'status': 'BUILT',
        'primary_source': str(SOURCE_B), 'primary_source_sha256': sha(SOURCE_B.read_bytes()),
        'supplement_source': str(SOURCE_A), 'supplement_source_sha256': sha(SOURCE_A.read_bytes()),
        'segment_count': len(segments), 'truth_count': len(TRUTHS), 'drift_count': len(DRIFT),
        'stream_paths': list(STREAMS),
        'truth_boundary': 'Ursprungsring ist rekonstruierte, quellengebundene Vor-VPS-Schicht; nicht behaupteter vollständiger 1:1-Gesamtverlauf.',
    }
    write_json(ROOT / 'MANIFEST.json', manifest)
    return manifest

if __name__ == '__main__':
    print(json.dumps(build(), ensure_ascii=False, indent=2))
