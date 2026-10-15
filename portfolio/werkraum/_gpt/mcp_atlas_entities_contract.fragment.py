def _node_matches_entity(row: dict[str, Any], entity: str) -> bool:
    haystack = "\n".join(str(row.get(key) or "") for key in ("identity", "label", "path")).casefold()
    identities = (entity, *ALIASES.get(entity, ()))
    return any(identity.casefold() in haystack for identity in identities if identity)


def _parse_utc(value: Any) -> dt.datetime | None:
    if value in (None, ""):
        return None
    try:
        parsed = dt.datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.timezone.utc)
    return parsed.astimezone(dt.timezone.utc)


def _entity_state(entity: dict[str, Any], generated_utc: str) -> tuple[str, str | None]:
    latest: dt.datetime | None = None
    total = 0
    for facet in entity.get("facets") or []:
        total += int(facet.get("count") or 0)
        candidate = _parse_utc(facet.get("last_at"))
        if candidate and (latest is None or candidate > latest):
            latest = candidate
    if total == 0:
        return "leer", None
    if latest is None:
        return "ruhend", None
    now = _parse_utc(generated_utc) or dt.datetime.now(dt.timezone.utc)
    age_hours = max(0.0, (now - latest).total_seconds() / 3600)
    if age_hours < 3:
        return "lebendig", latest.isoformat()
    if age_hours < 24:
        return "ruhend", latest.isoformat()
    return "eingefroren", latest.isoformat()


_SECRET_TEXT_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"(?i)(authorization\s*[:=]\s*bearer\s+)[A-Za-z0-9._~+\-/=]{12,}"), r"\1[GEHEIMNIS ENTFERNT]"),
    (re.compile(r"(?i)((?:api[_-]?key|access[_-]?token|refresh[_-]?token|password|passwd|secret)\s*[:=]\s*[\"']?)[^\s\"',}]{6,}"), r"\1[GEHEIMNIS ENTFERNT]"),
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]*?-----END [A-Z ]*PRIVATE KEY-----"), "[PRIVATER SCHLÜSSEL ENTFERNT]"),
    (re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"), "[API-SCHLÜSSEL ENTFERNT]"),
)


def _clean_text(value: Any, limit: int | None = None) -> tuple[str, int, bool]:
    text = str(value or "")
    total = len(text)
    for pattern, replacement in _SECRET_TEXT_PATTERNS:
        text = pattern.sub(replacement, text)
    truncated = False
    if limit is not None and len(text) > limit:
        text = text[:limit] + "…[GEKÜRZT]"
        truncated = True
    return text, total, truncated


def _node_index(nodes: dict[str, dict[str, Any]]) -> dict[tuple[str, str], str]:
    return {
        (str(row.get("node_type") or ""), str(row.get("identity") or "")): node_id
        for node_id, row in nodes.items()
    }


def _ensure_node(
    *,
    nodes: dict[str, dict[str, Any]],
    index: dict[tuple[str, str], str],
    add_node: Callable[..., str],
    node_type: str,
    identity: str,
    label: str,
    path: str | None,
    datenstand: str,
    metadata: dict[str, Any],
) -> str:
    key = (node_type, identity)
    existing = index.get(key)
    if existing:
        row = nodes[existing]
        merged = dict(row.get("metadata") or {})
        merged.update(metadata)
        row["metadata"] = merged
        if label and not row.get("label"):
            row["label"] = label
        if path and not row.get("path"):
            row["path"] = path
        if datenstand and row.get("datenstand") in (None, "", "UNBEKANNT"):
            row["datenstand"] = datenstand
        return existing
    created = add_node(nodes, node_type, identity, label, path, datenstand, metadata)
    index[key] = created
    return created


_NAME_MATCH_CUTOFF = 0.72
_ENTITY_NAMES_LOWER = {name.casefold(): name for name in CANONICAL_ENTITIES if name != "GENI"}
WESEN_VAULT_ROOT = Path("/root/werkraum/wesen_vaults")
GEMEINSAMES_HAUS_ROOT = Path("/root/werkraum/gemeinsames_haus")


