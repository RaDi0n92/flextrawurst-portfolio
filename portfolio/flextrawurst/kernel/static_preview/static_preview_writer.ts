import { writeFileSync, mkdirSync } from "node:fs";
import { dirname } from "node:path";
import type { StaticPreview } from "./static_preview_model.ts";

export function writeStaticPreview(preview: StaticPreview, filePath: string): void {
  mkdirSync(dirname(filePath), { recursive: true });
  writeFileSync(filePath, preview.html, "utf-8");
}
