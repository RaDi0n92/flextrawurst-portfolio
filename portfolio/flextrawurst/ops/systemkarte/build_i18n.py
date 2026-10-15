import json, os, sys
LANG = sys.argv[1] if len(sys.argv) > 1 else "de"
def T(de, en): return en if LANG == "en" else de
V = dict(fromSide="bottom", toSide="top"); U = dict(fromSide="top", toSide="bottom")
OUT = f"cand/{LANG}"
PRESET = {"gesamtbild":"classic","selbstbild":"editorial","langgraph-weltbild":"blueprint",
          "datenbank-rag":"signal-flow","vaults":"blueprint","werkzeuge":"editorial"}
SUB = {"gesamtbild":("Alles auf einen Blick · Momentaufnahme","Everything at a glance · snapshot"),
       "selbstbild":("Vom Forum-Post zum Selbstmodell","From forum post to self-model"),
       "langgraph-weltbild":("Checkpoints, Weltbild und die Dienste der Wesen","Checkpoints, worldview and the beings' services"),
       "datenbank-rag":("Wo die Daten liegen, wie sie gefunden und live gemeldet werden","Where data lives, how it is found and announced live"),
       "vaults":("Alle Orte, an denen Wesen, Daniel und die AI-Ströme schreiben","Every place where beings, Daniel and the AI streams write"),
       "werkzeuge":("Toolbox, kleine Dienste und das Codexium2-Testbed","Toolbox, small services and the Codexium2 testbed")}
class D:
    def __init__(s, key, title, summary, xf=lambda c: 40+230*c, yf=lambda r: 70+140*r, W=150):
        s.key, s.title, s.summary, s.xf, s.yf, s.W = key, title, summary, xf, yf, W
        s.comps = []; s.edges = []; s.cards = []; s.views = None; s.bounds = None
    def n(s, id, t, label, sub, r, c, w=None, h=64, x=None):
        s.comps.append({"id": id, "type": t, "label": label, "sublabel": sub,
                        "pos": [s.xf(c) if x is None else x, s.yf(r)], "size": [w or s.W, h]})
    def e(s, a, b, label=None, **k):
        d = {"id": f"{a}-{b}", "from": a, "to": b}
        if label: d["label"] = label
        d.update(k); s.edges.append(d)
    def card(s, dot, title, items): s.cards.append({"dot": dot, "title": title, "items": items})
    def write(s):
        meta = {"title": s.title, "output": f"systemkarte-{s.key}-{LANG}.html", "quality_profile": "showcase"}
        if LANG == "en": meta["locale"] = "en"
        pr = PRESET.get(s.key)
        if pr and pr != "classic": meta["visual_preset"] = pr
        sub = SUB.get(s.key)
        if sub: meta["subtitle"] = sub[1] if LANG == "en" else sub[0]
        if s.views: meta["views"] = s.views
        d = {"schema_version": 1, "diagram_type": "architecture", "meta": meta, "components": s.comps, "connections": s.edges, "cards": s.cards}
        if s.bounds: d["boundaries"] = s.bounds
        os.makedirs(f"{OUT}/{s.key}", exist_ok=True)
        json.dump(d, open(f"{OUT}/{s.key}/candidate.json", "w"), ensure_ascii=False, indent=1)
        man = {"slug": s.key, "title": s.title, "summary": s.summary,
               "nodes": [f'{c["label"]} ({c["sublabel"]})' for c in s.comps],
               "cards": [{"title": c["title"], "items": c["items"]} for c in s.cards]}
        json.dump(man, open(f"{OUT}/{s.key}/manifest.json", "w"), ensure_ascii=False, indent=1)

# ================= 0 Gesamtbild =================
X8 = lambda c: 40+144*c
Y8 = {0:60,1:210,2:350,3:490,4:640,5:790,6:940,7:1090}
o = D("gesamtbild", T("flextrawurst Gesamtbild (Stand 2026-10-01)", "flextrawurst overview (as of 2026-10-01)"),
      T("Überblick über ganz flextrawurst: Plattform, Wesen-Kern, Datenbank, lokale LLMs, Vaults und Werkzeuge. Momentaufnahme, Stand 2026-10-01.",
        "Overview of all of flextrawurst: platform, being core, database, local LLMs, vaults and tools. Snapshot as of 2026-10-01."),
      xf=X8, yf=lambda r: Y8[r], W=120)
