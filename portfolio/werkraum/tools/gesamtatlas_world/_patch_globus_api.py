from pathlib import Path
APP = Path("/root/werkraum/tools/gesamtatlas_world/app.py")
text = APP.read_text(encoding="utf-8")

anchor = '@app.get(f"{BASE}/megavault", response_class=HTMLResponse, include_in_schema=False)\ndef megavault_3d():'
n = text.count(anchor)
print("anchor:", n)
if n != 1:
    raise SystemExit("abbruch")

endpoint = '''# Cluster-Zuordnung fuer die Globus-Ansicht: echte node_type-Werte aus der DB
# (per SELECT node_type, COUNT(*) FROM nodes GROUP BY node_type verifiziert am
# 2026-08-14) auf sprechende Cluster-Namen gemappt. Keine erfundenen Kategorien --
# jeder Eintrag hier entspricht einem tatsaechlich vorkommenden node_type.
GLOBUS_CLUSTER = {
    "wesen":          {"label": "Wesen & Entitäten",     "farbe": "#EC4899"},
    "ai_stream":      {"label": "AI-Ströme",              "farbe": "#F59E0B"},
    "geni_knoten":    {"label": "GENI Wahrnehmung",       "farbe": "#8B5CF6"},
    "gedanke":        {"label": "Gedanken & Ideen",       "farbe": "#F97316"},
    "flarum_thread":  {"label": "Gespräche & Diskurse",   "farbe": "#FBBF24"},
    "session":        {"label": "Sitzungen",               "farbe": "#22C55E"},
    "file":           {"label": "Dateien & Archive",       "farbe": "#EAB308"},
    "vault":          {"label": "Vaults",                  "farbe": "#06B6D4"},
    "project":        {"label": "Projekte",                "farbe": "#3B82F6"},
    "service":        {"label": "Dienste & Infrastruktur", "farbe": "#10B981"},
    "validation":     {"label": "Tests & Beweise",         "farbe": "#EF4444"},
    "handoff":        {"label": "Übergaben",                "farbe": "#A78BFA"},
    "claim":          {"label": "Ansprüche",                "farbe": "#14B8A6"},
    "schlafphase":    {"label": "Schlafphasen",             "farbe": "#6366F1"},
    "generated_view": {"label": "Generierte Ansichten",    "farbe": "#84CC16"},
    "consensus":      {"label": "Konsens",                  "farbe": "#F43F5E"},
}
GLOBUS_SAMPLE_JE_CLUSTER = 60  # Deckel pro Cluster -- bei geni_knoten/gedanke (760k/99k)
                                 # ist das eine explizit benannte Stichprobe, keine Vollzaehlung.


@app.get(f"{BASE}/api/megavault/globus")
def api_megavault_globus():
    """Liefert die echten Cluster-Groessen (node_type-Zaehlung) plus eine
    gedeckelte, aber echte Stichprobe von Knoten je Cluster fuer die 3D-Globus-
    Ansicht. Zaehlung und Stichprobengroesse werden getrennt ausgewiesen, damit
    nie der Eindruck entsteht, die Stichprobe waere die Gesamtmenge."""
    if not REL_DB.exists():
        return {"ok": False, "error": "BEZIEHUNGSREGISTER.sqlite nicht gefunden"}
    conn = sqlite3.connect(REL_DB)
    conn.row_factory = sqlite3.Row

    counts = {r["node_type"]: r["c"] for r in conn.execute(
        "SELECT node_type, COUNT(*) c FROM nodes GROUP BY node_type"
    ).fetchall()}
    total_edges = conn.execute("SELECT COUNT(*) c FROM edges").fetchone()["c"]

    clusters = []
    for node_type, meta in GLOBUS_CLUSTER.items():
        total = counts.get(node_type, 0)
        if total == 0:
            continue
        rows = conn.execute(
            "SELECT node_id, node_type, label, path FROM nodes WHERE node_type = ? "
            "ORDER BY RANDOM() LIMIT ?", (node_type, GLOBUS_SAMPLE_JE_CLUSTER)
        ).fetchall()
        clusters.append({
            "node_type": node_type,
            "label": meta["label"],
            "farbe": meta["farbe"],
            "gesamt": total,
            "stichprobe_groesse": len(rows),
            "knoten": [dict(r) for r in rows],
        })
    conn.close()

    # Cluster mit den meisten Knoten zuerst -- entspricht der visuellen Gewichtung
    # in den Referenzbildern (groessere Cluster nehmen mehr Kugelflaeche ein).
    clusters.sort(key=lambda c: c["gesamt"], reverse=True)
    return {"ok": True, "gesamt_knoten": sum(counts.values()), "gesamt_kanten": total_edges, "clusters": clusters}


'''

text = text.replace(anchor, endpoint + anchor, 1)
APP.write_text(text, encoding="utf-8")
print("GLOBUS-ENDPOINT EINGEFUEGT")
