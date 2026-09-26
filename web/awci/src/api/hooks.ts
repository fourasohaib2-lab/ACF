/** Data hooks: one TanStack Query per route. Everything that depends on a run is immutable (staleTime Infinity). */
import { keepPreviousData, useQueries, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect } from "react";
import { parseVolume, type Volume } from "../volume/geometry";
import { ApiError, getEnsField, getField, getJson, getTerrain, getVolume } from "./client";
import type {
  AirportDetail, AirportsPayload, EnsMeta, EnsPoint, EnsRun, CloudsPayload, CloudsSeries, Domain, FieldData, Meta, PointPayload, ProfilePayload,
  EnsVerification, Registry, RunInfo, SigmetCollection, Summary, SummarySeries, TimeseriesPayload, Verification, WmsLayer, WmsTimes,
} from "./types";

const IMMUTABLE = { staleTime: Infinity, gcTime: 30 * 60_000 } as const;

/** Data of the query's current key only: the previous key's data kept as a placeholder is never "current". */
export const freshData = <T,>(q: { data?: T; isPlaceholderData: boolean }): T | undefined =>
  (q.isPlaceholderData ? undefined : q.data);
/** Retry transient failures only: a 4xx is an answer, not an outage. */
const retry = (count: number, error: unknown) => count < 2 && !(error instanceof ApiError && error.status < 500);

export const useDomains = () =>
  useQuery({ queryKey: ["domains"], queryFn: ({ signal }) => getJson<Domain[]>("/domains", {}, signal), ...IMMUTABLE, retry });

export const useRuns = (domain?: string) =>
  useQuery({ queryKey: ["runs", domain], enabled: !!domain, refetchInterval: 300_000, retry,
    queryFn: ({ signal }) => getJson<RunInfo[]>("/runs", { domain }, signal) });

export const useMeta = (domain?: string, run?: string) =>
  useQuery({ queryKey: ["meta", domain, run], enabled: !!domain && !!run, ...IMMUTABLE, retry,
    queryFn: ({ signal }) => getJson<Meta>("/meta", { domain, run }, signal) });

interface FieldKey { domain?: string; run?: string; layer?: string; step?: number; level?: number; perLevel?: boolean; source?: "ens" }

const fieldQuery = (k: FieldKey) => ({
  queryKey: ["field", k.source ?? "det", k.domain, k.run, k.layer, k.step, k.perLevel ? k.level : null],
  queryFn: ({ signal }: { signal: AbortSignal }) => k.source === "ens"
    ? getEnsField({ domain: k.domain, run: k.run, product: k.layer, step: k.step, level: k.perLevel ? k.level : undefined }, signal)
    : getField({ domain: k.domain, run: k.run, layer: k.layer, step: k.step, level: k.perLevel ? k.level : undefined }, signal),
  ...IMMUTABLE, retry,
});

export function useField(k: FieldKey, neighbours: number[] = []) {
  const client = useQueryClient();
  const ready = !!k.domain && !!k.run && !!k.layer && k.step !== undefined;
  const query = useQuery<FieldData>({ ...fieldQuery(k), enabled: ready, placeholderData: keepPreviousData });
  const key = neighbours.join(",");
  useEffect(() => {
    if (!ready) return;
    for (const step of key ? key.split(",").map(Number) : []) void client.prefetchQuery(fieldQuery({ ...k, step }));
  }, [client, ready, key, k.domain, k.run, k.layer, k.level, k.perLevel]); // eslint-disable-line react-hooks/exhaustive-deps
  return query;
}

const summaryQuery = (domain?: string, run?: string, step?: number, level?: number) => ({
  queryKey: ["summary", domain, run, step, level],
  queryFn: ({ signal }: { signal: AbortSignal }) => getJson<Summary>("/summary", { domain, run, step, level }, signal),
  ...IMMUTABLE, retry,
});

/** Domain KPIs of the step, with the neighbouring steps prefetched so stepping stays instant. */
export function useSummary(domain?: string, run?: string, step?: number, level?: number, neighbours: number[] = []) {
  const client = useQueryClient();
  const ready = !!run && step !== undefined && level !== undefined;
  const query = useQuery({ ...summaryQuery(domain, run, step, level), enabled: ready, placeholderData: keepPreviousData });
  const key = neighbours.join(",");
  useEffect(() => {
    if (!ready) return;
    for (const s of key ? key.split(",").map(Number) : []) void client.prefetchQuery(summaryQuery(domain, run, s, level));
  }, [client, ready, key, domain, run, level]);
  return query;
}

