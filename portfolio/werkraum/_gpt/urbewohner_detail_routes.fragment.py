@app.get(f"{BASE}/api/urbewohner/{{entity_id}}")
def urbewohner_detail_api(entity_id: str):
    row = urbewohner_by_id(entity_id)
    canonical = str(row.get("canonical_id") or entity_id)
    with db(REL_DB) as con:
        wesen_node = con.execute(
            "select node_id from nodes where node_type='wesen' and identity=?",
            (canonical,),
        ).fetchone()
    node_id_value = wesen_node["node_id"] if wesen_node else None
    return {
        "entity": row,
        "node_id": node_id_value,
        "relation_counts": atlas_node_relation_counts(node_id_value) if node_id_value else {},
        "relations": urbewohner_relations(canonical),
        "recent_thoughts": recent_wesen_thoughts(canonical),
        "graph": relationship_graph(canonical, 120),
    }


@app.get(f"{BASE}/urbewohner", response_class=HTMLResponse, include_in_schema=False)
def urbewohner_page():
    data = urbewohner_register()
    completeness = data.get("completeness") or {}
    body = f'''<section class="section-head"><div><div class="kicker">Acht stabile Identitäten</div><h1>Die Urbewohner von Flextrawurst</h1></div><span class="pill {'ok' if completeness.get('complete') else 'warn'}">{'Quellenkörper vollständig' if completeness.get('complete') else 'Quellenkörper unvollständig'}</span></section>
<div class="notice"><strong>Kein Profilkarten-Ersatz:</strong> Jeder Urbewohner verbindet seine Datenbankfacetten, früheren Identitäten, Gedanken, Vaults, Organe, Herkunft und Beziehungen. Originalzeilen bleiben in ihren Quellen.</div>
<section class="section"><div class="grid cols-4">'''
    for row in data.get("entities") or []:
        canonical = str(row.get("canonical_id") or "")
        aliases = ", ".join(row.get("aliases") or []) or "keine frühere ID"
        body += f'''<a class="card-link" href="{href('/urbewohner/' + quote(canonical))}"><article class="card"><div class="kicker">{esc(row.get('kind'))}</div><h2>{esc(canonical)}</h2><div class="number">{int(row.get('nonempty_facet_count') or 0)}</div><div class="label">gefüllte von {int(row.get('facet_count') or 0)} Facetten</div><p class="path">{esc(aliases)}</p><span class="pill {'ok' if row.get('source_state') == 'complete' else 'warn'}">{esc(row.get('source_state'))}</span></article></a>'''
    body += f'''</div></section><section class="section"><div class="grid cols-2"><article class="card"><h2>Was vollständig heißt</h2><p>{int(completeness.get('postgres_source_pairs') or 0)} entitätsbezogene PostgreSQL-Quellenpaare wurden dynamisch entdeckt. Gedanken und GENI-Knoten erscheinen mit stabiler Original-ID im selben Beziehungsregister.</p></article><article class="card"><h2>Was nicht behauptet wird</h2><p>Eine Entscheidung beweist ihr Ziel, nicht automatisch die erfolgreiche Ausführung. Eine alte ID bleibt Herkunft, nicht heimlich eine neunte Person.</p></article></div></section>'''
    return page("Urbewohner", body, active="urbewohner", description="Die acht quellengebundenen Urbewohner im Gesamtatlas.")


