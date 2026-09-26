import type { Meta, SummarySeries, TimeseriesPayload } from "../api/types";
import { LineChart, type Series } from "../charts/LineChart";
import { fmt, utcLabel } from "../lib/format";
import { CATEGORICAL } from "../theme/palette";

interface Props { point: TimeseriesPayload | undefined; domain: SummarySeries | undefined; meta: Meta; step: number }

/** AWCI over the run: at the chosen point (/timeseries) and domain P95 (/summary/series), current step marked. */
export function TimeEvolution({ point, domain, meta, step }: Props) {
  const t = (iso: string) => new Date(iso).getTime();
  const series: Series[] = [];
  if (point) series.push({ id: "point", label: "AWCI au point", color: CATEGORICAL[0], points: point.points.map((p) => ({ x: t(p.valid_time), y: p.awci })) });
  if (domain) series.push({ id: "domain", label: "AWCI P95 domaine", color: CATEGORICAL[1],
    points: domain.points.map((p) => ({ x: t(p.valid_time), y: p.missing ? null : p.awci_p95 ?? null })) });
  const si = meta.steps.indexOf(step);
  return (
    <section className="panel" aria-label="Évolution temporelle">
      <h2>Évolution temporelle</h2>
      {series.length ? (
        <LineChart series={series} yLabel="AWCI (0–100)" yDomain={[0, 100]} format={(v) => fmt(v, 0)}
                   xFormat={(x) => utcLabel(new Date(x).toISOString())} xCurrent={si >= 0 ? t(meta.valid_times[si]!) : undefined} />
      ) : <p className="panel-note">Chargement…</p>}
      {!point && <p className="panel-note">Cliquer sur la carte pour ajouter l'AWCI d'un point.</p>}
    </section>
  );
}
