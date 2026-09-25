"use client"

import { Activity, Globe2, Radio } from "lucide-react"
import { useEffect, useState } from "react"
import { useComplexityField } from "@/lib/hooks/use-complexity-field"
import { useRouteWeather } from "@/lib/hooks/use-route-weather"

function useUtcClock() {
  const [now, setNow] = useState<string>("--:--:--Z")
  useEffect(() => {
    const tick = () => {
      const d = new Date()
      const p = (n: number) => String(n).padStart(2, "0")
      setNow(`${p(d.getUTCHours())}:${p(d.getUTCMinutes())}:${p(d.getUTCSeconds())}Z`)
    }
    tick()
    const id = setInterval(tick, 1000)
    return () => clearInterval(id)
  }, [])
  return now
}

export function DashboardHeader() {
  const clock = useUtcClock()
  const field = useComplexityField()
  const route = useRouteWeather()

  const hasError = Boolean(field.error || route.error)
  const isLoading = field.loading || route.loading
  const feedValue = hasError ? "ERROR" : isLoading ? "SYNCING" : "LIVE"
  const feedTone: "ok" | "warning" | "critical" = hasError ? "critical" : isLoading ? "warning" : "ok"

  return (
    <header className="flex flex-col gap-3 border-b border-border-subtle bg-panel/40 px-4 py-3 md:flex-row md:items-center md:justify-between">
      <div className="flex items-center gap-3">
        <div className="flex size-9 items-center justify-center rounded-md border border-accent/40 bg-accent/10 text-accent">
          <Globe2 className="size-5" strokeWidth={1.6} />
        </div>
        <div>
          <h1 className="font-sans text-lg font-bold uppercase leading-none tracking-[0.22em] text-foreground">
            AWCI
          </h1>
          <p className="mt-1 font-sans text-[11px] uppercase tracking-[0.16em] text-muted">
            Aviation Weather Complexity Index
          </p>
        </div>
      </div>

      <div className="flex flex-wrap items-center gap-2 font-mono text-[11px]">
        <StatusPill
          icon={<Radio className="size-3" />}
          label="FEED"
          value={feedValue}
          tone={feedTone}
          title={hasError ? (field.error ?? route.error ?? undefined) : undefined}
        />
        <StatusPill icon={<Activity className="size-3" />} label="MODEL" value={field.model} />
        <div className="flex items-center gap-2 rounded-md border border-border-subtle bg-panel px-3 py-1.5">
          <span className="text-muted">UTC</span>
          <span className="tabular-nums text-accent">{clock}</span>
        </div>
      </div>
    </header>
  )
}

function StatusPill({
  icon,
  label,
  value,
  tone,
  title,
}: {
  icon: React.ReactNode
  label: string
  value: string
  tone?: "ok" | "warning" | "critical"
  title?: string
}) {
  const toneClass = tone === "ok" ? "text-accent" : tone === "warning" ? "text-warning" : tone === "critical" ? "text-critical" : "text-foreground"
  return (
    <div className="flex items-center gap-2 rounded-md border border-border-subtle bg-panel px-3 py-1.5" title={title}>
      <span className={tone ? toneClass : "text-muted"}>{icon}</span>
      <span className="text-muted">{label}</span>
      <span className={toneClass}>{value}</span>
    </div>
  )
}
