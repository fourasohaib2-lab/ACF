"use client"

import { useState } from "react"
import dynamic from "next/dynamic"
import { Loader2 } from "lucide-react"
import { Panel, PanelHeader } from "@/components/ui/panel"
import { LayerSelector, MAP_LAYERS } from "@/components/dashboard/layer-selector"
import { useComplexityField } from "@/lib/hooks/use-complexity-field"

const ComplexityMap = dynamic(() => import("@/components/dashboard/complexity-map"), {
  ssr: false,
  loading: () => (
    <div className="flex h-full w-full items-center justify-center text-muted">
      <Loader2 className="size-6 animate-spin" />
    </div>
  ),
})

export function RegionalMap() {
  const { error, loading, fetchedAt } = useComplexityField()
  const [activeLayer, setActiveLayer] = useState("dynamic")
  const activeLabel = MAP_LAYERS.find((l) => l.id === activeLayer)?.label ?? activeLayer

  return (
    <Panel className="overflow-hidden">
      <PanelHeader
        title="Regional Sector · NAT"
        subtitle={`${activeLabel} Complexity`}
        right={
          <span className="font-mono text-[10px] text-muted">
            {fetchedAt ? `Fetched ${new Date(fetchedAt).toISOString().slice(11, 16)}Z` : "—"}
          </span>
        }
      />

      <div className="relative aspect-[16/9] w-full">
        {error ? (
          <div className="flex h-full items-center justify-center p-4 text-center font-mono text-[11px] text-critical">
            AWCI field unavailable: {error}
          </div>
        ) : loading ? (
          <div className="flex h-full items-center justify-center text-muted">
            <Loader2 className="size-6 animate-spin" />
          </div>
        ) : (
          <ComplexityMap moduleKey={activeLayer} center={[45, -30]} zoom={3} showRoute showCursor={false} />
        )}

        <LayerSelector activeLayer={activeLayer} onChange={setActiveLayer} />

        <div className="pointer-events-none absolute bottom-3 left-3 z-[1000] rounded border border-white/10 bg-black/50 px-2 py-1 font-mono text-[10px] uppercase tracking-wider text-muted backdrop-blur-md">
          Live Snapshot · North Atlantic
        </div>
      </div>

      <div className="border-t border-border-subtle px-3 py-2 font-mono text-[10px] text-muted">
        Single real physics snapshot - no forecast time-stepping is computed yet, so there is no real timeline to
        scrub.
      </div>
    </Panel>
  )
}
