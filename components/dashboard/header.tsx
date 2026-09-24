"use client"

import { Activity, Globe2, Radio, RefreshCw } from "lucide-react"
import { useEffect, useState } from "react"

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
        <StatusPill icon={<Radio className="size-3" />} label="FEED" value="LIVE" tone="ok" />
        <StatusPill icon={<Activity className="size-3" />} label="MODEL" value="ECMWF-HRES" />
        <StatusPill icon={<RefreshCw className="size-3" />} label="CYCLE" value="12Z" />
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
}: {
  icon: React.ReactNode
  label: string
  value: string
  tone?: "ok"
}) {
  return (
    <div className="flex items-center gap-2 rounded-md border border-border-subtle bg-panel px-3 py-1.5">
      <span className={tone === "ok" ? "text-accent" : "text-muted"}>{icon}</span>
      <span className="text-muted">{label}</span>
      <span className={tone === "ok" ? "text-accent" : "text-foreground"}>{value}</span>
    </div>
  )
}
