"use client"

import { useEffect, useMemo, useRef, useState } from "react"
import { Search } from "lucide-react"
import type { AirportInfo } from "@/lib/api"

const MAX_RESULTS = 40

/**
 * Real searchable airport picker - replaces a plain `<select>` now
 * that `AirportDatabase` holds ~10,500 real world airports (task:
 * "ajoute tous les aéroports du monde"), too many for a usable native
 * dropdown. Filters the already-fetched real airport list client-side
 * by ICAO code, IATA code, name, or city (case-insensitive substring
 * match) - capped to the top `MAX_RESULTS` matches rendered at once so
 * typing a query never renders thousands of DOM rows.
 */
export function AirportCombobox({
  label,
  airports,
  value,
  onChange,
  disabled,
}: {
  label: string
  airports: AirportInfo[] | null
  value: string
  onChange: (icaoCode: string) => void
  disabled?: boolean
}) {
  const [query, setQuery] = useState("")
  const [open, setOpen] = useState(false)
  const rootRef = useRef<HTMLDivElement | null>(null)

  const selected = useMemo(() => airports?.find((a) => a.icao_code === value) ?? null, [airports, value])

  useEffect(() => {
    function onClickOutside(e: MouseEvent) {
      if (rootRef.current && !rootRef.current.contains(e.target as Node)) setOpen(false)
    }
    document.addEventListener("mousedown", onClickOutside)
    return () => document.removeEventListener("mousedown", onClickOutside)
  }, [])

  const results = useMemo(() => {
    if (!airports) return []
    const q = query.trim().toLowerCase()
    if (!q) return airports.slice(0, MAX_RESULTS)
    const matches = airports.filter(
      (a) =>
        a.icao_code.toLowerCase().includes(q) ||
        (a.iata_code?.toLowerCase().includes(q) ?? false) ||
        a.name.toLowerCase().includes(q) ||
        a.city.toLowerCase().includes(q),
    )
    return matches.slice(0, MAX_RESULTS)
  }, [airports, query])

  function select(a: AirportInfo) {
    onChange(a.icao_code)
    setQuery("")
    setOpen(false)
  }

  return (
    <div ref={rootRef} className="relative">
      <button
        type="button"
        aria-label={label}
        disabled={disabled || !airports}
        onClick={() => setOpen((o) => !o)}
        className="flex min-w-[220px] items-center gap-1.5 rounded-md border border-border-subtle bg-panel px-2 py-1.5 font-mono text-[11px] text-foreground outline-none transition-colors hover:border-accent/50 focus:border-accent disabled:opacity-50"
      >
        <Search className="size-3 shrink-0 text-muted" />
        <span className="truncate">
          {selected ? (
            <>
              {selected.icao_code} <span className="text-muted">· {selected.name}</span>
            </>
          ) : (
            value || "Select airport…"
          )}
        </span>
      </button>

      {open && airports && (
        <div className="absolute left-0 top-full z-50 mt-1 w-80 overflow-hidden rounded-md border border-border-subtle bg-panel-raised shadow-lg">
          <input
            autoFocus
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search ICAO, IATA, name, city…"
            className="w-full border-b border-border-subtle bg-transparent px-2.5 py-2 font-mono text-[11px] text-foreground outline-none placeholder:text-muted"
          />
          <ul className="scroll-thin max-h-72 overflow-y-auto">
            {results.length === 0 ? (
              <li className="px-2.5 py-3 font-mono text-[11px] text-muted">No match among {airports.length} real airports.</li>
            ) : (
              results.map((a) => (
                <li key={a.icao_code}>
                  <button
                    type="button"
                    onClick={() => select(a)}
                    className={`flex w-full flex-col items-start gap-0.5 px-2.5 py-1.5 text-left font-mono text-[11px] transition-colors hover:bg-accent/10 ${a.icao_code === value ? "bg-accent/15 text-accent" : "text-foreground"}`}
                  >
                    <span>
                      {a.icao_code}
                      {a.iata_code ? ` / ${a.iata_code}` : ""} · {a.name}
                    </span>
                    <span className="text-[10px] text-muted">
                      {a.city ? `${a.city}, ` : ""}
                      {a.country}
                    </span>
                  </button>
                </li>
              ))
            )}
          </ul>
          {results.length === MAX_RESULTS && (
            <div className="border-t border-border-subtle px-2.5 py-1 font-mono text-[9px] text-muted">
              Top {MAX_RESULTS} matches of {airports.length} real airports - refine your search.
            </div>
          )}
        </div>
      )}
    </div>
  )
}
