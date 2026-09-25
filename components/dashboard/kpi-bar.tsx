"use client"

import { AlertTriangle, Loader2 } from "lucide-react"
import { Panel } from "@/components/ui/panel"
import { useComplexityField } from "@/lib/hooks/use-complexity-field"
import { affectedAreaKm2, classifyLevel, maxField, meanConfidence, meanField, toneForLevel } from "@/lib/complexity-stats"
import { cn } from "@/lib/utils"

interface Kpi {
  label: string
  value: string
  unit: string
  tone: "normal" | "warning" | "severe" | "critical"
}

const toneText: Record<Kpi["tone"], string> = {
  normal: "text-accent",
  warning: "text-warning",
  severe: "text-severe",
  critical: "text-critical",
}

const toneBar: Record<Kpi["tone"], string> = {
  normal: "bg-accent",
  warning: "bg-warning",
  severe: "bg-severe",
  critical: "bg-critical",
}

export function KpiBar() {
  const { data, loading, error } = useComplexityField()

  if (error) {
    return (
      <Panel className="flex items-center gap-2 p-3 text-critical">
        <AlertTriangle className="size-4 shrink-0" />
        <p className="font-mono text-[11px]">AWCI field unavailable: {error}</p>
      </Panel>
    )
  }

  if (loading || !data) {
    return (
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        {Array.from({ length: 4 }, (_, i) => (
          <Panel key={i} className="flex h-[84px] items-center justify-center p-3 text-muted">
            <Loader2 className="size-4 animate-spin" />
          </Panel>
        ))}
      </div>
    )
  }

  const mean = meanField(data.awci_field)
  const max = maxField(data.awci_field)
  const affectedKm2 = affectedAreaKm2(data, "Moderate")
  const confidence = meanConfidence(data)

  const kpis: Kpi[] = [
    {
      label: "Global Mean AWCI",
      value: mean !== null ? mean.toFixed(1) : "—",
      unit: "idx",
      tone: mean !== null ? toneForLevel(classifyLevel(data.level_thresholds, mean)) : "normal",
    },
    {
      label: "Max AWCI",
      value: max !== null ? max.toFixed(0) : "—",
      unit: "idx",
      tone: max !== null ? toneForLevel(classifyLevel(data.level_thresholds, max)) : "normal",
    },
    {
      label: "Affected Area (≥ Moderate)",
      value: affectedKm2 !== null ? (affectedKm2 / 1_000_000).toFixed(2) : "—",
      unit: "M km²",
      tone: "warning",
    },
    {
      label: "Forecast Confidence",
      value: confidence !== null ? confidence.toFixed(0) : "—",
      unit: "%",
      tone: "normal",
    },
  ]

  return (
    <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
      {kpis.map((k) => (
        <Panel key={k.label} className="relative overflow-hidden p-3">
          <div className={cn("absolute inset-x-0 top-0 h-0.5", toneBar[k.tone])} />
          <p className="font-sans text-[10px] font-medium uppercase tracking-[0.14em] text-muted">{k.label}</p>
          <div className="mt-2 flex items-baseline gap-1.5">
            <span className={cn("font-mono text-2xl font-bold leading-none tabular-nums", toneText[k.tone])}>
              {k.value}
            </span>
            <span className="font-mono text-[11px] text-muted">{k.unit}</span>
          </div>
          <div className="mt-2 font-mono text-[10px] text-muted">
            {data.model} · {data.lats.length}×{data.lons.length} grid
          </div>
        </Panel>
      ))}
    </div>
  )
}