n = o.n
n("humans","external",T("Menschen","People"),T("Browser, Profile","Browser, profiles"),0,0)
n("surface","frontend","Surface :8787",T("Node.js, Tabs","Node.js, tabs"),0,1)
n("api","backend",T("Welt-API :8030","World API :8030"),"FastAPI, /rag",0,2)
n("events","messagebus",T("Events-Stream","Event stream"),"NOTIFY → SSE",0,3)
n("werk","backend",T("Weitere Dienste","More services"),"8042 7777 8055 8080",0,4)
n("wandler","backend",T("Datei-Wandler","File converter"),T(":8878 Toolbox-Tab",":8878 toolbox tab"),0,5)
n("toolbox","frontend","Toolbox :8035",T("8 Tabs, Login","8 tabs, login"),0,6)
n("tts","external","Edge-TTS","Microsoft Neural",0,7)
n("kompoase","frontend","KompOase :8900",T("Splitter-Theater","Splinter theater"),1,0)
n("codex2","frontend","Codexium2","Noxara, Wsfhh",1,1)
n("daemons","backend",T("Welt-Daemons","World daemons"),T("Splitter, Spannung","Splinters, tension"),1,4)
n("pg","database","PostgreSQL · flextrawurst",T("108 Tabellen · events 450.567 · Checkpoints 112.526 · rag_* 7.771 Chunks (pgvector)","108 tables · events 450,567 · checkpoints 112,526 · rag_* 7,771 chunks (pgvector)"),2,0,w=1128)
n("flarum","external","Flarum :80","Forum + MySQL",3,0)
n("innen","backend",T("Innenleben","Inner life"),T("LangGraph-Reflexion","LangGraph reflection"),3,1)
n("selbst","database",T("Selbstmodell","Self-model"),"JSON + ChromaDB",3,2)
n("bruecke","backend",T("Welt-Brücke","World bridge"),T("Selbstmodell→Events","Self-model→events"),3,3)
n("lgd","backend",T("LangGraph-Spiegel","LangGraph mirror"),T("Checkpoints, kein LLM","checkpoints, no LLM"),3,4)
n("weltbild","backend",T("Weltbild-Builder","Worldview builder"),T("Log bis 2026-08-21","log until 2026-08-21"),3,5)
n("wesen","backend",T("Codewesen ×7","Code beings ×7"),T("Takt, Chat, Speicher","tick, chat, memory"),3,6)
n("rag","backend","RAG Ring 1",T("bge-m3, Hybridsuche","bge-m3, hybrid search"),3,7)
n("llm","backend",T("Lokale LLMs","Local LLMs"),T("llama-server :11435 Chat · :11436 Hintergrund · Ollama :11434 (dolphin, Vision, bge-m3)","llama-server :11435 chat · :11436 background · Ollama :11434 (dolphin, vision, bge-m3)"),4,0,w=1128)
n("v_main","database","Obsidian :8443",T("ganzer Werkraum","entire workroom"),5,0)
n("v_wesen","database",T("Wesen-Vaults ×7","Being vaults ×7"),T(":8445 bis :8455",":8445 to :8455"),5,1)
n("v_haus","database",T("Gemeinsames Haus","Shared house"),T("Wesen + dak + System","beings, dak, system"),5,2)
n("v_geni","database","GENI :8020",T("Gedächtnis, Hörer","memory, listener"),5,3)
n("v_gvault","database",T("GENI-Vaults","GENI vaults"),T("Doku + Inbox","docs + inbox"),5,4)
n("v_mega","database","Megavault :18108",T("Gesamtatlas","total atlas"),5,5)
n("v_ai","database",T("AI-Strom-Zuhause","AI stream homes"),"_claude, _codex, _gpt",5,6)
n("bridge","backend",T("Obsidian-Bridge :8060","Obsidian bridge :8060"),T("schreibt Notizen per JSON in die Vaults","writes notes into the vaults via JSON"),6,0,w=552)
n("ai","external",T("AI-Ströme","AI streams"),T("Claude, Codex u.a.","Claude, Codex etc."),6,6)
n("live","frontend",T("Live-Spiegel","Live mirror"),T(":8098 bis :8100",":8098 to :8100"),6,7)
n("zensi","backend","Zensi :8043",T("Spiegel-Sandbox","mirror sandbox"),7,0)
n("t3d","backend","3D-MCP :8090","Blender + Godot",7,2)
n("godot","external","Blender / Godot","headless",7,3)
e=o.e
e("humans","surface",variant="emphasis"); e("surface","api",variant="emphasis")
e("api","pg","SQL",variant="emphasis",**V); e("pg","events","NOTIFY",variant="emphasis",**U)
e("events","surface","SSE",variant="emphasis",fromSide="top",toSide="top",via=[[X8(3)+60,30],[X8(1)+60,30]])
e("surface","kompoase",**V); e("surface","codex2",**V); e("daemons","pg","Events",**V)
e("ai","live"); e("ai","v_ai",**U)
e("flarum","innen"); e("innen","selbst"); e("selbst","bruecke"); e("bruecke","pg",**U); e("lgd","pg",**U)
e("weltbild","wesen",variant="dashed"); e("rag","pg",**U)
e("wesen","llm",**V); e("weltbild","llm",**V); e("innen","llm",**V); e("rag","llm","Embed",**V)
e("bridge","v_main",**U); e("bridge","v_wesen",**U); e("bridge","v_geni",**U); e("v_geni","v_gvault")
e("toolbox","wandler"); e("toolbox","tts"); e("t3d","godot")
o.bounds=[{"kind":"region","label":"Docker: Obsidian-Container" if LANG=="de" else "Docker: Obsidian containers","wraps":["v_main","v_wesen"]}]
c=o.card
c("cyan",T("Wesen-Kern (Details: 2 Diagramme)","Being core (details: 2 diagrams)"),
  [T("Selbstbild: Flarum-Feeder, Innenleben (LangGraph), Selbstmodell, Welt-Brücke nach events","Self-image: Flarum feeder, inner life (LangGraph), self-model, world bridge into events"),
   T("LangGraph-Spiegel: liest entity_thinking_log, schreibt Checkpoints, kein LLM-Aufruf","LangGraph mirror: reads entity_thinking_log, writes checkpoints, makes no LLM call"),
   T("Weltbild: weltbild.log endet 2026-08-21, Status ungeklärt","Worldview: weltbild.log ends 2026-08-21, status unresolved")])
