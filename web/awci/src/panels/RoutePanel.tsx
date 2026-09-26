import { useState, type FormEvent } from "react";
import type { RouteMeteogram as MeteogramPayload, RouteSection } from "../api/types";
import { CrossSection } from "../charts/CrossSection";
import { RouteMeteogram } from "../charts/RouteMeteogram";
import { MAX_WAYPOINTS, routeFromIcao, type LatLon } from "../lib/route";
import type { LayerDef } from "../map/layers";
import { ErrorBox, Skeleton } from "./StateViews";

interface Query<T> { data: T | undefined; isLoading: boolean; isPlaceholderData?: boolean; error: unknown }
interface Props {
  route: LatLon[] | undefined;
  editing: boolean;
  onEditing: (editing: boolean) => void;
  onRoute: (route: LatLon[] | undefined) => void;
  airports: { icao: string; lat: number; lon: number }[];
  section: Query<RouteSection>;
  meteogram: Query<MeteogramPayload>;
  def: LayerDef;
  /** The map layer has no vertical dimension: the section shows `def` (AWCI) instead, said so. */
  substituted?: string;
  awciBounds: number[];
  classLabels: string[];
  step: number;
  level: number;
  onSelect: (step: number, level: number) => void;
}

/** Waypoint names: the aerodrome at that position when there is one, else P1, P2… */
export function waypointLabels(route: LatLon[], airports: { icao: string; lat: number; lon: number }[]): string[] {
  return route.map(([la, lo], i) => airports.find((a) => Math.abs(a.lat - la) < 0.005 && Math.abs(a.lon - lo) < 0.005)?.icao ?? `P${i + 1}`);
}

export function RoutePanel({ route, editing, onEditing, onRoute, airports, section, meteogram, def, substituted, awciBounds,
  classLabels, step, level, onSelect }: Props) {
  const [icao, setIcao] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const n = route?.length ?? 0;
  const labels = route ? waypointLabels(route, airports) : [];
  const submit = (e: FormEvent) => {
    e.preventDefault();
    const { points, unknown } = routeFromIcao(icao, airports);
    if (unknown.length) { setMessage(`Aérodrome inconnu dans ce domaine : ${unknown.join(", ")}.`); return; }
    if (points.length < 2) { setMessage("Donner au moins deux aérodromes, par exemple « DAAG DTTA »."); return; }
    if (points.length > MAX_WAYPOINTS) { setMessage(`${MAX_WAYPOINTS} points au plus.`); return; }
    setMessage(null);
    onEditing(false);
    onRoute(points);
  };
  return (
    <section className="panel route-panel" aria-label="Route">
      <h2>Route {n >= 2 ? <span className="panel-note">{labels.join(" → ")}</span> : null}</h2>
      <div className="route-tools">
        <button type="button" className="text-button" aria-pressed={editing} onClick={() => onEditing(!editing)}>
          {editing ? "Terminer le tracé" : "Tracer sur la carte"}
        </button>
        {editing && n > 0 && <button type="button" className="text-button" onClick={() => onRoute(route!.slice(0, -1))}>Retirer le dernier point</button>}
        {n > 0 && <button type="button" className="text-button" onClick={() => { onEditing(false); onRoute(undefined); }}>Effacer la route</button>}
        <form className="route-icao" onSubmit={submit}>
          <label htmlFor="route-icao">Aérodromes OACI</label>
          <input id="route-icao" value={icao} onChange={(e) => setIcao(e.target.value)} placeholder="DAAG DTTA" autoComplete="off"
                 spellCheck={false} aria-describedby={message ? "route-icao-msg" : undefined} />
          <button type="submit" className="text-button">Tracer</button>
        </form>
      </div>
      {message && <p id="route-icao-msg" className="notice" role="alert">{message}</p>}
      {editing && (
        <p className="panel-note" role="status">Cliquer sur la carte (ou sur un aérodrome) pour ajouter un point : {n}/{MAX_WAYPOINTS}.
          Échap ou « Terminer le tracé » pour finir.</p>
      )}
      {n < 2 && !editing && <p className="panel-note">Tracer une route (deux points au moins) pour obtenir la coupe verticale et le météogramme de route.</p>}
      {n >= 2 && (
        <>
          <h3 className="subhead">Coupe verticale : {def.label}</h3>
          {substituted && <p className="panel-note">La couche « {substituted} » n'a pas de dimension verticale : la coupe montre l'AWCI.</p>}
          {section.error ? <ErrorBox error={section.error} what="Coupe verticale" />
            : section.data ? <CrossSection section={section.data} def={def} awciBounds={awciBounds} classLabels={classLabels} currentLevel={level}
                                           waypointLabels={labels} stale={section.isPlaceholderData} />
              : <Skeleton height={220} label="Calcul de la coupe verticale" />}
          <h3 className="subhead">Météogramme de route</h3>
          {meteogram.error ? <ErrorBox error={meteogram.error} what="Météogramme de route" />
            : meteogram.data ? <RouteMeteogram meteogram={meteogram.data} awciBounds={awciBounds} classLabels={classLabels}
                                               currentStep={step} currentLevel={level} onSelect={onSelect} />
              : <Skeleton height={160} label="Calcul du météogramme de route" />}
          {meteogram.data && <p className="provenance">{meteogram.data.provenance.model} · run {meteogram.data.provenance.run} · {meteogram.data.provenance.attribution}</p>}
        </>
      )}
    </section>
  );
}
