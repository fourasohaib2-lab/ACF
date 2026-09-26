import type { ProfilePayload } from "../api/types";
import { DataTable } from "../charts/DataTable";
import { flLabel, fmt } from "../lib/format";
import { SERIES } from "../theme/palette";

const W = 360;
const H = 300;
const PAD = { l: 56, r: 64, t: 10, b: 26 };

/** T and Td (server-computed) against real geopotential height, wind per level, cloud fraction band. */
export function AtmoProfile({ profile }: { profile: ProfilePayload }) {
  const rows = profile.levels.filter((l) => l.level_layers.t !== null && l.level_layers.gh !== null)
    .map((l) => ({ p: l.level_hpa, fl: l.flight_level, z: l.level_layers.gh! / 1000, t: l.level_layers.t! - 273.15,
      td: l.dewpoint_k === null ? null : l.dewpoint_k - 273.15, u: l.level_layers.u ?? null, v: l.level_layers.v ?? null,
      cf: l.level_layers.cloud_fraction ?? null }))
    .sort((a, b) => a.z - b.z);
  if (rows.length < 2) return null;
  const temps = rows.flatMap((r) => [r.t, r.td ?? r.t]);
  const [t0, t1] = [Math.floor(Math.min(...temps) / 10) * 10, Math.ceil(Math.max(...temps) / 10) * 10];
  const zMax = Math.ceil(rows[rows.length - 1]!.z);
  const sx = (t: number) => PAD.l + ((t - t0) / (t1 - t0 || 1)) * (W - PAD.l - PAD.r);
  const sy = (z: number) => PAD.t + (1 - z / zMax) * (H - PAD.t - PAD.b);
  const line = (key: "t" | "td") => rows.filter((r) => r[key] !== null).map((r, i) => `${i ? "L" : "M"}${sx(r[key]!).toFixed(1)},${sy(r.z).toFixed(1)}`).join("");
  return (
    <section className="panel" aria-label="Profil atmosphérique">
      <h2>Profil atmosphérique</h2>
      <svg viewBox={`0 0 ${W} ${H}`} className="chart-svg" role="img" aria-label="Température et point de rosée selon l'altitude">
        {[0, zMax / 2, zMax].map((z) => (
          <g key={z}><line x1={PAD.l} x2={W - PAD.r} y1={sy(z)} y2={sy(z)} className="chart-grid" />
            <text x={PAD.l - 6} y={sy(z) + 4} textAnchor="end" className="chart-tick">{fmt(z, 0)} km</text></g>
        ))}
        {[t0, 0, t1].filter((t, i, a) => t >= t0 && t <= t1 && a.indexOf(t) === i).map((t) => (
          <g key={t}><line x1={sx(t)} x2={sx(t)} y1={PAD.t} y2={H - PAD.b} className="chart-grid" />
            <text x={sx(t)} y={H - 8} textAnchor="middle" className="chart-tick">{t} °C</text></g>
        ))}
        {rows.map((r) => r.cf === null ? null : (
          <rect key={`cf-${r.p}`} x={8} y={sy(r.z) - 5} width={10} height={10} style={{ fill: SERIES[0] }} opacity={Math.max(0.08, r.cf)}>
            <title>{`${flLabel(r.fl)} : ${fmt(r.cf * 8, 1)} octas`}</title>
          </rect>
        ))}
        <path d={line("t")} fill="none" style={{ stroke: SERIES[1] }} strokeWidth={1.8} />
        <path d={line("td")} fill="none" style={{ stroke: SERIES[2] }} strokeWidth={1.8} strokeDasharray="4 3" />
        {rows.map((r) => {
          if (r.u === null || r.v === null) return null;
          const speed = Math.hypot(r.u, r.v);
          const len = Math.min(22, 6 + speed / 3);
          const angle = (Math.atan2(-r.v, r.u) * 180) / Math.PI; // arrow points where the air goes (SVG y down)
          return (
            <g key={`w-${r.p}`} transform={`translate(${W - PAD.r + 30},${sy(r.z)}) rotate(${angle})`}>
              <line x1={-len / 2} x2={len / 2} y1={0} y2={0} stroke="var(--text-2)" strokeWidth={1.4} />
              <path d={`M${len / 2},0 l-5,-3 v6 z`} fill="var(--text-2)" />
              <title>{`${flLabel(r.fl)} : ${fmt(speed * 1.943844, 0)} kt`}</title>
            </g>
          );
        })}
      </svg>
      <p className="chart-legend"><span><i style={{ background: SERIES[1] }} />T</span>
        <span><i style={{ background: SERIES[2] }} />Td (tirets)</span><span><i style={{ background: SERIES[0] }} />fraction nuageuse</span>
        <span>flèches : vent (kt au survol)</span></p>
      <details className="chart-data"><summary>Voir les données</summary>
        <DataTable caption="Profil atmosphérique" columns={["Niveau", "Altitude", "T", "Td", "Vent", "Nuages"]}
                   rows={rows.map((r) => [`${flLabel(r.fl)} · ${r.p} hPa`, `${fmt(r.z * 1000, 0)} m`, fmt(r.t, 1, "°C"), fmt(r.td, 1, "°C"),
                     r.u === null || r.v === null ? "—" : fmt(Math.hypot(r.u, r.v) * 1.943844, 0, "kt"), r.cf === null ? "—" : fmt(r.cf * 8, 1, "octas")])} />
      </details>
    </section>
  );
}
