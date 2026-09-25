"use client"

import { AlertTriangle, Loader2 } from "lucide-react"
import { CartesianGrid, Line, ComposedChart, ResponsiveContainer, Tooltip, XAxis, YAxis, Legend } from "recharts"
import { Panel, PanelHeader } from "@/components/ui/panel"
import { useRouteWeather } from "@/lib/hooks/use-route-weather"
import { useVerticalProfile } from "@/lib/hooks/use-vertical-profile"

/**
 * Real "Atmospheric Profile" - the solver's own real per-level
 * temperature and wind speed (`temperature_profile`/`wind_speed_profile`
 * from `GET /complexity/vertical-profile`, the same real 3D volume the
 * Vertical Profile (AWCI) panel already shares via
 * `VerticalProfileProvider`), plotted against the level's own real
 * local pressure. Not a standard-atmosphere sounding template - these
 * are the model's own native-level state variables at this real grid
 * column.
 */
export function AtmosphericProfile() {
  const route = useRouteWeather()
  const { data: profile, loading, error, samplePoint } = useVerticalProfile()

  const subtitle = samplePoint
    ? `${samplePoint.latitude.toFixed(1)}°N ${samplePoint.longitude.toFixed(1)}°E · Route Midpoint`
    : "T / Wind vs Native Level"

  if (error || route.error) {
    return (
      <Panel className="flex h-full flex-col overflow-hidden">
        <PanelHeader title="Atmospheric Profile" subtitle={subtitle} />
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
        <PanelHeader title="Atmospheric Profile" subtitle={subtitle} />
        <div className="flex flex-1 items-center justify-center text-muted">
          <Loader2 className="size-5 animate-spin" />
        </div>
      </Panel>
    )
  }

  const chartData = profile.temperature_profile.map((tempK, i) => ({
    pressureHpa: Math.round(profile.pressure_profile_hpa[i]),
    temperatureC: tempK - 273.15,
    windSpeedMs: profile.wind_speed_profile[i],
  }))

  const temps = chartData.map((d) => d.temperatureC)
  const tMin = Math.min(...temps)
  const tMax = Math.max(...temps)
  const tPad = Math.max(2, (tMax - tMin) * 0.15)
  const tDomain: [number, number] = [Math.floor(tMin - tPad), Math.ceil(tMax + tPad)]

  const winds = chartData.map((d) => d.windSpeedMs)
  const wMin = Math.min(...winds)
  const wMax = Math.max(...winds)
  const wPad = Math.max(1, (wMax - wMin) * 0.15)
  const wDomain: [number, number] = [Math.max(0, Math.floor(wMin - wPad)), Math.ceil(wMax + wPad)]

  return (
    <Panel className="flex h-full flex-col overflow-hidden">
      <PanelHeader
        title="Atmospheric Profile"
        subtitle={subtitle}
        right={<span className="font-mono text-[10px] text-muted">Surface → {profile.n_levels - 1}</span>}
      />
      <div className="min-h-0 flex-1 p-2">
        <ResponsiveContainer width="100%" height="100%" minHeight={200}>
          <ComposedChart data={chartData} margin={{ top: 8, right: 8, bottom: 0, left: -8 }}>
            <CartesianGrid stroke="var(--border-subtle)" strokeDasharray="2 4" vertical={false} />
            <XAxis
              dataKey="pressureHpa"
              reversed
              tick={{ fill: "var(--muted)", fontSize: 9, fontFamily: "var(--font-mono)" }}
              tickLine={false}
              axisLine={{ stroke: "var(--border-subtle)" }}
              label={{
                value: "hPa (native level, surface → TOA)",
                position: "insideBottom",
                offset: -2,
                fill: "var(--muted)",
                fontSize: 9,
              }}
            />
            <YAxis
              yAxisId="temp"
              domain={tDomain}
              tick={{ fill: "var(--critical)", fontSize: 9, fontFamily: "var(--font-mono)" }}
              tickLine={false}
              axisLine={false}
              width={30}
            />
            <YAxis
              yAxisId="wind"
              orientation="right"
              domain={wDomain}
              tick={{ fill: "var(--accent)", fontSize: 9, fontFamily: "var(--font-mono)" }}
              tickLine={false}
              axisLine={false}
              width={30}
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
              formatter={(value, name) => {
                if (typeof value !== "number") return ["—", name]
                if (name === "Temperature") return [`${value.toFixed(1)} °C`, name]
                return [`${value.toFixed(1)} m/s`, name]
              }}
              labelFormatter={(v) => `${v} hPa`}
            />
            <Legend
              wrapperStyle={{ fontFamily: "var(--font-mono)", fontSize: 9, color: "var(--muted)" }}
              iconType="plainline"
            />
            <Line
              yAxisId="temp"
              type="monotone"
              dataKey="temperatureC"
              name="Temperature"
              stroke="var(--critical)"
              strokeWidth={1.5}
              dot={false}
            />
            <Line
              yAxisId="wind"
              type="monotone"
              dataKey="windSpeedMs"
              name="Wind Speed"
              stroke="var(--accent)"
              strokeWidth={1.5}
              dot={false}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
      <div className="border-t border-border-subtle px-3 py-1.5 font-mono text-[10px] text-muted">
        {profile.model}'s real per-level temperature and wind speed at this grid column's native levels - not a
        standard-atmosphere template.
      </div>
    </Panel>
  )
}
