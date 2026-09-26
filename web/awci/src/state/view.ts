import { useCallback, useEffect, useState } from "react";
import type { Domain, EnsMeta, Meta, RunInfo } from "../api/types";
import { ENS_LAYER_DEFS, LAYER_DEFS, type LayerDef } from "../map/layers";
import { allowedWith, type VolumeLayerId } from "../volume/layers3d";

export interface ViewState {
  domain?: string; run?: string; step?: number; level?: number; layer: string;
  lat?: number; lon?: number; ov: string[]; panel?: string;
  /** Selected aerodrome (ICAO) and visible aeronautical observation layers. */
  ap?: string; aero: AeroLayer[];
  /** 3-D volume view (SP2B): volume layers (max 2), vertical exaggeration, cloud-fraction threshold. */
  mode3d: boolean; vol: VolumeLayerId[]; exag: number; cth: number;
}
const VOLUME_IDS: VolumeLayerId[] = ["clouds", "icing", "cat", "awci"];
export const EXAG_DEFAULT = 40;
export const CTH_DEFAULT = 0.625; // 5/8: broken (BKN)
const clamp = (x: number, lo: number, hi: number) => Math.min(hi, Math.max(lo, x));
function parseVol(raw: string | null): VolumeLayerId[] {
  if (raw === null) return ["clouds"];
  const out: VolumeLayerId[] = [];
  for (const id of raw.split(",")) {
    if ((VOLUME_IDS as string[]).includes(id) && allowedWith(out, id as VolumeLayerId) && !out.includes(id as VolumeLayerId)) {
      out.push(id as VolumeLayerId);
    }
  }
  return out;
}
export type AeroLayer = "metar" | "sigmet";
export const AERO_DEFAULT: AeroLayer[] = ["metar", "sigmet"];
export interface Resolved { domain: string; run: string; step: number; level: number; layer: string }

const NAME = /^[a-z0-9_]{1,64}$/;
const OVERLAY = /^[a-z0-9_]+:[a-z0-9_]+$/;
const ICAO = /^[A-Z][A-Z0-9]{3}$/;
const parseAero = (raw: string | null): AeroLayer[] =>
  raw === null ? [...AERO_DEFAULT] : AERO_DEFAULT.filter((l) => raw.split(",").includes(l));
const num = (s: string | null) => (s !== null && s.trim() !== "" && Number.isFinite(Number(s)) ? Number(s) : undefined);

export function parseView(search: string): ViewState {
  const q = new URLSearchParams(search);
  const text = (k: string, re: RegExp) => { const v = q.get(k); return v && re.test(v) ? v : undefined; };
  const lat = num(q.get("lat"));
  const lon = num(q.get("lon"));
  return {
    domain: text("domain", NAME), run: text("run", /^\d{10}$/), step: num(q.get("step")), level: num(q.get("level")),
    layer: text("layer", NAME) ?? "awci",
    lat: lat !== undefined && Math.abs(lat) <= 90 ? lat : undefined,
    lon: lon !== undefined && Math.abs(lon) <= 180 ? lon : undefined,
    ov: (q.get("ov") ?? "").split(",").filter((o) => OVERLAY.test(o)), panel: text("panel", NAME),
    ap: text("ap", ICAO), aero: parseAero(q.get("aero")),
    mode3d: q.get("view") === "3d", vol: parseVol(q.get("vol")),
    exag: clamp(Math.round(num(q.get("exag")) ?? EXAG_DEFAULT), 10, 100),
    cth: clamp(Math.round((num(q.get("cth")) ?? CTH_DEFAULT) * 8) / 8, 0.125, 1),
  };
}

export function serializeView(v: ViewState): string {
  const q = new URLSearchParams();
  const set = (k: string, val: string | number | undefined) => { if (val !== undefined && val !== "") q.set(k, String(val)); };
  set("domain", v.domain); set("run", v.run); set("step", v.step); set("level", v.level); set("layer", v.layer);
  set("lat", v.lat); set("lon", v.lon); set("ov", v.ov.join(",")); set("panel", v.panel); set("ap", v.ap);
  const aero = AERO_DEFAULT.filter((l) => v.aero.includes(l));
  if (aero.length !== AERO_DEFAULT.length) set("aero", aero.length ? aero.join(",") : "none");
  if (v.mode3d) set("view", "3d");
  if (v.vol.join(",") !== "clouds") set("vol", v.vol.length ? v.vol.join(",") : "none");
  if (v.exag !== EXAG_DEFAULT) set("exag", v.exag);
  if (v.cth !== CTH_DEFAULT) set("cth", v.cth);
  return `?${q.toString()}`;
}

