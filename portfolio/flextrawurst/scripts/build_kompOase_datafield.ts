import { writeFileSync, mkdirSync } from "node:fs";
import { buildKompOaseDatafieldHtml } from "../kernel/landscape/kompOase_datafield_html.ts";

const OUT = "out/process_camera/kompOase_datafield.html";

mkdirSync("out/process_camera", { recursive: true });
writeFileSync(OUT, buildKompOaseDatafieldHtml(), "utf-8");

console.log("KompOase Datafield erzeugt:");
console.log("  HTML:", OUT);
console.log("  ring:22N | datafield:true | nameless_count:6 | einzug:0");
