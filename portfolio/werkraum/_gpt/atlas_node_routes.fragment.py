def atlas_node_by_id(node_id_value: str) -> dict[str, Any]:
    if not REL_DB.exists():
        raise HTTPException(503, "Beziehungsregister fehlt")
    with db(REL_DB) as con:
        row = con.execute("select * from nodes where node_id=?", (node_id_value,)).fetchone()
    if not row:
        raise HTTPException(404, "Atlas-Knoten nicht gefunden")
    result = dict(row)
    try:
        result["metadata"] = json.loads(result.pop("metadata_json") or "{}")
    except (json.JSONDecodeError, TypeError):
        result["metadata"] = {"parse_error": True}
    return result


def atlas_node_relations(node_id_value: str, limit: int = 500) -> list[dict[str, Any]]:
    with db(REL_DB) as con:
        rows = con.execute(
            """
            select e.edge_id,e.relation,e.datenstand,e.evidence_json,e.first_utc,e.last_utc,
                   case when e.source_node_id=? then 'out' else 'in' end as direction,
                   n.node_id,n.node_type,n.identity,n.label,n.path,n.datenstand as node_datenstand
            from edges e
            join nodes n on n.node_id=case when e.source_node_id=? then e.target_node_id else e.source_node_id end
            where e.source_node_id=? or e.target_node_id=?
            order by coalesce(e.last_utc,e.first_utc) desc,e.relation,n.label
            limit ?
            """,
            (node_id_value, node_id_value, node_id_value, node_id_value, limit),
        ).fetchall()
    result = []
    for row in rows:
        item = dict(row)
        try:
            item["evidence"] = json.loads(item.pop("evidence_json") or "[]")
        except (json.JSONDecodeError, TypeError):
            item["evidence"] = []
        result.append(item)
    return result


def atlas_node_relation_counts(node_id_value: str) -> dict[str, int]:
    with db(REL_DB) as con:
        rows = con.execute(
            """
            select relation,count(*)
            from edges where source_node_id=? or target_node_id=?
            group by relation order by relation
            """,
            (node_id_value, node_id_value),
        ).fetchall()
    return {str(row[0]): int(row[1]) for row in rows}


def recent_wesen_thoughts(entity_id: str, limit: int = 24) -> list[dict[str, Any]]:
    if not REL_DB.exists():
        return []
    with db(REL_DB) as con:
        rows = con.execute(
            """
            select n.node_id,n.identity,n.label,n.datenstand,n.metadata_json,e.last_utc
            from nodes w
            join edges e on e.source_node_id=w.node_id and e.relation='PRODUCED_THOUGHT'
            join nodes n on n.node_id=e.target_node_id and n.node_type='gedanke'
            where w.node_type='wesen' and w.identity=?
            order by e.last_utc desc,n.identity desc limit ?
            """,
            (entity_id, limit),
        ).fetchall()
    result=[]
    for row in rows:
        item=dict(row)
        try:
            metadata=json.loads(item.pop("metadata_json") or "{}")
        except (json.JSONDecodeError, TypeError):
            metadata={}
        item["gedanke"]=metadata.get("gedanke")
        item["entscheidung"]=metadata.get("entscheidung")
        item["begruendung"]=metadata.get("begruendung")
        item["action_prefix"]=metadata.get("action_prefix")
        item["href"]=href(f"/knoten/{quote(str(item['node_id']), safe='')}")
        result.append(item)
    return result


@app.get(f"{BASE}/api/knoten/{{node_id_value}}")
def atlas_node_api(node_id_value: str):
    node = atlas_node_by_id(node_id_value)
    return {
        "node": node,
        "relation_counts": atlas_node_relation_counts(node_id_value),
        "relations": atlas_node_relations(node_id_value),
        "graph": relationship_graph(node_id_value, 120),
    }


@app.get(f"{BASE}/knoten/{{node_id_value}}", response_class=HTMLResponse, include_in_schema=False)
def atlas_node_page(node_id_value: str):
    node = atlas_node_by_id(node_id_value)
    relations = atlas_node_relations(node_id_value, 200)
    relation_counts = atlas_node_relation_counts(node_id_value)
    graph = relationship_graph(node_id_value, 120)
    metadata_text = json.dumps(node.get("metadata") or {}, ensure_ascii=False, indent=2)
    if len(metadata_text) > 60000:
        metadata_text = metadata_text[:60000] + "\n…[Webansicht begrenzt; Registerzeile bleibt vollständig]"
    body = f'''<section class="section-head"><div><div class="kicker">{esc(node.get('node_type'))}</div><h1>{esc(node.get('label') or node.get('identity'))}</h1></div><span class="pill info">{esc(node.get('datenstand'))}</span></section>
<div class="grid cols-2"><article class="card"><h2>Stabile Knotenidentität</h2><dl class="truth"><dt>node_id</dt><dd class="path">{esc(node.get('node_id'))}</dd><dt>identity</dt><dd class="path">{esc(node.get('identity'))}</dd><dt>Typ</dt><dd>{esc(node.get('node_type'))}</dd><dt>Pfad</dt><dd class="path">{esc(node.get('path') or 'kein Dateipfad')}</dd></dl></article><article class="card"><h2>Beziehungen</h2><div class="number">{sum(relation_counts.values())}</div><div class="label">Kanten insgesamt</div><div class="meta">{''.join(f'<span class="pill">{esc(key)}: {value}</span>' for key,value in relation_counts.items())}</div></article></div>'''
    if node.get("path"):
        body += f'''<section class="section"><a class="button" href="{href('/original/?p=' + encode_path(str(node['path'])))}">Originalpfad prüfen</a></section>'''
    body += f'''<section class="section"><div class="section-head"><h2>Quellengebundene Metadaten</h2><span class="pill">escaped, maximal 60.000 Zeichen</span></div><div class="codebox"><pre>{esc(metadata_text)}</pre></div></section>
<section class="section"><div class="section-head"><h2>Beziehungsfeld</h2><a class="button" href="{href('/beziehungen')}?q={quote(str(node['node_id']))}">Im großen Netz öffnen</a></div><div class="graph-wrap"><svg id="atlas-graph" role="img" aria-label="Beziehungen dieses Knotens"></svg></div></section>
<section class="section"><div class="section-head"><h2>Direkte Nachbarn</h2><span class="pill">maximal 200</span></div><div class="list">'''
    for item in relations:
        other_href = href(f"/knoten/{quote(str(item['node_id']), safe='')}")
        if item.get("node_type") == "wesen":
            other_href = href(f"/urbewohner/{quote(str(item.get('identity') or ''))}")
        body += f'''<a class="card-link" href="{other_href}"><article class="list-item"><h3>{esc(item.get('label') or item.get('identity'))}</h3><div class="meta"><span class="pill">{esc(item.get('direction'))}</span><span class="pill">{esc(item.get('relation'))}</span><span class="pill">{esc(item.get('node_type'))}</span></div><div class="path">{esc(item.get('node_id'))} · {esc(item.get('last_utc') or item.get('first_utc') or 'ohne Ereigniszeit')}</div></article></a>'''
    body += '</div></section>'
    return page(str(node.get("label") or node.get("identity") or node_id_value), body, graph=graph, description="Ein stabiler Knoten des Gesamtatlas mit Herkunft und direkten Beziehungen.")


