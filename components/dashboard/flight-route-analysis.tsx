"use client"

import { AlertTriangle, Loader2 } from "lucide-react"
import { Panel, PanelHeader } from "@/components/ui/panel"
import { useRouteWeather } from "@/lib/hooks/use-route-weather"
import { useComplexityField } from "@/lib/hooks/use-complexity-field"
import { classifyLevel, sampleFieldAt, toneForLevel } from "@/lib/complexity-stats"
import { cn } from "@/lib/utils"

const toneText = { normal: "text-accent", warning: "text-warning", severe: "text-severe", critical: "text-critical" } as const
const toneBg = { normal: "bg-accent/15", warning: "bg-warning/15", severe: "bg-severe/15", critical: "bg-critical/15" } as const

const KM_TO_NM = 0.539957

/**
 * Real "Flight Route Analysis" segment table - each row is one real
 * great-circle waypoint from `GET /flights/route-weather`
 * (`awci.flight.waypoint.generate_route_waypoints()`), with its real
 * cumulative along-track distance, its real position, and the shared
 * AWCI field (`ComplexityFieldProvider`) sampled at that position
 * (same nearest-grid-cell convention `RouteProfile`'s chart uses, so
 * both panels always agree on the same real number per waypoint).
 * Segment length (Δ) is the real distance between consecutive real
 * waypoints, not a fabricated fixed interval.
 */
export function FlightRouteAnalysis() {
  const route = useRouteWeather()
  const field = useComplexityField()

  const loading = route.loading || field.loading
  const error = route.error ?? field.error

  if (error) {
    return (
      <Panel className="flex h-full flex-col overflow-hidden">
        <PanelHeader title="Flight Route Analysis" subtitle={`${route.depIcao} → ${route.arrIcao}`} />
        <div className="flex flex-1 items-center gap-2 p-4 text-critical">
          <AlertTriangle className="size-4 shrink-0" />
          <p className="font-mono text-[11px]">{error}</p>
        </div>
      </Panel>
    )
  }

  if (loading || !route.data || !field.data) {
    return (
      <Panel className="flex h-full flex-col overflow-hidden">
        <PanelHeader title="Flight Route Analysis" subtitle={`${route.depIcao} → ${route.arrIcao}`} />
        <div className="flex flex-1 items-center justify-center text-muted">
          <Loader2 className="size-5 animate-spin" />
        </div>
      </Panel>
    )
  }

  const briefing = route.data
  const fieldData = field.data
  const rows = briefing.waypoints.map((wp, i) => {
    const prev = briefing.waypoints[i - 1]
    const deltaKm = prev ? wp.distance_from_origin_km - prev.distance_from_origin_km : 0
    const score = sampleFieldAt(fieldData, wp.latitude, wp.longitude)
    const level = score !== null ? classifyLevel(fieldData.level_thresholds, score) : "—"
    const tone = score !== null ? toneForLevel(level) : "normal"
    return { index: i, wp, deltaKm, score, level, tone }
  })

  return (
    <Panel className="flex h-full flex-col overflow-hidden">
      <PanelHeader
        title="Flight Route Analysis"
        subtitle={`${briefing.departure_icao} → ${briefing.arrival_icao} · ${rows.length} waypoints`}
        right={
          <span className="font-mono text-[10px] text-muted">{Math.round(briefing.great_circle_distance_nm)} NM</span>
        }
      />
      <div className="min-h-0 flex-1 overflow-y-auto">
        <table className="w-full font-mono text-[11px]">
          <thead className="sticky top-0 bg-panel">
            <tr className="border-b border-border-subtle text-[10px] uppercase tracking-widest text-muted">
              <td className="px-3 py-1.5">#</td>
              <td className="px-3 py-1.5">Position</td>
              <td className="px-3 py-1.5 text-right">Δ (NM)</td>
              <td className="px-3 py-1.5 text-right">Dist (NM)</td>
              <td className="px-3 py-1.5 text-right">AWCI</td>
              <td className="px-3 py-1.5 text-right">Level</td>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.index} className="border-b border-border-subtle/60 last:border-0">
                <td className="px-3 py-1.5 text-muted">{r.index}</td>
                <td className="px-3 py-1.5 text-foreground">
                  {r.wp.latitude.toFixed(1)}°, {r.wp.longitude.toFixed(1)}°
                </td>
                <td className="px-3 py-1.5 text-right tabular-nums text-muted">
                  {r.index === 0 ? "—" : Math.round(r.deltaKm * KM_TO_NM)}
                </td>
                <td className="px-3 py-1.5 text-right tabular-nums text-foreground">
                  {Math.round(r.wp.distance_from_origin_km * KM_TO_NM)}
                </td>
                <td className="px-3 py-1.5 text-right tabular-nums text-foreground">
                  {r.score !== null ? r.score.toFixed(1) : "—"}
                </td>
                <td className="px-3 py-1.5 text-right">
                  <span
                    className={cn("rounded px-1.5 py-0.5 text-[10px] font-semibold", toneText[r.tone], toneBg[r.tone])}
                  >
                    {r.level}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="border-t border-border-subtle px-3 py-1.5 font-mono text-[10px] text-muted">
        AWCI sampled at each real great-circle waypoint from the nearest cell of the {fieldData.lats.length}×
        {fieldData.lons.length} field ({fieldData.model}) - a coarse proxy at this resolution, not a fine-grained
        sounding along the route.
      </div>
    </Panel>
  )
}
