import type { FieldData } from "./types";

export class ApiError extends Error {
  constructor(public readonly status: number, message: string) { super(message); }
}
export const API_BASE = "/api/v1/awci";
type Params = Record<string, string | number | undefined>;

function query(params: Params): string {
  const q = new URLSearchParams();
  for (const [k, v] of Object.entries(params)) if (v !== undefined) q.set(k, String(v));
  const s = q.toString();
  return s ? `?${s}` : "";
}

async function fail(r: Response): Promise<never> {
  let detail = r.statusText;
  try { const body = (await r.json()) as { detail?: unknown }; if (body.detail) detail = String(body.detail); } catch { /* not JSON */ }
  throw new ApiError(r.status, detail);
}

export async function getJson<T>(path: string, params: Params = {}, signal?: AbortSignal): Promise<T> {
  const r = await fetch(`${API_BASE}${path}${query(params)}`, { signal });
  if (!r.ok) return fail(r);
  return (await r.json()) as T;
}

const pair = (h: Headers, name: string): [number, number] => {
  const raw = h.get(name);
  const parts = (raw ?? "").split(",").map(Number);
  if (parts.length !== 2 || parts.some((x) => !Number.isFinite(x))) throw new Error(`bad header ${name}: ${raw}`);
  return [parts[0]!, parts[1]!];
};

export function parseField(headers: Headers, buf: ArrayBuffer): FieldData {
  const [ny, nx] = pair(headers, "X-AWCI-Shape");
  const [lat0, lat1] = pair(headers, "X-AWCI-Lats");
  const [lon0, lon1] = pair(headers, "X-AWCI-Lons");
  const values = new Float32Array(buf); // little-endian on every supported browser platform
  if (values.length !== ny * nx) throw new Error(`field size ${values.length} != ${ny}x${nx}`);
  return { values, ny, nx, lat0, lat1, lon0, lon1, unit: headers.get("X-AWCI-Unit") ?? "" };
}

export async function getField(params: Params, signal?: AbortSignal): Promise<FieldData> {
  const r = await fetch(`${API_BASE}/field${query({ ...params, format: "f32" })}`, { signal });
  if (!r.ok) return fail(r);
  return parseField(r.headers, await r.arrayBuffer());
}
