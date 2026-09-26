import { render, screen, within } from "@testing-library/react";
import type { ComparePoint } from "../api/types";
import real from "../test-data/compare_point_fixture.json";
import { ModelAgreement } from "./ModelAgreement";

const data = real as unknown as ComparePoint;
const BOUNDS = [20, 35, 50, 65, 85];
const LABELS = ["Very Low", "Low", "Moderate", "High", "Very High", "Extreme"];

describe("ModelAgreement (real /compare/point, IFS and GFS 2026-09-25 00Z +3 h, 850 hPa, Algiers)", () => {
  it("sets IFS and GFS side by side and states the agreement", () => {
    render(<ModelAgreement data={data} isLoading={false} error={null} classLabels={LABELS} awciBounds={BOUNDS} />);
    const table = screen.getByRole("table", { name: "Valeurs IFS et GFS au point" });
    const awci = within(table).getByRole("row", { name: /^AWCI/ });
    expect(awci).toHaveTextContent(String(Math.round(data.models.ifs.values.awci!)));
    expect(awci).toHaveTextContent(String(Math.round(data.models.gfs.values.awci!)));
    expect(screen.getByRole("status")).toHaveTextContent("Même classe AWCI (Very Low)");
    expect(screen.getByRole("status")).toHaveTextContent("Aucun désaccord sur les dangers");
    expect(screen.getByText(/Différences de définition GFS/)).toBeInTheDocument();
  });

  it("names a hazard seen by one model only", () => {
    const icing = structuredClone(data);
    icing.models.gfs.values.icing_potential = 1;
    icing.models.ifs.values.icing_potential = 0;
    render(<ModelAgreement data={icing} isLoading={false} error={null} classLabels={LABELS} awciBounds={BOUNDS} />);
    expect(screen.getByRole("status")).toHaveTextContent("Désaccord sur : Givrage potentiel : GFS seul");
    expect(screen.getByRole("row", { name: /^Givrage potentiel/ })).toHaveTextContent("désaccord");
  });

  it("says why there is no comparison", () => {
    render(<ModelAgreement data={undefined} isLoading={false} error={null} classLabels={LABELS} awciBounds={BOUNDS}
                           unavailable="Pas de run GFS 2026092512 : aucune comparaison." />);
    expect(screen.getByText(/Pas de run GFS 2026092512/)).toBeInTheDocument();
  });
});
