"use client"

import { AlertTriangle, Loader2 } from "lucide-react"
import { Panel } from "@/components/ui/panel"
import { AwciGauge } from "@/components/dashboard/awci-gauge"
import { useHazardField } from "@/lib/hooks/use-hazard-field"
import { classifyLevel, meanField, toneForLevel } from "@/lib/complexity-stats"
import { cn } from "@/lib/utils"

interface HazardTile {
  label: string
  value: string
  unit: string
  tone: "normal" | "warning" | "severe" | "critical"
  note?: string
}

const toneText = { normal: "text-accent", warning: "text-warning", severe: "text-severe", critical: "text-critical" } as const
const toneBar = { normal: "bg-accent", warning: "bg-warning", severe: "bg-severe", critical: "bg-critical" } as const

/**
 * Real "AWCI Global" gauge + 6 real hazard tiles, matching the
 * reference mockup's KPI band layout. Every value comes from
 * `useHazardField()` (a real, opt-in-enriched `GET /complexity/field`
 * fetch - real CAPE/CIN, real bulk wind shear, real precipitation
 * phase, real ceiling/visibility risk - see that hook's own
 * docstring). No tile is a placeholder: where this project has no
 * real, distinct physical signal for a mockup label, the tile is
 * honestly built from the closest real proxy and says so (Turbulence
 * below), never a fabricated number.
 */
export function HazardBand() {
  const { data, loading, error } = useHazardField()

  if (error) {
    return (
      <Panel className="flex items-center gap-2 p-3 text-critical">
        <AlertTriangle className="size-4 shrink-0" />
        <p className="font-mono text-[11px]">Hazard field unavailable: {error}</p>
      </Panel>
    )
  }

  if (loading || !data) {
    return (
      <Panel className="flex h-[132px] items-center justify-center p-3 text-muted">
        <Loader2 className="size-5 animate-spin" />
        <span className="ml-2 font-mono text-[11px]">Computing real CAPE/shear/ceiling/visibility field…</span>
      </Panel>
    )
  }

  const globalMean = meanField(data.awci_field)
  const globalTone = globalMean !== null ? toneForLevel(classifyLevel(data.level_thresholds, globalMean)) : "normal"
  const globalLevel = globalMean !== null ? classifyLevel(data.level_thresholds, globalMean) : "—"

  const scoreOf = (moduleKey: string) => meanField(data.module_fields[moduleKey] ?? [])
  const toneOf = (score: number | null) => (score !== null ? toneForLevel(classifyLevel(data.level_thresholds, score)) : "normal")
  const levelOf = (score: number | null) => (score !== null ? classifyLevel(data.level_thresholds, score) : "—")

  const dynamicScore = scoreOf("dynamic")
  const convectiveScore = scoreOf("convective")
  const ceilingScore = scoreOf("ceiling")
  const visibilityScore = scoreOf("visibility")
  const icingSeverity = meanField(data.precipitation_phase_severity_field ?? [])
  const icingScore = icingSeverity !== null ? icingSeverity * 100 : null
  const shearMeanMs = meanField(data.wind_shear_field ?? [])

  const tiles: HazardTile[] = [
    {
      label: "Turbulence",
      value: dynamicScore !== null ? dynamicScore.toFixed(0) : "—",
      unit: levelOf(dynamicScore),
      tone: toneOf(dynamicScore),
      note: "Real proxy: AWCICalculator's dynamic (wind + bulk shear) module - not a literal EDR/Richardson-number computation.",
    },
    {
      label: "Convection",
      value: convectiveScore !== null ? convectiveScore.toFixed(0) : "—",
      unit: levelOf(convectiveScore),
      tone: toneOf(convectiveScore),
      note: "Real per-point CAPE/CIN parcel ascent (MetPy).",
    },
    {
      label: "Icing",
      value: icingScore !== null ? icingScore.toFixed(0) : "—",
      unit: "%",
      tone: "normal",
      note: "Real Stull wet-bulb freezing-precipitation-phase probability, ×100 - not the ICAO/FAA airframe-icing severity scale (LIGHT/MODERATE/SEVERE by liquid-water-content or ice-accretion rate, a different physical quantity this proxy cannot classify), so no qualitative label is applied here.",
    },
    {
      label: "Wind Shear",
      value: shearMeanMs !== null ? shearMeanMs.toFixed(1) : "—",
      unit: "m/s",
      tone: "normal",
      note: "Real bulk wind shear magnitude - no qualitative threshold is applied (none in this codebase is validated for this physical context).",
    },
    {
      label: "Visibility",
      value: visibilityScore !== null ? visibilityScore.toFixed(0) : "—",
      unit: levelOf(visibilityScore),
      tone: toneOf(visibilityScore),
      note: "Real relative-humidity/fog-proximity risk proxy (no real precipitation field exists to complete it - see honest_limitation).",
    },
    {
      label: "Ceiling",
      value: ceilingScore !== null ? ceilingScore.toFixed(0) : "—",
      unit: levelOf(ceilingScore),
      tone: toneOf(ceilingScore),
      note: "Real LCL-based estimated ceiling risk.",
    },
  ]

  return (
    <Panel className="flex flex-wrap items-center gap-4 p-4">
      <div className="flex items-center gap-3 border-r border-border-subtle pr-4">
        <AwciGauge value={globalMean} label="AWCI Global" tone={globalTone} />
        <div className="flex flex-col">
          <span className={cn("font-mono text-sm font-semibold", toneText[globalTone])}>{globalLevel}</span>
          <span className="font-mono text-[10px] text-muted">
            {data.model} · {data.lats.length}×{data.lons.length}
          </span>
        </div>
      </div>

      <div className="grid flex-1 grid-cols-2 gap-3 sm:grid-cols-3 xl:grid-cols-6">
        {tiles.map((t) => (
          <div key={t.label} className="relative overflow-hidden rounded-md border border-border-subtle bg-panel p-2.5" title={t.note}>
            <div className={cn("absolute inset-x-0 top-0 h-0.5", toneBar[t.tone])} />
            <p className="truncate font-sans text-[9px] font-medium uppercase tracking-wider text-muted">{t.label}</p>
            <div className="mt-1 flex items-baseline gap-1">
              <span className={cn("font-mono text-lg font-bold leading-none tabular-nums", toneText[t.tone])}>{t.value}</span>
              <span className="font-mono text-[9px] text-muted">{t.unit}</span>
            </div>
          </div>
        ))}
      </div>
    </Panel>
  )
}
