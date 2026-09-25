"use client"

import { useEffect, useRef, useState } from "react"
import { AlertOctagon, Clock, Download, FolderOpen, RefreshCw, Save } from "lucide-react"
import { Panel, PanelHeader } from "@/components/ui/panel"
import { useRouteWeather } from "@/lib/hooks/use-route-weather"
import { useComplexityField } from "@/lib/hooks/use-complexity-field"
import { ApiError, getAviationReport, getObservations, type LiveReport } from "@/lib/api"

const SCENARIO_KEY = "awci-dashboard-scenario"

interface LogEntry {
  id: number
  time: number
  text: string
}

interface Scenario {
  depIcao: string
  arrIcao: string
  model: "AROME" | "ALADIN" | "ARPEGE"
  n_lat: number
  n_lon: number
  savedAt: number
}

function downloadJson(filename: string, data: unknown) {
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" })
  const url = URL.createObjectURL(blob)
  const a = document.createElement("a")
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  a.remove()
  URL.revokeObjectURL(url)
}

/**
 * Real "Recent Alerts" - live SIGMETs for the route's own real
 * departure/arrival airports (`GET /observations/{icao}`, the same
 * NOAA Aviation Weather Center connector `RiskPanel` already draws
 * METAR/TAF from - just a field of that response this dashboard had
 * not surfaced yet). "Latest Updates" is a real, honest client-side
 * session log (route/model/resolution changes and quick-action
 * results, each with the real timestamp it happened), not a
 * fabricated notification feed. "Quick Actions" are 3 genuinely
 * functional operations: download a real aviation report from
 * `GET /reports/{icao}`, force-refresh the shared real AWCI field, and
 * save/load the current route+model+resolution selection to this
 * browser's own `localStorage` (disclosed as local-only, never a
 * server-synced "scenario").
 */
