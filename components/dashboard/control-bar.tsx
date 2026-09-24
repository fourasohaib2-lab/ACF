"use client"

import { useEffect, useState } from "react"
import { ArrowRight, Plane, Satellite } from "lucide-react"
import { Panel } from "@/components/ui/panel"
import { useComplexityField } from "@/lib/hooks/use-complexity-field"
import { useRouteWeather } from "@/lib/hooks/use-route-weather"
import { listAirports, type AirportInfo } from "@/lib/api"
import type { ComplexityFieldParams } from "@/lib/api"

/** Real model IDs from `acf.forecast.engine.MODEL_CONFIGS` - a fixed,
 * small, real enum (not guessed) already reused as the type union in
 * lib/api.ts's `ComplexityFieldParams.model`. */
const MODELS: NonNullable<ComplexityFieldParams["model"]>[] = ["ARPEGE", "AROME", "ALADIN"]

function selectClassName() {
  return "rounded-md border border-border-subtle bg-panel px-2 py-1.5 font-mono text-[11px] text-foreground outline-none transition-colors hover:border-accent/50 focus:border-accent"
}

export function ControlBar() {
  const { model, setModel } = useComplexityField()
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
    </Panel>
  )
}
