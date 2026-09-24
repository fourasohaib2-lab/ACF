"use client"

import { useState } from "react"
import dynamic from "next/dynamic"
import { Loader2, Locate } from "lucide-react"
import { Panel, PanelHeader } from "@/components/ui/panel"
import { TurboLegend } from "@/components/dashboard/turbo-legend"
import { LayerSelector } from "@/components/dashboard/layer-selector"
import { useComplexityField } from "@/lib/hooks/use-complexity-field"

const ComplexityMap = dynamic(() => import("@/components/dashboard/complexity-map"), {
  ssr: false,
  loading: () => (
    <div className="flex h-full w-full items-center justify-center text-muted">
      <Loader2 className="size-6 animate-spin" />
    </div>
  ),
})

export function GlobalMap() {
  const { data, error } = useComplexityField()
  const [activeLayer, setActiveLayer] = useState("awci")
  const [fitToRouteNonce, setFitToRouteNonce] = useState(0)

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
          <ComplexityMap moduleKey={activeLayer} center={[35, -20]} zoom={2} fitToRouteSignal={fitToRouteNonce} />
        )}

        <LayerSelector activeLayer={activeLayer} onChange={setActiveLayer} />

        {/* Legend (glassmorphism) */}
        <div className="pointer-events-none absolute bottom-3 left-3 z-[1000] rounded-md border border-white/10 bg-black/50 p-2.5 backdrop-blur-md">
          <TurboLegend />
        </div>

        <button
          type="button"
          onClick={() => setFitToRouteNonce((n) => n + 1)}
          className="pointer-events-auto absolute bottom-14 right-3 z-[1000] flex items-center gap-1.5 rounded-md border border-white/10 bg-black/50 px-2.5 py-1.5 font-mono text-[10px] uppercase tracking-wider text-muted backdrop-blur-md transition-colors hover:text-accent"
          title="Fit map to the current route"
        >
          <Locate className="size-3.5" />
          Fit Route
        </button>

        {data && (
          <div className="pointer-events-none absolute bottom-3 right-3 z-[1000] rounded border border-white/10 bg-black/50 px-2 py-1 font-mono text-[10px] text-muted backdrop-blur-md">
            {data.model} · {data.lats.length}×{data.lons.length} grid
          </div>
        )}
      </div>
    </Panel>
  )
}
