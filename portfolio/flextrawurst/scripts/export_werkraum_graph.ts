// Liest den kompletten Werkraum und baut einen echten Graphen mit allen Dateien und Verbindungen.
import { readFileSync, writeFileSync, mkdirSync, readdirSync, statSync, existsSync,
         openSync, readSync, closeSync } from "node:fs";
import { join, relative, basename, extname } from "node:path";

const ROOT = "/root/werkraum";
const OUT  = "out/process_camera/werkraum_graph.json";
const EXCERPT_LIMIT = 500;
const LARGE_FILE    = 40_000;
// Ab LARGE_FILE wird eine Datei nicht mehr komplett gelesen, sondern nur ihr Kopf.
// Grund: ein vollständiges readFileSync() auf den großen Beständen im Werkraum
// (SQLite-Register, Terminal-Logs, Videos, RAM-Snapshots) sprengt den V8-Heap.
const HEAD_BYTES    = 8_192;

const SKIP_DIRS = new Set([
  // Infrastruktur/Cache
  "__pycache__", "approvals", ".git", ".obsidian", ".venv", ".venv-agent", "venv",
  "node_modules", "graphify-out", "backups", "bilder", "quellen",
  "watchdog_venv", ".pytest_cache", ".claude", ".agent", "werkraum",
  "Meine-Textsammlung-erfahrun-frh-mit-ai",
  // Leere oder nicht relevante Ordner
  "telemetry", "brain", "tools", "watchdog", "agents", "reports", "templates",
  // Riesige Datenspeicher (GENI)
  "gedaechtnis", "sinne", "zugriffsschichten", "verbindungen",
  // Codewesen-Masse (processed posts, archives, drafts)
  "spiegel", "archiv", "processed", "posted", "entwuerfe",
  "gedanken", "fehler", "gespräche", "werkzeuge",
  // Erkenntnis-Masse
  "spiegelagenten",
  // Logs und SSL
  "ssl",
]);
const SKIP_EXT        = new Set([".pyc", ".pyo", ".png", ".jpg", ".jpeg", ".pdf",
                                   ".tar", ".gz", ".sql", ".xwd", ".pem", ".lock"]);
const SKIP_NAME_PARTS = [".bak", ".save", "package-lock", "pyvenv.cfg", "CACHEDIR",
                          "chunk_", ".graphify_", "nohup.out", "dateiname", "baum:",
                          "info:", "s\n", ".pid", ".xwd"];
const SKIP_NAMES      = new Set(["hello.txt", "dateiname", "s", "baum:", "info:"]);

interface GNode {
  id:      string;
  label:   string;
  type:    string;
  group:   string;
  size:    number;
  lines:   number;
  mtime:   string;
  excerpt: string;
  large:   boolean;
}
interface GLink {
  source: string;
  target: string;
  kind:   string;
}

function walk(startDir: string): string[] {
  const out: string[] = [];
  const ALLOWED_DOTS = new Set([".env.example", ".obsidianignore", ".gitignore"]);
  const queue: string[] = [startDir];
  const visited = new Set<string>();
  while (queue.length) {
    const dir = queue.pop()!;
    if (visited.has(dir)) continue;
    visited.add(dir);
    let entries: string[];
    try { entries = readdirSync(dir); } catch { continue; }
    for (const name of entries) {
      if (SKIP_DIRS.has(name)) continue;
      if (name.startsWith(".") && !ALLOWED_DOTS.has(name)) continue;
      const full = join(dir, name);
      let st;
      try { st = statSync(full); } catch { continue; }
      if (st.isSymbolicLink()) continue; // Symlinks überspringen
      if (st.isDirectory()) {
        if (!visited.has(full)) queue.push(full);
      } else {
        if (SKIP_EXT.has(extname(name).toLowerCase())) continue;
        if (SKIP_NAMES.has(name)) continue;
        if (SKIP_NAME_PARTS.some(p => name.includes(p))) continue;
        if (name.endsWith(".save") || /\.save\.\d+$/.test(name)) continue;
        out.push(relative(ROOT, full));
      }
    }
  }
  return out;
}

