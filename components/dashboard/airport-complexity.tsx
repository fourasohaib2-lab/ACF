"use client"

import { AlertTriangle, Loader2 } from "lucide-react"
import { Panel, PanelHeader } from "@/components/ui/panel"
import { useComplexityField } from "@/lib/hooks/use-complexity-field"
import { useAirports } from "@/lib/hooks/use-airports"
import { classifyLevel, sampleFieldAt, toneForLevel } from "@/lib/complexity-stats"
import { cn } from "@/lib/utils"

const toneText = { normal: "text-accent", warning: "text-warning", severe: "text-severe", critical: "text-critical" } as const
const toneBg = { normal: "bg-accent/15", warning: "bg-warning/15", severe: "bg-severe/15", critical: "bg-critical/15" } as const

const MAX_ROWS = 20

/**
 * Real "Airport Complexity" table - the reference mockup's per-
 * airport AWCI list, built by sampling the already-fetched shared
 * field (nearest real grid cell, `sampleFieldAt` - the same
 * convention the backend's own `vertical_profile_at_point()` uses)
 * at every real airport in `AirportDatabase` (GET /airports, now
 * ~10,500 real world airports - see
 * `scripts/build_world_airports.py`). Shows only the top `MAX_ROWS`
 * by real AWCI score - rendering all ~10,500 rows would be both
 * unusable and beside this panel's own point (surfacing the highest-
 * complexity airports at a glance), disclosed explicitly rather than
 * silently truncated. No trend arrow: no real historical/previous-run
 * value exists client-side to compare against yet, and a fabricated
 * arrow would be worse than none.
 */
export function AirportComplexity() {
  const field = useComplexityField()
  const { airports, error: airportsError } = useAirports()

  if (field.error || airportsError) {
    return (
      <Panel className="flex h-full flex-col overflow-hidden">
        <PanelHeader title="Airport Complexity" />
        <div className="flex flex-1 items-center gap-2 p-4 text-critical">
          <AlertTriangle className="size-4 shrink-0" />
          <p className="font-mono text-[11px]">{field.error ?? airportsError}</p>
        </div>
      </Panel>
    )
  }

  if (field.loading || !field.data || !airports) {
    return (
      <Panel className="flex h-full flex-col overflow-hidden">
        <PanelHeader title="Airport Complexity" />
        <div className="flex flex-1 items-center justify-center text-muted">
          <Loader2 className="size-5 animate-spin" />
        </div>
      </Panel>
    )
  }

  const data = field.data
  const ranked = airports
    .map((a) => {
      const score = sampleFieldAt(data, a.latitude, a.longitude)
      return { ...a, score }
    })
    .sort((a, b) => (b.score ?? -Infinity) - (a.score ?? -Infinity))
  const rows = ranked.slice(0, MAX_ROWS)

  return (
    <Panel className="flex h-full flex-col overflow-hidden">
      <PanelHeader
        title="Airport Complexity"
        subtitle={`${data.model} · nearest grid cell · top ${MAX_ROWS} of ${airports.length}`}
      />
      <table className="w-full font-mono text-[11px]">
        <thead>
          <tr className="border-b border-border-subtle text-[10px] uppercase tracking-widest text-muted">
            <td className="px-3 py-1.5">Airport</td>
            <td className="px-3 py-1.5 text-right">AWCI</td>
            <td className="px-3 py-1.5 text-right">Status</td>
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => {
            const level = r.score !== null ? classifyLevel(data.level_thresholds, r.score) : "—"
            const tone = r.score !== null ? toneForLevel(level) : "normal"
            return (
              <tr key={r.icao_code} className="border-b border-border-subtle/60 last:border-0">
                <td className="px-3 py-1.5 text-foreground">
                  {r.icao_code} <span className="text-muted">· {r.city}</span>
                </td>
                <td className="px-3 py-1.5 text-right tabular-nums text-foreground">
                  {r.score !== null ? r.score.toFixed(1) : "—"}
                </td>
                <td className="px-3 py-1.5 text-right">
                  <span className={cn("rounded px-1.5 py-0.5 text-[10px] font-semibold", toneText[tone], toneBg[tone])}>
                    {level}
                  </span>
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </Panel>
  )
}
