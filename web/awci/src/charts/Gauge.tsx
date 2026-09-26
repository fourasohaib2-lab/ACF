import { AWCI_CLASS_COLORS } from "../theme/palette";

interface Props { value: number | null; classIndex: number | null; label: string | null }

/** Half-ring gauge 0-100 for the domain AWCI P95; the class is written out, not only coloured. */
export function Gauge({ value, classIndex, label }: Props) {
  const r = 44;
  const c = Math.PI * r;
  const frac = value === null ? 0 : Math.min(1, Math.max(0, value / 100));
  const color = classIndex === null ? "var(--axis)" : AWCI_CLASS_COLORS[classIndex] ?? "var(--axis)";
  return (
    <svg viewBox="0 0 110 64" className="gauge" role="img"
         aria-label={value === null ? "AWCI P95 non disponible" : `AWCI P95 ${value.toFixed(0)} sur 100, classe ${label}`}>
      <path d="M 11 56 A 44 44 0 0 1 99 56" fill="none" stroke="var(--surface-3)" strokeWidth="9" strokeLinecap="round" />
      <path d="M 11 56 A 44 44 0 0 1 99 56" fill="none" stroke={color} strokeWidth="9" strokeLinecap="round"
            strokeDasharray={`${c * frac} ${c}`} />
      <text x="55" y="50" textAnchor="middle" className="gauge-value">{value === null ? "—" : value.toFixed(0)}</text>
    </svg>
  );
}