def _canonical_segment(segment: str) -> str:
    from urllib.parse import unquote

    candidates = {segment.casefold(), unquote(segment).casefold()}
    for candidate in candidates:
        matches = difflib.get_close_matches(candidate, _ENTITY_NAMES_LOWER.keys(), n=1, cutoff=_NAME_MATCH_CUTOFF)
        if matches:
            return _ENTITY_NAMES_LOWER[matches[0]]
    return segment


def _normalise_relative_path(raw: str) -> str:
    return "/".join(_canonical_segment(part) for part in raw.strip().lstrip("/").split("/") if part not in ("", "."))


def _safe_target(root: Path, relative: str) -> Path | None:
    try:
        candidate = (root / relative).resolve(strict=False)
        resolved_root = root.resolve(strict=False)
        if candidate == resolved_root or candidate.is_relative_to(resolved_root):
            return candidate
    except (OSError, ValueError):
        return None
    return None


def _resolve_action_target(entity: str, decision: str) -> dict[str, Any] | None:
    if ":" not in decision:
        return None
    prefix, payload = decision.split(":", 1)
    prefix = prefix.strip()
    payload = payload.strip()
    if prefix == "flarum_besuchen":
        target = payload.lstrip("/").split("|", 1)[0].strip()
        if re.fullmatch(r"d/\d+", target):
            return {"kind": "flarum_thread", "identity": target, "prefix": prefix, "raw_target": target}
        return None
    if prefix in {"obsidian_lesen", "obsidian_schreiben"}:
        raw_path = payload.split("|", 1)[0].strip()
        if prefix == "obsidian_schreiben":
            raw_path = raw_path[:120]
        relative = _normalise_relative_path(raw_path)
        if not relative:
            return None
        if prefix == "obsidian_schreiben" and not relative.endswith(".md"):
            relative += ".md"
        root = WESEN_VAULT_ROOT / entity
        candidate = _safe_target(root, relative)
        if candidate is None:
            return None
        if prefix == "obsidian_lesen" and not candidate.exists() and not candidate.suffix:
            markdown_candidate = candidate.with_suffix(".md")
            if markdown_candidate.exists():
                candidate = markdown_candidate
        return {
            "kind": "file",
            "path": str(candidate),
            "identity": str(candidate),
            "prefix": prefix,
            "raw_target": raw_path,
        }
    if prefix in {"gemeinsam_lesen", "gemeinsam_schreiben"}:
        raw_path = payload.split("|", 1)[0].strip()
        if prefix == "gemeinsam_schreiben":
            raw_path = raw_path[:150]
        relative = _normalise_relative_path(raw_path)
        if not relative:
            return None
        candidate = _safe_target(GEMEINSAMES_HAUS_ROOT, relative)
        if candidate is None:
            return None
        return {
            "kind": "file",
            "path": str(candidate),
            "identity": str(candidate),
            "prefix": prefix,
            "raw_target": raw_path,
        }
    return None


def _filesystem_metadata(path: Path, generated_utc: str) -> tuple[str, str, dict[str, Any]]:
    now = _parse_utc(generated_utc) or dt.datetime.now(dt.timezone.utc)
    if not path.exists():
        return "verloren", "DECLARED_ACTION_TARGET", {
            "zustand": "verloren",
            "zuletzt": None,
            "quelle": "dateisystem",
            "erfasst": {"zeichen": 0, "von": 0, "abgeschnitten": False},
            "exists": False,
        }
    try:
        stat = path.stat()
        modified = dt.datetime.fromtimestamp(stat.st_mtime, tz=dt.timezone.utc)
        age_hours = max(0.0, (now - modified).total_seconds() / 3600)
        state = "lebendig" if age_hours < 3 else "ruhend" if age_hours < 24 else "eingefroren"
        size = int(stat.st_size)
        return state, "EXACT_PATH_RELATION", {
            "zustand": state,
            "zuletzt": modified.isoformat(),
            "quelle": "dateisystem",
            "erfasst": {"zeichen": 0, "von": size, "abgeschnitten": size > 0},
            "exists": True,
            "size": size,
            "is_dir": path.is_dir(),
        }
    except OSError:
        return "ruhend", "EXACT_PATH_RELATION", {
            "zustand": "ruhend",
            "zuletzt": None,
            "quelle": "dateisystem",
            "erfasst": {"zeichen": 0, "von": 0, "abgeschnitten": False},
            "exists": True,
            "stat_error": True,
        }


