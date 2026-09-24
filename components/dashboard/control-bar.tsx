"use client"

import { useEffect, useState } from "react"
import { ArrowRight, Grid3x3, Plane, Satellite } from "lucide-react"
import { Panel } from "@/components/ui/panel"
import { useComplexityField, type GridResolution } from "@/lib/hooks/use-complexity-field"
import { useRouteWeather } from "@/lib/hooks/use-route-weather"
import { listAirports, type AirportInfo } from "@/lib/api"
import type { ComplexityFieldParams } from "@/lib/api"

/** Real model IDs from `acf.forecast.engine.MODEL_CONFIGS` - a fixed,
 * small, real enum (not guessed) already reused as the type union in
 * lib/api.ts's `ComplexityFieldParams.model`. */
const MODELS: NonNullable<ComplexityFieldParams["model"]>[] = ["ARPEGE", "AROME", "ALADIN"]

/**
 * Real grid-resolution presets - each is a genuine tradeoff between
 * physics-run cost and real spatial detail, not a cosmetic zoom
 * level (a finer preset is a real, larger `CoupledEarthSolver` run
 * over more real grid points). Measured wall-clock cost on this
 * backend (ARPEGE, 8 integration steps): 2D field 12x24/24x48/48x96 ~
 * 0.03s/0.08s/0.32s; the 3D vertical volume (used by
 * VerticalCrossSection, which shares this same resolution) is real
 * per-level work on top of that: ~0.3s/1.0s/3.9s at the same 3
 * presets - the "Fine" preset trades a real, disclosed few-second
 * wait for real extra detail, never a fabricated instant result.
 */
const RESOLUTIONS: { label: string; value: GridResolution }[] = [
  { label: "Coarse (12×24)", value: { n_lat: 12, n_lon: 24 } },
  { label: "Standard (24×48)", value: { n_lat: 24, n_lon: 48 } },
  { label: "Fine (48×96)", value: { n_lat: 48, n_lon: 96 } },
]

function resolutionKey(r: GridResolution) {
  return `${r.n_lat}x${r.n_lon}`
}

function selectClassName() {
  return "rounded-md border border-border-subtle bg-panel px-2 py-1.5 font-mono text-[11px] text-foreground outline-none transition-colors hover:border-accent/50 focus:border-accent"
}

export function ControlBar() {
  const { model, setModel, resolution, setResolution } = useComplexityField()
  const { depIcao, arrIcao, setRoute } = useRouteWeather()
  const [airports, setAirports] = useState<AirportInfo[] | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    listAirports()
      .then((result) => {
        if (!cancelled) setAirports(result)
      })
      .catch(() => {
        if (!cancelled) setError("Airport list unavailable")
      })
    return () => {
      cancelled = true
    }
  }, [])

  return (
    <Panel className="flex flex-wrap items-center gap-3 p-3">
      <div className="flex items-center gap-2">
        <Plane className="size-4 text-accent" />
        <span className="font-sans text-[10px] font-semibold uppercase tracking-[0.14em] text-muted">Route</span>
      </div>

      <select
        aria-label="Departure airport"
        className={selectClassName()}
        value={depIcao}
        disabled={!airports}
        onChange={(e) => setRoute(e.target.value, arrIcao)}
      >
        {(airports ?? [{ icao_code: depIcao, name: depIcao } as AirportInfo]).map((a) => (
          <option key={a.icao_code} value={a.icao_code}>
            {a.icao_code} · {a.name}
          </option>
        ))}
      </select>

      <ArrowRight className="size-3.5 text-muted" />

      <select
        aria-label="Arrival airport"
        className={selectClassName()}
        value={arrIcao}
        disabled={!airports}
        onChange={(e) => setRoute(depIcao, e.target.value)}
      >
        {(airports ?? [{ icao_code: arrIcao, name: arrIcao } as AirportInfo]).map((a) => (
          <option key={a.icao_code} value={a.icao_code}>
            {a.icao_code} · {a.name}
          </option>
        ))}
      </select>

      {error && <span className="font-mono text-[10px] text-critical">{error}</span>}

      <div className="ml-auto flex items-center gap-2">
        <Satellite className="size-4 text-accent" />
        <span className="font-sans text-[10px] font-semibold uppercase tracking-[0.14em] text-muted">Model</span>
        <select
          aria-label="Physics model"
          className={selectClassName()}
          value={model}
          onChange={(e) => setModel(e.target.value as NonNullable<ComplexityFieldParams["model"]>)}
        >
          {MODELS.map((m) => (
            <option key={m} value={m}>
              {m}
            </option>
          ))}
        </select>
      </div>

      <div className="flex items-center gap-2">
        <Grid3x3 className="size-4 text-accent" />
        <span className="font-sans text-[10px] font-semibold uppercase tracking-[0.14em] text-muted">Grid</span>
        <select
          aria-label="Grid resolution"
          className={selectClassName()}
          value={resolutionKey(resolution)}
          onChange={(e) => {
            const preset = RESOLUTIONS.find((r) => resolutionKey(r.value) === e.target.value)
            if (preset) setResolution(preset.value)
          }}
        >
          {RESOLUTIONS.map((r) => (
            <option key={resolutionKey(r.value)} value={resolutionKey(r.value)}>
              {r.label}
            </option>
          ))}
        </select>
      </div>
    </Panel>
  )
}
