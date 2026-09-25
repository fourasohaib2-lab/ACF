"use client"

import { AlertTriangle, Loader2 } from "lucide-react"
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts"
import { Panel, PanelHeader } from "@/components/ui/panel"
import { useRouteWeather } from "@/lib/hooks/use-route-weather"
import { useVerticalProfile } from "@/lib/hooks/use-vertical-profile"

export function VerticalCrossSection() {
  const route = useRouteWeather()
  const { data: profile, loading, error, samplePoint } = useVerticalProfile()

  const subtitle = samplePoint
    ? `${samplePoint.latitude.toFixed(1)}°N ${samplePoint.longitude.toFixed(1)}°E · Route Midpoint`
    : "AWCI vs Native Level"

  if (error || route.error) {
    return (
      <Panel className="flex h-full flex-col overflow-hidden">
        <PanelHeader title="Vertical Profile" subtitle={subtitle} />
        <div className="flex flex-1 items-center gap-2 p-4 text-critical">
          <AlertTriangle className="size-4 shrink-0" />
          <p className="font-mono text-[11px]">{error ?? route.error}</p>
        </div>
      </Panel>
    )
  }

  if (loading || route.loading || !profile) {
    return (
      <Panel className="flex h-full flex-col overflow-hidden">
        <PanelHeader title="Vertical Profile" subtitle={subtitle} />
        <div className="flex flex-1 items-center justify-center text-muted">
          <Loader2 className="size-5 animate-spin" />
        </div>
      </Panel>
    )
  }

  const chartData = profile.awci_profile.map((value, i) => ({
    level: i,
    pressureHpa: Math.round(profile.pressure_profile_hpa[i]),
    awci: value,
  }))
  const awciValues = chartData.map((d) => d.awci).filter((v): v is number => v !== null)
  const dataMin = awciValues.length > 0 ? Math.min(...awciValues) : 0
  const dataMax = awciValues.length > 0 ? Math.max(...awciValues) : 100
  const pad = Math.max(2, (dataMax - dataMin) * 0.25)
  const yDomain: [number, number] = [Math.max(0, Math.floor(dataMin - pad)), Math.min(100, Math.ceil(dataMax + pad))]

  return (
    <Panel className="flex h-full flex-col overflow-hidden">
      <PanelHeader
        title="Vertical Profile"
        subtitle={subtitle}
        right={<span className="font-mono text-[10px] text-muted">Surface → {profile.n_levels - 1}</span>}
      />
      <div className="min-h-0 flex-1 p-2">
        <ResponsiveContainer width="100%" height="100%" minHeight={200}>
          <AreaChart data={chartData} margin={{ top: 8, right: 8, bottom: 0, left: -12 }}>
            <defs>
              <linearGradient id="vcsFill" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="var(--critical)" stopOpacity={0.6} />
                <stop offset="55%" stopColor="var(--warning)" stopOpacity={0.35} />
                <stop offset="100%" stopColor="var(--accent)" stopOpacity={0.1} />
              </linearGradient>
            </defs>
            <CartesianGrid stroke="var(--border-subtle)" strokeDasharray="2 4" vertical={false} />
            <XAxis
              dataKey="pressureHpa"
              reversed
              tick={{ fill: "var(--muted)", fontSize: 9, fontFamily: "var(--font-mono)" }}
              tickLine={false}
              axisLine={{ stroke: "var(--border-subtle)" }}
              label={{ value: "hPa (native level, surface → TOA)", position: "insideBottom", offset: -2, fill: "var(--muted)", fontSize: 9 }}
            />
            <YAxis
              domain={yDomain}
              tick={{ fill: "var(--muted)", fontSize: 9, fontFamily: "var(--font-mono)" }}
              tickLine={false}
              axisLine={false}
              width={34}
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
              itemStyle={{ color: "var(--accent)" }}
              formatter={(value) => [typeof value === "number" ? value.toFixed(1) : "—", "AWCI"]}
              labelFormatter={(v) => `${v} hPa`}
            />
            <Area type="monotone" dataKey="awci" stroke="var(--accent)" strokeWidth={1.5} fill="url(#vcsFill)" />
          </AreaChart>
        </ResponsiveContainer>
      </div>
      <div className="border-t border-border-subtle px-3 py-1.5 font-mono text-[10px] text-muted">
        {profile.model}'s real native model levels (each with its own real local pressure) - not standard pressure
        levels, and not spatially interpolated beyond the nearest grid column.
      </div>
    </Panel>
  )
}