c("violet",T("Datenbank und RAG (live abgefragt)","Database and RAG (queried live)"),
  [T("108 Tabellen in public, 4 in Schema geni; pgvector, pg_trgm","108 tables in public, 4 in schema geni; pgvector, pg_trgm"),
   T("events 450.567, checkpoints 112.526, rag_embeddings 7.771, entity_slots 8","events 450,567, checkpoints 112,526, rag_embeddings 7,771, entity_slots 8"),
   T("RAG Ring 1: Flarum-Archiv + wissen/, bge-m3 über Ollama, Abruf /rag/suche","RAG ring 1: Flarum archive + wissen/, bge-m3 via Ollama, retrieval at /rag/suche")])
c("emerald",T("Vaults (Details: eigenes Diagramm)","Vaults (details: own diagram)"),
  [T("Obsidian :8443 mit dem ganzen Werkraum, 7 Wesen-Container :8445 bis :8455","Obsidian :8443 with the whole workroom, 7 being containers :8445 to :8455"),
   T("Gemeinsames Haus, GENI-Vaults, Megavault :18108, AI-Strom-Zuhause ×9","Shared house, GENI vaults, Megavault :18108, AI stream homes ×9"),
   T("Bridge :8060: im Code POST /wesen/geni/chat und Vault-Listing von geni/","Bridge :8060: in code POST /wesen/geni/chat and vault listing of geni/")])
c("amber",T("Werkzeuge (Details: eigenes Diagramm)","Tools (details: own diagram)"),
  [T("Toolbox :8035 mit 8 Tabs, Datei-Wandler :8878, Edge-TTS","Toolbox :8035 with 8 tabs, file converter :8878, Edge-TTS"),
   T("Fragen :8055, SystemWeiser :8080, Zensi :8043, Galerie :7777, Bildgenerator :8042","Questions :8055, SystemWeiser :8080, Zensi :8043, gallery :7777, image generator :8042"),
   T("Codexium2: Noxara, Wsfhh; Solarius2: Gabby; Quelle für Wesen-Speicher und Container","Codexium2: Noxara, Wsfhh; Solarius2: Gabby; source for being memory and containers")])
c("rose",T("Korrekturen und Grenzen","Corrections and limits"),
  [T("Korrigiert: kein eigener Entity-Kern-Dienst (Bibliothek im LG-Spiegel), kein Pfeil Wesen → LangGraph","Corrected: no separate entity-core service (library inside the LG mirror), no arrow beings → LangGraph"),
   T("Brücken-Takt, Daemon-Liste und Surface-Tabs nur aus Doku, nicht gezählt","Bridge interval, daemon list and surface tabs from docs only, not counted"),
   T("Pfeile an die Balken laufen renderbedingt zur Balkenmitte","Arrows to the bars converge at the bar center (renderer property)")])
