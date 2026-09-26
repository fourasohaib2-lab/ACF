import { lazy, Suspense, useCallback, useEffect, useMemo, useRef, useState } from "react";
import "./App.css";
import { freshData, useClouds, useCloudsSeries, useDomains, useField, useMeta, useOverlayTimes, usePoint, useWmsLayers, useProfile, useRegistry, useRuns, useSummary, useSummarySeries, useTimeseries } from "./api/hooks";
import { fr } from "./i18n/fr";
import { Legend } from "./map/Legend";
import { layerDef } from "./map/layers";
import type { WindGrid } from "./map/streamlines";
import { AtmoProfile } from "./panels/AtmoProfile";
import { AwciProfile } from "./panels/AwciProfile";
import { CloudsPanel } from "./panels/CloudsPanel";
import { CompareControl, FIELD_OPACITY, fieldOpacity } from "./panels/CompareControl";
import { ObservedBadges } from "./panels/ObservedBadge";
import { OverlayPanel, type OverlayState } from "./panels/OverlayPanel";
import { DataStatus } from "./panels/DataStatus";
import { Inspector } from "./panels/Inspector";
import { TimeEvolution } from "./panels/TimeEvolution";
import { KpiRow } from "./panels/KpiRow";
import { LatestRuns } from "./panels/LatestRuns";
import { RegistryPage } from "./panels/RegistryPage";
import { SavedViews } from "./panels/SavedViews";
import { ModelAgreement } from "./panels/ModelAgreement";
import { Situation } from "./panels/Situation";
import { SideNav } from "./panels/SideNav";
import { Banner, EmptyRuns, ErrorBox, Skeleton } from "./panels/StateViews";
import { TimeBar } from "./panels/TimeBar";
import { TopBar } from "./panels/TopBar";
import { runLabel } from "./lib/format";
import { ownsKeys } from "./lib/keys";
import { availableLayers, newerRun, nextLevel, nextStep, resolveView, useViewState, withPinnedRun, type ViewState } from "./state/view";

const MapView = lazy(() => import("./map/MapView").then((m) => ({ default: m.MapView })));

function useNow(periodMs = 30_000): Date {
  const [now, setNow] = useState(() => new Date());
  useEffect(() => {
    const id = window.setInterval(() => setNow(new Date()), periodMs);
    return () => window.clearInterval(id);
  }, [periodMs]);
  return now;
}

