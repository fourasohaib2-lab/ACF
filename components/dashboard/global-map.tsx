"use client"

import { useState } from "react"
import dynamic from "next/dynamic"
import { Layers, Loader2 } from "lucide-react"
import { Panel, PanelHeader } from "@/components/ui/panel"
import { TurboLegend } from "@/components/dashboard/turbo-legend"
import { useComplexityField } from "@/lib/hooks/use-complexity-field"
import { cn } from "@/lib/utils"

const ComplexityMap = dynamic(() => import("@/components/dashboard/complexity-map"), {
  ssr: false,
  loading: () => (
    <div className="flex h-full w-full items-center justify-center text-muted">
      <Loader2 className="size-6 animate-spin" />
    </div>
  ),
})

/** Real AWCICalculator module fields available at the field's default
 * weights (see radar-complexity.tsx's own comment on which modules
 * carry non-zero default weight). "Wind Vectors"/"ATS Routes" from
 * the original mockup layer list are not real toggleable data layers
 * here: no raw wind-vector field is exposed by the API (only scalar
 * wind speed feeds the dynamic module) - ATS Routes is instead always
 * shown when a route is loaded (see ComplexityMap's showRoute). */
const LAYERS: { id: string; label: string }[] = [
  { id: "awci", label: "AWCI Composite" },
  { id: "convective", label: "Convective" },
  { id: "thermodynamic", label: "Thermodynamic" },
  { id: "dynamic", label: "Dynamic (Wind)" },
]

export function GlobalMap() {
  const { data, error } = useComplexityField()
  const [activeLayer, setActiveLayer] = useState("awci")

  return (
    <Panel className="overflow-hidden">
      <PanelHeader
        title="Global Map"
        subtitle="AWCI Composite · Equirectangular"
        right={
          <span className="flex items-center gap-1.5 rounded border border-accent/30 bg-accent/10 px-2 py-0.5 font-mono text-[10px] uppercase tracking-wider text-accent">
            <span className="size-1.5 animate-pulse rounded-full bg-accent" />
            Live
          </span>
        }
      />

      <div className="relative aspect-[16/7] w-full">
        {error ? (
          <div className="flex h-full items-center justify-center p-4 text-center font-mono text-[11px] text-critical">
            AWCI field unavailable: {error}
          </div>
        ) : (
          <ComplexityMap moduleKey={activeLayer} center={[35, -20]} zoom={2} />
        )}

        {/* Layers panel (glassmorphism) */}
        <div className="pointer-events-auto absolute left-3 top-3 z-[1000] w-44 rounded-md border border-white/10 bg-black/50 p-3 backdrop-blur-md">
          <div className="mb-2 flex items-center gap-2 font-sans text-[10px] font-semibold uppercase tracking-widest text-foreground">
            <Layers className="size-3.5 text-accent" />
            Layer
          </div>
          <ul className="space-y-1.5">
            {LAYERS.map((l) => (
              <li key={l.id}>
                <button
                  type="button"
                  onClick={() => setActiveLayer(l.id)}
                  className="flex w-full items-center gap-2 font-mono text-[11px] text-muted transition-colors hover:text-foreground"
                >
                  <span
                    className={cn(
                      "flex size-3.5 items-center justify-center rounded-sm border",
                      activeLayer === l.id ? "border-accent bg-accent/20 text-accent" : "border-white/20 text-transparent",
                    )}
                  >
                    <span className="size-1.5 rounded-[1px] bg-accent" />
                  </span>
                  <span className={activeLayer === l.id ? "text-foreground" : ""}>{l.label}</span>
                </button>
              </li>
            ))}
          </ul>
        </div>

        {/* Legend (glassmorphism) */}
        <div className="pointer-events-none absolute bottom-3 left-3 z-[1000] rounded-md border border-white/10 bg-black/50 p-2.5 backdrop-blur-md">
          <TurboLegend />
        </div>

        {data && (
          <div className="pointer-events-none absolute bottom-3 right-3 z-[1000] rounded border border-white/10 bg-black/50 px-2 py-1 font-mono text-[10px] text-muted backdrop-blur-md">
            {data.model} · {data.lats.length}×{data.lons.length} grid
          </div>
        )}
      </div>
    </Panel>
  )
}