o.views=[
 {"id":"v-plattform","label":T("Plattform","Platform"),"focus":["humans","surface","api","events","pg","kompoase","daemons"],"note":T("Menschen bis Datenbank, plus Live-Kanal.","People to database, plus live channel.")},
 {"id":"v-wesen","label":T("Wesen-Kern","Being core"),"focus":["flarum","innen","selbst","bruecke","lgd","weltbild","wesen","pg","llm","codex2"],"note":T("LangGraph, Selbstmodell, Weltbild, LLMs.","LangGraph, self-model, worldview, LLMs.")},
 {"id":"v-rag","label":"RAG","focus":["rag","pg","llm","api","surface","flarum"],"note":T("Ring 1: Korpora, Embeddings, Abruf.","Ring 1: corpora, embeddings, retrieval.")},
 {"id":"v-vaults","label":"Vaults","focus":["v_main","v_wesen","v_haus","v_geni","v_gvault","v_mega","v_ai","bridge","ai"],"note":T("Alle Vault-Orte und die Bridge.","All vault locations and the bridge.")},
 {"id":"v-werk","label":T("Werkzeuge","Tools"),"focus":["toolbox","tts","wandler","zensi","werk","t3d","godot","codex2"],"note":T("Toolbox, Dienste, 3D, Codexium2.","Toolbox, services, 3D, Codexium2.")}]
o.write()

# ================= 1 Selbstbild =================
a = D("selbstbild", T("flextrawurst Detail: Selbstbild (Innenleben)","flextrawurst detail: self-image (inner life)"),
      T("Wie das Selbstbild der Wesen entsteht: Flarum-Feeder, Innenleben (LangGraph), Selbstmodell, ChromaDB und die Welt-Brücke nach events.",
        "How the beings' self-image arises: Flarum feeder, inner life (LangGraph), self-model, ChromaDB and the world bridge into events."))
a.n("score","backend","reflection_score",T("reflektieren oder nicht","reflect or not"),0,1)
a.n("chroma","database","ChromaDB",T("Erinnerungen je Wesen","memories per being"),0,2)
a.n("flarum","external","Flarum :80","Forum + MySQL",1,0)
a.n("feeder","backend","flarum_feeder",T("Daemon, alle 300 s","daemon, every 300 s"),1,1)
a.n("innen","backend",T("Innenleben","Inner life"),T("LangGraph-Reflexion","LangGraph reflection"),1,2)
a.n("selbst","database",T("Selbstmodell","Self-model"),T("JSON je Wesen","JSON per being"),1,3)
a.n("bruecke","backend",T("Welt-Brücke","World bridge"),T("Selbstmodell → events","self-model → events"),1,4)
a.n("llm","backend",T("Lokale LLMs","Local LLMs"),"hauhau_client + Scheduler",2,2)
a.n("events","database","events",T("Tabelle in PostgreSQL","table in PostgreSQL"),2,4)
a.e("flarum","feeder","MySQL"); a.e("feeder","innen",T("Ereignis","event")); a.e("innen","selbst",T("schreibt","writes"))
a.e("selbst","bruecke","Sync"); a.e("bruecke","events","Events",**V)
a.e("innen","chroma",T("Erinnern","recall"),**U); a.e("innen","llm","Prompt",**V)
a.e("score","innen",fromSide="bottom",toSide="top")
a.card("cyan",T("Selbstbild-Daten","Self-image data"),[
 T("self_model_<Wesen>.json: core, tendencies, current_state, open_questions","self_model_<being>.json: core, tendencies, current_state, open_questions"),
 T("emotional_history_*.jsonl: 12 Dateien (7 Wesen + 5 alte namelessAI)","emotional_history_*.jsonl: 12 files (7 beings + 5 old namelessAI)"),
 T("ChromaDB unter innenleben/chroma_db, 6 Collections laut init_collections.py","ChromaDB under innenleben/chroma_db, 6 collections per init_collections.py")])
a.card("emerald",T("Im Code gelesen","Read in the code"),[
 T("Graph: StateGraph mit reflection_node, memory_writer_node, self_model_integrator","Graph: StateGraph with reflection_node, memory_writer_node, self_model_integrator"),
 T("LLM-Aufrufe über hauhau_client und llm_scheduler (nodes.py)","LLM calls via hauhau_client and llm_scheduler (nodes.py)"),
 T("Feeder: jedes Wesen verarbeitet nur Posts anderer","Feeder: each being processes only posts by others")])
a.card("amber",T("Offen","Open"),[
 T("Brücken-Takt 30 s nur aus Doku 03 (Mai)","Bridge interval of 30 s only from doc 03 (May)"),
 T("Ob Innenleben heute als Dienst läuft: nicht geprüft","Whether inner life runs as a service today: not checked"),
 T("init_collections kennt 6 Wesen, es gibt 7","init_collections knows 6 beings, there are 7")])
a.write()

