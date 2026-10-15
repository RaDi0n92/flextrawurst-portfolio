// Liest echte dak+gord-Systemdaten aus werkraum und exportiert sie als JSON für den Browser.
import { readFileSync, writeFileSync, mkdirSync, readdirSync, existsSync } from "node:fs";
import { join } from "node:path";

const WERKRAUM = "/root/werkraum/agent/dak_gord_system";
const OUT = "out/process_camera/dakgord_live.json";

function readJson(path: string): unknown {
  try { return JSON.parse(readFileSync(path, "utf-8")); }
  catch { return null; }
}
function readText(path: string): string {
  try { return readFileSync(path, "utf-8"); }
  catch { return ""; }
}

// Parst Wochenlog-Einträge im Format:
// [2026-05-08 17:58:07] dak+gord-system\n\nWerkraum-Neugier: name | DATEI: path
function parseWochenlog(text: string): Array<{time:string,art:string,name:string,datei:string}> {
  const result: Array<{time:string,art:string,name:string,datei:string}> = [];
  const blocks = text.split(/\n(?=\[)/);
  for (const block of blocks) {
    const timeM  = block.match(/^\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]/);
    const artM   = block.match(/(Werkraum-Neugier|Vision-Zyklus):\s*([^\|]+)\|/);
    const dateiM = block.match(/DATEI:\s*([^\n]+)/);
    if (timeM && artM) {
      result.push({
        time:  timeM[1],
        art:   artM[1],
        name:  artM[2].trim(),
        datei: dateiM ? dateiM[1].trim() : artM[2].trim(),
      });
    }
  }
  return result;
}

function parseTraceEvents(text: string): unknown[] {
  return text.trim().split("\n").filter(Boolean).map(l => {
    try { return JSON.parse(l); } catch { return null; }
  }).filter(Boolean);
}

// Neuesten Wochenlog finden
function latestWochenlog(): string {
  const dir = join(WERKRAUM, "spuren/wochenlog");
  if (!existsSync(dir)) return "";
  const files = readdirSync(dir).filter(f => f.endsWith(".md")).sort();
  if (!files.length) return "";
  return readText(join(dir, files[files.length - 1]));
}

// Neueste Verdichtung finden
function latestVerdichtung(): string {
  const dir = join(WERKRAUM, "spuren/verdichtung");
  if (!existsSync(dir)) return "";
  const files = readdirSync(dir).filter(f => f.endsWith(".md")).sort();
  if (!files.length) return "";
  return readText(join(dir, files[files.length - 1])).slice(0, 600);
}

const erinnerungen   = readJson(join(WERKRAUM, "gedaechtnis_daten/erinnerungen.json"))   ?? [];
const abwaegungen    = readJson(join(WERKRAUM, "gedaechtnis_daten/abwaegungen.json"))    ?? [];
const zukunft        = readJson(join(WERKRAUM, "gedaechtnis_daten/zukunft.json"))        ?? [];
const zwischenraum   = readJson(join(WERKRAUM, "gedaechtnis_daten/zwischenraum.json"))   ?? [];
const neugier_zustand = readJson(join(WERKRAUM, "spuren/neugier_zustand.json"))          ?? {};
const verfassung_kern   = readText(join(WERKRAUM, "verfassung/01_kern_wesen.md")).slice(0, 700);
const verfassung_neugier = readText(join(WERKRAUM, "verfassung/03_neugier_und_wahrnehmung.md")).slice(0, 500);
const traceText = readText(join(WERKRAUM, "spuren/traces/events.jsonl"));
const letzte_aktivitaet = (parseTraceEvents(traceText) as any[]).slice(-12);
const wochenlog_text = latestWochenlog();
const letzte_neugier = parseWochenlog(wochenlog_text).slice(-12);
const letzte_verdichtung = latestVerdichtung();

const data = {
  export_kind:       "dakgord_live",
  wesen:             "dak+gord-system",
  exported_at:       new Date().toISOString(),
  erinnerungen,
  abwaegungen,
  zukunft,
  zwischenraum,
  neugier_zustand,
  letzte_neugier,
  letzte_aktivitaet,
  letzte_verdichtung,
  verfassung_kern,
  verfassung_neugier,
};

mkdirSync("out/process_camera", { recursive: true });
writeFileSync(OUT, JSON.stringify(data, null, 2), "utf-8");
console.log("dak+gord live export:", OUT);
