import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { KpiRow } from "./KpiRow";

test("KPI cards show value, unit, text badge and select their layer", async () => {
  const onSelect = vi.fn();
  render(<KpiRow classIndex={2} summary={{ awci_p95: 57.2, awci_class: "Moderate", turbulence_area_pct: 18.4, convection_area_pct: 2,
    mucape_max: 1800, icing_area_pct: null, shear_p95: 0.006, heavy_precip_area_pct: 0, low_ceiling_area_pct: 1.2,
    cb_area_pct: 13, valid_cells_pct: 99, badges: { turbulence_area_pct: "serious", shear_p95: "attention",
    icing_area_pct: null, convection_area_pct: "ok", cb_area_pct: "attention", low_ceiling_area_pct: "ok",
    heavy_precip_area_pct: "ok" }, awci_p95_by_level: [] } as never} onSelectLayer={onSelect} />);
  expect(screen.getByText((_, el) => !!el?.classList.contains("kpi-value") && el.textContent === "18,4 %")).toBeInTheDocument();
  expect(screen.getAllByText(/sérieux/i).length).toBeGreaterThan(0);
  expect(screen.getByText(/givrage/i).closest("button")).toHaveTextContent("—");
  await userEvent.click(screen.getByRole("button", { name: /turbulence/i }));
  expect(onSelect).toHaveBeenCalledWith("cat_category");
});
