"use client"

import { useEffect, useState } from "react"
import L from "leaflet"
import "leaflet/dist/leaflet.css"
import { MapContainer, Marker, Polyline, TileLayer, Tooltip, ZoomControl, useMap, useMapEvents } from "react-leaflet"
import GeoRasterLayer from "georaster-layer-for-leaflet"
import { Crosshair } from "lucide-react"
import { useComplexityField } from "@/lib/hooks/use-complexity-field"
import { useRouteWeather } from "@/lib/hooks/use-route-weather"
import { buildFieldGeoraster } from "@/lib/build-georaster"
import { classifyLevel, sampleFieldAt, toneForLevel } from "@/lib/complexity-stats"
import { turbo } from "@/lib/utils"
import type { ComplexityField } from "@/lib/api"

/**
 * Real OpenStreetMap standard tiles - replaces the dashboard's
 * earlier static PNG placeholder map images with a genuine,
 * pannable/zoomable tile layer. NOTE (correction): CARTO's
 * "dark_all" free basemap now requires an API key (their hosted
 * anonymous tier was restricted after this was first wired up -
 * caught live, the tiles rendered an "API KEY REQUIRED" watermark
 * instead of failing silently) - OSM's standard tiles are the one
 * genuinely free, no-key basemap this dashboard can rely on without
 * asking the user for a CARTO/Stadia/Mapbox account. `TILE_FILTER`
 * below re-styles OSM's light tiles to the dashboard's dark theme via
 * a real, standard CSS trick (invert + hue-rotate), not a data
 * change - the map data itself is unmodified.
 */
const TILE_URL = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
const TILE_ATTRIBUTION = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
const TILE_FILTER = "invert(1) hue-rotate(180deg) brightness(0.9) contrast(0.9) saturate(0.6)"

const toneColor = { normal: "var(--accent)", warning: "var(--warning)", critical: "var(--critical)" } as const

function airportIcon(color: string) {
  return L.divIcon({
    className: "",
    html: `<div style="width:10px;height:10px;border-radius:9999px;background:${color};border:2px solid rgba(255,255,255,0.85);box-shadow:0 0 6px ${color}"></div>`,
    iconSize: [10, 10],
    iconAnchor: [5, 5],
  })
}

function RasterOverlay({ field, moduleKey, opacity }: { field: ComplexityField; moduleKey: string; opacity: number }) {
  const map = useMap()

  useEffect(() => {
    let layer: GeoRasterLayer | null = null
    let cancelled = false
    buildFieldGeoraster(field, moduleKey).then((georaster) => {
      if (cancelled || !georaster) return
      layer = new GeoRasterLayer({
        georaster,
        resolution: 128,
        resampleMethod: "bilinear",
        pixelValuesToColorFn: (values: number[]) => {
          const v = values[0]
          if (v === undefined || Number.isNaN(v)) return null
          const [r, g, b] = turbo(Math.max(0, Math.min(1, v / 100)))
          return `rgba(${r},${g},${b},${opacity})`
        },
      })
      layer.addTo(map)
    })
    return () => {
      cancelled = true
      if (layer) map.removeLayer(layer)
    }
  }, [map, field, moduleKey, opacity])

  return null
}

function RouteOverlay() {
  const { data } = useRouteWeather()
  if (!data) return null
  const positions = data.waypoints.map((wp) => [wp.latitude, wp.longitude] as [number, number])
  const dep = data.waypoints[0]
  const arr = data.waypoints[data.waypoints.length - 1]

  return (
    <>
      <Polyline positions={positions} pathOptions={{ color: "var(--accent)", weight: 2, dashArray: "4 4" }} />
      {dep && (
        <Marker position={[dep.latitude, dep.longitude]} icon={airportIcon("var(--accent)")}>
          <Tooltip direction="top" offset={[0, -6]}>
            {data.departure_icao} · Departure
          </Tooltip>
        </Marker>
      )}
      {arr && (
        <Marker position={[arr.latitude, arr.longitude]} icon={airportIcon("var(--critical)")}>
          <Tooltip direction="top" offset={[0, -6]}>
            {data.arrival_icao} · Arrival
          </Tooltip>
        </Marker>
      )}
    </>
  )
}

