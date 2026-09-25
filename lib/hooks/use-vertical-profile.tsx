"use client"

import { createContext, useContext, useEffect, useState, type ReactNode } from "react"
import { ApiError, getVerticalProfile, type VerticalProfile } from "@/lib/api"
import { useRouteWeather } from "@/lib/hooks/use-route-weather"
import { useComplexityField } from "@/lib/hooks/use-complexity-field"

interface VerticalProfileState {
  data: VerticalProfile | null
  loading: boolean
  error: string | null
  /** The real route waypoint the profile was sampled at (the route's
   * own great-circle midpoint), or `null` before the route has loaded. */
  samplePoint: { latitude: number; longitude: number } | null
}

const VerticalProfileContext = createContext<VerticalProfileState | null>(null)

/**
 * Shared real Complexity(z) column - one real `GET
 * /complexity/vertical-profile` call (a genuine 3D `CoupledEarthSolver`
 * volume, genuinely more expensive than the 2D field at the same
 * resolution - see `vertical_field.py`) feeds every panel that needs a
 * vertical profile (VerticalCrossSection, AtmosphericProfile) instead
 * of each panel triggering its own redundant physics run.
 */
export function VerticalProfileProvider({ children }: { children: ReactNode }) {
  const route = useRouteWeather()
  const { model, resolution } = useComplexityField()
  const [data, setData] = useState<VerticalProfile | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Real sample point: the route's own great-circle midpoint waypoint
  // (a real position along the actual departure->arrival route), not
  // an arbitrary fixed coordinate.
  const midpoint = route.data?.waypoints[Math.floor(route.data.waypoints.length / 2)] ?? null

  useEffect(() => {
    if (!midpoint) return
    let cancelled = false
    setLoading(true)
    setError(null)
    getVerticalProfile({ lat: midpoint.latitude, lon: midpoint.longitude, model, ...resolution })
      .then((result) => {
        if (!cancelled) setData(result)
      })
      .catch((cause: unknown) => {
        if (cancelled) return
        const message = cause instanceof ApiError ? cause.message : "Unknown error fetching the vertical profile"
        setError(message)
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => {
      cancelled = true
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [midpoint?.latitude, midpoint?.longitude, model, resolution.n_lat, resolution.n_lon])

  const samplePoint = midpoint ? { latitude: midpoint.latitude, longitude: midpoint.longitude } : null

  return (
    <VerticalProfileContext.Provider value={{ data, loading, error, samplePoint }}>
      {children}
    </VerticalProfileContext.Provider>
  )
}

export function useVerticalProfile(): VerticalProfileState {
  const ctx = useContext(VerticalProfileContext)
  if (!ctx) {
    throw new Error("useVerticalProfile must be used within a VerticalProfileProvider")
  }
  return ctx
}
