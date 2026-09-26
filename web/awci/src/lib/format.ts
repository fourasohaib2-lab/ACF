export const FT_PER_M = 1 / 0.3048;

export function fmt(value: number | null | undefined, digits = 0, unit = ""): string {
  if (value === null || value === undefined || !Number.isFinite(value)) return "—";
  const s = value.toLocaleString("fr-FR", { minimumFractionDigits: digits, maximumFractionDigits: digits });
  return unit ? `${s} ${unit}` : s;
}

const p2 = (n: number) => String(n).padStart(2, "0");

export function utcLabel(iso: string): string {
  const d = new Date(iso);
  return `${p2(d.getUTCDate())}/${p2(d.getUTCMonth() + 1)} ${p2(d.getUTCHours())}:${p2(d.getUTCMinutes())} UTC`;
}

export const flLabel = (fl: number) => `FL${String(Math.round(fl)).padStart(3, "0")}`;
export const stepLabel = (step: number) => `+${step} h`;

export function ageLabel(iso: string, now: Date): string {
  const minutes = Math.max(0, Math.round((now.getTime() - new Date(iso).getTime()) / 60000));
  if (minutes < 60) return `il y a ${minutes} min`;
  const h = Math.floor(minutes / 60);
  const m = minutes % 60;
  return m ? `il y a ${h} h ${p2(m)}` : `il y a ${h} h`;
}

/** Run id "YYYYMMDDHH" as the same UTC label as the run selector. */
export const runLabel = (run: string) =>
  utcLabel(`${run.slice(0, 4)}-${run.slice(4, 6)}-${run.slice(6, 8)}T${run.slice(8, 10)}:00:00Z`);
