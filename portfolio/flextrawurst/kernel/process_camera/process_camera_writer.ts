import { writeFileSync, mkdirSync } from "node:fs";
import { dirname } from "node:path";

export function writeProcessCameraFiles(
  jsonPath: string,
  htmlPath: string,
  jsonContent: string,
  htmlContent: string
): void {
  mkdirSync(dirname(jsonPath), { recursive: true });
  mkdirSync(dirname(htmlPath), { recursive: true });
  writeFileSync(jsonPath, jsonContent, "utf-8");
  writeFileSync(htmlPath, htmlContent, "utf-8");
}
