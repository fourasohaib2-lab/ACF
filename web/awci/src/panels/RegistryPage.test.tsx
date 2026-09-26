import { render, screen } from "@testing-library/react";
import { RegistryPage } from "./RegistryPage";

test("registry page lists every layer with its status as text and links the OpenAPI docs", () => {
  render(<RegistryPage registry={{
    layers: {
      awci: { name: "awci", label: "AWCI", unit: "0-100", per_level: true, equation: "weighted", source: "ACF", status: "HYPOTHESIS" },
      mucape: { name: "mucape", label: "MUCAPE", unit: "J/kg", per_level: false, equation: "IFS field", source: "ECMWF IFS", status: "CONFIRMED" },
    },
    classes: [{ upper_bound: 20, label: "Very Low" }, { upper_bound: null, label: "Extreme" }],
    profile: { name: "operational-v1", version: "1.0.0", weights: {}, min_present_weight: 0.5 },
    cloud_profile: { name: "cloud-v1", version: "1.1.0" }, codes: {}, summary_thresholds: { status: "HYPOTHESIS" },
    attribution: "© ECMWF, CC-BY-4.0", license: "CC-BY-4.0",
  } as never} />);
  expect(screen.getAllByRole("row").length).toBeGreaterThanOrEqual(3);
  expect(screen.getByText("CONFIRMED")).toBeInTheDocument();
  expect(screen.getByRole("link", { name: /openapi/i })).toHaveAttribute("href", "/docs");
});