# ================= 2 LangGraph / Weltbild =================
b = D("langgraph-weltbild", T("flextrawurst Detail: LangGraph, Weltbild, Wesen-Dienste","flextrawurst detail: LangGraph, worldview, being services"),
      T("Der LangGraph-Checkpoint-Spiegel, der Weltbild-Builder und die Dienste der Codewesen.","The LangGraph checkpoint mirror, the worldview builder and the services of the code beings."))
b.n("kern","backend","entity_kern.py",T("Bibliothek, kein Dienst","library, not a service"),0,1)
b.n("think","database","entity_thinking_log",T("Quelle der Gedanken","source of thoughts"),1,0)
b.n("lgd","backend",T("LangGraph-Spiegel","LangGraph mirror"),"codewesen_lg_daemon",1,1)
b.n("ckpt","database","Checkpoints",T("112.526 Zeilen, 7 Wesen","112,526 rows, 7 beings"),1,2)
b.n("vault","database",T("flarum/ Vault","flarum/ vault"),T("diskussionen als MD","discussions as MD"),2,0)
b.n("weltbild","backend",T("Weltbild-Builder","Worldview builder"),T("Log bis 2026-08-21","log until 2026-08-21"),2,1)
b.n("wmd","database","weltbild.md",T("je Wesen, ca. 3k Token","per being, about 3k tokens"),2,2)
b.n("batch","backend",T("Batch-Generator","Batch generator"),T("Entwurfs-Queue","draft queue"),2,3)
b.n("llm","backend",T("Lokale LLMs","Local LLMs"),"llama-server :11436",3,2)
b.n("dienste","backend",T("Codewesen-Dienste","Being services"),T("Takt, Reaktion ×5, Neugier","tick, reaction ×5, curiosity"),3,3)
b.n("chat","frontend",T("Direktchat :8002","Direct chat :8002"),"codewesen_chat.py",3,4)
b.n("speicher","backend",T("Wesen-Speicher","Being memory"),T("Container, Gruppenchat","containers, group chat"),4,3)
b.e("think","lgd",T("liest","reads")); b.e("kern","lgd","import",variant="dashed",**V); b.e("lgd","ckpt","Saver")
b.e("vault","weltbild",T("liest","reads")); b.e("weltbild","wmd",T("schreibt","writes")); b.e("wmd","batch",T("liest","reads"))
b.e("weltbild","llm","LLM",fromSide="bottom",toSide="left")
b.e("dienste","llm","LLM"); b.e("chat","dienste","Chat"); b.e("speicher","dienste",T("Speicher","memory"),**U)
b.card("cyan",T("LangGraph (im Code gelesen)","LangGraph (read in the code)"),[
 T("Spiegel: liest den neuesten entity_thinking_log-Eintrag, schreibt State per PostgresSaver","Mirror: reads the newest entity_thinking_log entry, writes state via PostgresSaver"),
 T("Der aktive Graph ruft kein LLM auf und erzeugt keinen Gedanken","The active graph calls no LLM and creates no thought"),
 T("thread_id codewesen-<Name>: 7 Wesen mit je 14.585 bis 14.930 Checkpoints (live abgefragt)","thread_id codewesen-<name>: 7 beings with 14,585 to 14,930 checkpoints each (queried live)"),
 T("Alte namelessAI-Threads daneben, je ca. 1.400","Old namelessAI threads alongside, about 1,400 each")])
b.card("amber","Weltbild" if LANG=="de" else "Worldview",[
 T("Liest flarum/diskussionen, Übersicht ohne LLM, dann weltbild.md je Wesen per LLM","Reads flarum/diskussionen, overview without LLM, then weltbild.md per being via LLM"),
 T("weltbild.log endet 2026-08-21 mit 'leere Antwort'-Warnungen","weltbild.log ends 2026-08-21 with 'empty answer' warnings"),
 T("Läuft er seitdem? Nicht geklärt: Doku 09 und 54 widersprechen sich, ein systemd-Status ist hier nicht abfragbar","Does it run since then? Unresolved: docs 09 and 54 contradict each other, systemd status cannot be queried here")])
b.card("emerald",T("Wesen-Dienste (Doku 54, August)","Being services (doc 54, August)"),[
 T("Takt, Batch-Generator, Reaktion ×5, Forum-Neugier, Engagement, Chat","Tick, batch generator, reaction ×5, forum curiosity, engagement, chat"),
 T("Speicher, Container, Gruppenchat: laut Quelltext aus Codexium2 übernommen","Memory, containers, group chat: taken over from Codexium2 per source comments"),
 T("entity-kern.service war am 2026-08-14 disabled, Funktionen laufen im LG-Daemon mit","entity-kern.service was disabled on 2026-08-14, its functions run inside the LG daemon")])
b.write()

