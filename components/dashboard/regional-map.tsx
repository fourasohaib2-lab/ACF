"use client"

import { useEffect, useState } from "react"
import Image from "next/image"
import { Pause, Play, SkipForward } from "lucide-react"
import { HeatmapCanvas } from "@/components/heatmap-canvas"
import { Panel, PanelHeader } from "@/components/ui/panel"
import { TIMELINE } from "@/lib/data"

export function RegionalMap() {
  const [idx, setIdx] = useState(4)
  const [playing, setPlaying] = useState(false)
  const phase = idx / (TIMELINE.length - 1)

  useEffect(() => {
    if (!playing) return
    const id = setInterval(() => {
      setIdx((i) => (i + 1) % TIMELINE.length)
    }, 1200)
    return () => clearInterval(id)
  }, [playing])

  return (
    <Panel className="overflow-hidden">
      <PanelHeader
        title="Regional Sector · NAT"
        subtitle="Convective Complexity · Loop"
        right={
          <span className="font-mono text-[11px] text-accent">{TIMELINE[idx]}</span>
        }
      />

      <div className="relative aspect-[16/9] w-full">
        <Image
          src="/maps/regional-dark.png"
          alt="Dark regional North Atlantic aeronautical chart with weather complexity overlay"
          fill
          className="object-cover opacity-90"
        />
        <HeatmapCanvas seed={idx + 10} phase={phase} cells={6} className="absolute inset-0 h-full w-full" />

        <div className="absolute left-3 top-3 rounded border border-white/10 bg-black/50 px-2 py-1 font-mono text-[10px] uppercase tracking-wider text-muted backdrop-blur-md">
          Valid {TIMELINE[idx]} · FL340
        </div>
      </div>

      {/* Timeline scrubber */}
      <div className="flex items-center gap-3 border-t border-border-subtle px-3 py-2.5">
        <div className="flex items-center gap-1">
          <button
            type="button"
            onClick={() => setPlaying((p) => !p)}
            className="flex size-7 items-center justify-center rounded border border-border-subtle text-accent transition-colors hover:bg-accent/10"
            aria-label={playing ? "Pause" : "Play"}
          >
            {playing ? <Pause className="size-3.5" /> : <Play className="size-3.5" />}
          </button>
          <button
            type="button"
            onClick={() => setIdx((i) => (i + 1) % TIMELINE.length)}
            className="flex size-7 items-center justify-center rounded border border-border-subtle text-muted transition-colors hover:text-foreground"
            aria-label="Step forward"
          >
            <SkipForward className="size-3.5" />
          </button>
        </div>

        <input
          type="range"
          min={0}
          max={TIMELINE.length - 1}
          value={idx}
          onChange={(e) => setIdx(Number(e.target.value))}
          className="h-1 w-full cursor-pointer appearance-none rounded-full bg-border-subtle accent-accent"
          aria-label="Forecast time"
        />

        <span className="shrink-0 font-mono text-[11px] tabular-nums text-muted">
          +{idx * 3}h
        </span>
      </div>
    </Panel>
  )
}