function groupOf(rel: string): string {
  const parts = rel.split("/");
  if (parts.length === 1) return "werkraum-root";
  const [a, b, c] = parts;
  if (a === "agent" && b === "dak_gord_system") {
    if (!c) return "dak_gord_system";
    if (c === "kerne")           return "kerne";
    if (c === "graph" && parts[3] === "nodes")  return "graph/nodes";
    if (c === "graph" && parts[3] === "tools")  return "graph/tools";
    if (c === "graph" && parts[3] === "evals")  return "graph/evals";
    if (c === "graph")           return "graph";
    if (c === "verfassung")      return "verfassung";
    if (c === "verfassung_neu")  return "verfassung_neu";
    if (c === "verfassung_altbestand") return "verfassung_altbestand";
    if (c === "verfassung_prueffassungen") return "verfassung_prueffassungen";
    if (c === "aufforderungen")  return "aufforderungen";
    if (c === "spuren")          return "spuren";
    if (c === "gedaechtnis_daten") return "gedaechtnis_daten";
    if (c === "graphen")         return "graphen";
    if (c === "herz")            return "herz";
    return "dak_gord_system";
  }
  if (a === "agent")       return "agent-meta";
  if (a === "projekt")     return "projekt";
  if (a === "erkenntnis")  return "erkenntnis";
  if (a === "flarum")      return "flarum";
  if (a === "geni")        return "geni";
  if (a === "innenleben")  return "innenleben";
  if (a === "codewesen") {
    // Einzelne Wesen als eigene Gruppen
    if (b && b.startsWith("namelessAI_")) return b;
    return "codewesen";
  }
  if (a === "mission")     return "struktur";
  if (a === "policies")    return "struktur";
  if (a === "decisions")   return "struktur";
  if (a === "state")       return "state";
  if (a === "wissen")      return "wissen";
  if (a === "scripts")     return "scripts";
  if (a === "logs")        return "logs";
  if (a === "memory")      return "memory";
  if (a === "app")         return "app";
  if (a === "tests")       return "tests";
  if (a === "skills")      return "skills";
  return a;
}

const PKG_PREFIX = "agent.dak_gord_system.";

function parseImports(content: string): string[] {
  const mods: string[] = [];
  const fromRe = /^from\s+([\w.]+)\s+import/gm;
  const impRe  = /^import\s+([\w.]+)/gm;
  let m: RegExpExecArray | null;
  while ((m = fromRe.exec(content)) !== null) mods.push(m[1]);
  while ((m = impRe.exec(content))  !== null) mods.push(m[1]);
  const targets: string[] = [];
  for (let mod of mods) {
    mod = mod.replace(/^\.+/, "");
    // Versuche Auflösung als werkraum-Paket
    const cand1 = mod.replace(/\./g, "/") + ".py";
    if (existsSync(join(ROOT, cand1))) { targets.push(cand1); continue; }
    // dak_gord_system-Paket
    if (mod.startsWith(PKG_PREFIX)) mod = "agent/dak_gord_system/" + mod.slice(PKG_PREFIX.length).replace(/\./g, "/");
    else if (mod.startsWith("agent.")) {
      mod = mod.replace(/\./g, "/");
    } else continue;
    const cand2 = mod + ".py";
    if (existsSync(join(ROOT, cand2))) targets.push(cand2);
  }
  return [...new Set(targets)];
}

const paths = walk(ROOT);
const nodes: GNode[] = [];
const links: GLink[] = [];
const nodeSet = new Set<string>();

