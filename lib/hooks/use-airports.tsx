"use client"

import { useEffect, useState } from "react"
import { listAirports, type AirportInfo } from "@/lib/api"

/** Real `AirportDatabase` registry (GET /airports) - a small, mostly-
 * static list, fetched once per mount. Each consumer (ControlBar,
 * AirportComplexity) calls this independently rather than sharing a
 * context: the real cost is one small GET request, not worth the
 * extra provider wiring for a list this size. */
export function useAirports(): { airports: AirportInfo[] | null; error: string | null } {
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

  return { airports, error }
}
