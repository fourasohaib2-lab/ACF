"use client"

import { AlertTriangle, Loader2 } from "lucide-react"
import { PolarAngleAxis, PolarGrid, Radar, RadarChart, ResponsiveContainer } from "recharts"
import { Panel, PanelHeader } from "@/components/ui/panel"
import { useComplexityField } from "@/lib/hooks/use-complexity-field"
import { maxField, meanField } from "@/lib/complexity-stats"

/** The 5 real `AWCICalculator` physical modules that carry non-zero
 * default weight (`WeightsManager.DEFAULT_WEIGHTS`) - the other 9
 * real modules (ceiling/visibility/dust/ash/microburst/temporal/
 * confidence/ensemble_spread/model_disagreement) are opt-in at weight
 * 0.0 by default and would read as a flat, uninformative 0 here
 * unless the field was requested with their `compute_*` flag enabled
 * (see `spatial_field.py`). Showing only genuinely active modules
 * avoids implying a real-but-actually-off signal is "no risk". */
const PHYSICAL_MODULE_AXES: { key: string; label: string }[] = [
  { key: "dynamic", label: "Dynamic (Wind)" },
  { key: "thermodynamic", label: "Thermodynamic" },
  { key: "convective", label: "Convective" },
  { key: "microphysical", label: "Microphysical" },
  { key: "topographic", label: "Topographic" },
]

export function RadarComplexity() {
  const { data, loading, error } = useComplexityField()

  if (error) {
    return (
      <Panel className="flex h-full flex-col overflow-hidden">
        <PanelHeader title="Complexity Factors" subtitle="Live AWCI Physical Modules" />
        <div className="flex flex-1 items-center gap-2 p-4 text-critical">
          <AlertTriangle className="size-4 shrink-0" />
          <p className="font-mono text-[11px]">{error}</p>
        </div>
      </Panel>
    )
  }

  if (loading || !data) {
    return (
      <Panel className="flex h-full flex-col overflow-hidden">
        <PanelHeader title="Complexity Factors" subtitle="Live AWCI Physical Modules" />
        <div className="flex flex-1 items-center justify-center text-muted">
          <Loader2 className="size-5 animate-spin" />
        </div>
      </Panel>
    )
  }

  const rows = PHYSICAL_MODULE_AXES.map(({ key, label }) => {
    const field = data.module_fields[key]
    return {
      axis: label,
      mean: field ? meanField(field) : null,
      max: field ? maxField(field) : null,
    }
  })
  const radarData = rows.map((r) => ({ axis: r.axis, value: r.mean ?? 0 }))

  return (
    <Panel className="flex h-full flex-col overflow-hidden">
      <PanelHeader
        title="Complexity Factors"
        subtitle={`Live AWCI Physical Modules · ${data.model} · Mean over ${data.lats.length}×${data.lons.length} grid`}
      />
      <div className="grid min-h-0 flex-1 grid-rows-[1fr_auto]">
        <div className="min-h-0 p-1">
          <ResponsiveContainer width="100%" height="100%" minHeight={190}>
            <RadarChart data={radarData} outerRadius="72%">
              <PolarGrid stroke="var(--border-subtle)" />
              <PolarAngleAxis
                dataKey="axis"
                tick={{ fill: "var(--muted)", fontSize: 9, fontFamily: "var(--font-mono)" }}
              />
              <Radar
                name="Current (mean)"
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
            <thead>
              <tr className="border-b border-border-subtle/60 text-[10px] uppercase tracking-widest text-muted">
                <td className="px-3 py-1">Module</td>
                <td className="px-3 py-1 text-right">Mean</td>
                <td className="px-3 py-1 text-right">Max</td>
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr key={r.axis} className="border-b border-border-subtle/60 last:border-0">
                  <td className="px-3 py-1 text-muted">{r.axis}</td>
                  <td className="px-3 py-1 text-right tabular-nums text-foreground">
                    {r.mean !== null ? r.mean.toFixed(1) : "—"}
                  </td>
                  <td className="px-3 py-1 text-right tabular-nums text-foreground">
                    {r.max !== null ? r.max.toFixed(1) : "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </Panel>
  )
}
