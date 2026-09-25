"use client"

import { AlertTriangle, Loader2, Navigation, Radio } from "lucide-react"
import { Panel, PanelHeader } from "@/components/ui/panel"
import { useRouteWeather } from "@/lib/hooks/use-route-weather"
import type { AirportWeatherSnapshot } from "@/lib/api"
import { cn } from "@/lib/utils"

/** Real FAA/NOAA ceiling-only category cutoffs
 * (`awci.hazards.ceiling.classify_ceiling_category`) - LIFR/IFR are
 * the operationally critical bands, MVFR is a caution band, VFR is
 * normal. */
const CEILING_TONE: Record<string, "critical" | "warning" | "normal"> = {
  LIFR: "critical",
  IFR: "critical",
  MVFR: "warning",
  VFR: "normal",
}

const toneText = { critical: "text-critical", warning: "text-warning", normal: "text-accent" } as const
const toneBar = { critical: "bg-critical", warning: "bg-warning", normal: "bg-accent" } as const

function StationCard({ role, snapshot }: { role: string; snapshot: AirportWeatherSnapshot }) {
  const tone = snapshot.ceiling_category ? CEILING_TONE[snapshot.ceiling_category] ?? "normal" : "normal"

  if (!snapshot.is_real_data) {
    return (
      <div>
        <div className="mb-1 flex items-center justify-between font-mono text-[11px]">
          <span className="text-muted">
            {role} · {snapshot.icao_code}
          </span>
          <span className="font-semibold text-critical">NO DATA</span>
        </div>
        <p className="font-mono text-[10px] text-muted">{snapshot.status}</p>
      </div>
    )
  }

  return (
    <div>
      <div className="mb-1 flex items-center justify-between font-mono text-[11px]">
        <span className="text-muted">
          {role} · {snapshot.icao_code}
        </span>
        <span className={cn("font-semibold", toneText[tone])}>{snapshot.ceiling_category ?? "NO CEILING"}</span>
      </div>
      <div className="h-1.5 w-full overflow-hidden rounded-full bg-border-subtle">
        <div
          className={cn("h-full rounded-full", toneBar[tone])}
          style={{ width: tone === "critical" ? "90%" : tone === "warning" ? "55%" : "20%" }}
        />
      </div>
      <p className="mt-1 font-mono text-[10px] text-muted">
        {snapshot.visibility_m !== null ? `Vis ${Math.round(snapshot.visibility_m)} m` : "Vis n/a"}
        {snapshot.present_weather_descriptions.length > 0 ? ` · ${snapshot.present_weather_descriptions.join(", ")}` : ""}
      </p>
    </div>
  )
}

export function RiskPanel() {
  const { data, loading, error } = useRouteWeather()

  if (error) {
    return (
      <Panel className="flex h-full flex-col overflow-hidden">
        <PanelHeader title="Route Weather" subtitle="Departure / Arrival / Alternates" />
        <div className="flex flex-1 items-center gap-2 p-4 text-critical">
          <AlertTriangle className="size-4 shrink-0" />
          <p className="font-mono text-[11px]">{error}</p>
        </div>
      </Panel>
    )
  }

  if (loading || !data) {
    return (
      <Panel className="flex h-full flex-col overflow-hidden">
        <PanelHeader title="Route Weather" subtitle="Departure / Arrival / Alternates" />
        <div className="flex flex-1 items-center justify-center text-muted">
          <Loader2 className="size-5 animate-spin" />
        </div>
      </Panel>
    )
  }

  const alternates = Object.entries(data.alternate_weather)

  return (
    <Panel className="flex h-full flex-col overflow-hidden">
      <PanelHeader title="Route Weather" subtitle="Live METAR · Ceiling Category" />

      <div className="space-y-2.5 p-3">
        <StationCard role="Departure" snapshot={data.departure_weather} />
        <StationCard role="Arrival" snapshot={data.arrival_weather} />
        {alternates.map(([icao, snapshot]) => (
          <StationCard key={icao} role="Alternate" snapshot={snapshot} />
        ))}
      </div>

      <div className="mt-auto border-t border-border-subtle p-3">
        <div className="mb-2 flex items-center gap-2 font-sans text-[10px] font-semibold uppercase tracking-widest text-accent">
          <Navigation className="size-3.5" />
          Raw METAR
        </div>
        <ul className="space-y-2">
          {[data.departure_weather, data.arrival_weather, ...alternates.map(([, s]) => s)]
            .filter((s) => s.raw_metar)
            .map((s) => (
              <li key={s.icao_code} className="flex gap-2 font-mono text-[10px] leading-relaxed text-foreground">
                <Radio className="mt-0.5 size-3.5 shrink-0 text-muted" />
                <span>{s.raw_metar}</span>
              </li>
            ))}
        </ul>
      </div>
    </Panel>
  )
}
