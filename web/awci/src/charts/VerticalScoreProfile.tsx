import { fmt } from "../lib/format";
import { DataTable } from "./DataTable";

export interface ProfileSeries { label: string; color: string; dashed?: boolean; values: (number | null)[] }
interface Props {
  title: string; unit: string; levels: number[]; series: ProfileSeries[]; digits?: number;
  /** false when the caller draws one legend shared by several profiles */
  legend?: boolean;
}

const W = 300;
const H = 300;
const PAD = { l: 52, r: 14, t: 10, b: 34 };
const P_TICKS = [1000, 850, 700, 500, 300, 200, 100];

/** Nice tick step (1, 2 or 5 × 10^k) for about five ticks over `span`. */
function tickStep(span: number): number {
  const raw = span / 5;
  const mag = 10 ** Math.floor(Math.log10(raw));
  return [1, 2, 5, 10].map((m) => m * mag).find((s) => s >= raw) ?? 10 * mag;
}

/** Line sample of a legend (colour and dash of a series). */
export const LineKey = ({ color, dashed }: { color: string; dashed?: boolean }) => (
  <svg width="22" height="8" aria-hidden="true" style={{ color, marginRight: 4, verticalAlign: "middle" }}>
    <line x1="1" x2="21" y1="4" y2="4" stroke="currentColor" strokeWidth="2" strokeDasharray={dashed ? "5 3" : undefined} />
  </svg>
);

/**
 * Vertical profile of a score against pressure (logarithmic axis, 1000 hPa at the bottom, the usual aerological
 * convention), with the zero line. One polyline per series, broken where a level has no value; points marked.
 */
export function VerticalScoreProfile({ title, unit, levels, series, digits = 1, legend = true }: Props) {
  const values = series.flatMap((s) => s.values).filter((v): v is number => v !== null && Number.isFinite(v));
  const lo = Math.min(0, ...values);
  const hi = Math.max(0, ...values);
  const span = hi - lo || 1;
  const step = tickStep(span);
  const x0 = Math.floor(lo / step) * step;
  const x1 = Math.ceil(hi / step) * step || step;
  const pMax = Math.max(1000, ...levels);
  const pMin = Math.min(100, ...levels);
  const sx = (v: number) => PAD.l + ((v - x0) / (x1 - x0)) * (W - PAD.l - PAD.r);
  const sy = (p: number) => PAD.t + (Math.log(pMax / p) / Math.log(pMax / pMin)) * (H - PAD.t - PAD.b);
  const xTicks: number[] = [];
  for (let v = x0; v <= x1 + step / 2; v += step) xTicks.push(Number(v.toPrecision(10)));
  const path = (vals: (number | null)[]) => {
    let d = "";
    let pen = false;
    vals.forEach((v, i) => {
      if (v === null || !Number.isFinite(v)) { pen = false; return; }
      d += `${pen ? "L" : "M"}${sx(v).toFixed(1)},${sy(levels[i]!).toFixed(1)}`;
      pen = true;
    });
    return d;
  };
  const filled = series.map((s) => s.values.filter((v) => v !== null).length);
  return (
    <figure className="chart vertical-profile">
      <svg viewBox={`0 0 ${W} ${H}`} className="chart-svg" role="img"
           aria-label={`${title} (${unit}) selon la pression : ${series.map((s, i) => `${s.label}, ${filled[i]} niveaux`).join(" ; ")}.`}>
        {P_TICKS.filter((p) => p <= pMax && p >= pMin).map((p) => (
          <g key={p}>
            <line x1={PAD.l} x2={W - PAD.r} y1={sy(p)} y2={sy(p)} className="chart-grid" />
            <text x={PAD.l - 6} y={sy(p) + 4} textAnchor="end" className="chart-tick">{p}</text>
          </g>
        ))}
        {xTicks.map((v) => (
          <g key={v}>
            <line x1={sx(v)} x2={sx(v)} y1={sy(pMax)} y2={sy(pMin)} className={v === 0 ? "chart-zero" : "chart-grid"} />
            <text x={sx(v)} y={H - PAD.b + 14} textAnchor="middle" className="chart-tick">{fmt(v, step < 1 ? 2 : 0)}</text>
          </g>
        ))}
        {series.map((s) => (
          <g key={s.label} style={{ color: s.color }}>
            <path d={path(s.values)} fill="none" stroke="currentColor" strokeWidth={2} strokeDasharray={s.dashed ? "5 3" : undefined} />
            {s.values.map((v, i) => (v === null ? null : (
              <circle key={levels[i]} cx={sx(v)} cy={sy(levels[i]!)} r={2.6} fill="currentColor">
                <title>{`${s.label}, ${levels[i]} hPa : ${fmt(v, digits)} ${unit}`}</title>
              </circle>
            )))}
          </g>
        ))}
        <text x={(PAD.l + W - PAD.r) / 2} y={H - 4} textAnchor="middle" className="chart-tick">{`${title} (${unit})`}</text>
        <text x={12} y={sy(Math.sqrt(pMax * pMin))} textAnchor="middle" className="chart-tick"
              transform={`rotate(-90 12 ${sy(Math.sqrt(pMax * pMin))})`}>hPa</text>
      </svg>
      {legend && (
        <figcaption className="chart-legend">
          {series.map((s) => <span key={s.label}><LineKey color={s.color} dashed={s.dashed} />{s.label}</span>)}
        </figcaption>
      )}
      <details className="chart-data">
        <summary>Voir les données</summary>
        <DataTable caption={`${title} (${unit})`} columns={["Niveau (hPa)", ...series.map((s) => s.label)]}
                   rows={levels.map((p, i) => [p, ...series.map((s) => (s.values[i] === null ? "—" : fmt(s.values[i]!, digits)))])} />
      </details>
    </figure>
  );
}
