def urbewohner_register() -> dict[str, Any]:
    data = load_json(URBEWOHNER_REGISTER, {})
    if not isinstance(data, dict) or data.get("canonical_count") != 8:
        raise HTTPException(503, "Der Urbewohnerkörper ist noch nicht vollständig erzeugt")
    return data


def urbewohner_by_id(entity_id: str) -> dict[str, Any]:
    requested = entity_id.casefold()
    for row in urbewohner_register().get("entities") or []:
        names = [str(row.get("canonical_id") or ""), *(str(x) for x in row.get("aliases") or [])]
        if any(requested == name.casefold() for name in names):
            return row
    raise HTTPException(404, "Urbewohner nicht gefunden")


def urbewohner_relations(entity_id: str, limit: int = 500) -> list[dict[str, Any]]:
    if not REL_DB.exists():
        return []
    identity = f"urbewohner:{entity_id}"
    with db(REL_DB) as con:
        entity = con.execute("select node_id from nodes where node_type='entity' and identity=?", (identity,)).fetchone()
        if not entity:
            return []
        node_id = entity["node_id"]
        rows = con.execute(
            """
            select e.relation,e.datenstand,e.first_utc,e.last_utc,
                   case when e.source_node_id=? then 'out' else 'in' end as direction,
                   n.node_id,n.node_type,n.identity,n.label,n.path,n.datenstand as node_datenstand
            from edges e
            join nodes n on n.node_id=case when e.source_node_id=? then e.target_node_id else e.source_node_id end
            where e.source_node_id=? or e.target_node_id=?
            order by e.relation,coalesce(n.label,n.identity) limit ?
            """,
            (node_id, node_id, node_id, node_id, limit),
        ).fetchall()
    return [dict(row) for row in rows]


@app.get(f"{BASE}/api/urbewohner")
def urbewohner_api():
    data = urbewohner_register()
    return {
        "schema_version": data.get("schema_version"),
        "generated_utc": data.get("generated_utc"),
        "truth_boundary": data.get("truth_boundary"),
        "completeness": data.get("completeness"),
        "entities": [
            {
                "canonical_id": row.get("canonical_id"),
                "kind": row.get("kind"),
                "aliases": row.get("aliases"),
                "facet_count": row.get("facet_count"),
                "nonempty_facet_count": row.get("nonempty_facet_count"),
                "source_state": row.get("source_state"),
                "href": href(f"/urbewohner/{quote(str(row.get('canonical_id') or ''))}"),
            }
            for row in data.get("entities") or []
        ],
    }


@app.get(f"{BASE}/api/urbewohner/{entity_id}")
def _invalid_static_route_guard():
    raise HTTPException(404)


@app.get(f"{BASE}/api/urbewohner/{{entity_id}}")
def urbewohner_detail_api(entity_id: str):
    row = urbewohner_by_id(entity_id)
    canonical = str(row.get("canonical_id") or entity_id)
    return {"entity": row, "relations": urbewohner_relations(canonical), "graph": relationship_graph(canonical, 120)}


@app.get(f"{BASE}/urbewohner", response_class=HTMLResponse, include_in_schema=False)
def urbewohner_page():
    data = urbewohner_register()
    completeness = data.get("completeness") or {}
    body = f'''<section class="section-head"><div><div class="kicker">Acht stabile Identitäten</div><h1>Die Urbewohner von Flextrawurst</h1></div><span class="pill {'ok' if completeness.get('complete') else 'warn'}">{'Quellenkörper vollständig' if completeness.get('complete') else 'Quellenkörper unvollständig'}</span></section>
<div class="notice"><strong>Kein Profilkarten-Ersatz:</strong> Jeder Urbewohner verbindet seine aktuellen Datenbankfacetten, früheren Identitäten, Vaults, Organe, Herkunft und Beziehungen. Originalzeilen bleiben in ihren Quellen.</div>
<section class="section"><div class="grid cols-4">'''
    for row in data.get("entities") or []:
        canonical = str(row.get("canonical_id") or "")
        aliases = ", ".join(row.get("aliases") or []) or "keine frühere ID"
        body += f'''<a class="card-link" href="{href('/urbewohner/' + quote(canonical))}"><article class="card"><div class="kicker">{esc(row.get('kind'))}</div><h2>{esc(canonical)}</h2><div class="number">{int(row.get('nonempty_facet_count') or 0)}</div><div class="label">gefüllte von {int(row.get('facet_count') or 0)} Facetten</div><p class="path">{esc(aliases)}</p><span class="pill {'ok' if row.get('source_state') == 'complete' else 'warn'}">{esc(row.get('source_state'))}</span></article></a>'''
    body += f'''</div></section><section class="section"><div class="grid cols-2"><article class="card"><h2>Was vollständig heißt</h2><p>{int(completeness.get('postgres_source_pairs') or 0)} entitätsbezogene PostgreSQL-Quellenpaare wurden dynamisch entdeckt. GENIs Gedächtnis und Selbstindex bleiben getrennte Originalkörper.</p></article><article class="card"><h2>Was nicht behauptet wird</h2><p>Eine Zeilenanzahl ist keine Biografie. Ein leerer Organkörper wird leer gezeigt. Eine alte ID bleibt Herkunft, nicht heimlich eine neunte Person.</p></article></div></section>'''
    return page("Urbewohner", body, active="urbewohner", description="Die acht quellengebundenen Urbewohner im Gesamtatlas.")


