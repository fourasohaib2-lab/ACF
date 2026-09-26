import { render, screen } from "@testing-library/react";
import { CloudsPanel } from "./CloudsPanel";

test("clouds panel lists layers with genus, oktas and the model METAR line", () => {
  render(<CloudsPanel currentStep={24} series={undefined} clouds={{ lat: 36.75, lon: 3, elevation_m: 20,
    layers: [{ kind: "layer", genus: "Sc", etage: "low", species: ["castellanus"], base_agl_m: 900, base_ft: 2952,
      base_fl: 30, base_uncertainty_m: 300, top_amsl_m: 1500, top_fl: 50, oktas: 6, amount: "BKN" },
      { kind: "convective", genus: "Cb", etage: null, species: ["capillatus"], base_agl_m: 800, base_ft: 2624,
        base_uncertainty_m: null, top_amsl_m: 12000, top_fl: null, oktas: null, amount: null }],
    metar: "MODEL ///026CB BKN029", ceiling_m: 900, ceiling_ft: 2952,
    convective: { class: 4, label: "Cb capillatus", top_m: 12000, top_temp_k: 216 }, cloud_top_teff_k: 212,
    column_condensate: 1.2, tcc: 0.9, cloud_cover_bias: -0.05, etage_bounds_fl: { low_mid: 62, mid_high: 216 },
    run_cloud_status: "ok", scientific_status: { cloud_genus: "HYPOTHESIS" } } as never} />);
  expect(screen.getByText("MODEL ///026CB BKN029")).toBeInTheDocument();
  expect(screen.getByText(/Sc castellanus/)).toBeInTheDocument();
  expect(screen.getAllByText(/BKN/).length).toBeGreaterThanOrEqual(2); // layer label and METAR line
  expect(screen.getByText(/diagnostic modèle/i)).toBeInTheDocument();
});
