"use client"

import { useEffect, useRef, useState } from "react"
import { AlertTriangle, Loader2 } from "lucide-react"
import { CartesianGrid, Line, ComposedChart, ResponsiveContainer, Tooltip, XAxis, YAxis, Legend } from "recharts"
import { Panel, PanelHeader } from "@/components/ui/panel"
import { useComplexityField } from "@/lib/hooks/use-complexity-field"
import { meanField, maxField } from "@/lib/complexity-stats"

const MAX_HISTORY = 30

interface HistoryPoint {
  fetchedAt: number
  mean: number | null
  max: number | null
  model: string
}

/**
 * Real "Time Evolution" - NOT a forecast trend (this codebase has no
 * real time-stepped forecast to plot one from). Instead, this is a
 * genuine client-side session log: every time the shared AWCI field
 * (`ComplexityFieldProvider`) resolves a real new fetch (on model
 * switch, resolution change, or manual refresh), this panel appends
 * one real data point - the real client timestamp it arrived at, and
 * the real global mean/max of that real field
 * (`lib/complexity-stats.ts`). The history starts empty on page load
 * and holds only what this browser session has actually observed -
 * disclosed honestly below, never backfilled with invented past
 * values.
 */
export function TimeEvolution() {
  const field = useComplexityField()
  const [history, setHistory] = useState<HistoryPoint[]>([])
  const lastFetchedAt = useRef<number | null>(null)

  useEffect(() => {
    if (field.fetchedAt === null || field.fetchedAt === lastFetchedAt.current || !field.data) return
    lastFetchedAt.current = field.fetchedAt
    const point: HistoryPoint = {
      fetchedAt: field.fetchedAt,
      mean: meanField(field.data.awci_field),
      max: maxField(field.data.awci_field),
      model: field.data.model,
    }
    setHistory((prev) => [...prev, point].slice(-MAX_HISTORY))
  }, [field.fetchedAt, field.data])

  if (field.error) {
    return (
      <Panel className="flex h-full flex-col overflow-hidden">
        <PanelHeader title="Time Evolution" subtitle="Session AWCI History" />
        <div className="flex flex-1 items-center gap-2 p-4 text-critical">
          <AlertTriangle className="size-4 shrink-0" />
          <p className="font-mono text-[11px]">{field.error}</p>
        </div>
      </Panel>
    )
  }

  if (history.length === 0) {
    return (
      <Panel className="flex h-full flex-col overflow-hidden">
        <PanelHeader title="Time Evolution" subtitle="Session AWCI History" />
        <div className="flex flex-1 items-center justify-center text-muted">
          <Loader2 className="size-5 animate-spin" />
        </div>
      </Panel>
    )
  }

  const chartData = history.map((p) => ({
    time: new Date(p.fetchedAt).toLocaleTimeString(undefined, { hour: "2-digit", minute: "2-digit", second: "2-digit" }),
    mean: p.mean,
    max: p.max,
  }))
  const values = history.flatMap((p) => [p.mean, p.max]).filter((v): v is number => v !== null)
  const dataMin = values.length > 0 ? Math.min(...values) : 0
  const dataMax = values.length > 0 ? Math.max(...values) : 100
  const pad = Math.max(2, (dataMax - dataMin) * 0.2)
  const yDomain: [number, number] = [Math.max(0, Math.floor(dataMin - pad)), Math.min(100, Math.ceil(dataMax + pad))]

  return (
    <Panel className="flex h-full flex-col overflow-hidden">
      <PanelHeader
        title="Time Evolution"
        subtitle="Session AWCI History"
        right={<span className="font-mono text-[10px] text-muted">{history.length} real fetch(es)</span>}
      />
      <div className="min-h-0 flex-1 p-2">
        <ResponsiveContainer width="100%" height="100%" minHeight={200}>
          <ComposedChart data={chartData} margin={{ top: 8, right: 8, bottom: 0, left: -12 }}>
            <CartesianGrid stroke="var(--border-subtle)" strokeDasharray="2 4" vertical={false} />
            <XAxis
              dataKey="time"
              tick={{ fill: "var(--muted)", fontSize: 9, fontFamily: "var(--font-mono)" }}
              tickLine={false}
              axisLine={{ stroke: "var(--border-subtle)" }}
            />
            <YAxis
              domain={yDomain}
              tick={{ fill: "var(--muted)", fontSize: 9, fontFamily: "var(--font-mono)" }}
              tickLine={false}
              axisLine={false}
              width={28}
            />
            <Tooltip
              contentStyle={{
                background: "rgba(6,9,15,0.92)",
                border: "1px solid var(--border-subtle)",
                borderRadius: 6,
                fontFamily: "var(--font-mono)",
                fontSize: 11,
              }}
              labelStyle={{ color: "var(--muted)" }}
              formatter={(value, name) => [typeof value === "number" ? value.toFixed(1) : "—", name]}
            />
            <Legend
              wrapperStyle={{ fontFamily: "var(--font-mono)", fontSize: 9, color: "var(--muted)" }}
              iconType="plainline"
            />
            <Line type="monotone" dataKey="mean" name="Mean AWCI" stroke="var(--accent)" strokeWidth={1.5} dot />
            <Line type="monotone" dataKey="max" name="Max AWCI" stroke="var(--critical)" strokeWidth={1.5} dot />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
      <div className="border-t border-border-subtle px-3 py-1.5 font-mono text-[10px] text-muted">
        A real client-side session log, not a forecast: one point per real field fetch this browser tab has observed
        since it opened (model switch, resolution change, or refresh) - never a fabricated future trend.
      </div>
    </Panel>
  )
}