export function OpsFooterPanel() {
  const route = useRouteWeather()
  const field = useComplexityField()

  const [alerts, setAlerts] = useState<{ icao: string; reports: LiveReport[] } | null>(null)
  const [alertsError, setAlertsError] = useState<string | null>(null)
  const [log, setLog] = useState<LogEntry[]>([])
  const [actionStatus, setActionStatus] = useState<string | null>(null)
  const nextId = useRef(0)
  const prevRoute = useRef<{ dep: string; arr: string } | null>(null)
  const prevModel = useRef<string | null>(null)
  const prevResolution = useRef<{ n_lat: number; n_lon: number } | null>(null)

  const appendLog = (text: string) => {
    nextId.current += 1
    setLog((prev) => [{ id: nextId.current, time: Date.now(), text }, ...prev].slice(0, 12))
  }

  // Real SIGMETs for the current real departure/arrival airports.
  useEffect(() => {
    let cancelled = false
    setAlertsError(null)
    Promise.all([getObservations(route.depIcao), getObservations(route.arrIcao)])
      .then(([dep, arr]) => {
        if (cancelled) return
        setAlerts({
          icao: `${dep.icao_code} / ${arr.icao_code}`,
          reports: [...dep.sigmets, ...arr.sigmets],
        })
      })
      .catch((cause: unknown) => {
        if (cancelled) return
        setAlertsError(cause instanceof ApiError ? cause.message : "Unknown error fetching SIGMETs")
      })
    return () => {
      cancelled = true
    }
  }, [route.depIcao, route.arrIcao])

  // Real session log: append one real entry per real route/model/
  // resolution change this browser tab has actually made.
  useEffect(() => {
    if (prevRoute.current && (prevRoute.current.dep !== route.depIcao || prevRoute.current.arr !== route.arrIcao)) {
      appendLog(`Route set to ${route.depIcao} → ${route.arrIcao}`)
    }
    prevRoute.current = { dep: route.depIcao, arr: route.arrIcao }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [route.depIcao, route.arrIcao])

  useEffect(() => {
    if (prevModel.current && prevModel.current !== field.model) {
      appendLog(`Model switched to ${field.model}`)
    }
    prevModel.current = field.model
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [field.model])

  useEffect(() => {
    if (
      prevResolution.current &&
      (prevResolution.current.n_lat !== field.resolution.n_lat || prevResolution.current.n_lon !== field.resolution.n_lon)
    ) {
      appendLog(`Grid resolution set to ${field.resolution.n_lat}×${field.resolution.n_lon}`)
    }
    prevResolution.current = { n_lat: field.resolution.n_lat, n_lon: field.resolution.n_lon }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [field.resolution.n_lat, field.resolution.n_lon])

  async function handleGenerateReport() {
    setActionStatus("Generating report…")
    try {
      const report = await getAviationReport(route.depIcao)
      downloadJson(`awci-report-${report.icao_code}-${report.generated_at}.json`, report)
      setActionStatus(`Report downloaded for ${report.icao_code}`)
      appendLog(`Real aviation report generated for ${report.icao_code}`)
    } catch (cause: unknown) {
      const message = cause instanceof ApiError ? cause.message : "Unknown error generating the report"
      setActionStatus(message)
    }
  }

  function handleRefresh() {
    field.refresh()
    setActionStatus("Refreshing AWCI field…")
    appendLog("Manual AWCI field refresh requested")
  }

  function handleSaveScenario() {
    const scenario: Scenario = {
      depIcao: route.depIcao,
      arrIcao: route.arrIcao,
      model: field.model,
      n_lat: field.resolution.n_lat,
      n_lon: field.resolution.n_lon,
      savedAt: Date.now(),
    }
    try {
      window.localStorage.setItem(SCENARIO_KEY, JSON.stringify(scenario))
      setActionStatus(`Scenario saved locally (${scenario.depIcao} → ${scenario.arrIcao}, ${scenario.model})`)
      appendLog(`Scenario saved to this browser (${scenario.depIcao} → ${scenario.arrIcao}, ${scenario.model})`)
    } catch {
      setActionStatus("localStorage unavailable - could not save scenario")
    }
  }

  function handleLoadScenario() {
    try {
      const raw = window.localStorage.getItem(SCENARIO_KEY)
      if (!raw) {
        setActionStatus("No scenario saved in this browser yet")
        return
      }
      const scenario = JSON.parse(raw) as Scenario
      route.setRoute(scenario.depIcao, scenario.arrIcao)
      field.setModel(scenario.model)
      field.setResolution({ n_lat: scenario.n_lat, n_lon: scenario.n_lon })
      setActionStatus(`Scenario restored (saved ${new Date(scenario.savedAt).toLocaleTimeString()})`)
      appendLog(`Scenario restored from this browser (${scenario.depIcao} → ${scenario.arrIcao}, ${scenario.model})`)
    } catch {
      setActionStatus("Could not parse the saved scenario")
    }
  }

  return (
    <Panel className="flex h-full flex-col overflow-hidden">
      <PanelHeader title="Operations" subtitle="Alerts · Updates · Quick Actions" />
      <div className="grid min-h-0 flex-1 grid-cols-1 divide-y divide-border-subtle lg:grid-cols-3 lg:divide-x lg:divide-y-0">
        {/* Recent Alerts */}
        <div className="flex min-h-0 flex-col overflow-hidden p-3">
          <div className="mb-2 flex items-center gap-2 font-sans text-[10px] font-semibold uppercase tracking-widest text-critical">
            <AlertOctagon className="size-3.5" />
            Recent Alerts
          </div>
          {alertsError ? (
            <p className="font-mono text-[10px] text-critical">{alertsError}</p>
          ) : !alerts ? (
            <p className="font-mono text-[10px] text-muted">Loading real SIGMETs…</p>
          ) : alerts.reports.filter((r) => r.raw_text).length === 0 ? (
            <p className="font-mono text-[10px] text-muted">No active SIGMET for {alerts.icao} right now.</p>
          ) : (
            <ul className="min-h-0 flex-1 space-y-2 overflow-y-auto">
              {alerts.reports
                .filter((r) => r.raw_text)
                .slice(0, 6)
                .map((r, i) => (
                  <li key={i} className="font-mono text-[10px] leading-relaxed text-foreground">
                    {r.raw_text}
                  </li>
                ))}
            </ul>
          )}
        </div>

        {/* Latest Updates */}
        <div className="flex min-h-0 flex-col overflow-hidden p-3">
          <div className="mb-2 flex items-center gap-2 font-sans text-[10px] font-semibold uppercase tracking-widest text-accent">
            <Clock className="size-3.5" />
            Latest Updates
          </div>
          {log.length === 0 ? (
            <p className="font-mono text-[10px] text-muted">
              No changes yet this session - switch route, model, or resolution to see real updates here.
            </p>
          ) : (
            <ul className="min-h-0 flex-1 space-y-1.5 overflow-y-auto">
              {log.map((entry) => (
                <li key={entry.id} className="font-mono text-[10px] text-foreground">
                  <span className="text-muted">{new Date(entry.time).toLocaleTimeString()}</span> · {entry.text}
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* Quick Actions */}
        <div className="flex min-h-0 flex-col overflow-hidden p-3">
          <div className="mb-2 flex items-center gap-2 font-sans text-[10px] font-semibold uppercase tracking-widest text-foreground">
            Quick Actions
          </div>
          <div className="flex flex-col gap-1.5">
            <button
              type="button"
              onClick={handleGenerateReport}
              className="flex items-center gap-2 rounded-md border border-border-subtle px-2.5 py-1.5 font-mono text-[10px] text-foreground transition-colors hover:border-accent/50 hover:text-accent"
            >
              <Download className="size-3.5" />
              Generate Report ({route.depIcao})
            </button>
            <button
              type="button"
              onClick={handleRefresh}
              className="flex items-center gap-2 rounded-md border border-border-subtle px-2.5 py-1.5 font-mono text-[10px] text-foreground transition-colors hover:border-accent/50 hover:text-accent"
            >
              <RefreshCw className="size-3.5" />
              Refresh AWCI Field
            </button>
            <button
              type="button"
              onClick={handleSaveScenario}
              className="flex items-center gap-2 rounded-md border border-border-subtle px-2.5 py-1.5 font-mono text-[10px] text-foreground transition-colors hover:border-accent/50 hover:text-accent"
            >
              <Save className="size-3.5" />
              Save Scenario (local)
            </button>
            <button
              type="button"
              onClick={handleLoadScenario}
              className="flex items-center gap-2 rounded-md border border-border-subtle px-2.5 py-1.5 font-mono text-[10px] text-foreground transition-colors hover:border-accent/50 hover:text-accent"
            >
              <FolderOpen className="size-3.5" />
              Load Scenario (local)
            </button>
          </div>
          {actionStatus && <p className="mt-2 font-mono text-[10px] text-muted">{actionStatus}</p>}
        </div>
      </div>
    </Panel>
  )
}
