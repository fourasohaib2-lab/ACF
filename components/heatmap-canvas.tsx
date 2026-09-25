"use client"

import { useEffect, useRef } from "react"
import { turbo } from "@/lib/utils"

type Cell = { x: number; y: number; r: number; intensity: number }

/**
 * Procedural convective-weather heatmap drawn with a turbo colormap.
 * `seed` shifts the field so the global and regional maps look different,
 * and `phase` (0..1, from the timeline slider) animates the field.
 */
export function HeatmapCanvas({
  seed = 1,
  phase = 0,
  className,
  cells = 7,
}: {
  seed?: number
  phase?: number
  className?: string
  cells?: number
}) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext("2d")
    if (!ctx) return

    const parent = canvas.parentElement
    const w = parent?.clientWidth ?? 800
    const h = parent?.clientHeight ?? 400
    const dpr = Math.min(window.devicePixelRatio || 1, 2)
    canvas.width = w * dpr
    canvas.height = h * dpr
    canvas.style.width = `${w}px`
    canvas.style.height = `${h}px`
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
    ctx.clearRect(0, 0, w, h)

    // deterministic pseudo-random storm centers
    const rand = (n: number) => {
      const s = Math.sin((n + seed) * 127.1 + seed * 311.7) * 43758.5453
      return s - Math.floor(s)
    }

    const blobs: Cell[] = Array.from({ length: cells }, (_, i) => {
      const drift = Math.sin(phase * Math.PI * 2 + i) * 0.04
      return {
        x: (0.1 + rand(i) * 0.8 + drift) * w,
        y: (0.12 + rand(i + 40) * 0.72) * h,
        r: (0.08 + rand(i + 80) * 0.16) * Math.min(w, h) * 1.6,
        intensity: 0.45 + rand(i + 120) * 0.55,
      }
    })

    // Render the field on a downsampled grid then let CSS smooth it.
    const step = 6
    for (let py = 0; py < h; py += step) {
      for (let px = 0; px < w; px += step) {
        let v = 0
        for (const b of blobs) {
          const dx = px - b.x
          const dy = py - b.y
          const d2 = dx * dx + dy * dy
          v += (b.intensity * (b.r * b.r)) / (d2 + b.r * b.r)
        }
        const t = Math.max(0, Math.min(1, (v - 0.15) * 1.15))
        if (t < 0.06) continue
        const [r, g, bl] = turbo(t)
        ctx.fillStyle = `rgba(${r}, ${g}, ${bl}, ${0.16 + t * 0.5})`
        ctx.fillRect(px, py, step, step)
      }
    }
  }, [seed, phase, cells])

  return (
    <canvas
      ref={canvasRef}
      aria-hidden="true"
      className={className}
      style={{ filter: "blur(6px)", mixBlendMode: "screen" }}
    />
  )
}
