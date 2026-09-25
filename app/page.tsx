import { DashboardHeader } from "@/components/dashboard/header"
import { Sidebar } from "@/components/dashboard/sidebar"
import { ControlBar } from "@/components/dashboard/control-bar"
import { HazardBand } from "@/components/dashboard/hazard-band"
import { KpiBar } from "@/components/dashboard/kpi-bar"
import { GlobalMap } from "@/components/dashboard/global-map"
import { RegionalMap } from "@/components/dashboard/regional-map"
import { VerticalCrossSection } from "@/components/dashboard/vertical-cross-section"
import { RadarComplexity } from "@/components/dashboard/radar-complexity"
import { RouteProfile } from "@/components/dashboard/route-profile"
import { RiskPanel } from "@/components/dashboard/risk-panel"
import { FooterBar } from "@/components/dashboard/footer-bar"
import { ComplexityFieldProvider } from "@/lib/hooks/use-complexity-field"
import { RouteWeatherProvider } from "@/lib/hooks/use-route-weather"

export default function Page() {
  return (
    <ComplexityFieldProvider>
      <RouteWeatherProvider>
        <div className="flex min-h-screen bg-background">
          <Sidebar />

          <div className="flex min-h-screen flex-1 flex-col overflow-hidden">
            <DashboardHeader />

            <main className="flex-1 space-y-3 p-3 md:p-4">
              <section id="overview" className="scroll-mt-3 space-y-3">
                <ControlBar />
                <HazardBand />
                <KpiBar />
              </section>

              {/* Maps row */}
              <section id="map" className="scroll-mt-3 grid grid-cols-1 gap-3 xl:grid-cols-3">
                <div className="xl:col-span-2">
                  <GlobalMap />
                </div>
                <div>
                  <RegionalMap />
                </div>
              </section>

              <section id="hazards" className="scroll-mt-3">
                <RiskPanel />
              </section>

              {/* Analytics row */}
              <section id="analysis" className="scroll-mt-3 grid grid-cols-1 gap-3 lg:grid-cols-2 xl:grid-cols-3">
                <VerticalCrossSection />
                <RadarComplexity />
                <div className="lg:col-span-2 xl:col-span-1">
                  <RouteProfile />
                </div>
              </section>
            </main>

            <section id="reports" className="scroll-mt-3">
              <FooterBar />
            </section>
          </div>
        </div>
      </RouteWeatherProvider>
    </ComplexityFieldProvider>
  )
}