export const useSummarySeries = (domain?: string, run?: string, level?: number) =>
  useQuery({ queryKey: ["summary-series", domain, run, level], enabled: !!run && level !== undefined, ...IMMUTABLE, retry,
    queryFn: ({ signal }) => getJson<SummarySeries>("/summary/series", { domain, run, level }, signal) });

interface PointKey { domain?: string; run?: string; step?: number; level?: number; lat?: number; lon?: number }
const hasPoint = (k: PointKey) => !!k.run && k.lat !== undefined && k.lon !== undefined;

export const usePoint = (k: PointKey) =>
  useQuery({ queryKey: ["point", k], enabled: hasPoint(k) && k.step !== undefined && k.level !== undefined, ...IMMUTABLE,
    retry, queryFn: ({ signal }) => getJson<PointPayload>("/point", { ...k }, signal) });

export const useProfile = (k: PointKey) =>
  useQuery({ queryKey: ["profile", k.domain, k.run, k.step, k.lat, k.lon], enabled: hasPoint(k) && k.step !== undefined,
    ...IMMUTABLE, retry, queryFn: ({ signal }) =>
      getJson<ProfilePayload>("/profile", { domain: k.domain, run: k.run, step: k.step, lat: k.lat, lon: k.lon }, signal) });

export const useTimeseries = (k: PointKey) =>
  useQuery({ queryKey: ["timeseries", k.domain, k.run, k.level, k.lat, k.lon], enabled: hasPoint(k) && k.level !== undefined,
    ...IMMUTABLE, retry, queryFn: ({ signal }) =>
      getJson<TimeseriesPayload>("/timeseries", { domain: k.domain, run: k.run, level: k.level, lat: k.lat, lon: k.lon }, signal) });

export const useClouds = (k: PointKey, enabled = true) =>
  useQuery({ queryKey: ["clouds", k.domain, k.run, k.step, k.lat, k.lon], enabled: enabled && hasPoint(k) && k.step !== undefined,
    ...IMMUTABLE, retry, queryFn: ({ signal }) =>
      getJson<CloudsPayload>("/clouds", { domain: k.domain, run: k.run, step: k.step, lat: k.lat, lon: k.lon }, signal) });

export const useCloudsSeries = (k: PointKey, enabled = true) =>
  useQuery({ queryKey: ["clouds-series", k.domain, k.run, k.lat, k.lon], enabled: enabled && hasPoint(k), ...IMMUTABLE, retry,
    queryFn: ({ signal }) =>
      getJson<CloudsSeries>("/clouds/series", { domain: k.domain, run: k.run, lat: k.lat, lon: k.lon }, signal) });

export const useRegistry = () =>
  useQuery({ queryKey: ["registry"], queryFn: ({ signal }) => getJson<Registry>("/registry", {}, signal), ...IMMUTABLE, retry });

export const useWmsLayers = () =>
  useQuery({ queryKey: ["wms-layers"], queryFn: ({ signal }) => getJson<WmsLayer[]>("/wms/layers", {}, signal), ...IMMUTABLE, retry });

export const useWmsTimes = (layer: string | undefined, count = 1) =>
  useQuery({ queryKey: ["wms-times", layer, count], enabled: !!layer, staleTime: 60_000, refetchInterval: 120_000, retry: 1,
    queryFn: ({ signal }) => getJson<WmsTimes>("/wms/times", { layer, count }, signal) });

/** Latest observation time of every active overlay (tiles are then requested at that explicit time). */
export const useOverlayTimes = (layers: string[]) =>
  useQueries({ queries: layers.map((layer) => ({
    queryKey: ["wms-times", layer, 1], staleTime: 60_000, refetchInterval: 120_000, retry: 1,
    queryFn: ({ signal }: { signal: AbortSignal }) => getJson<WmsTimes>("/wms/times", { layer, count: 1 }, signal),
  })) });

// ---- SP3: observations are appended by acf-awci-obs, so they are refreshed (never immutable) ----
const OBS = { staleTime: 60_000, refetchInterval: 300_000, gcTime: 30 * 60_000 } as const;

/** Aerodromes with the METAR nearest (±30 min) to the valid time on screen. */
export const useAirports = (domain: string | undefined, time: string | undefined, enabled = true) =>
  useQuery({ queryKey: ["airports", domain, time], enabled: enabled && !!domain && !!time, ...OBS, retry,
    placeholderData: keepPreviousData,
    queryFn: ({ signal }) => getJson<AirportsPayload>("/airports", { domain, time }, signal) });

