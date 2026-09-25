"use client"

import { AlertTriangle, Loader2 } from "lucide-react"
import { Panel, PanelHeader } from "@/components/ui/panel"
import { useVerticalProfile } from "@/lib/hooks/use-vertical-profile"
import { useComplexityField } from "@/lib/hooks/use-complexity-field"
import { classifyLevel, toneForLevel } from "@/lib/complexity-stats"
import { cn } from "@/lib/utils"

const toneText = { normal: "text-accent", warning: "text-warning", critical: "text-critical" } as const
const toneBg = { normal: "bg-accent/15", warning: "bg-warning/15", critical: "bg-critical/15" } as const

/**
 * Real "AWCI Vertical Profile" table - one row per real native model
 * level of the same shared `GET /complexity/vertical-profile` column
 * the Vertical Profile / Atmospheric Profile charts already plot
 * (`VerticalProfileProvider`, no extra fetch). Level classification
 * reuses the shared 2D field's real `level_thresholds`
 * (`ComplexityFieldProvider`) - the same real bands every other panel
 * on this dashboard classifies against, not a duplicated copy.
 */
export function AwciVerticalProfileTable() {
  const { data: profile, loading, error, samplePoint } = useVerticalProfile()
  const field = useComplexityField()

  const subtitle = samplePoint
    ? `${samplePoint.latitude.toFixed(1)}°N ${samplePoint.longitude.toFixed(1)}°E · Route Midpoint`
    : "Per-Level Breakdown"

  if (error || field.error) {
    return (
      <Panel className="flex h-full flex-col overflow-hidden">
        <PanelHeader title="AWCI Vertical Profile" subtitle={subtitle} />
        <div className="flex flex-1 items-center gap-2 p-4 text-critical">
          <AlertTriangle className="size-4 shrink-0" />
          <p className="font-mono text-[11px]">{error ?? field.error}</p>
        </div>
      </Panel>
    )
  }

  if (loading || field.loading || !profile || !field.data) {
    return (
      <Panel className="flex h-full flex-col overflow-hidden">
        <PanelHeader title="AWCI Vertical Profile" subtitle={subtitle} />
        <div className="flex flex-1 items-center justify-center text-muted">
          <Loader2 className="size-5 animate-spin" />
        </div>
      </Panel>
    )
  }

  const thresholds = field.data.level_thresholds
  // Surface (index 0) at the top of the table, top-of-atmosphere last -
  // matches how a pilot/dispatcher reads a sounding table.
  const rows = profile.awci_profile
    .map((awci, i) => ({
      level: i,
      pressureHpa: Math.round(profile.pressure_profile_hpa[i]),
      temperatureC: profile.temperature_profile[i] - 273.15,
      windSpeedMs: profile.wind_speed_profile[i],
      awci,
      physical: profile.physical_profile[i],
      forecast: profile.forecast_profile[i],
    }))
    .reverse()

  return (
    <Panel className="flex h-full flex-col overflow-hidden">
      <PanelHeader
        title="AWCI Vertical Profile"
        subtitle={subtitle}
        right={<span className="font-mono text-[10px] text-muted">{profile.model} · {profile.n_levels} levels</span>}
      />
      <div className="min-h-0 flex-1 overflow-y-auto">
        <table className="w-full font-mono text-[11px]">
          <thead className="sticky top-0 bg-panel">
            <tr className="border-b border-border-subtle text-[10px] uppercase tracking-widest text-muted">
              <td className="px-3 py-1.5">Level</td>
              <td className="px-3 py-1.5 text-right">hPa</td>
              <td className="px-3 py-1.5 text-right">T (°C)</td>
              <td className="px-3 py-1.5 text-right">Wind (m/s)</td>
              <td className="px-3 py-1.5 text-right">Physical</td>
              <td className="px-3 py-1.5 text-right">Forecast</td>
              <td className="px-3 py-1.5 text-right">AWCI</td>
              <td className="px-3 py-1.5 text-right">Level</td>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => {
              const label = r.awci !== null ? classifyLevel(thresholds, r.awci) : "—"
              const tone = r.awci !== null ? toneForLevel(label) : "normal"
              return (
                <tr key={r.level} className="border-b border-border-subtle/60 last:border-0">
                  <td className="px-3 py-1.5 text-muted">
                    {r.level === profile.n_levels - 1 ? "TOA" : r.level === 0 ? "Surface" : r.level}
                  </td>
                  <td className="px-3 py-1.5 text-right tabular-nums text-foreground">{r.pressureHpa}</td>
                  <td className="px-3 py-1.5 text-right tabular-nums text-foreground">{r.temperatureC.toFixed(1)}</td>
                  <td className="px-3 py-1.5 text-right tabular-nums text-foreground">{r.windSpeedMs.toFixed(1)}</td>
                  <td className="px-3 py-1.5 text-right tabular-nums text-muted">
                    {r.physical !== null ? r.physical.toFixed(1) : "—"}
                  </td>
                  <td className="px-3 py-1.5 text-right tabular-nums text-muted">
                    {r.forecast !== null ? r.forecast.toFixed(1) : "—"}
                  </td>
                  <td className="px-3 py-1.5 text-right tabular-nums text-foreground">
                    {r.awci !== null ? r.awci.toFixed(1) : "—"}
                  </td>
                  <td className="px-3 py-1.5 text-right">
                    <span
                      className={cn("rounded px-1.5 py-0.5 text-[10px] font-semibold", toneText[tone], toneBg[tone])}
                    >
                      {label}
                    </span>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
      <div className="border-t border-border-subtle px-3 py-1.5 font-mono text-[10px] text-muted">
        {profile.model}'s real native levels at this grid column - AWCI classified against the shared field's real
        {" "}
        {field.data.model} thresholds.
      </div>
    </Panel>
  )
}
