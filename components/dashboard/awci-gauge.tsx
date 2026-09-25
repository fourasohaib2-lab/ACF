"use client"

/** Real circular gauge - a plain SVG arc, value-driven (no fabricated
 * animation/decoration beyond what the real number implies). Sweeps
 * 270 real degrees (-135 to +135) so 0 and 100 read as distinct
 * endpoints, matching common aviation-gauge convention. */
const TONE_COLOR = {
  normal: "var(--accent)",
  warning: "var(--warning)",
  severe: "var(--severe)",
  critical: "var(--critical)",
} as const

export function AwciGauge({
  value,
  label,
  size = 108,
  tone = "normal",
}: {
  value: number | null
  label: string
  size?: number
  tone?: "normal" | "warning" | "severe" | "critical"
}) {
  const stroke = 10
  const radius = (size - stroke) / 2
  const circumference = 2 * Math.PI * radius
  const sweepFraction = 270 / 360
  const arcLength = circumference * sweepFraction
  const filledLength = value !== null ? arcLength * Math.max(0, Math.min(1, value / 100)) : 0
  const toneColor = TONE_COLOR[tone]

  return (
    <div className="flex flex-col items-center justify-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} className="-rotate-[225deg]">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="var(--border-subtle)"
          strokeWidth={stroke}
          strokeDasharray={`${arcLength} ${circumference}`}
          strokeLinecap="round"
        />
        {value !== null && (
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke={toneColor}
            strokeWidth={stroke}
            strokeDasharray={`${filledLength} ${circumference}`}
            strokeLinecap="round"
            style={{ transition: "stroke-dasharray 0.4s ease" }}
          />
        )}
      </svg>
      <div className="-mt-[68%] flex flex-col items-center">
        <span className="font-mono text-2xl font-bold leading-none" style={{ color: toneColor }}>
          {value !== null ? value.toFixed(0) : "—"}
        </span>
        <span className="mt-1 font-mono text-[9px] uppercase tracking-wider text-muted">{label}</span>
      </div>
    </div>
  )
}