// Secret-Redaktion: verhindert, dass Credentials in den oeffentlich
// ausgelieferten Graph-Export (out/process_camera/werkraum_graph.json) gelangen.
function redactSecrets(text: string): string {
  return text
    // DB-URIs mit Passwort: postgresql://user:pass@host -> postgresql://user:***@host
    .replace(/((?:postgres(?:ql)?|mysql|mongodb(?:\+srv)?|redis):\/\/[^:\s/@]+:)[^@\s"']+@/gi, "$1***REDACTED***@")
    // generische Zuweisungen von PASSWORD/SECRET/TOKEN/API_KEY/MASTER_KEY
    .replace(/((?:password|passwd|secret|token|api[_-]?key|master[_-]?key|bridge[_-]?token|jwt[_-]?secret)\s*[:=]\s*["']?)[^\s"'#]+/gi, "$1***REDACTED***");
}

for (const rel of paths) {
  const full = join(ROOT, rel);
  let st;
  try { st = statSync(full); } catch { continue; }
  const ext  = extname(rel).slice(1) || "txt";
  const large = st.size > LARGE_FILE;
  // Kleine Dateien ganz lesen (Zeilenzahl + Auszug). Große nur am Kopf anlesen:
  // der Auszug braucht EXCERPT_LIMIT Zeichen, eine Zeilenzahl über hunderte MB
  // wäre weder brauchbar noch bezahlbar.
  let content = "";
  let kopf    = "";
  if (!large) {
    try { content = readFileSync(full, "utf-8"); kopf = content; } catch { /* skip */ }
  } else {
    try {
      const fd  = openSync(full, "r");
      const buf = Buffer.alloc(HEAD_BYTES);
      const n   = readSync(fd, buf, 0, HEAD_BYTES, 0);
      closeSync(fd);
      kopf = buf.subarray(0, n).toString("utf-8");
    } catch { /* skip */ }
  }
  nodes.push({
    id:      rel,
    label:   basename(rel, "." + ext),
    type:    ext,
    group:   groupOf(rel),
    size:    st.size,
    lines:   content ? content.split("\n").length : 0,
    mtime:   st.mtime.toISOString(),
    excerpt: redactSecrets(kopf.slice(0, EXCERPT_LIMIT)),
    large,
  });
  nodeSet.add(rel);
}

// Inhalte werden bei Bedarf gelesen statt alle gleichzeitig gehalten: der Werkraum
// enthält hunderttausende Dateien, deren gesammelter Text jeden Heap sprengt.
// Gecacht wird nur bis CACHE_BUDGET; darüber hinaus wird erneut von Platte gelesen.
// Die fachliche Regel bleibt: nur Dateien bis CONTENT_MAX tragen zur Verlinkung bei.
const CONTENT_MAX  = 200_000;
const CACHE_BUDGET = 400_000_000;
const contentCache = new Map<string, string>();
const nodeSize     = new Map<string, number>();
for (const node of nodes) nodeSize.set(node.id, node.size);
let cacheBytes = 0;

function inhalt(id: string): string {
  const treffer = contentCache.get(id);
  if (treffer !== undefined) return treffer;
  if ((nodeSize.get(id) ?? Number.MAX_SAFE_INTEGER) > CONTENT_MAX) return "";
  let text = "";
  try { text = readFileSync(join(ROOT, id), "utf-8"); } catch { /* skip */ }
  if (cacheBytes + text.length <= CACHE_BUDGET) {
    contentCache.set(id, text);
    cacheBytes += text.length;
  }
  return text;
}

const linkSet = new Set<string>();
function addLink(src: string, tgt: string, kind: string) {
  if (src === tgt || !nodeSet.has(src) || !nodeSet.has(tgt)) return;
  const key = `${src}|${tgt}|${kind}`;
  if (!linkSet.has(key)) { linkSet.add(key); links.push({ source: src, target: tgt, kind }); }
}

// 1. Python-Imports
for (const node of nodes) {
  if (node.type !== "py") continue;
  const content = inhalt(node.id);
  for (const target of parseImports(content)) addLink(node.id, target, "import");
}

// 2. Absolute Pfad-Referenzen (Dateien <100KB die andere Dateien per absolutem Pfad nennen)
const ABS_RE = new RegExp(ROOT.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + "/([\\w./ -]+)", "g");
for (const node of nodes) {
  if (node.size > 100_000) continue;
  const content = inhalt(node.id);
  let m: RegExpExecArray | null;
  ABS_RE.lastIndex = 0;
  while ((m = ABS_RE.exec(content)) !== null) {
    const candidate = m[1].replace(/\\/g, "/").replace(/\/$/, "").trim();
    if (nodeSet.has(candidate)) addLink(node.id, candidate, "ref");
  }
}

// 3. Bekannte Dateinamen als Strings (langer eindeutiger Basename >12 Zeichen, nur py/md als Quelle)
const longNames = new Map<string, string>();
for (const id of nodeSet) {
  const base = basename(id);
  if (base.length > 12 && !base.includes(".save") && !base.includes("chunk")) {
    longNames.set(base, id);
  }
}
// Ein Durchlauf pro Datei statt einer Schleife über alle Namen: der Text wird in
// Wort-Kandidaten zerlegt und jedes Token in longNames nachgeschlagen.
const TOKEN_RE = /[\w.-]{6,}/g;
for (const node of nodes) {
  if (node.type !== "py" && node.type !== "md") continue;
  if (node.size > 80_000) continue;
  const content = inhalt(node.id);
  if (!content) continue;
  TOKEN_RE.lastIndex = 0;
  const gesehen = new Set<string>();
  let t: RegExpExecArray | null;
  while ((t = TOKEN_RE.exec(content)) !== null) {
    const token = t[0];
    if (gesehen.has(token)) continue;
    gesehen.add(token);
    const target = longNames.get(token);
    if (target) addLink(node.id, target, "ref");
  }
}

// 4. Wikilinks: [[Dateiname]] oder [[ordner/datei]] in .md-Dateien
const WIKILINK_RE = /\[\[([^\]]+)\]\]/g;
const labelIndex = new Map<string, string>(); // label/basename → node id
for (const id of nodeSet) {
  const base = id.split("/").pop()!;
  const noext = base.replace(/\.[^.]+$/, "");
  labelIndex.set(base.toLowerCase(), id);
  labelIndex.set(noext.toLowerCase(), id);
  labelIndex.set(id.toLowerCase(), id);
}
for (const node of nodes) {
  if (node.type !== "md") continue;
  if (node.size > 100_000) continue;
  const content = inhalt(node.id);
  let m: RegExpExecArray | null;
  WIKILINK_RE.lastIndex = 0;
  while ((m = WIKILINK_RE.exec(content)) !== null) {
    const target = labelIndex.get(m[1].toLowerCase().trim());
    if (target) addLink(node.id, target, "wikilink");
  }
}

// 5. Ordner-Cluster: Dateien im selben Unterordner (Ring-Topologie)
const folderMap = new Map<string, string[]>();
for (const id of nodeSet) {
  const slash = id.lastIndexOf("/");
  const folder = slash === -1 ? "__root__" : id.slice(0, slash);
  if (!folderMap.has(folder)) folderMap.set(folder, []);
  folderMap.get(folder)!.push(id);
}
for (const [folder, members] of folderMap) {
  if (folder === "__root__") continue;
  const jsonOnly = members.every(id => id.endsWith(".json") || id.endsWith(".jsonl"));
  // JSON-only-Ordner: immer Ring (bis 60), gemischte Ordner: nur bis 15
  const limit = jsonOnly ? 60 : 15;
  if (members.length < 2 || members.length > limit) continue;
  for (let i = 0; i < members.length; i++) {
    addLink(members[i], members[(i + 1) % members.length], "folder");
  }
}

// 6. JSON-Referenzen: py/ts/md die einen JSON-Dateinamen im Inhalt erwähnen
const jsonNodes = nodes.filter(n => n.type === "json");
// Basename → alle JSON-Knoten mit diesem Namen (mehrere Ordner können ihn tragen).
const jsonNachName = new Map<string, string[]>();
for (const jn of jsonNodes) {
  const base = basename(jn.id);
  if (base.length <= 6) continue;
  const liste = jsonNachName.get(base);
  if (liste) liste.push(jn.id); else jsonNachName.set(base, [jn.id]);
}
// Ein Dateiname wie "package.json" liegt im Werkraum 1205-mal. Seine Erwähnung in
// einem Text sagt deshalb nicht, WELCHE gemeint ist — eine Kante zu allen 1205 ist
// keine Auskunft, sondern Rauschen. Eindeutige Namen werden weiterhin überall
// verbunden. Ein mehrdeutiger Name verbindet nur die Kandidaten, die dem Text im
// Ordnerbaum am nächsten liegen; gibt es keinen gemeinsamen Pfad oder liegen zu
// viele gleich nah, trägt der Name keine Auskunft und es entsteht keine Kante.
const AMBIG_MAX_TIE = 4;

function ordnerVonPfad(id: string): string {
  const i = id.lastIndexOf("/");
  return i === -1 ? "" : id.slice(0, i);
}
function gemeinsameTiefe(a: string, b: string): number {
  if (a === "" || b === "") return 0;
  const x = a.split("/"), y = b.split("/");
  let i = 0;
  while (i < x.length && i < y.length && x[i] === y[i]) i++;
  return i;
}
function jsonZiele(quellOrdner: string, token: string): string[] {
  const kandidaten = jsonNachName.get(token);
  if (!kandidaten) return [];
  if (kandidaten.length === 1) return kandidaten;
  let beste = 0;
  let treffer: string[] = [];
  for (const k of kandidaten) {
    const tiefe = gemeinsameTiefe(quellOrdner, ordnerVonPfad(k));
    if (tiefe === 0 || tiefe < beste) continue;
    if (tiefe > beste) { beste = tiefe; treffer = [k]; } else treffer.push(k);
  }
  return treffer.length <= AMBIG_MAX_TIE ? treffer : [];
}

for (const node of nodes) {
  if (node.type !== "py" && node.type !== "ts" && node.type !== "md") continue;
  if (node.size > 100_000) continue;
  const content = inhalt(node.id);
  if (!content) continue;
  const quellOrdner = ordnerVonPfad(node.id);
  TOKEN_RE.lastIndex = 0;
  const gesehen = new Set<string>();
  let t: RegExpExecArray | null;
  while ((t = TOKEN_RE.exec(content)) !== null) {
    const token = t[0];
    if (gesehen.has(token)) continue;
    gesehen.add(token);
    for (const ziel of jsonZiele(quellOrdner, token)) addLink(node.id, ziel, "uses-json");
  }
}

// 7. JSON ↔ Geschwister-Code: JSON-Dateien mit .py/.md/.ts im gleichen Ordner verknüpfen
for (const jn of jsonNodes) {
  const slash = jn.id.lastIndexOf("/");
  const folder = slash === -1 ? "" : jn.id.slice(0, slash);
  const siblings = folderMap.get(folder === "" ? "__root__" : folder) ?? [];
  for (const sib of siblings) {
    if (sib === jn.id) continue;
    const ext = sib.split(".").pop() ?? "";
    if (ext === "py" || ext === "md" || ext === "ts") {
      addLink(jn.id, sib, "owns");
    }
  }
}

// ---------------------------------------------------------------------------
// 8. Ausgabe als Kacheln.
//
// Der Werkraum ist zu groß für einen einzelnen JSON-String: V8 begrenzt die
// Länge eines Strings, und JSON.stringify() über alle Knoten bricht mit
// RangeError ab, lange bevor der Heap voll ist. Statt einer Datei wird der
// Graph deshalb in Regionen zerlegt. Eine Region ist ein Ordner-Teilbaum mit
// höchstens REGION_MAX Knoten. Ist ein Teilbaum größer, bilden seine direkten
// Dateien eine eigene Region, und jeder Unterordner wird für sich zerlegt.
//
// index.json trägt nur die Regionsebene. Die Knoten einer Region liegen in
// r/<region>.json und werden erst geladen, wenn die Sichtreichweite sie
// erfasst. Kein Knoten geht dabei verloren — er wandert nur in eine Kachel.
// ---------------------------------------------------------------------------
const GRAPH_DIR  = "out/process_camera/graph";
const REGION_MAX = 3_000;
const exportiertAm = new Date().toISOString();

function ordnerVon(id: string): string {
  const i = id.lastIndexOf("/");
  return i === -1 ? "" : id.slice(0, i);
}

// Direkte Dateien je Ordner, und die Ordnerhierarchie darüber.
const direkt = new Map<string, string[]>();
for (const node of nodes) {
  const d = ordnerVon(node.id);
  const liste = direkt.get(d);
  if (liste) liste.push(node.id); else direkt.set(d, [node.id]);
}
const kinder = new Map<string, Set<string>>();
for (const d of direkt.keys()) {
  let pfad = d;
  while (pfad !== "") {
    const eltern = ordnerVon(pfad);
    const menge = kinder.get(eltern);
    if (menge) menge.add(pfad); else kinder.set(eltern, new Set([pfad]));
    pfad = eltern;
  }
}

// Wie viele Knoten hängen unter einem Ordner insgesamt?
const teilbaum = new Map<string, number>();
function zaehle(ordner: string): number {
  const schon = teilbaum.get(ordner);
  if (schon !== undefined) return schon;
  let n = (direkt.get(ordner) ?? []).length;
  for (const k of kinder.get(ordner) ?? []) n += zaehle(k);
  teilbaum.set(ordner, n);
  return n;
}
zaehle("");

interface Region {
  id: string; pfad: string; ganzerTeilbaum: boolean; knoten: string[];
}
const regionen: Region[] = [];
const regionVonKnoten = new Map<string, string>();
const vergeben = new Map<string, number>();

function slug(pfad: string): string {
  const roh = pfad === "" ? "__wurzel__" : pfad.replace(/[^\w.-]+/g, "_");
  return roh.slice(0, 120);
}
function eindeutig(basis: string): string {
  const n = vergeben.get(basis) ?? 0;
  vergeben.set(basis, n + 1);
  return n === 0 ? basis : `${basis}~${n}`;
}
function neueRegion(pfad: string, knoten: string[], ganzerTeilbaum: boolean) {
  // Auch ein einzelner Ordner kann mehr als REGION_MAX direkte Dateien tragen;
  // dann wird er in mehrere gleich benannte Kacheln aufgeteilt.
  for (let i = 0; i < knoten.length; i += REGION_MAX) {
    const teil = knoten.slice(i, i + REGION_MAX);
    const id = eindeutig(slug(pfad) + (ganzerTeilbaum ? "" : ".direkt"));
    regionen.push({ id, pfad, ganzerTeilbaum, knoten: teil });
    for (const k of teil) regionVonKnoten.set(k, id);
  }
}
function sammle(ordner: string, ziel: string[]) {
  for (const id of direkt.get(ordner) ?? []) ziel.push(id);
  for (const k of kinder.get(ordner) ?? []) sammle(k, ziel);
}
function zerlege(ordner: string) {
  if (zaehle(ordner) <= REGION_MAX) {
    const knoten: string[] = [];
    sammle(ordner, knoten);
    if (knoten.length) neueRegion(ordner, knoten, true);
    return;
  }
  const eigene = direkt.get(ordner) ?? [];
  if (eigene.length) neueRegion(ordner, eigene.slice(), false);
  for (const k of kinder.get(ordner) ?? []) zerlege(k);
}
zerlege("");

// Kanten einsortieren: innerhalb einer Region, oder über ihren Rand hinaus.
const innen    = new Map<string, GLink[]>();
const rand     = new Map<string, GLink[]>();
const zwischen = new Map<string, number>();
for (const l of links) {
  const a = regionVonKnoten.get(l.source);
  const b = regionVonKnoten.get(l.target);
  if (!a || !b) continue;
  if (a === b) {
    const liste = innen.get(a);
    if (liste) liste.push(l); else innen.set(a, [l]);
  } else {
    const key = `${a}|${b}`;
    zwischen.set(key, (zwischen.get(key) ?? 0) + 1);
    for (const r of [a, b]) {
      const liste = rand.get(r);
      if (liste) liste.push(l); else rand.set(r, [l]);
    }
  }
}

mkdirSync(join(GRAPH_DIR, "r"), { recursive: true });
const knotenNach = new Map<string, GNode>();
for (const node of nodes) knotenNach.set(node.id, node);

const indexRegionen: Record<string, unknown>[] = [];
let groessteDatei = 0;
for (const r of regionen) {
  const rKnoten = r.knoten.map(id => knotenNach.get(id)!).filter(Boolean);
  const rInnen  = innen.get(r.id) ?? [];
  const rRand   = (rand.get(r.id) ?? []).map(l => ({
    source: l.source, target: l.target, kind: l.kind,
    quellRegion: regionVonKnoten.get(l.source),
    zielRegion:  regionVonKnoten.get(l.target),
  }));
  // Jede Region wird für sich serialisiert — nie entsteht ein großer String.
  const text = JSON.stringify({
    region: r.id, pfad: r.pfad, exported_at: exportiertAm,
    nodes: rKnoten, links: rInnen, randkanten: rRand,
  });
  writeFileSync(join(GRAPH_DIR, "r", r.id + ".json"), text, "utf-8");
  if (text.length > groessteDatei) groessteDatei = text.length;

  const typen: Record<string, number> = {};
  let bytes = 0;
  let neuste = "";
  for (const n of rKnoten) {
    typen[n.type] = (typen[n.type] ?? 0) + 1;
    bytes += n.size;
    if (n.mtime > neuste) neuste = n.mtime;
  }
  indexRegionen.push({
    id: r.id, pfad: r.pfad, ganzerTeilbaum: r.ganzerTeilbaum,
    knoten: rKnoten.length, bytes, neuste, typen,
    innenkanten: rInnen.length, randkanten: rRand.length,
    datei: `r/${r.id}.json`,
  });
}

const indexKanten: Record<string, unknown>[] = [];
for (const [key, anzahl] of zwischen) {
  const trenner = key.indexOf("|");
  indexKanten.push({ source: key.slice(0, trenner), target: key.slice(trenner + 1), anzahl });
}
writeFileSync(join(GRAPH_DIR, "index.json"), JSON.stringify({
  root: ROOT, exported_at: exportiertAm, region_max: REGION_MAX,
  regionen: indexRegionen, kanten: indexKanten,
}, null, 2), "utf-8");

const kinds: Record<string, number> = {};
for (const l of links) kinds[l.kind] = (kinds[l.kind] ?? 0) + 1;

// Die alte Einzeldatei bleibt erhalten, solange sie überhaupt schreibbar ist —
// der bestehende Explorer liest noch sie. Ist der Graph dafür zu groß, bleibt
// die vorhandene Datei unangetastet, und meta.json hält fest warum.
let einzeldatei = "geschrieben";
try {
  mkdirSync("out/process_camera", { recursive: true });
  writeFileSync(OUT, JSON.stringify({ nodes, links, root: ROOT, exported_at: exportiertAm }), "utf-8");
} catch (e) {
  einzeldatei = `nicht geschrieben: ${e instanceof Error ? e.message : String(e)}`;
}

writeFileSync(join(GRAPH_DIR, "meta.json"), JSON.stringify({
  root: ROOT, exported_at: exportiertAm,
  knoten: nodes.length, kanten: links.length, kantenarten: kinds,
  regionen: regionen.length, region_max: REGION_MAX,
  groesste_regionsdatei_bytes: groessteDatei,
  einzeldatei: { pfad: OUT, status: einzeldatei },
}, null, 2), "utf-8");

console.log(`Werkraum-Graph: ${nodes.length} Knoten, ${links.length} Kanten (${JSON.stringify(kinds)})`);
console.log(`  ${regionen.length} Regionen → ${GRAPH_DIR}/r/ , größte Kachel ${(groessteDatei / 1e6).toFixed(1)} MB`);
console.log(`  Einzeldatei ${OUT}: ${einzeldatei}`);
