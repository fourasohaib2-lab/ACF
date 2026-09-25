"use client"

import { createContext, useContext, useEffect, useState, type ReactNode } from "react"
import { ApiError, getComplexityField, type ComplexityField } from "@/lib/api"
import { useComplexityField } from "@/lib/hooks/use-complexity-field"

/** Small, dedicated grid - the 5 real opt-in hazard flags together
 * cost ~20s at the dashboard's usual 24x48 map resolution (measured,
 * see GET /complexity/field's own docstring) but ~2s at this size,
 * so the hazard KPI band (which only needs a real global mean/max,
 * not a renderable raster) uses its own small fetch rather than
 * slowing down the shared map field. */
const HAZARD_RESOLUTION = { n_lat: 8, n_lon: 16 }

interface HazardFieldState {
  data: ComplexityField | null
  loading: boolean
  error: string | null
}

const HazardFieldContext = createContext<HazardFieldState | null>(null)

/** Real hazard-enriched field, refetched whenever the dashboard's
 * shared model selection changes (reuses ComplexityFieldProvider's
 * `model`, so this tile band always matches whatever model the rest
 * of the dashboard is showing). Shared via context so every consumer
 * (HazardBand, CurrentSituation) reads the same one real fetch
 * instead of each triggering its own redundant ~2s physics run. */
export function HazardFieldProvider({ children }: { children: ReactNode }) {
  const { model } = useComplexityField()
  const [data, setData] = useState<ComplexityField | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError(null)
    getComplexityField({
      model,
      ...HAZARD_RESOLUTION,
      compute_convective_energy: true,
      compute_wind_shear: true,
      compute_precipitation_phase: true,
      compute_ceiling: true,
      compute_visibility: true,
    })
      .then((result) => {
        if (!cancelled) setData(result)
      })
      .catch((cause: unknown) => {
        if (cancelled) return
        const message = cause instanceof ApiError ? cause.message : "Unknown error fetching the hazard field"
        setError(message)
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [model])

  return <HazardFieldContext.Provider value={{ data, loading, error }}>{children}</HazardFieldContext.Provider>
}

export function useHazardField(): HazardFieldState {
  const ctx = useContext(HazardFieldContext)
  if (!ctx) {
    throw new Error("useHazardField must be used within a HazardFieldProvider")
  }
  return ctx
}