function FitToRoute({ signal }: { signal: number }) {
  const map = useMap()
  const { data } = useRouteWeather()

  useEffect(() => {
    if (!signal || !data || data.waypoints.length === 0) return
    const bounds = L.latLngBounds(data.waypoints.map((wp) => [wp.latitude, wp.longitude] as [number, number]))
    map.fitBounds(bounds, { padding: [40, 40] })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [signal])

  return null
}

function CursorTracker({
  field,
  onMove,
}: {
  field: ComplexityField
  onMove: (readout: { lat: number; lon: number; awci: number | null } | null) => void
}) {
  useMapEvents({
    mousemove: (e) => {
      onMove({ lat: e.latlng.lat, lon: e.latlng.lng, awci: sampleFieldAt(field, e.latlng.lat, e.latlng.lng) })
    },
    mouseout: () => onMove(null),
  })
  return null
}

export default function ComplexityMap({
  moduleKey = "awci",
  center = [20, 0],
  zoom = 2,
  showRoute = true,
  showCursor = true,
  fitToRouteSignal = 0,
}: {
  moduleKey?: string
  center?: [number, number]
  zoom?: number
  showRoute?: boolean
  showCursor?: boolean
  /** Incrementing this number re-fits the map to the current real
   * route's bounds (see FitToRoute) - a real Leaflet fitBounds() call
   * on the route's own waypoint coordinates, not a canned zoom. */
  fitToRouteSignal?: number
}) {
  const { data: field } = useComplexityField()
  const [cursor, setCursor] = useState<{ lat: number; lon: number; awci: number | null } | null>(null)

  if (!field) return null

  const tone = cursor?.awci !== null && cursor?.awci !== undefined
    ? toneForLevel(classifyLevel(field.level_thresholds, cursor.awci))
    : "normal"

  return (
    <div className="relative h-full w-full">
      <style jsx global>{`
        .map-tiles-dark {
          filter: ${TILE_FILTER};
        }
      `}</style>
      <MapContainer
        center={center}
        zoom={zoom}
        minZoom={2}
        worldCopyJump
        zoomControl={false}
        className="h-full w-full"
        style={{ background: "#0a0e14" }}
      >
        <TileLayer url={TILE_URL} attribution={TILE_ATTRIBUTION} className="map-tiles-dark" />
        <ZoomControl position="bottomright" />
        <RasterOverlay field={field} moduleKey={moduleKey} opacity={0.75} />
        {showRoute && <RouteOverlay />}
        {showCursor && <CursorTracker field={field} onMove={setCursor} />}
        <FitToRoute signal={fitToRouteSignal} />
      </MapContainer>

      {showCursor && cursor && (
        <div className="pointer-events-none absolute right-3 top-3 z-[1000] w-48 rounded-md border border-white/10 bg-black/60 p-3 backdrop-blur-md">
          <div className="mb-2 flex items-center gap-1.5 font-sans text-[10px] font-semibold uppercase tracking-widest text-foreground">
            <Crosshair className="size-3.5 text-accent" />
            Cursor
          </div>
          <dl className="grid grid-cols-2 gap-x-3 gap-y-1 font-mono text-[11px]">
            <dt className="text-muted">LAT</dt>
            <dd className="text-right text-foreground">{cursor.lat.toFixed(2)}°</dd>
            <dt className="text-muted">LON</dt>
            <dd className="text-right text-foreground">{cursor.lon.toFixed(2)}°</dd>
          </dl>
          <div className="mt-2 flex items-center justify-between border-t border-white/10 pt-2">
            <span className="font-mono text-[10px] uppercase tracking-wider text-muted">AWCI</span>
            <span className="font-mono text-lg font-bold leading-none" style={{ color: toneColor[tone] }}>
              {cursor.awci !== null ? cursor.awci.toFixed(1) : "—"}
            </span>
          </div>
        </div>
      )}
    </div>
  )
}
