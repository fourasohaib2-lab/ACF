/** Data hooks: one TanStack Query per route. Everything that depends on a run is immutable (staleTime Infinity). */
import { keepPreviousData, useQueries, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect } from "react";
import { ApiError, getField, getJson } from "./client";
import type {
  CloudsPayload, CloudsSeries, Domain, FieldData, Meta, PointPayload, ProfilePayload, Registry, RunInfo, Summary,
  SummarySeries, TimeseriesPayload, WmsLayer, WmsTimes,
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

interface FieldKey { domain?: string; run?: string; layer?: string; step?: number; level?: number; perLevel?: boolean }

const fieldQuery = (k: FieldKey) => ({
  queryKey: ["field", k.domain, k.run, k.layer, k.step, k.perLevel ? k.level : null],
  queryFn: ({ signal }: { signal: AbortSignal }) =>
    getField({ domain: k.domain, run: k.run, layer: k.layer, step: k.step, level: k.perLevel ? k.level : undefined }, signal),
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
