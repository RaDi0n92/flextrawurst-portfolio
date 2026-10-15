import { writeFileSync, mkdirSync } from "node:fs";
import { buildWerkraumExplorerHtml } from "../kernel/werkraum/werkraum_explorer_html.ts";

const OUT = "out/process_camera/werkraum_explorer.html";
mkdirSync("out/process_camera", { recursive: true });
writeFileSync(OUT, buildWerkraumExplorerHtml(), "utf-8");
console.log("Werkraum Explorer:", OUT);
