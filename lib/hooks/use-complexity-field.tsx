"use client"

import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from "react"
import { ApiError, getComplexityField, type ComplexityField, type ComplexityFieldParams } from "@/lib/api"

/**
 * Shared real AWCI field state - one real `GET /complexity/field` call
 * (a genuine `CoupledEarthSolver` run + a real `AWCICalculator`
 * evaluation at every grid point, see `spatial_field.py`) feeds every
 * panel that needs it (KpiBar, RadarComplexity, GlobalMap,
 * RegionalMap) instead of each panel triggering its own redundant
 * physics run. No fallback/mock data is ever substituted on failure -
 * `error` is surfaced honestly for the UI to render an explicit error
 * state.
 */
export interface GridResolution {
  n_lat: number
  n_lon: number
}

interface ComplexityFieldState {
  data: ComplexityField | null
  loading: boolean
  error: string | null
  /** Real client-side timestamp (ms since epoch) of when this fetch
   * resolved - not a server-side generation time (the field response
   * carries none), but a real, honest record of when this browser
   * last received it. */
  fetchedAt: number | null
  model: NonNullable<ComplexityFieldParams["model"]>
  /** Switches the real backend model (AROME/ALADIN/ARPEGE - see
   * `acf.forecast.engine.MODEL_CONFIGS`) and refetches a real field
   * at that model's own grid configuration. */
  setModel: (model: NonNullable<ComplexityFieldParams["model"]>) => void
  resolution: GridResolution
  /** Overrides the real grid size `compute_real_complexity_field()`
   * runs `CoupledEarthSolver` at (n_lat x n_lon real grid points) -
   * a real cost/detail tradeoff, not a cosmetic zoom: a finer grid is
   * a genuinely larger real physics run (see ControlBar's own timing
   * comment for measured real costs at each preset). */
  setResolution: (resolution: GridResolution) => void
  refresh: () => void
}

const ComplexityFieldContext = createContext<ComplexityFieldState | null>(null)

/** Coarse enough for a fast, responsive global overview field (a few
 * hundred grid points) while still real - not the model's full native
 * resolution (see ComplexityFieldParams docs in lib/api.ts to request
 * a finer field for a zoomed-in view). */
const DEFAULT_RESOLUTION: GridResolution = { n_lat: 24, n_lon: 48 }
const DEFAULT_PARAMS: ComplexityFieldParams = { model: "ARPEGE", ...DEFAULT_RESOLUTION }

export function ComplexityFieldProvider({
  params: initialParams = DEFAULT_PARAMS,
  children,
}: {
  params?: ComplexityFieldParams
  children: ReactNode
}) {
  const [model, setModel] = useState<NonNullable<ComplexityFieldParams["model"]>>(initialParams.model ?? "ARPEGE")
  const [resolution, setResolution] = useState<GridResolution>({
    n_lat: initialParams.n_lat ?? DEFAULT_RESOLUTION.n_lat,
    n_lon: initialParams.n_lon ?? DEFAULT_RESOLUTION.n_lon,
  })
  const [data, setData] = useState<ComplexityField | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [fetchedAt, setFetchedAt] = useState<number | null>(null)
  const [nonce, setNonce] = useState(0)

  const refresh = useCallback(() => setNonce((n) => n + 1), [])

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError(null)
    getComplexityField({ ...initialParams, model, n_lat: resolution.n_lat, n_lon: resolution.n_lon })
      .then((result) => {
        if (!cancelled) {
          setData(result)
          setFetchedAt(Date.now())
        }
      })
      .catch((cause: unknown) => {
        if (cancelled) return
        const message = cause instanceof ApiError ? cause.message : "Unknown error fetching the AWCI complexity field"
        setError(message)
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => {
      cancelled = true
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [nonce, model, resolution.n_lat, resolution.n_lon])

  return (
    <ComplexityFieldContext.Provider
      value={{ data, loading, error, fetchedAt, model, setModel, resolution, setResolution, refresh }}
    >
      {children}
    </ComplexityFieldContext.Provider>
  )
}

export function useComplexityField(): ComplexityFieldState {
  const ctx = useContext(ComplexityFieldContext)
  if (!ctx) {
    throw new Error("useComplexityField must be used within a ComplexityFieldProvider")
  }
  return ctx
}
