import type { ReadOnlyConsoleModel } from "./read_only_console_model.ts";

export interface ConsoleExport {
  export_version: 1;
  created_from: "in_memory_console_model";
  console_version: number;
  title: string;
  section_ids: string[];
  section_count: number;
  navigation_count: number;
  warning_count: number;
}

export function buildConsoleExport(
  consoleModel: ReadOnlyConsoleModel
): ConsoleExport {
  return {
    export_version: 1,
    created_from: "in_memory_console_model",
    console_version: consoleModel.console_version,
    title: consoleModel.title,
    section_ids: consoleModel.sections.map((s) => s.id),
    section_count: consoleModel.sections.length,
    navigation_count: consoleModel.navigation.length,
    warning_count: consoleModel.warnings.length,
  };
}

export function serializeConsoleExport(
  consoleModel: ReadOnlyConsoleModel
): string {
  return JSON.stringify(buildConsoleExport(consoleModel));
}
