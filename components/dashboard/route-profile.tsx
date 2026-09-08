"use client"

import {
  Area,
  ComposedChart,
  Line,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts"
import { Panel, PanelHeader } from "@/components/ui/panel"
import { ROUTE_PROFILE } from "@/lib/data"

export function RouteProfile() {
  return (
    <Panel className="flex h-full flex-col overflow-hidden">
      <PanelHeader
        title="Route Risk Profile"
        subtitle="EGLL → KJFK · Along-track"
        right={<span className="font-mono text-[10px] text-muted">3200 NM</span>}
      />
      <div className="min-h-0 flex-1 p-2">
        <ResponsiveContainer width="100%" height="100%" minHeight={200}>
          <ComposedChart data={ROUTE_PROFILE} margin={{ top: 8, right: 8, bottom: 0, left: -12 }}>
            <defs>
              <linearGradient id="riskFill" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="var(--critical)" stopOpacity={0.5} />
                <stop offset="100%" stopColor="var(--critical)" stopOpacity={0.03} />
              </linearGradient>
            </defs>
            <CartesianGrid stroke="var(--border-subtle)" strokeDasharray="2 4" vertical={false} />
            <XAxis
              dataKey="dist"
              tick={{ fill: "var(--muted)", fontSize: 9, fontFamily: "var(--font-mono)" }}
              tickLine={false}
              axisLine={{ stroke: "var(--border-subtle)" }}
              tickFormatter={(v) => `${v}`}
              interval={7}
            />
            <YAxis
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
            />
            <Area
              type="monotone"
              dataKey="risk"
              stroke="var(--critical)"
              strokeWidth={1.25}
              fill="url(#riskFill)"
              name="Risk"
            />
            <Line
              type="monotone"
              dataKey="alt"
              stroke="var(--accent)"
              strokeWidth={1.75}
              dot={false}
              name="Alt (FL/10)"
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </Panel>
  )
}