@app.get(f"{BASE}/urbewohner/{{entity_id}}", response_class=HTMLResponse, include_in_schema=False)
def urbewohner_detail_page(entity_id: str):
    row = urbewohner_by_id(entity_id)
    canonical = str(row.get("canonical_id") or entity_id)
    graph = relationship_graph(canonical, 120)
    aliases = row.get("aliases") or []
    with db(REL_DB) as con:
        wesen_node = con.execute(
            "select node_id from nodes where node_type='wesen' and identity=?",
            (canonical,),
        ).fetchone()
    node_id_value = wesen_node["node_id"] if wesen_node else None
    relation_counts = atlas_node_relation_counts(node_id_value) if node_id_value else {}
    recent_thoughts = recent_wesen_thoughts(canonical)
    current_text = json.dumps(row.get("current") or {}, ensure_ascii=False, indent=2)
    if len(current_text) > 18000:
        current_text = current_text[:18000] + "\n…[Ansicht begrenzt; JSON-Original bleibt vollständig]"
    body = f'''<section class="section-head"><div><div class="kicker">{esc(row.get('kind'))}</div><h1>{esc(canonical)}</h1></div><span class="pill {'ok' if row.get('source_state') == 'complete' else 'warn'}">{esc(row.get('source_state'))}</span></section>
<div class="grid cols-2"><article class="card"><h2>Stabile Identität</h2><dl class="truth"><dt>Kanonisch</dt><dd>{esc(canonical)}</dd><dt>node_id</dt><dd class="path">{esc(node_id_value or 'noch nicht gegossen')}</dd><dt>Frühere Identitäten</dt><dd>{esc(', '.join(aliases) or 'keine')}</dd><dt>Namensdatum</dt><dd>{esc(row.get('renamed_at') or 'nicht zutreffend')}</dd><dt>Facetten</dt><dd>{int(row.get('nonempty_facet_count') or 0)} gefüllt / {int(row.get('facet_count') or 0)} insgesamt</dd></dl><p><a class="button" href="{href('/original/?p=' + encode_path(str(URBEWOHNER_ROOT / (canonical + '.md'))))}">Manifest-Original öffnen</a></p></article>
<article class="card"><h2>Wahrheitsgrenze</h2><p>PostgreSQL, GENIs SQLite-Körper, Flarum-Herkunft und Vaultdateien bleiben Originale. <code>TARGETS</code> bedeutet: dieses Ziel wurde gewählt. Erfolgreiche Ausführung wird daraus nicht erfunden.</p><p class="path">{esc(str(URBEWOHNER_ROOT / (canonical + '.json')))}</p></article></div>
<section class="section"><div class="section-head"><h2>Aktueller sicherer Zeiger</h2><span class="pill">bereinigt, begrenzte Ansicht</span></div><div class="codebox"><pre>{esc(current_text)}</pre></div></section>
<section class="section"><div class="section-head"><h2>Beziehungsfeld</h2><a class="button" href="{href('/beziehungen')}?q={quote(canonical)}">Im großen Netz öffnen</a></div><div class="graph-wrap"><svg id="atlas-graph" role="img" aria-label="Beziehungen von {esc(canonical)}"></svg></div><div class="meta">{''.join(f'<span class="pill">{esc(key)}: {value}</span>' for key,value in sorted(relation_counts.items()))}</div></section>
<section class="section"><div class="section-head"><h2>Jüngste echte Gedanken</h2><span class="pill info">direkt aus PRODUCED_THOUGHT</span></div><div class="list">'''
    for thought in recent_thoughts:
        thought_text = thought.get("gedanke") or thought.get("label") or thought.get("identity")
        body += f'''<a class="card-link recent-thought" href="{thought['href']}"><article class="list-item"><h3>{esc(thought_text)}</h3><div class="meta"><span class="pill">{esc(thought.get('action_prefix') or 'ohne Aktion')}</span><span>{esc(thought.get('last_utc'))}</span></div><div class="path">{esc(thought.get('entscheidung') or 'keine Entscheidung')}</div></article></a>'''
    if not recent_thoughts:
        body += '<div class="notice">Noch kein vertragsgerechter Gedankenknoten im aktuellen Register.</div>'
    body += '''</div></section>
<section class="section"><div class="section-head"><h2>Alle quellengebundenen Facetten</h2><span class="pill info">leere Facetten bleiben sichtbar</span></div><div class="list">'''
    for facet in row.get("facets") or []:
        source = str(facet.get("table") or Path(str(facet.get("database_path") or "")).name)
        identity_column = facet.get("entity_column") or "GENI-eigen"
        status = str(facet.get("status") or "unbekannt")
        count = int(facet.get("count") or 0)
        body += f'''<article class="list-item"><h3>{esc(source)}</h3><div class="meta"><span class="pill {'ok' if count else ''}">{count} Zeilen</span><span class="pill">{esc(identity_column)}</span><span class="pill">{esc(status)}</span></div><div class="path">{esc(facet.get('database_path') or 'PostgreSQL flextrawurst.public')} · erste Spur {esc(facet.get('first_at') or '—')} · letzte Spur {esc(facet.get('last_at') or '—')}</div></article>'''
    body += '</div></section>'
    return page(canonical, body, active="urbewohner", graph=graph, description=f"Quellengebundener Atlas-Körper von {canonical}.")