# ================= 3 Datenbank / RAG =================
r = D("datenbank-rag", T("flextrawurst Detail: PostgreSQL, RAG, Events-Kanal","flextrawurst detail: PostgreSQL, RAG, event channel"),
      T("PostgreSQL mit pgvector, das RAG Ring 1 und der Events-Kanal für Live-Updates.","PostgreSQL with pgvector, RAG ring 1 and the event channel for live updates."))
r.n("vault","database",T("flarum/ Vault","flarum/ vault"),"diskussionen/*.md",0,0)
r.n("ingest","backend","rag_ingest.py",T("Chunks + Embedding","chunks + embedding"),0,1)
r.n("pgrag","database",T("rag_* (5 Tabellen)","rag_* (5 tables)"),T("7.771 Chunks, pgvector","7,771 chunks, pgvector"),0,2)
r.n("retrieve","backend","rag_retrieve.py",T("0,7 Vektor + 0,3 Text","0.7 vector + 0.3 text"),0,3)
r.n("api","backend","Welt-API /rag/suche" if LANG=="de" else "World API /rag/suche",T("admin- oder entity-Auth","admin or entity auth"),0,4)
r.n("wissen","database","wissen/",T("120 MD-Dateien","120 MD files"),1,0)
r.n("ollama","backend","Ollama :11434",T("bge-m3, 1024 Dim.","bge-m3, 1024 dims"),1,2)
r.n("agent","backend","browser_agent",T("Aktion rag_erkunden","action rag_erkunden"),1,3)
r.n("tab","frontend",T("Surface RAG-Tab","Surface RAG tab"),T("Daniel schaut zu","Daniel watches"),1,4)
r.n("vorlese","backend","vorlese_daemon",T("Billiges Vorlesen","cheap pre-reading"),2,3)
r.n("pge","database","events",T("450.567 Zeilen","450,567 rows"),3,0)
r.n("trig","backend","trg_notify_events","AFTER INSERT",3,1)
r.n("chan","messagebus","events_stream",T("NOTIFY-Kanal","NOTIFY channel"),3,2)
r.n("sse","backend","events_stream_api","GET /events/stream",3,3)
r.n("surf","frontend","Surface :8787","EventSource",3,4)
r.e("vault","ingest",T("liest","reads")); r.e("wissen","ingest",T("liest","reads")); r.e("ingest","pgrag",T("schreibt","writes"))
r.e("ingest","ollama","Embed"); r.e("retrieve","ollama","Embed"); r.e("pgrag","retrieve",T("Suche","search"))
r.e("retrieve","api",T("Treffer","hits")); r.e("api","tab",**V); r.e("api","agent")
r.e("pge","trig"); r.e("trig","chan","NOTIFY"); r.e("chan","sse","LISTEN"); r.e("sse","surf","SSE")
r.e("chan","vorlese","LISTEN"); r.e("vorlese","ollama","Embed",fromSide="left",toSide="bottom")
r.card("violet",T("PostgreSQL (live abgefragt 2026-10-01, nur gelesen)","PostgreSQL (queried live 2026-10-01, read only)"),[
 T("108 Tabellen in public, 4 im Schema geni; Erweiterungen pgvector, pg_trgm","108 tables in public, 4 in schema geni; extensions pgvector, pg_trgm"),
 T("Größte Präfixe: entity_ 16, group_ 8, wesen_ 6, rag_ 5, human_ 4, mw_ 4, post_ 4, splitter_ 4","Largest prefixes: entity_ 16, group_ 8, wesen_ 6, rag_ 5, human_ 4, mw_ 4, post_ 4, splitter_ 4"),
 T("Zeilen: events 450.567, checkpoints 112.526, rag_embeddings 7.771, entity_slots 8","Rows: events 450,567, checkpoints 112,526, rag_embeddings 7,771, entity_slots 8")])
r.card("cyan",T("RAG Ring 1 (Doku 23, Code)","RAG ring 1 (doc 23, code)"),[
 T("Ring 1 von 8 aus Daniels Konzeptdokument; GENI bewusst nicht im Korpus","Ring 1 of 8 from Daniel's concept document; GENI deliberately not in the corpus"),
 T("Abfrage embedded die Frage per bge-m3, hybride Suche, jede Suche wird protokolliert","The query embeds the question via bge-m3, hybrid search, every search is logged"),
 T("Zugang: Surface-Tab und Wesen per rag_erkunden","Access: surface tab and beings via rag_erkunden")])