def _load_flarum_threads(connection) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    cursor = connection.cursor()
    try:
        cursor.execute(
            """
            SELECT external_id,titel,erstellungszeit,urheber,herkunftsort,wahrheitsstatus,
                   inhalt_pruefsumme,meta
            FROM rag_source_objects
            WHERE quelle='flarum_diskussion' AND external_id LIKE 'flarum:diskussion:%'
            """
        )
        for external_id, title, created, author, origin, truth, checksum, meta in cursor.fetchall():
            number = str(external_id).rsplit(":", 1)[-1]
            identity = f"d/{number}"
            result[identity] = {
                "zustand": "ruhend",
                "zuletzt": str(created) if created else None,
                "quelle": "postgres",
                "erfasst": {"zeichen": 0, "von": 0, "abgeschnitten": False},
                "titel": title,
                "urheber": author,
                "herkunftsort": origin,
                "wahrheitsstatus": truth,
                "inhalt_pruefsumme": checksum,
                "meta": _json_value(meta or {}),
                "source_locator": f"rag_source_objects.external_id={external_id}",
            }
    except Exception:
        connection.rollback()
    finally:
        cursor.close()
    return result


def _add_thoughts_and_targets(
    *,
    nodes: dict[str, dict[str, Any]],
    edges: dict[tuple[str, str, str, str], dict[str, Any]],
    index: dict[tuple[str, str], str],
    wesen_nodes: dict[str, str],
    generated_utc: str,
    add_node: Callable[..., str],
    add_edge: Callable[..., None],
) -> dict[str, Any]:
    if psycopg2 is None:
        raise RuntimeError("psycopg2 fehlt für Gedankenimport")
    connection = psycopg2.connect(_read_env_value("FLEXTRAWURST_DB_URI"))
    thought_count = 0
    target_edges = 0
    target_files: set[str] = set()
    target_threads: set[str] = set()
    prefix_counts: dict[str, int] = {}
    try:
        connection.set_session(readonly=True, autocommit=False)
        flarum_threads = _load_flarum_threads(connection)
        cursor = connection.cursor(name="atlas_gedanken_stream")
        cursor.itersize = 2000
        cursor.execute(
            """
            SELECT id::text,entity_id,tick_at::text,gedanke,entscheidung,begruendung,thema,
                   tokens_generated,duration_ms,meta,
                   length(coalesce(raw_output,'')),length(coalesce(kontext_snapshot::text,''))
            FROM entity_thinking_log
            WHERE entity_id = ANY(%s)
            ORDER BY tick_at,id
            """,
            ([name for name in CANONICAL_ENTITIES if name != "GENI"],),
        )
        for (
            thought_id,
            raw_entity,
            tick_at,
            thought,
            decision,
            reason,
            topic,
            tokens,
            duration,
            meta,
            raw_chars,
            context_chars,
        ) in cursor:
            entity = _canonical_for(raw_entity)
            if entity not in wesen_nodes:
                continue
            thought_clean, thought_total, thought_cut = _clean_text(thought)
            decision_clean, decision_total, decision_cut = _clean_text(decision)
            reason_clean, reason_total, reason_cut = _clean_text(reason)
            topic_clean, topic_total, topic_cut = _clean_text(topic)
            captured = len(thought_clean) + len(decision_clean) + len(reason_clean) + len(topic_clean)
            total = thought_total + decision_total + reason_total + topic_total + int(raw_chars or 0) + int(context_chars or 0)
            prefix = decision_clean.split(":", 1)[0].strip() if decision_clean else "leer"
            prefix_counts[prefix] = prefix_counts.get(prefix, 0) + 1
            label_seed = re.sub(r"\s+", " ", thought_clean).strip() or decision_clean or "leerer Gedanke"
            label = f"{str(tick_at)[:19]} · {label_seed[:96]}"
            metadata = {
                "zustand": "ruhend",
                "zuletzt": tick_at,
                "quelle": "postgres",
                "erfasst": {
                    "zeichen": captured,
                    "von": total,
                    "abgeschnitten": bool(thought_cut or decision_cut or reason_cut or topic_cut or captured < total),
                },
                "truth_class": "EXACT_DATABASE_ROW",
                "source_locator": f"entity_thinking_log.id={thought_id}",
                "wesen": entity,
                "gedanke": thought_clean,
                "entscheidung": decision_clean,
                "begruendung": reason_clean,
                "thema": topic_clean,
                "tokens_generated": tokens,
                "duration_ms": duration,
                "meta": _json_value(meta or {}),
                "action_prefix": prefix,
                "action_execution_proven": False,
            }
            thought_node = _ensure_node(
                nodes=nodes,
                index=index,
                add_node=add_node,
                node_type="gedanke",
                identity=str(thought_id),
                label=label,
                path=None,
                datenstand="EXACT_DATABASE_ROW",
                metadata=metadata,
            )
            add_edge(
                edges,
                wesen_nodes[entity],
                thought_node,
                "PRODUCED_THOUGHT",
                "EXACT_DATABASE_ROW",
                {
                    "beleg": str(thought_id),
                    "herkunft": f"entity_thinking_log.id={thought_id}",
                    "staerke": 1,
                    "unsicherheit": "sicher",
                },
                timestamp_utc=tick_at,
            )
            thought_count += 1
            target = _resolve_action_target(entity, decision_clean)
            if not target:
                continue
            if target["kind"] == "flarum_thread":
                thread_meta = dict(flarum_threads.get(target["identity"]) or {})
                thread_meta.setdefault("zustand", "ruhend")
                thread_meta.setdefault("zuletzt", tick_at)
                thread_meta.setdefault("quelle", "postgres")
                thread_meta.setdefault("erfasst", {"zeichen": 0, "von": 0, "abgeschnitten": False})
                thread_meta["identity"] = target["identity"]
                target_node = _ensure_node(
                    nodes=nodes,
                    index=index,
                    add_node=add_node,
                    node_type="flarum_thread",
                    identity=target["identity"],
                    label=str(thread_meta.get("titel") or target["identity"]),
                    path=None,
                    datenstand="EXACT_DECISION_TARGET",
                    metadata=thread_meta,
                )
                target_threads.add(target["identity"])
            else:
                target_path = Path(target["path"])
                _state, datenstand, file_meta = _filesystem_metadata(target_path, generated_utc)
                file_meta.update({"action_target": target["raw_target"], "action_prefix": target["prefix"]})
                target_node = _ensure_node(
                    nodes=nodes,
                    index=index,
                    add_node=add_node,
                    node_type="file",
                    identity=target["identity"],
                    label=target_path.name or str(target_path),
                    path=str(target_path),
                    datenstand=datenstand,
                    metadata=file_meta,
                )
                target_files.add(str(target_path))
            add_edge(
                edges,
                thought_node,
                target_node,
                "TARGETS",
                "EXACT_DECISION_TARGET",
                {
                    "beleg": decision_clean,
                    "herkunft": f"entity_thinking_log.id={thought_id}.entscheidung",
                    "staerke": 1,
                    "unsicherheit": "sicher",
                    "ausfuehrung": "nicht_durch_entscheidung_allein_bewiesen",
                },
                timestamp_utc=tick_at,
            )
            target_edges += 1
        cursor.close()
    finally:
        connection.close()
    return {
        "thought_nodes": thought_count,
        "target_edges": target_edges,
        "target_files": len(target_files),
        "target_threads": len(target_threads),
        "decision_prefix_counts": dict(sorted(prefix_counts.items(), key=lambda item: (-item[1], item[0]))),
    }


