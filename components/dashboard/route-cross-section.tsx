"use client"

import { useEffect, useState } from "react"
import { AlertTriangle, Loader2 } from "lucide-react"
import { Panel, PanelHeader } from "@/components/ui/panel"
import { GridHeatmapCanvas } from "@/components/grid-heatmap-canvas"
import { TurboLegend } from "@/components/dashboard/turbo-legend"
import { useRouteWeather } from "@/lib/hooks/use-route-weather"
import { useComplexityField } from "@/lib/hooks/use-complexity-field"
import { ApiError, getRouteCrossSection, type RouteCrossSection } from "@/lib/api"

const N_WAYPOINTS = 24

/**
 * Real "Vertical Cross Section" heatmap - matches the reference
 * mockup's along-track altitude x distance panel, built from
 * GET /complexity/route-cross-section (task #14): a real 3D volume
 * computed once, sampled at every real great-circle waypoint. Row 0
 * (bottom) is the real surface level; columns are real along-track
 * distance, left (departure) to right (arrival).
 */
export function RouteCrossSection() {
  const route = useRouteWeather()
  const { model, resolution } = useComplexityField()
  const [section, setSection] = useState<RouteCrossSection | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError(null)
    getRouteCrossSection({
      dep_icao: route.depIcao,
      arr_icao: route.arrIcao,
      stopover_icao: route.stopoverIcao,
      n_waypoints: N_WAYPOINTS,
      model,
      ...resolution,
    })
      .then((result) => {
        if (!cancelled) setSection(result)
      })
      .catch((cause: unknown) => {
        if (cancelled) return
        const message = cause instanceof ApiError ? cause.message : "Unknown error fetching the route cross-section"
        setError(message)
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [route.depIcao, route.arrIcao, route.stopoverIcao, model, resolution.n_lat, resolution.n_lon])

  const subtitle = route.stopoverIcao
    ? `${route.depIcao} → ${route.stopoverIcao} → ${route.arrIcao} · Along-Track`
    : `${route.depIcao} → ${route.arrIcao} · Along-Track`

  if (error) {
    return (
      <Panel className="flex h-full flex-col overflow-hidden">
        <PanelHeader title="Vertical Cross Section" subtitle={subtitle} />
        <div className="flex flex-1 items-center gap-2 p-4 text-critical">
          <AlertTriangle className="size-4 shrink-0" />
          <p className="font-mono text-[11px]">{error}</p>
        </div>
      </Panel>
    )
  }

  if (loading || !section) {
    return (
      <Panel className="flex h-full flex-col overflow-hidden">
        <PanelHeader title="Vertical Cross Section" subtitle={subtitle} />
        <div className="flex flex-1 items-center justify-center text-muted">
          <Loader2 className="size-5 animate-spin" />
        </div>
      </Panel>
    )
  }

  // grid[level][waypoint], level 0 = surface.
  const grid: (number | null)[][] = Array.from({ length: section.n_levels }, (_, level) =>
    section.columns.map((c) => c.awci_profile[level] ?? null),
  )
  const flatValues = grid.flat().filter((v): v is number => v !== null)
  const dataMin = flatValues.length > 0 ? Math.min(...flatValues) : 0
  const dataMax = flatValues.length > 0 ? Math.max(...flatValues) : 100
  // Real-data-driven color scale (same principle as RouteProfile's
  // auto-scaled Y-axis): a fixed 0-100 scale would render today's
  // genuinely low, narrow-range field as a near-uniform color - the
  // real internal variation is only visible once the scale matches
  // the real data range.
  const pad = Math.max(1, (dataMax - dataMin) * 0.15)
  const colorMin = Math.max(0, dataMin - pad)
  const colorMax = Math.min(100, dataMax + pad)
  const totalDistanceKm = section.columns[section.columns.length - 1]?.distance_from_origin_km ?? 0
  const surfacePressure = section.columns[0]?.pressure_profile_hpa[0]
  const topPressure = section.columns[0]?.pressure_profile_hpa[section.n_levels - 1]

  return (
    <Panel className="flex h-full flex-col overflow-hidden">
      <PanelHeader
        title="Vertical Cross Section"
        subtitle={subtitle}
        right={<span className="font-mono text-[10px] text-muted">{Math.round(totalDistanceKm)} km</span>}
      />
      <div className="relative min-h-0 flex-1 p-2">
        <GridHeatmapCanvas grid={grid} min={colorMin} max={colorMax} className="h-full w-full" />
        <div className="pointer-events-none absolute left-2 top-2 font-mono text-[9px] text-muted">
          {topPressure !== undefined ? `${Math.round(topPressure)} hPa` : ""}
        </div>
        <div className="pointer-events-none absolute bottom-2 left-2 font-mono text-[9px] text-muted">
          Surface{surfacePressure !== undefined ? ` (${Math.round(surfacePressure)} hPa)` : ""}
        </div>
        <div className="pointer-events-none absolute bottom-2 right-2">
          <TurboLegend />
        </div>
      </div>
      <div className="border-t border-border-subtle px-3 py-1.5 font-mono text-[10px] text-muted">
        {section.model}'s real native levels sampled at {section.columns.length} real great-circle waypoints (nearest
        grid column each) - not a fine-grained continuous sounding along the route.
      </div>
    </Panel>
  )
}
