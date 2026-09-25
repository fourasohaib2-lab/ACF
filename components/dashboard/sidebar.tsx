"use client"

import { useState } from "react"
import {
  Globe2,
  LayoutGrid,
  Map,
  AlertTriangle,
  BarChart3,
  Database,
  ChevronRight,
} from "lucide-react"
import { cn } from "@/lib/utils"

/**
 * Real navigation, not decorative: each entry is a functional anchor
 * link to a real, already-real-data-backed section already on this
 * single-page dashboard (see the matching `id` attributes in
 * app/page.tsx) - genuine `scrollIntoView`, not a route to a page
 * that doesn't exist. No sub-items beyond what this dashboard
 * actually has a real panel for (e.g. no "Icing"/"Turbulence" links
 * under Hazards distinct from the real Hazard Band tiles already on
 * screen - those ARE the real per-hazard view, not a separate page).
 */
const SECTIONS: { id: string; label: string; icon: React.ComponentType<{ className?: string }> }[] = [
  { id: "overview", label: "Overview", icon: LayoutGrid },
  { id: "map", label: "Map & Visualization", icon: Map },
  { id: "hazards", label: "Hazards", icon: AlertTriangle },
  { id: "analysis", label: "Analysis", icon: BarChart3 },
  { id: "reports", label: "Data & Reports", icon: Database },
]

export function Sidebar() {
  const [active, setActive] = useState("overview")

  const handleClick = (id: string) => (e: React.MouseEvent) => {
    e.preventDefault()
    setActive(id)
    document.getElementById(id)?.scrollIntoView({ behavior: "smooth", block: "start" })
  }

  return (
    <aside className="hidden w-52 shrink-0 flex-col border-r border-border-subtle bg-panel/40 lg:flex">
      <div className="flex items-center gap-2 border-b border-border-subtle px-4 py-4">
        <div className="flex size-8 items-center justify-center rounded-md border border-accent/40 bg-accent/10 text-accent">
          <Globe2 className="size-4" strokeWidth={1.6} />
        </div>
        <span className="font-sans text-sm font-bold uppercase tracking-[0.18em] text-foreground">AWCI</span>
      </div>

      <nav className="flex-1 space-y-1 p-3">
        {SECTIONS.map((s) => {
          const Icon = s.icon
          const isActive = active === s.id
          return (
            <a
              key={s.id}
              href={`#${s.id}`}
              onClick={handleClick(s.id)}
              className={cn(
                "flex items-center gap-2.5 rounded-md px-3 py-2 font-mono text-[11px] uppercase tracking-wide transition-colors",
                isActive ? "bg-accent/10 text-accent" : "text-muted hover:bg-white/5 hover:text-foreground",
              )}
            >
              <Icon className="size-3.5 shrink-0" />
              <span className="flex-1 truncate">{s.label}</span>
              {isActive && <ChevronRight className="size-3 shrink-0" />}
            </a>
          )
        })}
      </nav>

      <div className="border-t border-border-subtle p-3 font-mono text-[9px] uppercase tracking-wider text-muted">
        AWCI Dashboard · Real Data
      </div>
    </aside>
  )
}
