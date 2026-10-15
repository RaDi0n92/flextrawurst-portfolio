import { writeFileSync, mkdirSync } from "node:fs";
import { buildKompOaseVorformHtml } from "../kernel/landscape/kompOase_landscape_html.ts";

const OUT = "out/process_camera/kompOase_vorform.html";

mkdirSync("out/process_camera", { recursive: true });
writeFileSync(OUT, buildKompOaseVorformHtml(), "utf-8");

console.log("KompOase-Vorform erzeugt:");
console.log(`  HTML: ${OUT}`);
console.log("  static:true | no_runtime:true | nameless_count:6 | einzug:0");
