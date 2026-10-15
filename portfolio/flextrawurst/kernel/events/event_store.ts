import type { FlextrawurstEvent } from "./types.ts";
import { validateEvent } from "./validate.ts";

export class InMemoryEventStore {
  private readonly _events: FlextrawurstEvent[] = [];
  private readonly _ids: Set<string> = new Set();

  append(event: FlextrawurstEvent): void {
    validateEvent(event, this._ids);
    const stored = Object.freeze({
      ...event,
      causal_links: Object.freeze([...event.causal_links]),
    }) as FlextrawurstEvent;
    this._events.push(stored);
    this._ids.add(stored.event_id);
  }

  getAll(): readonly FlextrawurstEvent[] {
    return Object.freeze([...this._events]);
  }

  getById(event_id: string): FlextrawurstEvent | null {
    return this._events.find((e) => e.event_id === event_id) ?? null;
  }

  has(event_id: string): boolean {
    return this._ids.has(event_id);
  }

  clear(): void {
    this._events.length = 0;
    this._ids.clear();
  }

  get length(): number {
    return this._events.length;
  }
}
