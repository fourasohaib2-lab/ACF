"use client"

import {
  PolarAngleAxis,
  PolarGrid,
  Radar,
  RadarChart,
  ResponsiveContainer,
} from "recharts"
import { Panel, PanelHeader } from "@/components/ui/panel"
import { RADAR, RADAR_TABLE } from "@/lib/data"

export function RadarComplexity() {
  return (
    <Panel className="flex h-full flex-col overflow-hidden">
      <PanelHeader title="Complexity Factors" subtitle="Current vs Climatology" />
      <div className="grid min-h-0 flex-1 grid-rows-[1fr_auto]">
        <div className="min-h-0 p-1">
          <ResponsiveContainer width="100%" height="100%" minHeight={190}>
            <RadarChart data={RADAR} outerRadius="72%">
              <PolarGrid stroke="var(--border-subtle)" />
              <PolarAngleAxis
                dataKey="axis"
                tick={{ fill: "var(--muted)", fontSize: 9, fontFamily: "var(--font-mono)" }}
              />
              <Radar
                name="Climatology"
                dataKey="ref"
                stroke="var(--muted)"
                fill="var(--muted)"
                fillOpacity={0.08}
                strokeWidth={1}
              />
              <Radar
                name="Current"
                dataKey="value"
                stroke="var(--accent)"
                fill="var(--accent)"
                fillOpacity={0.28}
                strokeWidth={1.5}
              />
            </RadarChart>
          </ResponsiveContainer>
        </div>

        <div className="border-t border-border-subtle">
          <table className="w-full font-mono text-[11px]">
            <tbody>
              {RADAR_TABLE.map((r) => {
                const up = r.delta.startsWith("+")
                return (
                  <tr key={r.name} className="border-b border-border-subtle/60 last:border-0">
                    <td className="px-3 py-1 text-muted">{r.name}</td>
                    <td className="px-3 py-1 text-right tabular-nums text-foreground">{r.value}</td>
                    <td
                      className="px-3 py-1 text-right tabular-nums"
                      style={{ color: up ? "var(--critical)" : "var(--accent)" }}
                    >
                      {r.delta}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>
    </Panel>
  )
}
