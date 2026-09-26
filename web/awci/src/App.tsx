import { lazy, Suspense, useCallback, useEffect, useMemo, useRef, useState } from "react";
import "./App.css";
import { freshData, useAirport, useAirports, useClouds, useCloudsSeries, useDomains, useField, useMeta, useSigmets, useTerrain, useVerification, useVolume, useEnsMeta, useEnsPoint, useEnsRuns, useOverlayTimes, usePoint, useWmsLayers, useProfile, useRegistry, useRuns, useSummary, useSummarySeries, useTimeseries } from "./api/hooks";
import { fr } from "./i18n/fr";
import { Legend, ObsLegend } from "./map/Legend";
import { layerDef } from "./map/layers";
import type { Map as MlMap } from "maplibre-gl";
import type { WindGrid } from "./map/streamlines";
import { hasWebGL2 } from "./lib/webgl";
import { VOLUME_LAYERS } from "./volume/layers3d";
import { View3DControls, type CameraPreset } from "./volume/View3DControls";
import { airportFeatures } from "./lib/aero";
import { AeroControls } from "./panels/AeroControls";
import { AirportPanel } from "./panels/AirportPanel";
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
import { EnsemblePanel } from "./panels/EnsemblePanel";
import { Situation } from "./panels/Situation";
import { SideNav } from "./panels/SideNav";
import { SigmetList } from "./panels/SigmetList";
import { ValidationPage } from "./panels/ValidationPage";
import { Banner, EmptyRuns, ErrorBox, Skeleton } from "./panels/StateViews";
import { TimeBar } from "./panels/TimeBar";
import { TopBar } from "./panels/TopBar";
import { runLabel, stepLabel } from "./lib/format";
import { ownsKeys } from "./lib/keys";
import { availableLayers, ensStepAvailable, newerRun, nextLevel, nextStep, resolveView, useViewState, withPinnedRun, type ViewState } from "./state/view";

