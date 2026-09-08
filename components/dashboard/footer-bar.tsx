export function FooterBar() {
  return (
    <footer className="flex flex-wrap items-center justify-between gap-2 border-t border-border-subtle bg-panel/40 px-4 py-2 font-mono text-[10px] uppercase tracking-wider text-muted">
      <div className="flex flex-wrap items-center gap-x-4 gap-y-1">
        <span>SRC · ECMWF-HRES / GFS / RAP</span>
        <span>GRID · 0.1°</span>
        <span>PROJ · EPSG:4326</span>
      </div>
      <div className="flex items-center gap-2">
        <span className="size-1.5 rounded-full bg-accent" />
        <span className="text-accent">SYNC OK</span>
        <span>· AWCI v2.4 · REFERENCE UI</span>
      </div>
    </footer>
  )
}
