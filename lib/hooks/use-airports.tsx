"use client"

import { useEffect, useState } from "react"
import { listAirports, type AirportInfo } from "@/lib/api"

/** Real `AirportDatabase` registry (GET /airports) - now ~10,500 real
 * world airports (6 hand-curated + the real OurAirports-sourced bulk
 * import, see `scripts/build_world_airports.py`), fetched once per
 * mount (~3.6 MB, one real request) and filtered/searched client-side
 * by consumers (`AirportCombobox`). Each consumer (ControlBar,
 * AirportComplexity) calls this independently rather than sharing a
 * context: the real cost is one GET request per mount, not worth the
 * extra provider wiring. */
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