const validSteps = (m: Meta) => m.steps.filter((s) => !m.missing_steps.includes(s));

export function nextStep(m: Meta, step: number, dir: 1 | -1): number {
  const ok = validSteps(m);
  const candidates = dir > 0 ? ok.filter((s) => s > step) : ok.filter((s) => s < step).reverse();
  return candidates[0] ?? step;
}

/** dir = +1 moves up (lower pressure). */
export function nextLevel(m: Meta, level: number, dir: 1 | -1): number {
  const sorted = [...m.levels_hpa].sort((a, b) => b - a);
  const i = sorted.indexOf(level);
  return sorted[Math.min(sorted.length - 1, Math.max(0, i + dir))] ?? level;
}

export function availableLayers(m: Meta, ens?: Pick<EnsMeta, "steps" | "missing_steps">): LayerDef[] {
  const present = new Set([...m.level_layers, ...m.surface_layers]);
  return [...LAYER_DEFS.filter((d) => present.has(d.id)), ...(ens ? ENS_LAYER_DEFS : [])];
}

/** ENS steps are 6-hourly; a step not computed (or missing) is never replaced by a neighbouring one. */
export const ensStepAvailable = (ens: Pick<EnsMeta, "steps" | "missing_steps"> | undefined, step: number) =>
  !!ens && ens.steps.includes(step) && !ens.missing_steps.includes(step);

export function resolveView(v: ViewState, domains: Domain[], runs: RunInfo[], meta: Meta | undefined,
                            now: Date, ens?: Pick<EnsMeta, "steps" | "missing_steps">): Resolved | null {
  const domain = domains.find((d) => d.name === v.domain)?.name ?? domains.find((d) => d.default)?.name ?? domains[0]?.name;
  const usable = runs.filter((r) => r.status !== "failed");
  const run = usable.find((r) => r.run === v.run)?.run ?? usable[0]?.run;
  if (!domain || !run || !meta) return null;
  const ok = validSteps(meta);
  let step = v.step !== undefined && ok.includes(v.step) ? v.step : undefined;
  if (step === undefined) {
    const t = now.getTime();
    step = ok.reduce((best, s) => {
      const d = (x: number) => Math.abs(new Date(meta.valid_times[meta.steps.indexOf(x)]!).getTime() - t);
      return d(s) < d(best) ? s : best;
    }, ok[0]!);
  }
  const level = v.level !== undefined && meta.levels_hpa.includes(v.level) ? v.level
    : meta.levels_hpa.includes(300) ? 300 : meta.levels_hpa[0]!;
  const layer = availableLayers(meta, ens).some((d) => d.id === v.layer) ? v.layer : "awci";
  return { domain, run, step, level, layer };
}

/**
 * Pins the run on screen at the first interaction: stepping writes the run into the URL, so a newer run
 * ingested meanwhile never changes the valid time silently. A patch that sets `run` itself (even to
 * undefined, "Maintenant") is left as is.
 */
export function withPinnedRun(view: ViewState, shown: string | undefined, patch: Partial<ViewState>): Partial<ViewState> {
  return "run" in patch || view.run !== undefined || shown === undefined ? patch : { ...patch, run: shown };
}

/** The latest usable run when it is newer than the pinned one. */
export function newerRun(runs: RunInfo[], pinned: string | undefined): string | undefined {
  const latest = runs.find((r) => r.status !== "failed")?.run;
  return pinned !== undefined && latest !== undefined && latest > pinned ? latest : undefined;
}

export type ViewPatch = Partial<ViewState> | ((old: ViewState) => Partial<ViewState>);

export function useViewState(): [ViewState, (patch: ViewPatch) => void] {
  const [view, setView] = useState<ViewState>(() => parseView(window.location.search));
  useEffect(() => {
    const onPop = () => setView(parseView(window.location.search));
    window.addEventListener("popstate", onPop);
    return () => window.removeEventListener("popstate", onPop);
  }, []);
  const update = useCallback((patch: ViewPatch) => {
    setView((old) => {
      const next = { ...old, ...(typeof patch === "function" ? patch(old) : patch) };
      window.history.replaceState(null, "", serializeView(next));
      return next;
    });
  }, []);
  return [view, update];
}
