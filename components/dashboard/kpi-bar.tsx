import { ArrowDownRight, ArrowUpRight } from "lucide-react"
import { Panel } from "@/components/ui/panel"
import { KPIS } from "@/lib/data"
import { cn } from "@/lib/utils"

const toneText: Record<string, string> = {
  normal: "text-accent",
  warning: "text-warning",
  critical: "text-critical",
}

export function KpiBar() {
  return (
    <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
      {KPIS.map((k) => {
        const up = k.trend.trim().startsWith("+")
        return (
          <Panel key={k.label} className="relative overflow-hidden p-3">
            <div
              className={cn(
                "absolute inset-x-0 top-0 h-0.5",
                k.tone === "critical"
                  ? "bg-critical"
                  : k.tone === "warning"
                    ? "bg-warning"
                    : "bg-accent",
              )}
            />
            <p className="font-sans text-[10px] font-medium uppercase tracking-[0.14em] text-muted">
              {k.label}
            </p>
            <div className="mt-2 flex items-baseline gap-1.5">
              <span className={cn("font-mono text-2xl font-bold leading-none tabular-nums", toneText[k.tone])}>
                {k.value}
              </span>
              <span className="font-mono text-[11px] text-muted">{k.unit}</span>
            </div>
            <div className="mt-2 flex items-center gap-1 font-mono text-[11px]">
              {up ? (
                <ArrowUpRight className="size-3.5 text-critical" />
              ) : (
                <ArrowDownRight className="size-3.5 text-accent" />
              )}
              <span className={up ? "text-critical" : "text-accent"}>{k.trend}</span>
              <span className="text-muted">vs 6h</span>
            </div>
          </Panel>
        )
      })}
    </div>
  )
}