@app.get(f"{BASE}/urbewohner/{{entity_id}}", response_class=HTMLResponse, include_in_schema=False)
def urbewohner_detail_page(entity_id: str):
    row = urbewohner_by_id(entity_id)
    canonical = str(row.get("canonical_id") or entity_id)
    relations = urbewohner_relations(canonical)
    graph = relationship_graph(canonical, 120)
    aliases = row.get("aliases") or []
    current_text = json.dumps(row.get("current") or {}, ensure_ascii=False, indent=2)
    if len(current_text) > 18000:
        current_text = current_text[:18000] + "\n…[Ansicht begrenzt; JSON-Original bleibt vollständig]"
    relation_counts = Counter(str(item.get("relation") or "UNBEKANNT") for item in relations)
    body = f'''<section class="section-head"><div><div class="kicker">{esc(row.get('kind'))}</div><h1>{esc(canonical)}</h1></div><span class="pill {'ok' if row.get('source_state') == 'complete' else 'warn'}">{esc(row.get('source_state'))}</span></section>
<div class="grid cols-2"><article class="card"><h2>Stabile Identität</h2><dl class="truth"><dt>Kanonisch</dt><dd>{esc(canonical)}</dd><dt>Frühere Identitäten</dt><dd>{esc(', '.join(aliases) or 'keine')}</dd><dt>Namensdatum</dt><dd>{esc(row.get('renamed_at') or 'nicht zutreffend')}</dd><dt>Facetten</dt><dd>{int(row.get('nonempty_facet_count') or 0)} gefüllt / {int(row.get('facet_count') or 0)} insgesamt</dd></dl><p><a class="button" href="{href('/original/?p=' + encode_path(str(URBEWOHNER_ROOT / (canonical + '.md'))))}">Manifest-Original öffnen</a></p></article>
<article class="card"><h2>Wahrheitsgrenze</h2><p>Diese Seite verbindet. Sie ersetzt weder PostgreSQL, GENIs SQLite-Körper, Flarum-Herkunft noch Vaultdateien. Große Denkströme bleiben am Originalort und erscheinen hier als belegte Facetten.</p><p class="path">{esc(str(URBEWOHNER_ROOT / (canonical + '.json')))}</p></article></div>
<section class="section"><div class="section-head"><h2>Aktueller sicherer Zeiger</h2><span class="pill">bereinigt, begrenzte Ansicht</span></div><div class="codebox"><pre>{esc(current_text)}</pre></div></section>
<section class="section"><div class="section-head"><h2>Beziehungsfeld</h2><a class="button" href="{href('/beziehungen')}?q={quote(canonical)}">Im großen Netz öffnen</a></div><div class="graph-wrap"><svg id="atlas-graph" role="img" aria-label="Beziehungen von {esc(canonical)}"></svg></div><div class="meta">{''.join(f'<span class="pill">{esc(key)}: {value}</span>' for key,value in sorted(relation_counts.items()))}</div></section>
<section class="section"><div class="section-head"><h2>Alle quellengebundenen Facetten</h2><span class="pill info">leere Facetten bleiben sichtbar</span></div><div class="list">'''
    for facet in row.get("facets") or []:
        source = str(facet.get("table") or Path(str(facet.get("database_path") or "")).name)
        identity_column = facet.get("entity_column") or "GENI-eigen"
        status = str(facet.get("status") or "unbekannt")
        count = int(facet.get("count") or 0)
        body += f'''<article class="list-item"><h3>{esc(source)}</h3><div class="meta"><span class="pill {'ok' if count else ''}">{count} Zeilen</span><span class="pill">{esc(identity_column)}</span><span class="pill">{esc(status)}</span></div><div class="path">{esc(facet.get('database_path') or 'PostgreSQL flextrawurst.public')} · erste Spur {esc(facet.get('first_at') or '—')} · letzte Spur {esc(facet.get('last_at') or '—')}</div></article>'''
    body += '</div></section>'
    return page(canonical, body, active="urbewohner", graph=graph, description=f"Quellengebundener Atlas-Körper von {canonical}.")