export function App() {
  const [view, setView] = useViewState();
  const now = useNow();
  const [playing, setPlaying] = useState(false);
  const [toast, setToast] = useState<string | null>(null);
  const [streamlines, setStreamlines] = useState(true);
  const [opacity, setOpacity] = useState(FIELD_OPACITY);
  const [tileErrors, setTileErrors] = useState<Record<string, boolean>>({});
  const layerListRef = useRef<HTMLFieldSetElement>(null);

  const domains = useDomains();
  const domain = domains.data?.find((d) => d.name === view.domain) ?? domains.data?.find((d) => d.default) ?? domains.data?.[0];
  const runs = useRuns(domain?.name);
  const usableRuns = useMemo(() => (runs.data ?? []).filter((r) => r.status !== "failed"), [runs.data]);
  const runId = usableRuns.find((r) => r.run === view.run)?.run ?? usableRuns[0]?.run;
  const meta = useMeta(domain?.name, runId);
  const registry = useRegistry();
  const resolved = domains.data && runs.data ? resolveView(view, domains.data, runs.data, meta.data, now) : null;
  const run = usableRuns.find((r) => r.run === resolved?.run);
  const shownRun = useRef<string | undefined>(undefined);
  useEffect(() => { shownRun.current = resolved?.run; }, [resolved?.run]);
  // Any interaction pins the run on screen (see withPinnedRun); "Maintenant" and the run selector set it explicitly.
  const update = useCallback((patch: Partial<ViewState>) => setView((old) => withPinnedRun(old, shownRun.current, patch)), [setView]);
  const newer = newerRun(runs.data ?? [], view.run);

  const def = layerDef(resolved?.layer ?? "awci");
  const neighbours = useMemo(() => (meta.data && resolved
    ? [nextStep(meta.data, resolved.step, 1), nextStep(meta.data, resolved.step, -1)].filter((s) => s !== resolved.step) : []),
  [meta.data, resolved?.step]); // eslint-disable-line react-hooks/exhaustive-deps
  const field = useField({ domain: resolved?.domain, run: resolved?.run, layer: resolved?.layer, step: resolved?.step,
    level: resolved?.level, perLevel: def.perLevel }, neighbours);
  const uField = useField({ domain: resolved?.domain, run: resolved?.run, layer: streamlines ? "u" : undefined,
    step: resolved?.step, level: resolved?.level, perLevel: true }, neighbours);
  const vField = useField({ domain: resolved?.domain, run: resolved?.run, layer: streamlines ? "v" : undefined,
    step: resolved?.step, level: resolved?.level, perLevel: true }, neighbours);
  // Only data of the current key reaches the map: a neighbour's field kept as placeholder is never drawn as current,
  // and u and v always come from the same step and level.
  const fieldData = freshData(field);
  const u = freshData(uField);
  const v = freshData(vField);
  const wind = useMemo<WindGrid | undefined>(() => (streamlines && u && v ? { ...u, u: u.values, v: v.values } : undefined),
    [streamlines, u, v]);

  const classes = useMemo(() => registry.data?.classes ?? [], [registry.data]);
  const awciBounds = useMemo(() => classes.filter((c) => c.upper_bound !== null).map((c) => c.upper_bound as number), [classes]);
  const classLabels = useMemo(() => classes.map((c) => c.label), [classes]);
  const layers = useMemo(() => (meta.data ? availableLayers(meta.data) : []), [meta.data]);
  const summary = useSummary(resolved?.domain, resolved?.run, resolved?.step, resolved?.level, neighbours);
  const classIndex = summary.data?.awci_class ? classLabels.indexOf(summary.data.awci_class) : -1;
  const pointKey = { domain: resolved?.domain, run: resolved?.run, step: resolved?.step, level: resolved?.level, lat: view.lat, lon: view.lon };
  const point = usePoint(pointKey);
  const profile = useProfile(pointKey);
  const timeseries = useTimeseries(pointKey);
  const hasClouds = !!meta.data?.level_layers.includes("cloud_fraction");
  const clouds = useClouds(pointKey, hasClouds);
  const cloudsSeries = useCloudsSeries(pointKey, hasClouds);
  const domainSeries = useSummarySeries(resolved?.domain, resolved?.run, resolved?.level);
  const wmsLayers = useWmsLayers();
  const overlayTimes = useOverlayTimes(view.ov);
  const overlayStates: Record<string, OverlayState> = Object.fromEntries(view.ov.map((layer, i) => {
    const q = overlayTimes[i];
    return [layer, { time: q?.data?.times.at(-1), error: !!q?.isError || !!tileErrors[layer], loading: !!q?.isLoading }];
  }));
  const overlayKey = view.ov.filter((l) => overlayStates[l]?.time && !overlayStates[l]?.error)
    .map((l) => `${l}@${overlayStates[l]!.time!}`).join(",");
  const overlays = useMemo(() => (overlayKey ? overlayKey.split(",") : []).map((k) => {
    const [layer, time] = k.split("@") as [string, string];
    return { layer, time, opacity: 0.9 };
  }), [overlayKey]);
  const labelOf = (l: string) => wmsLayers.data?.find((w) => w.layer === l)?.label ?? l;
  const toggleOverlay = useCallback((layer: string) => {
    setTileErrors((e) => ({ ...e, [layer]: false }));
    update({ ov: view.ov.includes(layer) ? view.ov.filter((l) => l !== layer) : [...view.ov, layer] });
  }, [update, view.ov]);
  const retryOverlay = useCallback((layer: string) => {
    setTileErrors((e) => ({ ...e, [layer]: false }));
    overlayTimes[view.ov.indexOf(layer)]?.refetch();
  }, [overlayTimes, view.ov]);
  const onOverlayError = useCallback((layer: string) => setTileErrors((e) => (e[layer] ? e : { ...e, [layer]: true })), []);
  const IR = "mtg_fd:ir105_hrfi";
  const comparing = def.id === "cloud_top_teff_k" && view.ov.includes(IR);
  const selectLayer = useCallback((id: string) => {
    if (layers.some((d) => d.id === id)) update({ layer: id });
  }, [layers, update]);

  const step = useCallback((dir: 1 | -1) => {
    if (meta.data && resolved) update({ step: nextStep(meta.data, resolved.step, dir) });
  }, [meta.data, resolved, update]);

  useEffect(() => {
    if (!playing || !meta.data || !resolved) return;
    const id = window.setTimeout(() => {
      const next = nextStep(meta.data!, resolved.step, 1);
      if (next === resolved.step) setPlaying(false); else update({ step: next });
    }, 1000);
    return () => window.clearTimeout(id);
  }, [playing, meta.data, resolved, update]);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") { update({ lat: undefined, lon: undefined, panel: undefined }); setToast(null); return; }
      if (ownsKeys(e.target) || e.ctrlKey || e.metaKey || e.altKey || !meta.data || !resolved) return;
      if (e.key === "ArrowRight") { step(1); e.preventDefault(); }
      else if (e.key === "ArrowLeft") { step(-1); e.preventDefault(); }
      else if (e.key === "ArrowUp") { update({ level: nextLevel(meta.data, resolved.level, 1) }); e.preventDefault(); }
      else if (e.key === "ArrowDown") { update({ level: nextLevel(meta.data, resolved.level, -1) }); e.preventDefault(); }
      else if (e.key === " " && !(e.target instanceof HTMLButtonElement)) { setPlaying((p) => !p); e.preventDefault(); }
      else if (e.key.toLowerCase() === "l") layerListRef.current?.querySelector<HTMLInputElement>("input:checked")?.focus();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [meta.data, resolved, step, update]);

  const onPick = useCallback((lat: number, lon: number) => {
    if (!domain || lat < domain.south || lat > domain.north || lon < domain.west || lon > domain.east) {
      setToast(fr.outsideDomain);
      return;
    }
    setToast(null);
    update({ lat: Math.round(lat * 100) / 100, lon: Math.round(lon * 100) / 100 });
  }, [domain, update]);

  const onNow = useCallback(() => update({ run: undefined, step: undefined }), [update]);

  if (domains.isError) return <main className="app-state"><ErrorBox error={domains.error} what="Domaines" /></main>;
  if (!domain) return <main className="app-state"><Skeleton height={200} /></main>;

  return (
    <div className="app">
      <TopBar domains={domains.data ?? []} domain={domain.name} runs={runs.data ?? []} run={resolved?.run ?? ""}
              meta={meta.data} step={resolved?.step} level={resolved?.level} now={now} onChange={update}
              onPrev={() => step(-1)} onNext={() => step(1)} onNow={onNow}
              status={<DataStatus run={run} cloudStatus={meta.data?.cloud_status} now={now} />} />
      <SideNav layers={layers} layer={def.id} onLayer={(id) => update({ layer: id })} streamlines={streamlines}
               onStreamlines={setStreamlines} panel={view.panel} onPanel={(panel) => update({ panel })} layerListRef={layerListRef}>
        <OverlayPanel layers={wmsLayers.data} active={view.ov} states={overlayStates} onToggle={toggleOverlay} onRetry={retryOverlay} />
        <SavedViews onApply={(search) => { window.history.replaceState(null, "", search); window.dispatchEvent(new PopStateEvent("popstate")); }} />
      </SideNav>
      <main className="main" id="main">
        {runs.isSuccess && usableRuns.length === 0 && <EmptyRuns domain={domain.name} />}
        {runs.isError && <ErrorBox error={runs.error} what="Runs" />}
        {meta.isError && <ErrorBox error={meta.error} what="Métadonnées du run" />}
        {run?.status === "partial" && <Banner>{fr.partialRun}</Banner>}
        {newer && (
          <Banner>
            Run plus récent disponible : {runLabel(newer)}. La vue reste sur le run {runLabel(view.run!)}.{" "}
            <button type="button" className="text-button" onClick={() => update({ run: newer, step: undefined })}>
              Afficher le run {runLabel(newer)} (échéance la plus proche de maintenant)
            </button>
          </Banner>
        )}
        {view.panel === "api" && <div className="api-overlay"><RegistryPage registry={registry.data} /></div>}
        {resolved && meta.data && (
          <KpiRow summary={summary.data} classIndex={classIndex >= 0 ? classIndex : null} onSelectLayer={selectLayer}
                  stale={summary.isPlaceholderData} />
        )}
        {summary.isError && <ErrorBox error={summary.error} what="Indicateurs du domaine" />}
        {resolved && meta.data && (
          <section className="map-panel" aria-label="Carte">
            <div className="map-stage">
              <Suspense fallback={<Skeleton height={420} label="Chargement de la carte" />}>
                <MapView domain={domain} field={fieldData} stale={field.isPlaceholderData} def={def} awciBounds={awciBounds} wind={wind} overlays={overlays}
                         onOverlayError={onOverlayError}
                         point={view.lat !== undefined && view.lon !== undefined ? { lat: view.lat, lon: view.lon } : undefined}
                         opacity={fieldOpacity(comparing, opacity)} onPick={onPick} />
              </Suspense>
              <Legend def={def} classLabels={classLabels} awciBounds={awciBounds} />
              {field.isPlaceholderData && <div className="map-loading" role="status">Chargement : {def.label}…</div>}
              {field.isError && <div className="map-error"><ErrorBox error={field.error} what={def.label} /></div>}
              {toast && <div className="toast" role="alert">{toast}</div>}
              <ObservedBadges items={overlays.map((o) => ({ label: labelOf(o.layer), time: o.time }))} now={now} />
            </div>
            {def.id === "cloud_top_teff_k" && !view.ov.includes(IR) && (
              <button type="button" className="text-button" onClick={() => toggleOverlay(IR)}>Comparer à l'observation MTG IR 10,5 µm</button>
            )}
            {comparing && (
              <CompareControl forecastValid={meta.data.valid_times[meta.data.steps.indexOf(resolved.step)]}
                              observedAt={overlayStates[IR]?.time} opacity={opacity} onOpacity={setOpacity} />
            )}
            <TimeBar meta={meta.data} step={resolved.step} onStep={(s) => update({ step: s })} playing={playing}
                     onTogglePlay={() => setPlaying((p) => !p)} />
          </section>
        )}
        {resolved && meta.data && (
          <aside className="side-column" aria-label="Situation et point">
            <Situation summary={freshData(summary)} meta={meta.data} step={resolved.step} domainLabel={domain.label} />
            {point.isError && <ErrorBox error={point.error} what="Point" />}
            <Inspector point={point.data} registry={registry.data} />
            <ModelAgreement />
            <LatestRuns runs={runs.data ?? []} now={now} />
          </aside>
        )}
        {resolved && meta.data && (
          <div className="bottom-row">
            <TimeEvolution point={timeseries.data} domain={domainSeries.data} meta={meta.data} step={resolved.step} />
            {profile.data && <AwciProfile profile={profile.data} awciBounds={awciBounds} current={resolved.level} />}
            {profile.data && <AtmoProfile profile={profile.data} />}
            {view.lat !== undefined && (
              <CloudsPanel clouds={clouds.data} series={cloudsSeries.data} currentStep={resolved.step} unavailable={!hasClouds} />
            )}
            {view.lat === undefined && view.panel === "clouds" && (
              <section className="panel clouds-panel"><h2>Nuages</h2><p className="panel-note">Cliquer sur la carte pour afficher les couches nuageuses d'un point.</p></section>
            )}
            {clouds.isError && <ErrorBox error={clouds.error} what="Nuages" />}
          </div>
        )}
      </main>
    </div>
  );
}