export const useAirport = (domain: string | undefined, icao: string | undefined, run: string | undefined) =>
  useQuery({ queryKey: ["airport", domain, icao, run], enabled: !!domain && !!icao && !!run, ...OBS, retry,
    queryFn: ({ signal }) => getJson<AirportDetail>("/airport", { domain, icao, run }, signal) });

export const useSigmets = (domain: string | undefined, time: string | undefined, enabled = true) =>
  useQuery({ queryKey: ["sigmets", domain, time], enabled: enabled && !!domain && !!time, ...OBS, retry,
    placeholderData: keepPreviousData,
    queryFn: ({ signal }) => getJson<SigmetCollection>("/sigmets", { domain, time }, signal) });

export const useVerification = (domain: string | undefined, run: string | undefined, enabled = true) =>
  useQuery({ queryKey: ["verification", domain, run], enabled: enabled && !!domain && !!run, ...OBS, retry,
    queryFn: ({ signal }) => getJson<Verification>("/verification", { domain, run }, signal) });

// ---- SP2B: 3-D volume view. Volumes are immutable per (run, layer, step, stride). ----
interface VolumeKey { domain?: string; run?: string; layer?: string; step?: number; stride: number }
const volumeQuery = (k: VolumeKey) => ({
  queryKey: ["volume", k.domain, k.run, k.layer, k.step, k.stride],
  queryFn: async ({ signal }: { signal: AbortSignal }): Promise<Volume> => {
    const { body, headers } = await getVolume({ domain: k.domain, run: k.run, layer: k.layer, step: k.step, stride: k.stride }, signal);
    return parseVolume(body, headers);
  },
  ...IMMUTABLE, gcTime: 5 * 60_000, retry,
});

/** One volume at the valid time on screen; the next two steps are preloaded for the 4-D playback (spec §3). */
export function useVolume(k: VolumeKey, next: number[] = [], enabled = true) {
  const client = useQueryClient();
  const ready = enabled && !!k.domain && !!k.run && !!k.layer && k.step !== undefined;
  const query = useQuery<Volume>({ ...volumeQuery(k), enabled: ready, placeholderData: keepPreviousData });
  const key = next.join(",");
  useEffect(() => {
    if (!ready) return;
    for (const step of key ? key.split(",").map(Number) : []) void client.prefetchQuery(volumeQuery({ ...k, step }));
  }, [client, ready, key, k.domain, k.run, k.layer, k.stride]); // eslint-disable-line react-hooks/exhaustive-deps
  return query;
}

export const useTerrain = (domain: string | undefined, run: string | undefined, stride: number, enabled = true) =>
  useQuery({ queryKey: ["terrain", domain, run, stride], enabled: enabled && !!domain && !!run, ...IMMUTABLE, retry,
    queryFn: ({ signal }) => getTerrain({ domain, run, stride }, signal) });

// ---- SP5: IFS ENS (runs are appended by acf-awci-ens; a run's content is immutable) ----
export const useEnsRuns = (domain: string | undefined) =>
  useQuery({ queryKey: ["ens-runs", domain], enabled: !!domain, refetchInterval: 300_000, retry,
    queryFn: ({ signal }) => getJson<EnsRun[]>("/ens/runs", { domain }, signal) });

export const useEnsMeta = (domain: string | undefined, run: string | undefined, enabled: boolean) =>
  useQuery({ queryKey: ["ens-meta", domain, run], enabled: enabled && !!domain && !!run, ...IMMUTABLE, retry,
    queryFn: ({ signal }) => getJson<EnsMeta>("/ens/meta", { domain, run }, signal) });

export const useEnsPoint = (k: { domain?: string; run?: string; lat?: number; lon?: number; level?: number }, enabled: boolean) =>
  useQuery({ queryKey: ["ens-point", k.domain, k.run, k.lat, k.lon, k.level], ...IMMUTABLE, retry,
    enabled: enabled && !!k.run && k.lat !== undefined && k.lon !== undefined && k.level !== undefined,
    queryFn: ({ signal }) => getJson<EnsPoint>("/ens/point", { ...k }, signal) });

export const useEnsVerification = (domain: string | undefined, run: string | undefined, enabled: boolean) =>
  useQuery({ queryKey: ["ens-verification", domain, run], enabled: enabled && !!domain && !!run, ...OBS, retry,
    queryFn: ({ signal }) => getJson<EnsVerification>("/ens/verification", { domain, run }, signal) });
