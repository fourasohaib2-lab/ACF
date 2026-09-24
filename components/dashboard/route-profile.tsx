"use client"

import { AlertTriangle, Loader2 } from "lucide-react"
import { Area, CartesianGrid, ComposedChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts"
import { Panel, PanelHeader } from "@/components/ui/panel"
import { useRouteWeather } from "@/lib/hooks/use-route-weather"
import { useComplexityField } from "@/lib/hooks/use-complexity-field"
import { classifyLevel, sampleFieldAt, toneForLevel } from "@/lib/complexity-stats"

const toneColor = { normal: "var(--accent)", warning: "var(--warning)", critical: "var(--critical)" } as const

const KM_TO_NM = 0.539957

export function RouteProfile() {
  const route = useRouteWeather()
  const field = useComplexityField()

  const loading = route.loading || field.loading
  const error = route.error ?? field.error

  if (error) {
    return (
      <Panel className="flex h-full flex-col overflow-hidden">
        <PanelHeader title="Route AWCI Profile" subtitle={`${route.depIcao} → ${route.arrIcao} · Along-track`} />
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
        <PanelHeader title="Route AWCI Profile" subtitle={`${route.depIcao} → ${route.arrIcao} · Along-track`} />
        <div className="flex flex-1 items-center justify-center text-muted">
          <Loader2 className="size-5 animate-spin" />
        </div>
      </Panel>
    )
  }

  const briefing = route.data
  const chartData = briefing.waypoints.map((wp) => ({
    dist: Math.round(wp.distance_from_origin_km * KM_TO_NM),
    awci: sampleFieldAt(field.data!, wp.latitude, wp.longitude),
  }))

  const awciValues = chartData.map((d) => d.awci).filter((v): v is number => v !== null)
  const dataMin = awciValues.length > 0 ? Math.min(...awciValues) : 0
  const dataMax = awciValues.length > 0 ? Math.max(...awciValues) : 100
  const pad = Math.max(2, (dataMax - dataMin) * 0.25)
  const yDomain: [number, number] = [Math.max(0, Math.floor(dataMin - pad)), Math.min(100, Math.ceil(dataMax + pad))]
  const tone = awciValues.length > 0 ? toneForLevel(classifyLevel(field.data!.level_thresholds, dataMax)) : "normal"
  const lineColor = toneColor[tone]

  return (
    <Panel className="flex h-full flex-col overflow-hidden">
      <PanelHeader
        title="Route AWCI Profile"
        subtitle={`${briefing.departure_icao} → ${briefing.arrival_icao} · Along-track`}
        right={
          <span className="font-mono text-[10px] text-muted">{Math.round(briefing.great_circle_distance_nm)} NM</span>
        }
      />
      <div className="min-h-0 flex-1 p-2">
        <ResponsiveContainer width="100%" height="100%" minHeight={200}>
          <ComposedChart data={chartData} margin={{ top: 8, right: 8, bottom: 0, left: -12 }}>
            <defs>
              <linearGradient id="awciFill" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={lineColor} stopOpacity={0.5} />
                <stop offset="100%" stopColor={lineColor} stopOpacity={0.03} />
              </linearGradient>
            </defs>
            <CartesianGrid stroke="var(--border-subtle)" strokeDasharray="2 4" vertical={false} />
            <XAxis
              dataKey="dist"
              tick={{ fill: "var(--muted)", fontSize: 9, fontFamily: "var(--font-mono)" }}
              tickLine={false}
              axisLine={{ stroke: "var(--border-subtle)" }}
              tickFormatter={(v) => `${v}`}
            />
            <YAxis
              domain={yDomain}
              tick={{ fill: "var(--muted)", fontSize: 9, fontFamily: "var(--font-mono)" }}
              tickLine={false}
              axisLine={false}
              width={28}
            />
            <Tooltip
              contentStyle={{
                background: "rgba(6,9,15,0.92)",
                border: "1px solid var(--border-subtle)",
                borderRadius: 6,
                fontFamily: "var(--font-mono)",
                fontSize: 11,
              }}
              labelStyle={{ color: "var(--muted)" }}
              formatter={(value) => [typeof value === "number" ? value.toFixed(1) : "—", "AWCI"]}
              labelFormatter={(v) => `${v} NM`}
            />
            <Area type="monotone" dataKey="awci" stroke={lineColor} strokeWidth={1.25} fill="url(#awciFill)" name="AWCI" />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
      <div className="border-t border-border-subtle px-3 py-1.5 font-mono text-[10px] text-muted">
        AWCI sampled at each real great-circle waypoint from the nearest cell of the {field.data.lats.length}×
        {field.data.lons.length} field ({field.data.model}) - a coarse proxy at this resolution, not a fine-grained
        sounding along the route.
      </div>
    </Panel>
  )
}
