import { cn } from "@/lib/utils"

export function Panel({
  className,
  children,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        "rounded-md border border-border-subtle bg-panel",
        className,
      )}
      {...props}
    >
      {children}
    </div>
  )
}

export function PanelHeader({
  title,
  subtitle,
  right,
  className,
}: {
  title: string
  subtitle?: string
  right?: React.ReactNode
  className?: string
}) {
  return (
    <div
      className={cn(
        "flex items-center justify-between gap-3 border-b border-border-subtle px-3 py-2",
        className,
      )}
    >
      <div className="min-w-0">
        <h2 className="truncate font-sans text-[11px] font-semibold uppercase tracking-[0.18em] text-foreground">
          {title}
        </h2>
        {subtitle ? (
          <p className="truncate font-mono text-[10px] uppercase tracking-widest text-muted">
            {subtitle}
          </p>
        ) : null}
      </div>
      {right ? <div className="flex shrink-0 items-center gap-2">{right}</div> : null}
    </div>
  )
}
