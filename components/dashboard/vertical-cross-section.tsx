"use client"

import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts"
import { Panel, PanelHeader } from "@/components/ui/panel"
import { CROSS_SECTION } from "@/lib/data"

export function VerticalCrossSection() {
  return (
    <Panel className="flex h-full flex-col overflow-hidden">
      <PanelHeader
        title="Vertical Profile"
        subtitle="AWCI vs Flight Level"
        right={<span className="font-mono text-[10px] text-muted">FL100–FL560</span>}
      />
      <div className="min-h-0 flex-1 p-2">
        <ResponsiveContainer width="100%" height="100%" minHeight={200}>
          <AreaChart data={CROSS_SECTION} margin={{ top: 8, right: 8, bottom: 0, left: -12 }}>
            <defs>
              <linearGradient id="awciFill" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="var(--critical)" stopOpacity={0.6} />
                <stop offset="55%" stopColor="var(--warning)" stopOpacity={0.35} />
                <stop offset="100%" stopColor="var(--accent)" stopOpacity={0.1} />
              </linearGradient>
            </defs>
            <CartesianGrid stroke="var(--border-subtle)" strokeDasharray="2 4" vertical={false} />
            <XAxis
              dataKey="fl"
              tick={{ fill: "var(--muted)", fontSize: 9, fontFamily: "var(--font-mono)" }}
              tickLine={false}
              axisLine={{ stroke: "var(--border-subtle)" }}
              interval={3}
            />
            <YAxis
              domain={[0, 100]}
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
            />
            <Area
              type="monotone"
              dataKey="complexity"
              stroke="var(--accent)"
              strokeWidth={1.5}
              fill="url(#awciFill)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </Panel>
  )
}