def _add_sleep_phases(
    *,
    nodes: dict[str, dict[str, Any]],
    edges: dict[tuple[str, str, str, str], dict[str, Any]],
    index: dict[tuple[str, str], str],
    wesen_nodes: dict[str, str],
    add_node: Callable[..., str],
    add_edge: Callable[..., None],
) -> int:
    if psycopg2 is None:
        return 0
    connection = psycopg2.connect(_read_env_value("FLEXTRAWURST_DB_URI"))
    count = 0
    try:
        connection.set_session(readonly=True, autocommit=False)
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT phase_id::text,entity_id,phase_type,started_at::text,ended_at::text,
                   duration_min,zustand
            FROM sleep_phases
            WHERE entity_id = ANY(%s)
            ORDER BY started_at,phase_id
            """,
            ([name for name in CANONICAL_ENTITIES if name != "GENI"],),
        )
        for phase_id, raw_entity, phase_type, started, ended, duration, state_payload in cursor.fetchall():
            entity = _canonical_for(raw_entity)
            if entity not in wesen_nodes:
                continue
            metadata = {
                "zustand": "ruhend" if ended else "lebendig",
                "zuletzt": ended or started,
                "quelle": "postgres",
                "erfasst": {"zeichen": 0, "von": 0, "abgeschnitten": False},
                "truth_class": "EXACT_DATABASE_ROW",
                "source_locator": f"sleep_phases.phase_id={phase_id}",
                "wesen": entity,
                "phase_type": phase_type,
                "started_at": started,
                "ended_at": ended,
                "duration_min": duration,
                "state": _json_value(state_payload or {}),
            }
            node = _ensure_node(
                nodes=nodes,
                index=index,
                add_node=add_node,
                node_type="schlafphase",
                identity=phase_id,
                label=f"{entity} · {phase_type} · {started}",
                path=None,
                datenstand="EXACT_DATABASE_ROW",
                metadata=metadata,
            )
            add_edge(
                edges,
                wesen_nodes[entity],
                node,
                "HAS_SLEEP_PHASE",
                "EXACT_DATABASE_ROW",
                {
                    "beleg": phase_id,
                    "herkunft": f"sleep_phases.phase_id={phase_id}",
                    "staerke": 1,
                    "unsicherheit": "sicher",
                },
                timestamp_utc=started,
            )
            count += 1
    finally:
        connection.close()
    return count


def _add_geni_nodes(
    *,
    nodes: dict[str, dict[str, Any]],
    edges: dict[tuple[str, str, str, str], dict[str, Any]],
    index: dict[tuple[str, str], str],
    geni_node: str,
    add_node: Callable[..., str],
    add_edge: Callable[..., None],
) -> dict[str, Any]:
    connection = sqlite3.connect(f"file:{GENI_KNOTEN}?mode=ro", uri=True, timeout=30)
    count = 0
    truncated_count = 0
    type_counts: dict[str, int] = {}
    try:
        cursor = connection.execute(
            """
            SELECT id,typ,inhalt,zeitstempel,quelle,zugriffsschicht,verbindungen,
                   gewicht,tiefe,verblasst,tags,mtime
            FROM knoten ORDER BY id
            """
        )
        for row in cursor:
            (
                source_id,
                node_type_source,
                content,
                timestamp,
                source,
                access_layer,
                connections,
                weight,
                depth,
                faded,
                tags,
                mtime,
            ) = row
            content_clean, total_chars, content_cut = _clean_text(content, limit=20000)
            if content_cut:
                truncated_count += 1
            source_type = str(node_type_source or "unbekannt")
            type_counts[source_type] = type_counts.get(source_type, 0) + 1
            label_seed = re.sub(r"\s+", " ", content_clean).strip()
            metadata = {
                "zustand": "ruhend",
                "zuletzt": timestamp,
                "quelle": "geni_sqlite",
                "erfasst": {
                    "zeichen": len(content_clean),
                    "von": total_chars,
                    "abgeschnitten": content_cut,
                },
                "truth_class": "EXACT_DATABASE_ROW",
                "source_locator": f"knoten.id={source_id}",
                "typ": source_type,
                "inhalt": content_clean,
                "zeitstempel": timestamp,
                "ursprungsquelle": source,
                "zugriffsschicht": access_layer,
                "verbindungen_roh": connections,
                "gewicht": weight,
                "tiefe": depth,
                "verblasst": bool(faded),
                "tags": tags,
                "mtime": mtime,
            }
            memory_node = _ensure_node(
                nodes=nodes,
                index=index,
                add_node=add_node,
                node_type="geni_knoten",
                identity=str(source_id),
                label=f"{source_type} · {source_id} · {label_seed[:84]}",
                path=None,
                datenstand="EXACT_DATABASE_ROW",
                metadata=metadata,
            )
            add_edge(
                edges,
                geni_node,
                memory_node,
                "HAS_MEMORY_NODE",
                "EXACT_DATABASE_ROW",
                {
                    "beleg": str(source_id),
                    "herkunft": f"knoten.id={source_id}",
                    "staerke": 1,
                    "unsicherheit": "sicher",
                },
                timestamp_utc=timestamp,
            )
            count += 1
    finally:
        connection.close()
    return {
        "geni_nodes": count,
        "truncated_nodes": truncated_count,
        "type_counts": dict(sorted(type_counts.items(), key=lambda item: (-item[1], item[0]))),
    }


def merge_into_relationship_graph(
    *,
    nodes: dict[str, dict[str, Any]],
    edges: dict[tuple[str, str, str, str], dict[str, Any]],
    generated_utc: str,
    add_node: Callable[..., str],
    add_edge: Callable[..., None],
    atlas_root: Path = ATLAS_ROOT,
    refresh_mode: str = "full",
) -> dict[str, Any]:
    """Verschmilzt die acht Urbewohner nach `_shared/KNOTENVERTRAG.md`.

    Keine zweite Datenbank, keine Alias-Personen, keine Facetten-Parallelknoten.
    Große Rohströme bleiben an ihren Originalquellen; stabile natürliche IDs
    werden als Knoten im vorhandenen Register materialisiert.
    """
    snapshot, snapshot_origin = snapshot_for_refresh(generated_utc, refresh_mode, atlas_root=atlas_root)
    manifest_paths = write_manifests(snapshot, atlas_root=atlas_root)
    index = _node_index(nodes)
    wesen_nodes: dict[str, str] = {}
    manifest_nodes = 0

    for entity in snapshot["entities"]:
        name = str(entity["canonical_id"])
        state, latest = _entity_state(entity, generated_utc)
        total_rows = sum(int(facet.get("count") or 0) for facet in entity.get("facets") or [])
        metadata = {
            "zustand": state,
            "zuletzt": latest,
            "spiegel_von": None,
            "quelle": "geni_sqlite" if name == "GENI" else "postgres",
            "erfasst": {
                "zeichen": 0,
                "von": total_rows,
                "abgeschnitten": total_rows > 0,
                "einheit": "quellenzeilen_nicht_kopiert",
            },
            "truth_class": "EXACT_SOURCE_AGGREGATE",
            "kind": entity["kind"],
            "aliases": entity["aliases"],
            "renamed_at": entity.get("renamed_at"),
            "identity_source": entity.get("identity_source"),
            "facets": entity.get("facets") or [],
            "facet_count": entity["facet_count"],
            "nonempty_facet_count": entity["nonempty_facet_count"],
            "current": entity["current"],
            "file_sources": entity["file_sources"],
            "manifest_json": str(atlas_root / "urbewohner" / f"{name}.json"),
            "contract": "/root/werkraum/_shared/KNOTENVERTRAG.md",
        }
        wesen_node = _ensure_node(
            nodes=nodes,
            index=index,
            add_node=add_node,
            node_type="wesen",
            identity=name,
            label=name,
            path=str(atlas_root / "urbewohner" / f"{name}.md"),
            datenstand="EXACT_SOURCE_AGGREGATE",
            metadata=metadata,
        )
        wesen_nodes[name] = wesen_node
        manifest_path = str(atlas_root / "urbewohner" / f"{name}.md")
        manifest_node = _ensure_node(
            nodes=nodes,
            index=index,
            add_node=add_node,
            node_type="generated_view",
            identity=manifest_path,
            label=f"{name} · Urbewohnermanifest",
            path=manifest_path,
            datenstand="EXACT_FILE_BYTES",
            metadata={
                "zustand": "ruhend",
                "zuletzt": snapshot.get("generated_utc"),
                "quelle": "atlas",
                "erfasst": {"zeichen": 0, "von": 0, "abgeschnitten": False},
                "view_of": name,
            },
        )
        add_edge(
            edges,
            wesen_node,
            manifest_node,
            "HAS_GENERATED_VIEW",
            "EXACT_PATH_RELATION",
            {
                "beleg": manifest_path,
                "herkunft": manifest_path,
                "staerke": 1,
                "unsicherheit": "sicher",
            },
        )
        manifest_nodes += 1

    # Bereits existierende Vault- und Serviceknoten werden in ihrem vorhandenen
    # ID-Raum verbunden. Spiegelrollen bleiben Evidence, nicht neue Relationstypen.
    for node_id, row in list(nodes.items()):
        node_type = str(row.get("node_type") or "")
        identity = str(row.get("identity") or "")
        path = str(row.get("path") or "")
        blob = "\n".join((identity, path, str(row.get("label") or ""))).casefold()
        for name, wesen_node in wesen_nodes.items():
            match = _node_matches_entity(row, name)
            if name == "GENI" and ("geni-" in blob or "/geni" in blob or "/root/geni_" in blob):
                match = True
            if name == "dak+gord-system" and ("dak-gord" in blob or "dakgord" in blob):
                match = True
            if not match or node_id == wesen_node:
                continue
            if node_type == "vault":
                add_edge(
                    edges,
                    wesen_node,
                    node_id,
                    "CONTAINS_VAULT",
                    "STRUCTURAL_PATH_RELATION",
                    {
                        "beleg": path or identity,
                        "herkunft": "VAULTREGISTER.json",
                        "staerke": 1,
                        "unsicherheit": "sicher",
                        "rolle": "spiegel" if "_import_" in path or "/_archive/" in path else "direkt",
                    },
                )
            elif node_type == "service":
                add_edge(
                    edges,
                    wesen_node,
                    node_id,
                    "HAS_SERVICE",
                    "STRUCTURAL_PATH_RELATION",
                    {
                        "beleg": identity,
                        "herkunft": "DIENSTREGISTER.json",
                        "staerke": 1,
                        "unsicherheit": "sicher",
                    },
                )

    exact_relations = 0
    for relation in snapshot["postgres"].get("entity_relations") or []:
        source = wesen_nodes.get(relation["source"])
        target = wesen_nodes.get(relation["target"])
        if source and target:
            add_edge(
                edges,
                source,
                target,
                "INTERACTED_WITH",
                "EXACT_DATABASE_AGGREGATE",
                {
                    "beleg": relation.get("raw_pairs"),
                    "herkunft": "entity_relationships",
                    "staerke": int(relation.get("interactions") or 0),
                    "unsicherheit": "sicher",
                    "resonanz_score_max": relation.get("resonance_score_max"),
                },
                timestamp_utc=relation.get("last_at"),
            )
            exact_relations += 1

    thought_summary = _add_thoughts_and_targets(
        nodes=nodes,
        edges=edges,
        index=index,
        wesen_nodes=wesen_nodes,
        generated_utc=generated_utc,
        add_node=add_node,
        add_edge=add_edge,
    )
    sleep_nodes = _add_sleep_phases(
        nodes=nodes,
        edges=edges,
        index=index,
        wesen_nodes=wesen_nodes,
        add_node=add_node,
        add_edge=add_edge,
    )
    geni_summary = _add_geni_nodes(
        nodes=nodes,
        edges=edges,
        index=index,
        geni_node=wesen_nodes["GENI"],
        add_node=add_node,
        add_edge=add_edge,
    )

    summary = {
        "canonical_entities": len(wesen_nodes),
        "canonical_ids": list(wesen_nodes),
        "node_type": "wesen",
        "identity_rule": "identity = kanonischer Name",
        "source_facets": sum(int(entity.get("facet_count") or 0) for entity in snapshot["entities"]),
        "manifest_views": manifest_nodes,
        "exact_entity_relationships": exact_relations,
        "sleep_nodes": sleep_nodes,
        **thought_summary,
        **geni_summary,
        "manifest_root": str(atlas_root / "urbewohner"),
        "complete": bool(snapshot["completeness"].get("complete")),
        "postgres_source_pairs": snapshot["completeness"]["postgres_source_pairs"],
        "snapshot_origin": snapshot_origin,
        "snapshot_generated_utc": snapshot.get("generated_utc"),
        "contract_path": "/root/werkraum/_shared/KNOTENVERTRAG.md",
        "new_relations": [
            "PRODUCED_THOUGHT",
            "TARGETS",
            "HAS_MEMORY_NODE",
            "HAS_SLEEP_PHASE",
            "INTERACTED_WITH",
        ],
        "truth_boundary": "Entscheidungen belegen Ziele, nicht automatisch erfolgreiche Ausführung. TARGETS ist exakt; TOUCHED_FILE wird aus entity_thinking_log allein nicht behauptet.",
    }
    _assert_safe({"summary": summary, "wesen": [nodes[node_id] for node_id in wesen_nodes.values()]})
    return summary