const MapView = lazy(() => import("./map/MapView").then((m) => ({ default: m.MapView })));
const Volume3D = lazy(() => import("./volume/Volume3D"));
const CAMERA: Record<CameraPreset, { pitch: number; bearing: number }> = {
  top: { pitch: 0, bearing: 0 }, south: { pitch: 55, bearing: 0 }, west: { pitch: 55, bearing: 90 },
};

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
  // SP5: IFS ENS for the run on screen, when acf-awci-ens produced it
  const ensRuns = useEnsRuns(domain?.name);
  const hasEns = !!runId && !!ensRuns.data?.some((r) => r.run === runId);
  const ensMeta = useEnsMeta(domain?.name, runId, hasEns);
  const registry = useRegistry();
  const resolved = domains.data && runs.data ? resolveView(view, domains.data, runs.data, meta.data, now, ensMeta.data) : null;
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
  // An ENS layer at a step the ensemble did not compute is not requested (and never borrowed from a neighbour).
  const ensGap = def.source === "ens" && resolved !== null && !ensStepAvailable(ensMeta.data, resolved.step);
  const ensNeighbours = useMemo(() => (def.source === "ens" ? neighbours.filter((s) => ensStepAvailable(ensMeta.data, s)) : neighbours),
    [def.source, neighbours, ensMeta.data]);
  const field = useField({ domain: resolved?.domain, run: resolved?.run, layer: ensGap ? undefined : resolved?.layer,
    step: resolved?.step, level: resolved?.level, perLevel: def.perLevel, source: def.source }, ensNeighbours);
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
  const layers = useMemo(() => (meta.data ? availableLayers(meta.data, ensMeta.data) : []), [meta.data, ensMeta.data]);
  const summary = useSummary(resolved?.domain, resolved?.run, resolved?.step, resolved?.level, neighbours);
  const classIndex = summary.data?.awci_class ? classLabels.indexOf(summary.data.awci_class) : -1;
  const pointKey = { domain: resolved?.domain, run: resolved?.run, step: resolved?.step, level: resolved?.level, lat: view.lat, lon: view.lon };
  const point = usePoint(pointKey);
  const ensPoint = useEnsPoint({ domain: resolved?.domain, run: resolved?.run, lat: view.lat, lon: view.lon, level: resolved?.level }, hasEns);
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
  // SP3: aeronautical observations at the valid time on screen (never the previous time's, see freshData).
  const validTime = meta.data && resolved ? meta.data.valid_times[meta.data.steps.indexOf(resolved.step)] : undefined;
  const airportsQ = useAirports(domain?.name, validTime);
  const sigmetsQ = useSigmets(domain?.name, validTime, view.aero.includes("sigmet"));
  const airportQ = useAirport(domain?.name, view.ap, resolved?.run);
  const verificationQ = useVerification(domain?.name, resolved?.run, view.panel === "validation");
  const freshAirports = freshData(airportsQ);
  const airportPoints = useMemo(() => (view.aero.includes("metar") ? airportFeatures(freshAirports) : undefined),
    [view.aero, freshAirports]);
  const freshSigmets = freshData(sigmetsQ);
  const sigmetShapes = view.aero.includes("sigmet") ? freshSigmets : undefined;
  const selectAirport = useCallback((icao: string | undefined) => {
    const a = icao ? airportsQ.data?.airports.find((x) => x.icao === icao) : undefined;
    update(a ? { ap: a.icao, lat: Math.round(a.lat * 100) / 100, lon: Math.round(a.lon * 100) / 100 } : { ap: undefined });
  }, [airportsQ.data, update]);
  // SP2B: 3-D volume view. Volumes of the valid time on screen only (freshData); the next two steps preloaded.
  const [mapInstance, setMapInstance] = useState<MlMap | null>(null);
  const [webgl2] = useState(hasWebGL2);
  const mode3d = view.mode3d && webgl2;
  const volDefs = VOLUME_LAYERS.filter((d) => view.vol.includes(d.id));
  const next3d = useMemo(() => {
    if (!meta.data || !resolved) return [];
    const a = nextStep(meta.data, resolved.step, 1);
    const b = nextStep(meta.data, a, 1);
    return [a, b].filter((s, i, all) => s !== resolved.step && all.indexOf(s) === i);
  }, [meta.data, resolved?.step]); // eslint-disable-line react-hooks/exhaustive-deps
  const volKey = (layer: string | undefined) => ({ domain: resolved?.domain, run: resolved?.run, layer, step: resolved?.step, stride: 1 });
  const vol0 = useVolume(volKey(volDefs[0]?.source), next3d, mode3d && !!volDefs[0]);
  const aux0 = useVolume(volKey(volDefs[0]?.aux), next3d, mode3d && !!volDefs[0]?.aux);
  const vol1 = useVolume(volKey(volDefs[1]?.source), next3d, mode3d && !!volDefs[1]);
  const aux1 = useVolume(volKey(volDefs[1]?.aux), next3d, mode3d && !!volDefs[1]?.aux);
  const terrain = useTerrain(resolved?.domain, resolved?.run, 1, mode3d);
  const volIds = view.vol.join(",");
  const volumeInputs = useMemo(() => {
    const volDefs = VOLUME_LAYERS.filter((d) => volIds.split(",").includes(d.id));
    const slots = [[vol0, aux0], [vol1, aux1]] as const;
    const out = [];
    for (const [i, d] of volDefs.entries()) {
      const [v, a] = slots[i]!;
      const volume = freshData(v);
      const aux = d.aux ? freshData(a) : undefined;
      if (!volume || (d.aux && !aux)) continue;
      out.push({ def: d, volume, aux });
    }
    return out;
  }, [volIds, vol0.data, aux0.data, vol1.data, aux1.data, vol0.isPlaceholderData, aux0.isPlaceholderData, vol1.isPlaceholderData, aux1.isPlaceholderData]); // eslint-disable-line react-hooks/exhaustive-deps
  const volumeLoading = [vol0, aux0, vol1, aux1].some((q) => q.isFetching && (q.isPlaceholderData || !q.data));
  const flightLevels = useMemo(() => Object.fromEntries((meta.data?.levels_hpa ?? []).map((p, i) => [p, meta.data!.flight_levels[i]!])),
    [meta.data]);
  const onPickVoxel = useCallback((lat: number, lon: number, levelHpa: number) =>
    update({ lat: Math.round(lat * 100) / 100, lon: Math.round(lon * 100) / 100, level: levelHpa }), [update]);
  // In 3-D a ground click would pick the point under the perspective, not the voxel seen: only voxels pick.
  const noPick = useCallback(() => undefined, []);
  const onCamera = useCallback((preset: CameraPreset) => {
    const reduce = window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;
    mapInstance?.easeTo({ ...CAMERA[preset], duration: reduce ? 0 : 600 });
  }, [mapInstance]);
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
      if (e.key === "Escape") { update({ lat: undefined, lon: undefined, panel: undefined, ap: undefined }); setToast(null); return; }
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
        <AeroControls airports={airportsQ.data} layers={view.aero} selected={view.ap} now={now}
                      onLayers={(aero) => update({ aero })} onSelect={selectAirport} />
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
        {view.panel === "validation" && (
          <div className="api-overlay"><ValidationPage verification={verificationQ.data} isLoading={verificationQ.isLoading} error={verificationQ.error} /></div>
        )}
        {resolved && meta.data && (
          <KpiRow summary={summary.data} classIndex={classIndex >= 0 ? classIndex : null} onSelectLayer={selectLayer}
                  stale={summary.isPlaceholderData} />
        )}
        {summary.isError && <ErrorBox error={summary.error} what="Indicateurs du domaine" />}
        {resolved && meta.data && (
          <section className="map-panel" aria-label="Carte">
            <div className="map-stage">
              <Suspense fallback={<Skeleton height={420} label="Chargement de la carte" />}>
                <MapView domain={domain} field={ensGap ? undefined : fieldData} stale={!ensGap && field.isPlaceholderData} def={def} awciBounds={awciBounds} wind={wind} overlays={overlays}
                         onOverlayError={onOverlayError} airports={airportPoints} sigmets={sigmetShapes} onPickAirport={selectAirport}
                         point={view.lat !== undefined && view.lon !== undefined ? { lat: view.lat, lon: view.lon } : undefined}
                         opacity={fieldOpacity(comparing, opacity)} onPick={mode3d ? noPick : onPick} mode3d={mode3d} onMap={setMapInstance} />
              </Suspense>
              {mode3d && mapInstance && (
                <Suspense fallback={<div className="map-loading" role="status">Chargement de la vue 3D…</div>}>
                  <Volume3D map={mapInstance} inputs={volumeInputs} terrain={terrain.data} exaggeration={view.exag}
                            threshold={view.cth} awciBounds={awciBounds} flightLevels={flightLevels} onPickVoxel={onPickVoxel} />
                </Suspense>
              )}
              <div className="map-toolbar">
                <button type="button" className="text-button" aria-pressed={mode3d} disabled={!webgl2}
                        onClick={() => update({ mode3d: !view.mode3d })}>{mode3d ? "Vue 2D" : "Vue 3D"}</button>
              </div>
              {!mode3d && <Legend def={def} classLabels={classLabels} awciBounds={awciBounds} />}
              {field.isPlaceholderData && !ensGap && <div className="map-loading" role="status">Chargement : {def.label}…</div>}
              {ensGap && (
                <div className="map-loading" role="status">
                  Pas de probabilité ENS à {stepLabel(resolved.step)} : l'ensemble est calculé à {(ensMeta.data?.steps ?? []).filter((s) => !ensMeta.data?.missing_steps.includes(s)).map(stepLabel).join(", ")}.
                </div>
              )}
              {field.isError && <div className="map-error"><ErrorBox error={field.error} what={def.label} /></div>}
              {toast && <div className="toast" role="alert">{toast}</div>}
              <ObservedBadges items={overlays.map((o) => ({ label: labelOf(o.layer), time: o.time }))} now={now} />
            </div>
            {def.id === "cloud_top_teff_k" && !view.ov.includes(IR) && (
              <button type="button" className="text-button" onClick={() => toggleOverlay(IR)}>Comparer à l'observation MTG IR 10,5 µm</button>
            )}
            {view.mode3d && !webgl2 && <p className="notice">Vue 3D indisponible : ce navigateur ne fournit pas WebGL2.</p>}
            {mode3d && (
              <View3DControls vol={view.vol} exag={view.exag} cth={view.cth} loading={volumeLoading}
                              onChange={(patch) => update(patch)} onCamera={onCamera} onExit={() => update({ mode3d: false })} />
            )}
            <ObsLegend metar={view.aero.includes("metar")}
                       hazards={[...new Set((sigmetShapes?.features ?? []).map((f) => f.properties.hazard))]} />
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
            {view.aero.includes("sigmet") && <SigmetList sigmets={freshSigmets} isError={sigmetsQ.isError} />}
            <EnsemblePanel point={ensPoint.data} step={resolved.step} deterministicAwci={point.data?.awci ?? null} unavailable={!hasEns}
                           ensCloudProfile={ensMeta.data?.cloud_profile_version} detCloudProfile={meta.data.cloud_profile?.version} />
            <LatestRuns runs={runs.data ?? []} now={now} />
          </aside>
        )}
        {resolved && meta.data && (
          <div className="bottom-row">
            {view.ap && <AirportPanel detail={airportQ.data} currentStep={resolved.step} now={now} loading={airportQ.isLoading} />}
            {view.ap && airportQ.isError && <ErrorBox error={airportQ.error} what={`Aérodrome ${view.ap}`} />}
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
