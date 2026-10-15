import { writeFileSync, mkdirSync } from "node:fs";
import { buildWerkraumKarteHtml } from "../kernel/werkraum/werkraum_karte_html.ts";

const OUT = "out/process_camera/werkraum_karte.html";
mkdirSync("out/process_camera", { recursive: true });
writeFileSync(OUT, buildWerkraumKarteHtml(), "utf-8");
console.log("Werkraum-Karte:", OUT);
