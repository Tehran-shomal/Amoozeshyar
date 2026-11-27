export type JsonObject = Record<string, unknown>;

export function asObject(value: unknown): JsonObject {
  return typeof value === "object" && value !== null ? value as JsonObject : {};
}

export function asList(value: unknown): unknown[] {
  return Array.isArray(value) ? value : [];
}

export function displayText(value: unknown, fallback = "—"): string {
  return value === null || value === undefined || value === "" ? fallback : String(value);
}

export function displayCount(value: unknown): string {
  return typeof value === "number" && Number.isFinite(value) ? String(value) : "۰";
}

export function displayTime(value: unknown): string {
  const time = displayText(value, "");
  return time ? time.slice(0, 5) : "—";
}
