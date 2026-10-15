from pathlib import Path
APP = Path("/root/werkraum/tools/gesamtatlas_world/app.py")
text = APP.read_text(encoding="utf-8")

old = '''    clusters.sort(key=lambda c: c["gesamt"], reverse=True)
    return {"ok": True, "gesamt_knoten": sum(counts.values()), "gesamt_kanten": total_edges, "clusters": clusters}'''
n = text.count(old)
print("anchor:", n)
if n != 1:
    raise SystemExit("abbruch")

new = '''    clusters.sort(key=lambda c: c["gesamt"], reverse=True)

    # Echte Kanten NUR zwischen den tatsaechlich gezogenen Stichproben-Knoten --
    # keine erfundenen Verbindungen, nur was im Register wirklich zwischen genau
    # diesen Knoten-IDs existiert.
    alle_stichproben_ids = [k["node_id"] for c in clusters for k in c["knoten"]]
    kanten = []
    if alle_stichproben_ids:
        edge_conn = sqlite3.connect(REL_DB)
        edge_conn.row_factory = sqlite3.Row
        placeholders = ",".join("?" for _ in alle_stichproben_ids)
        kanten_rows = edge_conn.execute(
            f"SELECT source_node_id, target_node_id, relation FROM edges "
            f"WHERE source_node_id IN ({placeholders}) AND target_node_id IN ({placeholders}) LIMIT 3000",
            alle_stichproben_ids + alle_stichproben_ids,
        ).fetchall()
        kanten = [dict(r) for r in kanten_rows]
        edge_conn.close()

    return {"ok": True, "gesamt_knoten": sum(counts.values()), "gesamt_kanten": total_edges, "clusters": clusters, "kanten_in_stichprobe": kanten}'''

text = text.replace(old, new, 1)
APP.write_text(text, encoding="utf-8")
print("ECHTE KANTEN ZWISCHEN STICHPROBEN-KNOTEN EINGEFUEGT")