r.card("emerald",T("Events-Kanal","Event channel"),[
 T("Trigger auf events sendet NOTIFY mit minimalem Payload","A trigger on events sends NOTIFY with a minimal payload"),
 T("vorlese_daemon lauscht am selben Kanal und vergleicht per Embedding, ohne LLM","vorlese_daemon listens on the same channel and compares by embedding, without an LLM"),
 T("Der Stream trägt nie Inhalte, nur ein Signal; Daten kommen über die REST-Endpunkte","The stream never carries content, only a signal; data comes through the REST endpoints")])
r.write()

# ================= 4 Vaults =================
v = D("vaults", T("flextrawurst Detail: alle Vault-Orte","flextrawurst detail: all vault locations"),
      T("Alle Vault-Orte: Obsidian, Wesen-Vaults, Gemeinsames Haus, GENI, Megavault und AI-Strom-Zuhause.","All vault locations: Obsidian, being vaults, shared house, GENI, Megavault and AI stream homes."))
v.n("ai","database",T("AI-Strom-Zuhause ×9","AI stream homes ×9"),T("_claude bis _haiku","_claude to _haiku"),0,0)
v.n("shared","database","_shared",T("Briefkasten, Bridge, MCP","mailbox, bridge, MCP"),0,1)
v.n("main","database","Obsidian :8443",T("Docker, ganzer Werkraum","Docker, entire workroom"),1,0)
v.n("wc","database",T("Wesen-Container ×7","Being containers ×7"),T("Docker, :8445 bis :8455","Docker, :8445 to :8455"),1,1)
v.n("haus","database",T("Gemeinsames Haus","Shared house"),T("Wesen + dak + System","beings + dak + system"),1,2)
v.n("mega","database","Megavault :18108",T("Gesamtatlas, app.py","total atlas, app.py"),1,3)
v.n("flv","database",T("flarum/ Vault","flarum/ vault"),T("diskussionen als MD","discussions as MD"),1,4)
v.n("bridge","backend",T("Obsidian-Bridge :8060","Obsidian bridge :8060"),"obsidian_api.py",2,0)
v.n("wdirs","database","wesen_vaults/<Wesen>" if LANG=="de" else "wesen_vaults/<being>",T("privat, selbst geschrieben","private, self-written"),2,1)
v.n("geni","database","GENI :8020",T("Gedächtnis, Hörer","memory, listener"),3,0)
v.n("gv","database",T("GENI-Vaults","GENI vaults"),T("Doku + Inbox","docs + inbox"),3,1)
v.e("ai","shared",T("Briefe","letters")); v.e("bridge","main",**U); v.e("wdirs","wc","Mount",**U)
v.e("bridge","geni","Chat",**V); v.e("geni","gv","Inbox")
v.card("emerald",T("Vault-Orte (im Dateisystem gesehen)","Vault locations (seen in the file system)"),[
 T("wesen_vaults: 7 Wesen + TestWesen + _altes_haus_2026-08-02","wesen_vaults: 7 beings + TestWesen + _altes_haus_2026-08-02"),
 T("geni_vaults_gemeinsam: geni_dokumentation, geni_inbox","geni_vaults_gemeinsam: geni_dokumentation, geni_inbox"),
 T("AI-Zuhause: _claude, _claudeweb, _codex, _gemini, _glm, _gpt, _grok, _haiku, _kimi","AI homes: _claude, _claudeweb, _codex, _gemini, _glm, _gpt, _grok, _haiku, _kimi")])
v.card("cyan",T("Zugriff (Doku 30, 41)","Access (docs 30, 41)"),[
 T("Haupt-Obsidian mountet /root/werkraum komplett","The main Obsidian mounts /root/werkraum completely"),
 T("Wesen-Container: eigener HTTPS-Port je Wesen, Login-geschützt, Tippen per xdotool","Being containers: own HTTPS port per being, login protected, typing via xdotool"),
 T("Gemeinsames Haus ist getrennt von den privaten Wesen-Vaults","The shared house is separate from the private being vaults")])
v.card("amber",T("Belegt und offen","Verified and open"),[
 T("Live lauschend: 8445, 8450, 8455, 18108","Listening live: 8445, 8450, 8455, 18108"),
 T("Bridge: im Code POST /wesen/geni/chat und Vault-Listing von geni/","Bridge: in code POST /wesen/geni/chat and vault listing of geni/"),
 T("Nicht eingezeichnet: Zugriff der Bridge auf die Wesen-Vaults (nur Doku)","Not drawn: bridge access to the being vaults (docs only)")])
v.write()

# ================= 5 Werkzeuge =================
t = D("werkzeuge", T("flextrawurst Detail: Toolbox, Dienste, Codexium2","flextrawurst detail: toolbox, services, Codexium2"),
      T("Toolbox mit acht Tabs, weitere Dienste, das Codexium2/Solarius2-Testbed, KompOase, 3D und Live-Spiegel.","Toolbox with eight tabs, further services, the Codexium2/Solarius2 testbed, KompOase, 3D and the live mirror."))
