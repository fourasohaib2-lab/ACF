"use client"

import { useComplexityField } from "@/lib/hooks/use-complexity-field"

/** Real data sources this dashboard actually fetches from - never the
 * placeholder "ECMWF-HRES / GFS / RAP" (NWP models this app does not
 * ingest at all). ACF Physics = the real CoupledEarthSolver +
 * AWCICalculator run behind /complexity/field; the rest are the real
 * live connectors behind /observations, /airports, /flights (NOAA
 * Aviation Weather Center for METAR/TAF/SIGMET/PIREP, EUMETSAT for
 * MTG satellite imagery). */
const REAL_SOURCES = "ACF Physics / NOAA AWC / EUMETSAT"

export function FooterBar() {
  const { data, error } = useComplexityField()
  const gridResolutionDeg = data && data.lats.length > 1 ? Math.abs(data.lats[1] - data.lats[0]) : null

  return (
    <footer className="flex flex-wrap items-center justify-between gap-2 border-t border-border-subtle bg-panel/40 px-4 py-2 font-mono text-[10px] uppercase tracking-wider text-muted">
      <div className="flex flex-wrap items-center gap-x-4 gap-y-1">
        <span>SRC · {REAL_SOURCES}</span>
        <span>GRID · {gridResolutionDeg !== null ? `${gridResolutionDeg.toFixed(1)}°` : "—"}</span>
        <span>PROJ · EPSG:4326</span>
      </div>
      <div className="flex items-center gap-2">
        <span className={`size-1.5 rounded-full ${error ? "bg-critical" : "bg-accent"}`} />
        <span className={error ? "text-critical" : "text-accent"}>{error ? "SYNC ERROR" : "SYNC OK"}</span>
        <span>· AWCI Dashboard · Real Data</span>
      </div>
    </footer>
  )
}
