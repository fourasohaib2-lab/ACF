"use client"

import { AlertTriangle, Loader2 } from "lucide-react"
import { Panel, PanelHeader } from "@/components/ui/panel"
import { useComplexityField } from "@/lib/hooks/use-complexity-field"
import { useHazardField } from "@/lib/hooks/use-hazard-field"
import { affectedAreaKm2, classifyLevel, meanConfidence, meanField, toneForLevel } from "@/lib/complexity-stats"
import { cn } from "@/lib/utils"

const toneText = { normal: "text-accent", warning: "text-warning", critical: "text-critical" } as const

/**
 * Real "Current Situation" panel - the reference mockup's ranked
 * hazard list + affected-area/confidence readout, built from the
 * same 2 real field fetches the rest of the dashboard already uses
 * (ComplexityFieldProvider's main field for area/confidence,
 * HazardFieldProvider's opt-in-enriched field for the ranked hazard
 * list) - no new fetch, no new physics.
 */
export function CurrentSituation() {
  const field = useComplexityField()
  const hazard = useHazardField()

  if (field.error || hazard.error) {
    return (
      <Panel className="flex h-full flex-col overflow-hidden">
        <PanelHeader title="Current Situation" subtitle="Main Hazards" />
        <div className="flex flex-1 items-center gap-2 p-4 text-critical">
          <AlertTriangle className="size-4 shrink-0" />
          <p className="font-mono text-[11px]">{field.error ?? hazard.error}</p>
        </div>
      </Panel>
    )
  }

  if (field.loading || hazard.loading || !field.data || !hazard.data) {
    return (
      <Panel className="flex h-full flex-col overflow-hidden">
        <PanelHeader title="Current Situation" subtitle="Main Hazards" />
        <div className="flex flex-1 items-center justify-center text-muted">
          <Loader2 className="size-5 animate-spin" />
        </div>
      </Panel>
    )
  }

  const hazardScores: { label: string; score: number | null }[] = [
    { label: "Turbulence", score: meanField(hazard.data.module_fields.dynamic ?? []) },
    { label: "Convection", score: meanField(hazard.data.module_fields.convective ?? []) },
    { label: "Icing", score: meanField(hazard.data.precipitation_phase_severity_field ?? [])},
    { label: "Visibility", score: meanField(hazard.data.module_fields.visibility ?? []) },
    { label: "Ceiling", score: meanField(hazard.data.module_fields.ceiling ?? []) },
  ]
  // Icing severity is [0,1] like the others are [0,100] once *100 -
  // normalize here so ranking compares like with like.
  const normalized = hazardScores.map((h) => ({
    ...h,
    score: h.label === "Icing" && h.score !== null ? h.score * 100 : h.score,
  }))
  const ranked = normalized
    .filter((h): h is { label: string; score: number } => h.score !== null)
    .sort((a, b) => b.score - a.score)
    .slice(0, 5)

  const affectedKm2 = affectedAreaKm2(field.data, "Moderate")
  const confidence = meanConfidence(field.data)

  return (
    <Panel className="flex h-full flex-col overflow-hidden">
      <PanelHeader title="Current Situation" subtitle="Main Hazards" />
      <div className="space-y-2 p-3">
        {ranked.map((h) => {
          const level = classifyLevel(hazard.data!.level_thresholds, h.score)
          const tone = toneForLevel(level)
          return (
            <div key={h.label} className="flex items-center justify-between font-mono text-[11px]">
              <span className="text-muted">{h.label}</span>
              <span className={cn("font-semibold", toneText[tone])}>{level}</span>
            </div>
          )
        })}
      </div>

      <div className="mt-auto grid grid-cols-2 gap-2 border-t border-border-subtle p-3 font-mono text-[11px]">
        <div>
          <p className="text-[10px] uppercase tracking-wider text-muted">Affected Area</p>
          <p className="mt-0.5 text-foreground">
            {affectedKm2 !== null ? `${(affectedKm2 / 1_000_000).toFixed(2)} M km²` : "—"}
          </p>
        </div>
        <div>
          <p className="text-[10px] uppercase tracking-wider text-muted">Confidence</p>
          <p className="mt-0.5 text-foreground">{confidence !== null ? `${confidence.toFixed(0)}%` : "—"}</p>
        </div>
        <div className="col-span-2">
          <p className="text-[10px] uppercase tracking-wider text-muted">Model Agreement</p>
          <p className="mt-0.5 text-muted" title="No real multi-model ensemble fusion is wired to this endpoint yet - a single-model snapshot has no real agreement metric to report.">
            Not yet computed (single-model snapshot)
          </p>
        </div>
      </div>
    </Panel>
  )
}
