"use client"

import { useEffect, useRef } from "react"
import { turbo } from "@/lib/utils"

/**
 * Real raster of an arbitrary `rows x cols` numeric grid using the
 * turbo colormap - a generic sibling of
 * `components/complexity-heatmap-canvas.tsx`-style rendering (that
 * one is geo-referenced via Leaflet/GeoRaster; this one just fills
 * its container, for a non-map 2D grid like a route cross-section).
 * `grid[0]` is drawn at the BOTTOM (row 0 = the real surface level,
 * matching this codebase's own vertical-field convention), and
 * `null`/non-finite cells are fully transparent - never a fabricated
 * color for a value the backend didn't compute.
 */
export function GridHeatmapCanvas({
  grid,
  min = 0,
  max = 100,
  className,
}: {
  grid: (number | null)[][]
  min?: number
  max?: number
  className?: string
}) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext("2d")
    if (!ctx) return

    const parent = canvas.parentElement
    const w = parent?.clientWidth ?? 600
    const h = parent?.clientHeight ?? 240
    const dpr = Math.min(window.devicePixelRatio || 1, 2)
    canvas.width = w * dpr
    canvas.height = h * dpr
    canvas.style.width = `${w}px`
    canvas.style.height = `${h}px`

    const rows = grid.length
    const cols = rows > 0 ? grid[0].length : 0
    if (rows === 0 || cols === 0) return

    const off = document.createElement("canvas")
    off.width = cols
    off.height = rows
    const offCtx = off.getContext("2d")
    if (!offCtx) return
    const imageData = offCtx.createImageData(cols, rows)

    for (let i = 0; i < rows; i++) {
      const destRow = rows - 1 - i // row 0 (surface) at the bottom
      for (let j = 0; j < cols; j++) {
        const value = grid[i][j]
        const idx = (destRow * cols + j) * 4
        if (value === null || value === undefined || !Number.isFinite(value)) {
          imageData.data[idx + 3] = 0
          continue
        }
        const t = Math.max(0, Math.min(1, (value - min) / (max - min)))
        const [r, g, b] = turbo(t)
        imageData.data[idx] = r
        imageData.data[idx + 1] = g
        imageData.data[idx + 2] = b
        imageData.data[idx + 3] = 255
      }
    }
    offCtx.putImageData(imageData, 0, 0)

    ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
    ctx.clearRect(0, 0, w, h)
    ctx.imageSmoothingEnabled = true
    ctx.imageSmoothingQuality = "high"
    ctx.drawImage(off, 0, 0, cols, rows, 0, 0, w, h)
  }, [grid, min, max])

  return <canvas ref={canvasRef} className={className} />
}
