import { AlertTriangle, Navigation } from "lucide-react"
import { Panel, PanelHeader } from "@/components/ui/panel"
import { RECOMMENDATIONS, RISK_SUMMARY } from "@/lib/data"
import { cn } from "@/lib/utils"

export function RiskPanel() {
  return (
    <Panel className="flex h-full flex-col overflow-hidden">
      <PanelHeader title="Hazard Assessment" subtitle="Active Sector" />

      <div className="space-y-2.5 p-3">
        {RISK_SUMMARY.map((r) => (
          <div key={r.label}>
            <div className="mb-1 flex items-center justify-between font-mono text-[11px]">
              <span className="text-muted">{r.label}</span>
              <span
                className={cn(
                  "font-semibold",
                  r.tone === "critical" ? "text-critical" : "text-warning",
                )}
              >
                {r.level}
              </span>
            </div>
            <div className="h-1.5 w-full overflow-hidden rounded-full bg-border-subtle">
              <div
                className={cn(
                  "h-full rounded-full",
                  r.tone === "critical" ? "bg-critical" : "bg-warning",
                )}
                style={{ width: `${r.value}%` }}
              />
            </div>
          </div>
        ))}
      </div>

      <div className="mt-auto border-t border-border-subtle p-3">
        <div className="mb-2 flex items-center gap-2 font-sans text-[10px] font-semibold uppercase tracking-widest text-accent">
          <Navigation className="size-3.5" />
          Advisories
        </div>
        <ul className="space-y-2">
          {RECOMMENDATIONS.map((rec, i) => (
            <li key={i} className="flex gap-2 font-mono text-[11px] leading-relaxed text-foreground">
              <AlertTriangle className="mt-0.5 size-3.5 shrink-0 text-warning" />
              <span>{rec}</span>
            </li>
          ))}
        </ul>
      </div>
    </Panel>
  )
}
