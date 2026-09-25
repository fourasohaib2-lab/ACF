"use client"

import { createContext, useCallback, useContext, useEffect, useState, type ReactNode } from "react"
import { ApiError, getRouteWeather, type RouteWeatherBriefing } from "@/lib/api"

/**
 * Shared real route-weather briefing state - one real
 * `GET /flights/route-weather` call (genuine great-circle route
 * geometry + live METAR fetch at departure/arrival/every real
 * recommended alternate, see `route_weather.py`) feeds every panel
 * that needs it (RouteProfile, RiskPanel). No fallback/mock data on
 * failure - `error` is surfaced honestly.
 */
interface RouteWeatherState {
  data: RouteWeatherBriefing | null
  loading: boolean
  error: string | null
  depIcao: string
  arrIcao: string
  /** Real, optional intermediate airport - `null` for a real direct
   * route (the default). Set via `setStopover()`. */
  stopoverIcao: string | null
  setRoute: (depIcao: string, arrIcao: string) => void
  /** Sets/clears the real stopover airport - pass `null` to go back to
   * a real direct route. */
  setStopover: (stopoverIcao: string | null) => void
  refresh: () => void
}

const RouteWeatherContext = createContext<RouteWeatherState | null>(null)

const DEFAULT_DEP = "EGLL"
const DEFAULT_ARR = "KJFK"
const N_WAYPOINTS = 20

export function RouteWeatherProvider({ children }: { children: ReactNode }) {
  const [depIcao, setDepIcao] = useState(DEFAULT_DEP)
  const [arrIcao, setArrIcao] = useState(DEFAULT_ARR)
  const [stopoverIcao, setStopoverIcao] = useState<string | null>(null)
  const [data, setData] = useState<RouteWeatherBriefing | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [nonce, setNonce] = useState(0)

  const refresh = useCallback(() => setNonce((n) => n + 1), [])
  const setRoute = useCallback((dep: string, arr: string) => {
    setDepIcao(dep.toUpperCase())
    setArrIcao(arr.toUpperCase())
  }, [])
  const setStopover = useCallback((stopover: string | null) => {
    setStopoverIcao(stopover ? stopover.toUpperCase() : null)
  }, [])

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError(null)
    getRouteWeather(depIcao, arrIcao, N_WAYPOINTS, stopoverIcao)
      .then((result) => {
        if (!cancelled) setData(result)
      })
      .catch((cause: unknown) => {
        if (cancelled) return
        const message = cause instanceof ApiError ? cause.message : "Unknown error fetching the route weather briefing"
        setError(message)
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [depIcao, arrIcao, stopoverIcao, nonce])

  return (
    <RouteWeatherContext.Provider
      value={{ data, loading, error, depIcao, arrIcao, stopoverIcao, setRoute, setStopover, refresh }}
    >
      {children}
    </RouteWeatherContext.Provider>
  )
}

export function useRouteWeather(): RouteWeatherState {
  const ctx = useContext(RouteWeatherContext)
  if (!ctx) {
    throw new Error("useRouteWeather must be used within a RouteWeatherProvider")
  }
  return ctx
}
