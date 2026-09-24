import { DashboardHeader } from "@/components/dashboard/header"
import { KpiBar } from "@/components/dashboard/kpi-bar"
import { GlobalMap } from "@/components/dashboard/global-map"
import { RegionalMap } from "@/components/dashboard/regional-map"
import { VerticalCrossSection } from "@/components/dashboard/vertical-cross-section"
import { RadarComplexity } from "@/components/dashboard/radar-complexity"
import { RouteProfile } from "@/components/dashboard/route-profile"
import { RiskPanel } from "@/components/dashboard/risk-panel"
import { FooterBar } from "@/components/dashboard/footer-bar"

export default function Page() {
  return (
    <div className="flex min-h-screen flex-col bg-background">
      <DashboardHeader />

      <main className="flex-1 space-y-3 p-3 md:p-4">
        <KpiBar />

        {/* Maps row */}
        <div className="grid grid-cols-1 gap-3 xl:grid-cols-3">
          <div className="xl:col-span-2">
            <GlobalMap />
          </div>
          <div>
            <RegionalMap />
          </div>
        </div>

        {/* Analytics row */}
        <div className="grid grid-cols-1 gap-3 lg:grid-cols-2 xl:grid-cols-4">
          <VerticalCrossSection />
          <RadarComplexity />
          <div className="lg:col-span-2 xl:col-span-1 xl:row-span-1">
            <RouteProfile />
          </div>
          <RiskPanel />
        </div>
      </main>

      <FooterBar />
    </div>
  )
}
