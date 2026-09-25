import { turboCss } from "@/lib/utils"

export function TurboLegend() {
  const stops = Array.from({ length: 12 }, (_, i) => turboCss(i / 11, 1)).join(", ")
  return (
    <div className="w-40">
      <div className="mb-1 flex items-center justify-between font-mono text-[9px] uppercase tracking-wider text-muted">
        <span>AWCI</span>
        <span>index</span>
      </div>
      <div
        className="h-2 w-full rounded-sm"
        style={{ background: `linear-gradient(to right, ${stops})` }}
      />
      <div className="mt-1 flex justify-between font-mono text-[9px] text-muted">
        <span>0</span>
        <span>25</span>
        <span>50</span>
        <span>75</span>
        <span>100</span>
      </div>
    </div>
  )
}
