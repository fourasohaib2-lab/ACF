"use client"

import { Layers } from "lucide-react"
import { cn } from "@/lib/utils"

/** Real AWCICalculator module fields available at the field's default
 * weights (see radar-complexity.tsx's own comment on which modules
 * carry non-zero default weight). "Wind Vectors"/"ATS Routes" from
 * the original mockup layer list are not real toggleable data layers
 * here: no raw wind-vector field is exposed by the API (only scalar
 * wind speed feeds the dynamic module) - ATS Routes is instead always
 * shown when a route is loaded (see ComplexityMap's showRoute). */
export const MAP_LAYERS: { id: string; label: string }[] = [
  { id: "awci", label: "AWCI Composite" },
  { id: "convective", label: "Convective" },
  { id: "thermodynamic", label: "Thermodynamic" },
  { id: "dynamic", label: "Dynamic (Wind)" },
]

export function LayerSelector({
  activeLayer,
  onChange,
}: {
  activeLayer: string
  onChange: (id: string) => void
}) {
  return (
    <div className="pointer-events-auto absolute left-3 top-3 z-[1000] w-44 rounded-md border border-white/10 bg-black/50 p-3 backdrop-blur-md">
      <div className="mb-2 flex items-center gap-2 font-sans text-[10px] font-semibold uppercase tracking-widest text-foreground">
        <Layers className="size-3.5 text-accent" />
        Layer
      </div>
      <ul className="space-y-1.5">
        {MAP_LAYERS.map((l) => (
          <li key={l.id}>
            <button
              type="button"
              onClick={() => onChange(l.id)}
              className="flex w-full items-center gap-2 font-mono text-[11px] text-muted transition-colors hover:text-foreground"
            >
              <span
                className={cn(
                  "flex size-3.5 items-center justify-center rounded-sm border",
                  activeLayer === l.id ? "border-accent bg-accent/20 text-accent" : "border-white/20 text-transparent",
                )}
              >
                <span className="size-1.5 rounded-[1px] bg-accent" />
              </span>
              <span className={activeLayer === l.id ? "text-foreground" : ""}>{l.label}</span>
            </button>
          </li>
        ))}
      </ul>
    </div>
  )
}
