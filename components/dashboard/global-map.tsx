"use client"

import { useState } from "react"
import Image from "next/image"
import { Layers, MapPin, Crosshair, Plus, Minus } from "lucide-react"
import { HeatmapCanvas } from "@/components/heatmap-canvas"
import { Panel, PanelHeader } from "@/components/ui/panel"
import { HOVER_POINT, MAP_LAYERS } from "@/lib/data"
import { TurboLegend } from "@/components/dashboard/turbo-legend"
import { cn } from "@/lib/utils"

export function GlobalMap() {
  const [layers, setLayers] = useState(MAP_LAYERS)

  return (
    <Panel className="overflow-hidden">
      <PanelHeader
        title="Global Map · FL300"
        subtitle="AWCI Composite · Equirectangular"
        right={
          <span className="flex items-center gap-1.5 rounded border border-accent/30 bg-accent/10 px-2 py-0.5 font-mono text-[10px] uppercase tracking-wider text-accent">
            <span className="size-1.5 animate-pulse rounded-full bg-accent" />
            Nowcast
          </span>
        }
      />

      <div className="relative aspect-[16/7] w-full">
        <Image
          src="/maps/global-dark.png"
          alt="Dark world map showing global aviation weather complexity"
          fill
          priority
          className="object-cover opacity-90"
        />
        <HeatmapCanvas seed={3} cells={9} className="absolute inset-0 h-full w-full" />

        {/* scan sweep */}
        <div className="pointer-events-none absolute inset-0 overflow-hidden">
          <div className="animate-sweep absolute inset-y-0 w-1/3 bg-gradient-to-r from-transparent via-accent/5 to-transparent" />
        </div>

        {/* Layers overlay (glassmorphism) */}
        <div className="absolute left-3 top-3 w-44 rounded-md border border-white/10 bg-black/50 p-3 backdrop-blur-md">
          <div className="mb-2 flex items-center gap-2 font-sans text-[10px] font-semibold uppercase tracking-widest text-foreground">
            <Layers className="size-3.5 text-accent" />
            Layers
          </div>
          <ul className="space-y-1.5">
            {layers.map((l) => (
              <li key={l.id}>
                <button
                  type="button"
                  onClick={() =>
                    setLayers((prev) =>
                      prev.map((p) => (p.id === l.id ? { ...p, active: !p.active } : p)),
                    )
                  }
                  className="flex w-full items-center gap-2 font-mono text-[11px] text-muted transition-colors hover:text-foreground"
                >
                  <span
                    className={cn(
                      "flex size-3.5 items-center justify-center rounded-sm border",
                      l.active
                        ? "border-accent bg-accent/20 text-accent"
                        : "border-white/20 text-transparent",
                    )}
                  >
                    <span className="size-1.5 rounded-[1px] bg-accent" />
                  </span>
                  <span className={l.active ? "text-foreground" : ""}>{l.label}</span>
                </button>
              </li>
            ))}
          </ul>
        </div>

        {/* Hover point readout (glassmorphism) */}
        <div className="absolute right-3 top-3 w-52 rounded-md border border-white/10 bg-black/50 p-3 backdrop-blur-md">
          <div className="mb-2 flex items-center justify-between">
            <span className="flex items-center gap-1.5 font-sans text-[10px] font-semibold uppercase tracking-widest text-foreground">
              <Crosshair className="size-3.5 text-accent" />
              Cursor
            </span>
            <span className="font-mono text-[10px] text-muted">{HOVER_POINT.fl}</span>
          </div>
          <dl className="grid grid-cols-2 gap-x-3 gap-y-1 font-mono text-[11px]">
            <Row k="LAT" v={HOVER_POINT.lat} />
            <Row k="LON" v={HOVER_POINT.lon} />
            <Row k="CAPE" v={HOVER_POINT.cape} />
            <Row k="SHEAR" v={HOVER_POINT.shear} />
            <Row k="CLD TOP" v={HOVER_POINT.cloudTop} />
            <Row k="ECHO" v={HOVER_POINT.echoTop} />
          </dl>
          <div className="mt-2 flex items-center justify-between border-t border-white/10 pt-2">
            <span className="font-mono text-[10px] uppercase tracking-wider text-muted">AWCI</span>
            <span className="font-mono text-lg font-bold leading-none text-critical">
              {HOVER_POINT.awci}
            </span>
          </div>
        </div>

        {/* Legend (glassmorphism) */}
        <div className="absolute bottom-3 left-3 rounded-md border border-white/10 bg-black/50 p-2.5 backdrop-blur-md">
          <TurboLegend />
        </div>

        {/* Zoom controls */}
        <div className="absolute bottom-3 right-3 flex flex-col overflow-hidden rounded-md border border-white/10 bg-black/50 backdrop-blur-md">
          <button className="p-1.5 text-muted transition-colors hover:text-accent" aria-label="Zoom in">
            <Plus className="size-4" />
          </button>
          <div className="h-px bg-white/10" />
          <button className="p-1.5 text-muted transition-colors hover:text-accent" aria-label="Zoom out">
            <Minus className="size-4" />
          </button>
        </div>

        {/* focus reticle */}
        <div className="pointer-events-none absolute left-[58%] top-[38%] -translate-x-1/2 -translate-y-1/2">
          <MapPin className="size-5 text-critical drop-shadow-[0_0_6px_rgba(255,60,40,0.8)]" />
        </div>
      </div>
    </Panel>
  )
}

function Row({ k, v }: { k: string; v: string }) {
  return (
    <>
      <dt className="text-muted">{k}</dt>
      <dd className="text-right text-foreground">{v}</dd>
    </>
  )
}