tabs=[("tts","TTS","Edge-TTS"),("sound","Soundboard",T("Bibliothek","library")),("diktat",T("Diktat","Dictation"),T("Browser-API","browser API")),("uebers",T("Übersetzen","Translate"),"Tab"),("ocr","OCR","Tab"),("doku",T("Dokumente","Documents"),"Tab"),("web",T("Webarchiv","Web archive"),"Tab"),("wandler",T("Datei-Wandler","File converter"),":8878")]
for i,(id,l,sl) in enumerate(tabs): t.n(id,"frontend",l,sl,0,0,w=110,x=40+140*i)
t.n("edge","external","Edge-TTS","Microsoft Neural",1,0,w=110,x=40)
t.e("tts","edge",**V)
t.bounds=[{"kind":"region","label":T("Toolbox :8035 (tts_service.py, ein Login)","Toolbox :8035 (tts_service.py, one login)"),"wraps":[i for i,_,_ in tabs]}]
t.n("fragen","backend",T("Fragen :8055","Questions :8055"),"qwen2.5:0.5b + SQL",2,0)
t.n("sysw","backend","SystemWeiser :8080","llama-server + Bridge",2,1)
t.n("zensi","backend","Zensi :8043",T("Spiegel-Sandbox","mirror sandbox"),2,2)
t.n("galerie","backend",T("Galerie :7777","Gallery :7777"),T("Proxy der Welt-API","proxy of the World API"),2,3)
t.n("bild","backend",T("Bildgenerator :8042","Image generator :8042"),T("Dienst","service"),2,4)
t.n("pg","database","PostgreSQL","flextrawurst",3,0)
t.n("llm","backend",T("Lokale LLMs","Local LLMs"),"llama-server",3,1)
t.n("bridge","backend",T("Obsidian-Bridge :8060","Obsidian bridge :8060"),"obsidian_api.py",3,2)
t.n("api","backend",T("Welt-API :8030","World API :8030"),"FastAPI",3,3)
t.e("fragen","pg","SQL",**V); t.e("sysw","llm","LLM",**V); t.e("sysw","bridge","Bridge",**V); t.e("api","galerie","Proxy",**U)
t.n("testbed","frontend","Codexium2 / Solarius2","Noxara, Wsfhh, Gabby",4,0)
t.n("surface","frontend","Surface :8787","Node.js",4,1)
t.n("kompo","frontend","KompOase :8900",T("Splitter-Theater","Splinter theater"),4,2)
t.n("ai","external",T("AI-Ströme","AI streams"),T("Claude, Codex u.a.","Claude, Codex etc."),4,3)
t.n("live","frontend",T("Live-Spiegel","Live mirror"),T(":8098 bis :8100",":8098 to :8100"),4,4)
t.e("surface","testbed","Testbed"); t.e("surface","kompo","Proxy"); t.e("ai","live","Logs")
t.n("t3d","backend","3D-MCP :8090","Blender + Godot",5,0)
t.n("godot","external","Blender / Godot","headless",5,1)
t.e("t3d","godot")
t.card("amber","Toolbox",[
 T("Acht Tabs, ein Login","Eight tabs, one login"),
 T("Textablage im Browser (localStorage) verbindet die Tabs","A text shelf in the browser (localStorage) connects the tabs"),
 T("TTS schneidet Text in ca. 280-Zeichen-Stücke wegen Microsoft-Drosselung","TTS cuts text into pieces of about 280 characters because of Microsoft throttling")])
t.card("cyan","Codexium2 / Solarius2",[
 T("Ordner codexium2: Noxara, Wsfhh; solarius2: Gabby","Folder codexium2: Noxara, Wsfhh; solarius2: Gabby"),
 T("Testbed-Spawner im 8787-Server, Frontend wesen_chat.html (Doku 21)","Testbed spawner in the 8787 server, frontend wesen_chat.html (doc 21)"),
 T("Quelle für Speicher, Container, Gruppenchat der Wesen (Quelltext-Kommentare)","Source for memory, containers and group chat of the beings (source comments)")])
t.card("rose",T("Live und Belege","Live and evidence"),[
 T("Live lauschend: 8035, 8043, 8055, 8080, 7777, 8042, 8090","Listening live: 8035, 8043, 8055, 8080, 7777, 8042, 8090"),
 T("Nur Doku: Galerie-Proxy über Port 7777 (api.py nennt _PROXY_ALLOWED_PORT)","Docs only: gallery proxy via port 7777 (api.py names _PROXY_ALLOWED_PORT)")])
t.write()
print(LANG, "fertig")
