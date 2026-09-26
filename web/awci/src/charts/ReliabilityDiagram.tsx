import type { ReliabilityBin } from "../api/types";
import { DataTable } from "./DataTable";

interface Props { bins: ReliabilityBin[]; climatology: number | null; label: string; minCases?: number }

const W = 320;
const H = 300;
const HIST = 56; // sharpness histogram under the diagram
const PAD = { l: 58, r: 20, t: 10, b: 30 };
const TICKS = [0, 0.2, 0.4, 0.6, 0.8, 1];
const pct = (v: number) => `${(v * 100).toFixed(v > 0 && v < 0.1 ? 1 : 0)} %`;

/**
 * Reliability diagram (Wilks 2011, ch. 8): observed frequency against mean forecast probability per bin, the
 * diagonal of perfect reliability, the sample climatology (no resolution) and the no-skill line halfway between
 * them (Hsu & Murphy 1986). Point area follows the number of cases; bins with fewer than `minCases` cases are
 * hollow. Under it, the sharpness histogram (cases per bin, log scale: the lowest bin usually dominates).
 */
export function ReliabilityDiagram({ bins, climatology, label, minCases = 10 }: Props) {
  const size = W - PAD.l - PAD.r;
  const sx = (p: number) => PAD.l + p * size;
  const sy = (p: number) => PAD.t + (1 - p) * (H - PAD.t - PAD.b);
  const used = bins.filter((b) => b.n > 0 && b.mean_forecast !== null && b.observed_frequency !== null);
  const nMax = Math.max(1, ...bins.map((b) => b.n));
  const radius = (n: number) => 2.5 + 6 * Math.sqrt(n / nMax);
  const line = used.map((b, i) => `${i ? "L" : "M"}${sx(b.mean_forecast!).toFixed(1)},${sy(b.observed_frequency!).toFixed(1)}`).join("");
  const logMax = Math.log10(nMax + 1);
  const barH = (n: number) => (n > 0 ? (Math.log10(n + 1) / logMax) * (HIST - 14) : 0);
  const c = climatology;
  return (
    <figure className="chart reliability">
      <svg viewBox={`0 0 ${W} ${H + HIST}`} className="chart-svg" role="img"
           aria-label={`Diagramme de fiabilité : ${label}. ${used.length} classes de probabilité renseignées.`}>
        {TICKS.map((t) => (
          <g key={t}>
            <line x1={sx(0)} x2={sx(1)} y1={sy(t)} y2={sy(t)} className="chart-grid" />
            <line x1={sx(t)} x2={sx(t)} y1={sy(0)} y2={sy(1)} className="chart-grid" />
            <text x={PAD.l - 6} y={sy(t) + 4} textAnchor="end" className="chart-tick">{pct(t)}</text>
            <text x={sx(t)} y={H - PAD.b + 14} textAnchor="middle" className="chart-tick">{pct(t)}</text>
          </g>
        ))}
        <line x1={sx(0)} y1={sy(0)} x2={sx(1)} y2={sy(1)} className="rel-diagonal" />
        {c !== null && (
          <>
            <line x1={sx(0)} x2={sx(1)} y1={sy(c)} y2={sy(c)} className="rel-climatology" />
            <line x1={sx(0)} y1={sy(c / 2)} x2={sx(1)} y2={sy((1 + c) / 2)} className="rel-noskill" />
          </>
        )}
        <path d={line} fill="none" className="rel-line" />
        {used.map((b) => (
          <circle key={b.lower} cx={sx(b.mean_forecast!)} cy={sy(b.observed_frequency!)} r={radius(b.n)}
                  className={b.n >= minCases ? "rel-point" : "rel-point rel-point-thin"}>
            <title>{`P ${pct(b.lower)}–${pct(b.upper)} : prévu ${pct(b.mean_forecast!)}, observé ${pct(b.observed_frequency!)}, ${b.n} cas`}</title>
          </circle>
        ))}
        <text x={sx(0.5)} y={H - 2} textAnchor="middle" className="chart-tick">Probabilité prévue</text>
        <text x={12} y={sy(0.5)} textAnchor="middle" className="chart-tick" transform={`rotate(-90 12 ${sy(0.5)})`}>Fréquence observée</text>
        {bins.map((b) => (
          <rect key={`h${b.lower}`} x={sx(b.lower) + 1} width={size / bins.length - 2} y={H + HIST - 4 - barH(b.n)} height={barH(b.n)}
                className="rel-hist"><title>{`${b.n} cas`}</title></rect>
        ))}
        <text x={PAD.l - 6} y={H + 12} textAnchor="end" className="chart-tick">cas</text>
      </svg>
      <figcaption className="chart-legend">
        <span><i className="rel-key-diagonal" />fiabilité parfaite</span>
        {c !== null && <span><i className="rel-key-clim" />climatologie de l'échantillon ({pct(c)})</span>}
        {c !== null && <span><i className="rel-key-noskill" />pas de gain (Brier)</span>}
        <span>cercle creux : moins de {minCases} cas · histogramme en échelle log</span>
      </figcaption>
      <details className="chart-data">
        <summary>Voir les données</summary>
        <DataTable caption={`Données du diagramme de fiabilité : ${label}`} columns={["Classe de P", "Cas", "P moyenne", "Fréquence observée"]}
                   rows={bins.map((b) => [`${pct(b.lower)}–${pct(b.upper)}`, b.n,
                     b.mean_forecast === null ? "—" : pct(b.mean_forecast), b.observed_frequency === null ? "—" : pct(b.observed_frequency)])} />
      </details>
    </figure>
  );
}
